import subprocess
import json
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone
import httpx
from packaging import version
import logging

from core.config import settings
from .models import ChangelogEntry, ChangelogView, LastProcessedCommit, ChangeType


class GitService:
    """Service for git operations"""
    
    @staticmethod
    def get_commits_since(hash_since: Optional[str] = None) -> List[Dict]:
        """Get git commits since a specific hash"""
        try:
            # Get commits with detailed information
            cmd = [
                "git", "log", "--pretty=format:%H|%an|%ae|%ad|%s|%b",
                "--date=iso"
            ]
            
            if hash_since:
                cmd.append(f"{hash_since}..HEAD")
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
            
            if result.returncode != 0:
                raise Exception(f"Git command failed: {result.stderr}")
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                    
                parts = line.split('|', 5)
                if len(parts) >= 5:
                    commit_hash, author_name, author_email, date_str, subject = parts[:5]
                    body = parts[5] if len(parts) > 5 else ""
                    
                    # Parse date
                    try:
                        commit_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except:
                        commit_date = datetime.now(timezone.utc)
                    
                    commits.append({
                        "hash": commit_hash,
                        "author_name": author_name,
                        "author_email": author_email,
                        "date": commit_date,
                        "subject": subject,
                        "body": body
                    })
            
            return commits
            
        except Exception as e:
            raise Exception(f"Failed to get git commits: {str(e)}")
    
    @staticmethod
    def get_last_commit_hash() -> Optional[str]:
        """Get the hash of the last commit"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd="."
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            return None
            
        except Exception:
            return None
    
    @staticmethod
    def get_current_version() -> str:
        """Get current version from git tags or default to 1.0.0"""
        try:
            # Get the latest tag
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                capture_output=True,
                text=True,
                cwd="."
            )
            
            if result.returncode == 0:
                tag = result.stdout.strip()
                # Remove 'v' prefix if present
                if tag.startswith('v'):
                    tag = tag[1:]
                return tag
            
            return "1.0.0"
            
        except Exception:
            return "1.0.0"


class DeepSeekService:
    """Service for DeepSeek AI integration"""
    
    def __init__(self):
        self.api_key = settings.deepseek_api_key
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
        

        
        self.base_url = "https://api.deepseek.com/v1"
        self.timeout = getattr(settings, "deepseek_timeout", 30.0)
        self.logger = logging.getLogger("DeepSeekService")

    async def humanize_commits(self, commits: List[Dict]) -> List[Dict]:
        """Use DeepSeek to humanize git commits into changelog entries. Fallback to raw commits if DeepSeek fails."""
        if not commits:
            return []
        
        # Prepare commits for AI processing
        commits_text = "\n\n".join([
            f"Commit: {commit['hash'][:8]}\n"
            f"Date: {commit['date'].isoformat()}\n"
            f"Author: {commit['author_name']}\n"
            f"Subject: {commit['subject']}\n"
            f"Body: {commit['body']}"
            for commit in commits
        ])
        
        prompt = f"""
You are a changelog generator. Convert these git commits into human-readable changelog entries following these rules:

1. Use semantic versioning (MAJOR.MINOR.PATCH)
2. Group by category: Added, Changed, Fixed, Removed, Deprecated, Security
3. Write for humans - short, clear, no jargon
4. Be transparent - include even small but user-visible changes
5. Highlight breaking changes with ⚠️ or "Breaking:" prefix
6. Each entry should have: version, title, description, change_type, is_breaking

Git commits:
{commits_text}

Return a JSON array of changelog entries with this structure:
[
  {{
    "version": "1.2.0",
    "title": "Add user authentication",
    "description": "Implemented JWT-based authentication system with Google OAuth support",
    "change_type": "added",
    "is_breaking": false
  }}
]

Only return valid JSON, no other text.
"""
        
        retries = 2
        for attempt in range(retries + 1):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "deepseek-chat",
                            "messages": [
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ],
                            "temperature": 0.3,
                            "max_tokens": 2000
                        },
                        timeout=self.timeout
                    )
                    
                    if response.status_code != 200:
                        raise Exception(f"DeepSeek API error: {response.status_code} - {response.text}")
                    
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    # Parse JSON response
                    try:
                        changelog_entries = json.loads(content)
                        return changelog_entries
                    except json.JSONDecodeError:
                        # Try to extract JSON from response
                        json_match = re.search(r'\[.*\]', content, re.DOTALL)
                        if json_match:
                            return json.loads(json_match.group())
                        else:
                            raise Exception("Failed to parse DeepSeek response as JSON")
            except (httpx.ReadTimeout, httpx.ConnectTimeout) as e:
                self.logger.warning(f"DeepSeek API timeout (attempt {attempt+1}/{retries+1}): {e}")
                if attempt == retries:
                    break
            except Exception as e:
                self.logger.error(f"DeepSeek API call failed (attempt {attempt+1}/{retries+1}): {e}")
                if attempt == retries:
                    break
        # Fallback: return raw commit messages as changelog entries
        self.logger.error("DeepSeek unavailable, falling back to raw commit messages.")
        fallback_entries = []
        for commit in commits:
            fallback_entries.append({
                "version": "AI unavailable",
                "title": commit["subject"],
                "description": commit["body"] or commit["subject"],
                "change_type": "changed",
                "is_breaking": False
            })
        return fallback_entries

    async def summarize_commits(self, commits: List[Dict]) -> List[Dict]:
        """Summarize multiple commits into a single changelog entry"""
        if not commits:
            return []
        
        # Prepare commits for AI processing
        commits_text = "\n\n".join([
            f"Commit: {commit['hash'][:8]}\n"
            f"Date: {commit['date'].isoformat()}\n"
            f"Author: {commit['author_name']}\n"
            f"Subject: {commit['subject']}\n"
            f"Body: {commit['body']}"
            for commit in commits
        ])
        
        prompt = f"""
You are a changelog summarizer. Analyze these git commits and create a single, concise changelog entry that summarizes all the changes.

Rules:
1. Group related changes together
2. Use semantic versioning (MAJOR.MINOR.PATCH) - determine appropriate version bump
3. Create one comprehensive title that captures the main theme
4. Write a detailed description that covers all significant changes
5. Determine the primary change type (added, changed, fixed, removed, deprecated, security)
6. Mark as breaking if any changes are backward-incompatible
7. Focus on user-visible changes, not technical details

Git commits:
{commits_text}

Return a single JSON object with this structure:
{{
    "version": "1.2.0",
    "title": "Add user authentication and improve API structure",
    "description": "Implemented JWT-based authentication system with Google OAuth support. Refactored API endpoints for better organization. Added comprehensive error handling and improved documentation.",
    "change_type": "added",
    "is_breaking": false,
    "commit_hash": "first_commit_hash",
    "commit_date": "2024-01-15T10:30:00Z",
    "commit_message": "Summary of all changes"
}}

Only return valid JSON, no other text.
"""
        
        retries = 2
        for attempt in range(retries + 1):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "deepseek-chat",
                            "messages": [
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ],
                            "temperature": 0.3,
                            "max_tokens": 2000
                        },
                        timeout=self.timeout
                    )
                    
                    if response.status_code != 200:
                        raise Exception(f"DeepSeek API error: {response.status_code} - {response.text}")
                    
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    # Parse JSON response
                    try:
                        changelog_entry = json.loads(content)
                        return [changelog_entry]
                    except json.JSONDecodeError:
                        # Try to extract JSON from response
                        json_match = re.search(r'\{.*\}', content, re.DOTALL)
                        if json_match:
                            return [json.loads(json_match.group())]
                        else:
                            raise Exception("Failed to parse DeepSeek response as JSON")
            except (httpx.ReadTimeout, httpx.ConnectTimeout) as e:
                self.logger.warning(f"DeepSeek API timeout (attempt {attempt+1}/{retries+1}): {e}")
                if attempt == retries:
                    break
            except Exception as e:
                self.logger.error(f"DeepSeek API call failed (attempt {attempt+1}/{retries+1}): {e}")
                if attempt == retries:
                    break
        
        # Fallback: create a simple summary
        self.logger.error("DeepSeek unavailable, creating simple summary.")
        first_commit = commits[0]
        last_commit = commits[-1]
        
        # Create a simple summary
        summary = {
            "version": "AI unavailable",
            "title": f"Update with {len(commits)} commits",
            "description": f"Processed {len(commits)} commits from {first_commit['hash'][:8]} to {last_commit['hash'][:8]}. Latest: {last_commit['subject']}",
            "change_type": "changed",
            "is_breaking": False,
            "commit_hash": first_commit["hash"],
            "commit_date": first_commit["date"],
            "commit_message": f"Summary of {len(commits)} commits"
        }
        return [summary]


class ChangelogService:
    """Service for changelog management"""
    
    def __init__(self):
        self.git_service = GitService()
        self.deepseek_service = DeepSeekService()
    
    async def process_new_commits(self) -> int:
        """Process new commits and create changelog entries"""
        try:
            # Get last processed commit
            last_processed = await LastProcessedCommit.objects.first()
            last_hash = last_processed.commit_hash if last_processed else None
            
            # Get new commits
            commits = self.git_service.get_commits_since(last_hash)
            
            if not commits:
                return 0
            
            # Summarize commits using DeepSeek (creates one entry per batch)
            changelog_entries = await self.deepseek_service.summarize_commits(commits)
            
            # Create database entries
            created_count = 0
            for entry_data in changelog_entries:
                # Create changelog entry
                title = entry_data.get("title", "Update")
                # Truncate title to fit within 255 character limit
                if len(title) > 255:
                    title = title[:252] + "..."
                
                # Also truncate description if needed
                description = entry_data.get("description", "Update")
                if len(description) > 1000:
                    description = description[:997] + "..."
                
                await ChangelogEntry.objects.create(
                    version=entry_data.get("version", "1.0.0"),
                    title=title,
                    description=description,
                    change_type=entry_data.get("change_type", "changed"),
                    commit_hash=entry_data.get("commit_hash", commits[0]["hash"]),
                    commit_date=entry_data.get("commit_date", commits[0]["date"]),
                    commit_message=entry_data.get("commit_message", f"Summary of {len(commits)} commits"),
                    is_breaking=entry_data.get("is_breaking", False),
                    release_date=datetime.now(timezone.utc)
                )
                created_count += 1
            
            # Update last processed commit
            latest_hash = commits[0]["hash"]
            if last_processed:
                last_processed.commit_hash = latest_hash
                await last_processed.save()
            else:
                await LastProcessedCommit.objects.create(commit_hash=latest_hash)
            
            return created_count
            
        except Exception as e:
            raise Exception(f"Failed to process new commits: {str(e)}")
    
    async def get_changelog_entries(
        self,
        page: int = 1,
        per_page: int = 20,
        version: Optional[str] = None,
        change_type: Optional[ChangeType] = None
    ) -> Tuple[List[ChangelogEntry], int]:
        """Get paginated changelog entries"""
        query = ChangelogEntry.objects.all()
        
        if version:
            query = query.filter(version=version)
        
        if change_type:
            query = query.filter(change_type=change_type)
        
        # Get total count
        total = await query.count()
        
        # Get paginated results
        offset = (page - 1) * per_page
        entries = await query.offset(offset).limit(per_page).order_by("-release_date").all()
        
        return entries, total
    
    async def get_unread_entries(self, user_identifier: str) -> List[ChangelogEntry]:
        """Get unread changelog entries for a user"""
        # Get all changelog entries
        all_entries = await ChangelogEntry.objects.order_by("-release_date").all()
        
        # Get viewed entries for this user
        viewed_entries = await ChangelogView.objects.filter(
            user_identifier=user_identifier
        ).all()
        viewed_entry_ids = [str(view.entry) for view in viewed_entries]
        
        # Filter out viewed entries
        unread_entries = [
            entry for entry in all_entries 
            if str(entry.id) not in viewed_entry_ids
        ]
        
        return unread_entries
    
    async def mark_as_viewed(self, entry_id: str, user_identifier: str) -> bool:
        """Mark a changelog entry as viewed by a user"""
        try:
            # Check if entry exists
            entry = await ChangelogEntry.objects.get(id=entry_id)
            
            # Check if already viewed
            existing_view = await ChangelogView.objects.filter(
                entry=entry_id,
                user_identifier=user_identifier
            ).first()
            
            if not existing_view:
                await ChangelogView.objects.create(
                    entry=entry_id,
                    user_identifier=user_identifier
                )
            
            return True
            
        except Exception:
            return False
    
    async def get_changelog_summary(self, version: Optional[str] = None) -> Dict:
        """Get summary statistics for changelog entries"""
        query = ChangelogEntry.objects.all()
        
        if version:
            query = query.filter(version=version)
        
        entries = await query.order_by("-release_date").all()
        
        if not entries:
            return {
                "version": version or "unknown",
                "release_date": None,
                "total_changes": 0,
                "breaking_changes": 0,
                "changes_by_type": {},
                "entries": []
            }
        
        # Calculate statistics
        total_changes = len(entries)
        breaking_changes = sum(1 for entry in entries if entry.is_breaking)
        
        changes_by_type = {}
        for entry in entries:
            change_type = entry.change_type.value
            changes_by_type[change_type] = changes_by_type.get(change_type, 0) + 1
        
        return {
            "version": entries[0].version,
            "release_date": entries[0].release_date,
            "total_changes": total_changes,
            "breaking_changes": breaking_changes,
            "changes_by_type": changes_by_type,
            "entries": entries
        } 