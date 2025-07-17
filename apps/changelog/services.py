import subprocess
import json
import re
import hashlib
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
        self.enabled = bool(self.api_key)
        
        if not self.enabled:
            self.logger = logging.getLogger("DeepSeekService")
            self.logger.warning("DEEPSEEK_API_KEY not found in environment variables. DeepSeek service will be disabled.")
            return
        
        self.base_url = "https://api.deepseek.com/v1"
        self.timeout = getattr(settings, "deepseek_timeout", 30.0)
        self.logger = logging.getLogger("DeepSeekService")

    async def humanize_commits(self, commits: List[Dict]) -> List[Dict]:
        """Use DeepSeek to humanize git commits into changelog entries. Fallback to raw commits if DeepSeek fails."""
        if not commits:
            return []
        
        if not self.enabled:
            # Fallback: return raw commit messages as changelog entries
            self.logger.warning("DeepSeek service is disabled, falling back to raw commit messages.")
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
        
        if not self.enabled:
            # Fallback: return raw commit messages as changelog entries
            self.logger.warning("DeepSeek service is disabled, falling back to raw commit messages.")
            fallback_entries = []
            for commit in commits:
                fallback_entries.append({
                    "version": "AI unavailable",
                    "title": commit["subject"],
                    "description": commit["body"] or commit["subject"],
                    "change_type": "changed",
                    "is_breaking": False,
                    "commit_hash": commit["hash"],
                    "commit_date": commit["date"].isoformat(),
                    "commit_message": commit["subject"]
                })
            return fallback_entries
        
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
        self.logger = logging.getLogger("ChangelogService")
    
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
        change_type: Optional[ChangeType] = None,
        include_drafts: bool = False
    ) -> Tuple[List[ChangelogEntry], int]:
        """Get paginated changelog entries"""
        query = ChangelogEntry.objects.all()
        
        # Filter by published status based on include_drafts parameter
        if include_drafts:
            # When include_drafts=True, we want both published and drafts (all entries)
            # So no filter on is_published
            pass
        else:
            # When include_drafts=False, we want only published entries
            query = query.filter(is_published=True)
        
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
    
    async def get_changelog_entries_by_status(
        self,
        page: int = 1,
        per_page: int = 20,
        version: Optional[str] = None,
        change_type: Optional[ChangeType] = None,
        status: str = "published"
    ) -> Tuple[List[ChangelogEntry], int]:
        """Get paginated changelog entries filtered by status"""
        query = ChangelogEntry.objects.all()
        
        # Filter by status
        if status == "published":
            query = query.filter(is_published=True)
        elif status == "drafts":
            query = query.filter(is_published=False)
        elif status == "all":
            # No filter - include both published and drafts
            pass
        else:
            raise ValueError(f"Invalid status: {status}. Use 'published', 'drafts', or 'all'")
        
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
    
    async def get_latest_changelog_entries(self, limit: int = 10) -> List[ChangelogEntry]:
        """Get the latest changelog entries (most recent version)"""
        # Get only published entries, ordered by release date (newest first)
        entries = await ChangelogEntry.objects.filter(
            is_published=True
        ).order_by("-release_date").limit(limit).all()
        
        return entries
    
    async def get_changelog_entries_by_version(self, version: str) -> List[ChangelogEntry]:
        """Get all changelog entries for a specific version"""
        entries = await ChangelogEntry.objects.filter(
            version=version,
            is_published=True
        ).order_by("-release_date").all()
        
        return entries
    
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
    
    async def publish_changelog_entry(self, entry_id: str, user_id: str) -> bool:
        """Publish a changelog entry"""
        try:
            from apps.auth.models import User
            
            # Get the entry
            entry = await ChangelogEntry.objects.get(id=entry_id)
            
            # Get the user
            user = await User.objects.get(id=user_id)
            
            # Update entry
            entry.is_published = True
            entry.published_by = user
            entry.published_at = datetime.now(timezone.utc)
            await entry.save()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to publish changelog entry: {e}")
            return False
    
    async def unpublish_changelog_entry(self, entry_id: str) -> bool:
        """Unpublish a changelog entry"""
        try:
            entry = await ChangelogEntry.objects.get(id=entry_id)
            entry.is_published = False
            entry.published_by = None
            entry.published_at = None
            await entry.save()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unpublish changelog entry: {e}")
            return False
    
    async def delete_changelog_entry(self, entry_id: str) -> bool:
        """Delete a changelog entry"""
        try:
            entry = await ChangelogEntry.objects.get(id=entry_id)
            await entry.delete()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete changelog entry: {e}")
            return False
    
    async def update_changelog_entry(self, entry_id: str, **kwargs) -> bool:
        """Update a changelog entry"""
        try:
            entry = await ChangelogEntry.objects.get(id=entry_id)
            
            # Update fields
            for field, value in kwargs.items():
                if hasattr(entry, field):
                    setattr(entry, field, value)
            
            await entry.save()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update changelog entry: {e}")
            return False

    def _generate_anonymous_id(self, ip_address: str, user_agent: str) -> str:
        """Generate a privacy-protected anonymous identifier"""
        # Combine IP and User-Agent with a salt for additional security
        salt = getattr(settings, "anonymous_id_salt", "default_salt_change_in_production")
        combined = f"{ip_address}:{user_agent}:{salt}"
        
        # Create SHA-256 hash for privacy protection
        return hashlib.sha256(combined.encode()).hexdigest()

    def _hash_ip_address(self, ip_address: str) -> str:
        """Hash IP address for privacy protection"""
        salt = getattr(settings, "ip_salt", "default_ip_salt_change_in_production")
        return hashlib.sha256(f"{ip_address}:{salt}".encode()).hexdigest()

    def _hash_user_agent(self, user_agent: str) -> str:
        """Hash user agent for privacy protection"""
        salt = getattr(settings, "user_agent_salt", "default_ua_salt_change_in_production")
        return hashlib.sha256(f"{user_agent}:{salt}".encode()).hexdigest()

    async def get_latest_version(self) -> Optional[str]:
        """Get the latest published version"""
        try:
            latest_entry = await ChangelogEntry.objects.filter(
                is_published=True
            ).order_by("-release_date").first()
            
            return latest_entry.version if latest_entry else None
        except Exception:
            return None

    async def get_changelog_status(
        self, 
        ip_address: str, 
        user_agent: str
    ) -> Dict:
        """
        Get changelog status for any user (anonymous or authenticated).
        Returns whether user should see changelog and what version they've seen.
        """
        try:
            hashed_ip = self._hash_ip_address(ip_address)
            hashed_user_agent = self._hash_user_agent(user_agent)
            latest_version = await self.get_latest_version()
            
            # Debug logging
            self.logger.info(f"Changelog status check - IP: {ip_address[:10]}..., UA: {user_agent[:30]}...")
            self.logger.info(f"Hashed IP: {hashed_ip[:16]}..., Hashed UA: {hashed_user_agent[:16]}...")
            self.logger.info(f"Latest version: {latest_version}")
            
            if not latest_version:
                self.logger.info("No latest version found")
                return {
                    "should_show": False,
                    "latest_version": None,
                    "user_version": None,
                    "has_new_content": False
                }
            
            # Check if user has seen this version
            user_view = await ChangelogView.objects.filter(
                hashed_ip=hashed_ip,
                hashed_user_agent=hashed_user_agent
            ).first()
            
            if not user_view:
                # New user - should show changelog
                self.logger.info("New user - should show changelog")
                return {
                    "should_show": True,
                    "latest_version": latest_version,
                    "user_version": None,
                    "has_new_content": True
                }
            
            # Check if user has seen the latest version
            self.logger.info(f"User has seen version: {user_view.latest_version_seen}, Latest: {latest_version}")
            
            if user_view.latest_version_seen == latest_version:
                # User has seen latest version - don't show changelog
                self.logger.info("User has seen latest version - don't show changelog")
                return {
                    "should_show": False,
                    "latest_version": latest_version,
                    "user_version": user_view.latest_version_seen,
                    "has_new_content": False
                }
            else:
                # User hasn't seen latest version - show changelog
                self.logger.info("User hasn't seen latest version - show changelog")
                return {
                    "should_show": True,
                    "latest_version": latest_version,
                    "user_version": user_view.latest_version_seen,
                    "has_new_content": True
                }
                
        except Exception as e:
            self.logger.error(f"Error getting changelog status: {e}")
            return {
                "should_show": False,
                "latest_version": None,
                "user_version": None,
                "has_new_content": False
            }

    async def mark_as_viewed(
        self, 
        ip_address: str, 
        user_agent: str
    ) -> bool:
        """Mark changelog as viewed by any user (anonymous or authenticated)"""
        try:
            hashed_ip = self._hash_ip_address(ip_address)
            hashed_user_agent = self._hash_user_agent(user_agent)
            latest_version = await self.get_latest_version()
            
            # Enhanced debug logging with full hash values
            # self.logger.info("=" * 60)
            # self.logger.info("🔍 /changelog/viewed REQUEST DEBUG")
            # self.logger.info("=" * 60)
            # self.logger.info(f"📝 Raw IP Address: {ip_address}")
            # self.logger.info(f"📝 Raw User-Agent: {user_agent}")
            # self.logger.info(f"🔐 Full Hashed IP: {hashed_ip}")
            # self.logger.info(f"🔐 Full Hashed User-Agent: {hashed_user_agent}")
            # self.logger.info(f"📊 Latest version to mark as seen: {latest_version}")
            
            # Also print to console for immediate visibility
            # print("=" * 60)
            # print("🔍 /changelog/viewed REQUEST DEBUG")
            # print("=" * 60)
            # print(f"📝 Raw IP Address: {ip_address}")
            # print(f"📝 Raw User-Agent: {user_agent}")
            # print(f"🔐 Full Hashed IP: {hashed_ip}")
            # print(f"🔐 Full Hashed User-Agent: {hashed_user_agent}")
            # print(f"📊 Latest version to mark as seen: {latest_version}")
            
            if not latest_version:
                self.logger.warning("⚠️  No latest version found for marking as viewed")
                self.logger.info("=" * 60)
                return False
            
            # Get or create user view record
            user_view, created = await ChangelogView.objects.get_or_create(
                hashed_ip=hashed_ip,
                hashed_user_agent=hashed_user_agent,
                defaults={
                    "latest_version_seen": latest_version,
                    "view_count": 1
                }
            )
            
            if created:
                self.logger.info("✅ Created NEW user view record")
                self.logger.info(f"📊 Version marked as seen: {latest_version}")
                self.logger.info(f"📊 View count: 1")
            else:
                # Update existing record
                old_version = user_view.latest_version_seen
                user_view.latest_version_seen = latest_version
                user_view.last_seen = datetime.now(timezone.utc)
                user_view.view_count += 1
                await user_view.save()
                self.logger.info("✅ Updated EXISTING user view record")
                self.logger.info(f"📊 Old version: {old_version}")
                self.logger.info(f"📊 New version: {latest_version}")
                self.logger.info(f"📊 View count: {user_view.view_count}")
                self.logger.info(f"📊 Last seen: {user_view.last_seen}")
            
            self.logger.info("✅ Successfully marked changelog as viewed")
            self.logger.info("=" * 60)
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error marking as viewed: {e}")
            self.logger.info("=" * 60)
            return False

    async def get_latest_changelog_for_user(
        self, 
        ip_address: str, 
        user_agent: str,
        limit: int = 10
    ) -> Dict:
        """
        Get latest changelog entries for any user (anonymous or authenticated).
        First checks if hashed data exists in database, returns empty if it does.
        """
        try:
            hashed_ip = self._hash_ip_address(ip_address)
            hashed_user_agent = self._hash_user_agent(user_agent)
            
            # Enhanced debug logging with full hash values
            self.logger.info("=" * 60)
            self.logger.info("🔍 /changelog/latest REQUEST DEBUG")
            self.logger.info("=" * 60)
            self.logger.info(f"📝 Raw IP Address: {ip_address}")
            self.logger.info(f"📝 Raw User-Agent: {user_agent}")
            self.logger.info(f"🔐 Full Hashed IP: {hashed_ip}")
            self.logger.info(f"🔐 Full Hashed User-Agent: {hashed_user_agent}")
            self.logger.info(f"🔍 Looking for hash combination in database...")
            
            # Also print to console for immediate visibility
            print("=" * 60)
            print("🔍 /changelog/latest REQUEST DEBUG")
            print("=" * 60)
            print(f"📝 Raw IP Address: {ip_address}")
            print(f"📝 Raw User-Agent: {user_agent}")
            print(f"🔐 Full Hashed IP: {hashed_ip}")
            print(f"🔐 Full Hashed User-Agent: {hashed_user_agent}")
            print(f"🔍 Looking for hash combination in database...")
            
            # First check if hashed data exists in database
            user_view = await ChangelogView.objects.filter(
                hashed_ip=hashed_ip,
                hashed_user_agent=hashed_user_agent
            ).first()
            
            if user_view:
                # Hash data exists - user has seen changelog before
                self.logger.info("✅ HASH FOUND in database!")
                self.logger.info(f"📊 User has seen version: {user_view.latest_version_seen}")
                self.logger.info(f"📊 View count: {user_view.view_count}")
                self.logger.info(f"📊 First seen: {user_view.first_seen}")
                self.logger.info(f"📊 Last seen: {user_view.last_seen}")
                
                latest_version = await self.get_latest_version()
                self.logger.info(f"📊 Latest version available: {latest_version}")
                self.logger.info("🚫 Returning empty response - user already seen changelog")
                self.logger.info("=" * 60)
                
                # Also print to console
                print("✅ HASH FOUND in database!")
                print(f"📊 User has seen version: {user_view.latest_version_seen}")
                print(f"📊 View count: {user_view.view_count}")
                print(f"📊 First seen: {user_view.first_seen}")
                print(f"📊 Last seen: {user_view.last_seen}")
                print(f"📊 Latest version available: {latest_version}")
                print("🚫 Returning empty response - user already seen changelog")
                print("=" * 60)
                
                return {
                    "entries": [],
                    "total": 0,
                    "latest_version": latest_version,
                    "user_version": user_view.latest_version_seen,
                    "has_new_content": False,
                    "reason": "user_already_seen"
                }
            
            # Hash data doesn't exist - new user, should show changelog
            self.logger.info("❌ HASH NOT FOUND in database")
            self.logger.info("🆕 This appears to be a new user")
            self.logger.info("📋 Will show changelog entries")
            
            # Also print to console
            print("❌ HASH NOT FOUND in database")
            print("🆕 This appears to be a new user")
            print("📋 Will show changelog entries")
            
            # Get latest version and entries
            latest_version = await self.get_latest_version()
            if not latest_version:
                self.logger.info("⚠️  No latest version found")
                self.logger.info("=" * 60)
                print("⚠️  No latest version found")
                print("=" * 60)
                return {
                    "entries": [],
                    "total": 0,
                    "latest_version": None,
                    "user_version": None,
                    "has_new_content": False,
                    "reason": "no_latest_version"
                }
            
            # Get latest entries
            entries = await self.get_latest_changelog_entries(limit=limit)
            self.logger.info(f"📋 Found {len(entries)} changelog entries")
            self.logger.info(f"📊 Latest version: {latest_version}")
            self.logger.info("✅ Returning changelog entries for new user")
            self.logger.info("=" * 60)
            
            # Also print to console
            print(f"📋 Found {len(entries)} changelog entries")
            print(f"📊 Latest version: {latest_version}")
            print("✅ Returning changelog entries for new user")
            print("=" * 60)
            
            return {
                "entries": entries,
                "total": len(entries),
                "latest_version": latest_version,
                "user_version": None,
                "has_new_content": True,
                "reason": "new_user"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting latest changelog for user: {e}")
            self.logger.info("=" * 60)
            return {
                "entries": [],
                "total": 0,
                "latest_version": None,
                "user_version": None,
                "has_new_content": False,
                "reason": "error"
            }

    async def debug_user_views(self, ip_address: str, user_agent: str) -> Dict:
        """Debug method to check user views in database"""
        try:
            hashed_ip = self._hash_ip_address(ip_address)
            hashed_user_agent = self._hash_user_agent(user_agent)
            
            # Get all user views
            views = await ChangelogView.objects.filter(
                hashed_ip=hashed_ip,
                hashed_user_agent=hashed_user_agent
            ).all()
            
            # Get latest version
            latest_version = await self.get_latest_version()
            
            return {
                "ip_address": ip_address[:10] + "...",
                "user_agent": user_agent[:30] + "...",
                "hashed_ip": hashed_ip[:16] + "...",
                "hashed_user_agent": hashed_user_agent[:16] + "...",
                "latest_version": latest_version,
                "total_views": len(views),
                "views": [
                    {
                        "id": str(view.id),
                        "latest_version_seen": view.latest_version_seen,
                        "view_count": view.view_count,
                        "first_seen": view.first_seen.isoformat(),
                        "last_seen": view.last_seen.isoformat()
                    }
                    for view in views
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error in debug_user_views: {e}")
            return {"error": str(e)} 