from typing import Optional
from esmerald import get, post, put, Query, Path, Body
from esmerald.responses import JSONResponse
from esmerald.exceptions import HTTPException

from .models import ChangeType
from .schemas import (
    ChangelogEntryResponse,
    ChangelogViewCreate,
    ChangelogListResponse,
    ChangelogSummary,
    UnreadChangelogResponse
)
from .services import ChangelogService


# Initialize service
changelog_service = ChangelogService()


@get(
    tags=["Changelog"],
    summary="Get changelog entries",
    description="Retrieve paginated changelog entries with optional filtering"
)
async def get_changelog_entries(
    page: int = 1,
    per_page: int = 20,
    version: Optional[str] = None,
    change_type: Optional[ChangeType] = None
) -> ChangelogListResponse:
    """Get paginated changelog entries"""
    try:
        entries, total = await changelog_service.get_changelog_entries(
            page=page,
            per_page=per_page,
            version=version,
            change_type=change_type
        )
        
        has_next = (page * per_page) < total
        has_prev = page > 1
        
        return ChangelogListResponse(
            entries=[ChangelogEntryResponse.from_orm(entry) for entry in entries],
            total=total,
            page=page,
            per_page=per_page,
            has_next=has_next,
            has_prev=has_prev
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get changelog entries: {str(e)}")


@get(
    tags=["Changelog"],
    summary="Get changelog entry by ID",
    description="Retrieve a specific changelog entry by its ID"
)
async def get_changelog_entry(
    entry_id: str
) -> ChangelogEntryResponse:
    """Get a specific changelog entry"""
    try:
        from .models import ChangelogEntry
        entry = await ChangelogEntry.objects.get(id=entry_id)
        return ChangelogEntryResponse.from_orm(entry)
        
    except Exception as e:
        raise HTTPException(status_code=404, detail="Changelog entry not found")


@get(
    tags=["Changelog"],
    summary="Get changelog summary for version",
    description="Get summary statistics and entries for a specific version"
)
async def get_changelog_summary(
    version: str
) -> ChangelogSummary:
    """Get changelog summary for a specific version"""
    try:
        summary_data = await changelog_service.get_changelog_summary(version=version)
        
        return ChangelogSummary(
            version=summary_data["version"],
            release_date=summary_data["release_date"],
            total_changes=summary_data["total_changes"],
            breaking_changes=summary_data["breaking_changes"],
            changes_by_type=summary_data["changes_by_type"],
            entries=[ChangelogEntryResponse.from_orm(entry) for entry in summary_data["entries"]]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get changelog summary: {str(e)}")


@get(
    tags=["Changelog"],
    summary="Get unread changelog entries",
    description="Get changelog entries that haven't been viewed by the user"
)
async def get_unread_changelog(
    user_identifier: str
) -> UnreadChangelogResponse:
    """Get unread changelog entries for a user"""
    try:
        unread_entries = await changelog_service.get_unread_entries(user_identifier)
        
        latest_version = None
        if unread_entries:
            latest_version = unread_entries[0].version
        
        return UnreadChangelogResponse(
            unread_count=len(unread_entries),
            latest_version=str(latest_version) if latest_version else None,
            entries=[ChangelogEntryResponse.from_orm(entry) for entry in unread_entries]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get unread changelog: {str(e)}")


@post(
    tags=["Changelog"],
    summary="Mark changelog entry as viewed",
    description="Mark a changelog entry as viewed by a user"
)
async def mark_changelog_viewed(
    data: ChangelogViewCreate
) -> JSONResponse:
    """Mark a changelog entry as viewed"""
    try:
        success = await changelog_service.mark_as_viewed(
            entry_id=data.entry_id,
            user_identifier=data.user_identifier
        )
        
        if success:
            return JSONResponse({"message": "Changelog entry marked as viewed"})
        else:
            raise HTTPException(status_code=404, detail="Changelog entry not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark as viewed: {str(e)}")


@post(
    tags=["Changelog"],
    summary="Process new git commits",
    description="Process new git commits and create changelog entries using DeepSeek AI"
)
async def process_new_commits() -> JSONResponse:
    """Process new git commits and create changelog entries"""
    try:
        created_count = await changelog_service.process_new_commits()
        
        return JSONResponse({
            "message": f"Successfully processed {created_count} new changelog entries",
            "created_count": created_count
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process commits: {str(e)}")


@get(
    tags=["Changelog"],
    summary="Get available versions",
    description="Get list of all available changelog versions"
)
async def get_available_versions() -> JSONResponse:
    """Get list of available changelog versions"""
    try:
        from .models import ChangelogEntry
        
        # Get unique versions ordered by release date
        entries = await ChangelogEntry.objects.order_by("-release_date").all()
        
        versions = []
        seen_versions = set()
        
        for entry in entries:
            if entry.version not in seen_versions:
                versions.append({
                    "version": entry.version,
                    "release_date": entry.release_date,
                    "total_changes": 0,  # Will be calculated in summary
                    "breaking_changes": 0  # Will be calculated in summary
                })
                seen_versions.add(entry.version)
        
        # Calculate statistics for each version
        for version_info in versions:
            summary = await changelog_service.get_changelog_summary(version=version_info["version"])
            version_info["total_changes"] = summary["total_changes"]
            version_info["breaking_changes"] = summary["breaking_changes"]
        
        return JSONResponse({
            "versions": versions,
            "total_versions": len(versions)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get versions: {str(e)}")


@get(
    tags=["Changelog"],
    summary="Get current version",
    description="Get the current application version from git tags"
)
async def get_current_version() -> JSONResponse:
    """Get current application version"""
    try:
        from .services import GitService
        current_version = GitService.get_current_version()
        
        return JSONResponse({
            "version": current_version,
            "source": "git_tags"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get current version: {str(e)}") 