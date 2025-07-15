from typing import Optional
from esmerald import get, post, put, delete, Query, Path, Body
from esmerald.responses import JSONResponse
from esmerald.exceptions import HTTPException
from esmerald.requests import Request

from .models import ChangeType
from .schemas import (
    ChangelogEntryResponse,
    ChangelogViewCreate,
    ChangelogListResponse,
    ChangelogSummary,
    UnreadChangelogResponse,
    ChangelogPublishRequest,
    ChangelogPublishResponse,
    AnonymousChangelogStatus,
    AnonymousChangelogResponse,
    AnonymousViewRequest
)
from .services import ChangelogService
from core.permissions import require_permission, Permissions
from core.dependencies import get_current_user_dependency


# Initialize service
changelog_service = ChangelogService()


@get(
    tags=["Changelog"],
    summary="Get changelog entries",
    description="Retrieve paginated changelog entries with filtering options"
)
@require_permission(Permissions.CHANGELOG_VIEW)
async def get_changelog_entries(
    request: Request,
    page: int = 1,
    per_page: int = 20,
    version: Optional[str] = None,
    change_type: Optional[ChangeType] = None,
    status: str = "published"
) -> ChangelogListResponse:
    """Get paginated changelog entries with status filtering"""
    try:
        # Get user using dependency
        user = await get_current_user_dependency(request)
        
        # Check permissions based on status
        if status == "drafts" or status == "all":
            # Check if user can view drafts
            if not user.has_permission(Permissions.CHANGELOG_VIEW_DRAFTS):
                raise HTTPException(status_code=403, detail="Permission to view drafts required")
        
        entries, total = await changelog_service.get_changelog_entries_by_status(
            page=page,
            per_page=per_page,
            version=version,
            change_type=change_type,
            status=status
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
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
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
    summary="Get changelog by version",
    description="Get all changelog entries for a specific version"
)
async def get_changelog_by_version(
    version: str
) -> JSONResponse:
    """Get changelog entries for a specific version"""
    try:
        entries = await changelog_service.get_changelog_entries_by_version(version=version)
        
        return JSONResponse({
            "version": version,
            "entries": [ChangelogEntryResponse.from_orm(entry) for entry in entries],
            "total": len(entries)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get changelog for version: {str(e)}")


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


@post(
    tags=["Changelog"],
    summary="Publish changelog entry",
    description="Publish a draft changelog entry (admin only)"
)
@require_permission(Permissions.CHANGELOG_PUBLISH)
async def publish_changelog_entry(
    request: Request,
    data: ChangelogPublishRequest
) -> ChangelogPublishResponse:
    """Publish a changelog entry"""
    try:
        from datetime import datetime
        
        # Get user using dependency
        user = await get_current_user_dependency(request)
        
        success = await changelog_service.publish_changelog_entry(
            entry_id=data.entry_id,
            user_id=str(user.id)
        )
        
        if success:
            return ChangelogPublishResponse(
                success=True,
                message="Changelog entry published successfully",
                entry_id=data.entry_id
            )
        else:
            raise HTTPException(status_code=404, detail="Changelog entry not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish entry: {str(e)}")


@post(
    tags=["Changelog"],
    summary="Unpublish changelog entry",
    description="Unpublish a published changelog entry (admin only)"
)
@require_permission(Permissions.CHANGELOG_PUBLISH)
async def unpublish_changelog_entry(
    request: Request,
    data: ChangelogPublishRequest
) -> JSONResponse:
    """Unpublish a changelog entry"""
    try:
        success = await changelog_service.unpublish_changelog_entry(
            entry_id=data.entry_id
        )
        
        if success:
            return JSONResponse({"message": "Changelog entry unpublished successfully"})
        else:
            raise HTTPException(status_code=404, detail="Changelog entry not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to unpublish entry: {str(e)}")


@delete(
    tags=["Changelog"],
    summary="Delete changelog entry",
    description="Delete a changelog entry (admin/editor only)",
    status_code=200
)
@require_permission(Permissions.CHANGELOG_DELETE)
async def delete_changelog_entry(
    request: Request,
    entry_id: str
) -> JSONResponse:
    """Delete a changelog entry"""
    try:
        success = await changelog_service.delete_changelog_entry(entry_id)
        
        if success:
            return JSONResponse({"message": "Changelog entry deleted successfully"})
        else:
            raise HTTPException(status_code=404, detail="Changelog entry not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete entry: {str(e)}")


@put(
    tags=["Changelog"],
    summary="Update changelog entry",
    description="Update a changelog entry (admin/editor only)",
    status_code=200
)
@require_permission(Permissions.CHANGELOG_UPDATE)
async def update_changelog_entry(
    request: Request,
    entry_id: str,
    data: dict
) -> JSONResponse:
    """Update a changelog entry"""
    try:
        success = await changelog_service.update_changelog_entry(entry_id, **data)
        
        if success:
            return JSONResponse({"message": "Changelog entry updated successfully"})
        else:
            raise HTTPException(status_code=404, detail="Changelog entry not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update entry: {str(e)}")


@get(
    tags=["Changelog"],
    summary="Get changelog status",
    description="Check if user should see changelog based on their view history"
)
async def get_changelog_status(
    request: Request,
    ip_address: str,
    user_agent: Optional[str] = None,
    userAgent: Optional[str] = None
) -> AnonymousChangelogStatus:
    """Get changelog status for any user"""
    try:
        # Handle both user_agent and userAgent parameters
        actual_user_agent = user_agent or userAgent
        if not actual_user_agent:
            raise HTTPException(status_code=400, detail="user_agent or userAgent parameter is required")
        
        status = await changelog_service.get_changelog_status(
            ip_address=ip_address,
            user_agent=actual_user_agent
        )
        
        return AnonymousChangelogStatus(**status)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get changelog status: {str(e)}")


@get(
    tags=["Changelog"],
    summary="Get latest changelog for user",
    description="Get latest changelog entries for any user. Returns empty if user has seen latest version."
)
async def get_latest_changelog_for_user(
    request: Request,
    ip_address: str,
    user_agent: Optional[str] = None,
    userAgent: Optional[str] = None,
    limit: int = 10
) -> AnonymousChangelogResponse:
    """Get latest changelog entries for any user"""
    try:
        # Handle both user_agent and userAgent parameters
        actual_user_agent = user_agent or userAgent
        if not actual_user_agent:
            raise HTTPException(status_code=400, detail="user_agent or userAgent parameter is required")
        
        result = await changelog_service.get_latest_changelog_for_user(
            ip_address=ip_address,
            user_agent=actual_user_agent,
            limit=limit
        )
        
        return AnonymousChangelogResponse(
            entries=[ChangelogEntryResponse.from_orm(entry) for entry in result["entries"]],
            total=result["total"],
            latest_version=result["latest_version"],
            user_version=result["user_version"],
            has_new_content=result["has_new_content"],
            reason=result.get("reason")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get latest changelog: {str(e)}")


@post(
    tags=["Changelog"],
    summary="Mark changelog as viewed",
    description="Mark changelog as viewed by any user (updates their latest version seen)"
)
async def mark_changelog_viewed(
    data: AnonymousViewRequest
) -> JSONResponse:
    """Mark changelog as viewed by any user"""
    try:
        success = await changelog_service.mark_as_viewed(
            ip_address=data.ip_address,
            user_agent=data.user_agent
        )
        
        if success:
            return JSONResponse({"message": "Changelog marked as viewed"})
        else:
            raise HTTPException(status_code=404, detail="No changelog entries found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark as viewed: {str(e)}")


@get(
    tags=["Changelog"],
    summary="Debug user views",
    description="Debug endpoint to check user views in database (development only)"
)
async def debug_user_views(
    request: Request,
    ip_address: str,
    user_agent: Optional[str] = None,
    userAgent: Optional[str] = None
) -> JSONResponse:
    """Debug user views in database"""
    try:
        # Handle both user_agent and userAgent parameters
        actual_user_agent = user_agent or userAgent
        if not actual_user_agent:
            raise HTTPException(status_code=400, detail="user_agent or userAgent parameter is required")
        
        debug_info = await changelog_service.debug_user_views(
            ip_address=ip_address,
            user_agent=actual_user_agent
        )
        
        return JSONResponse(debug_info)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to debug user views: {str(e)}") 