"""Announcement endpoints for the High School Management System API."""

import logging
from datetime import date
from typing import Any, Dict, Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from pymongo.errors import PyMongoError

from ..database import announcements_collection
from .auth import get_authenticated_teacher

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)


class AnnouncementInput(BaseModel):
    """Fields accepted when creating or updating an announcement."""

    message: str = Field(min_length=1, max_length=500)
    expiration_date: date
    start_date: Optional[date] = None


def require_teacher(session_token: Optional[str]) -> None:
    """Require a known teacher for announcement management operations."""
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required for this action"
        )
    get_authenticated_teacher(session_token)


def serialize_announcement(announcement: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a MongoDB announcement into an API-safe object."""
    return {
        "id": str(announcement["_id"]),
        "message": announcement["message"],
        "start_date": announcement.get("start_date"),
        "expiration_date": announcement["expiration_date"]
    }


def validated_document(announcement: AnnouncementInput) -> Dict[str, Any]:
    """Validate dates and prepare an announcement for MongoDB."""
    message = announcement.message.strip()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Announcement message is required"
        )

    if announcement.start_date and announcement.expiration_date < announcement.start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Expiration date must be on or after the start date"
        )

    return {
        "message": message,
        "start_date": announcement.start_date.isoformat()
        if announcement.start_date else None,
        "expiration_date": announcement.expiration_date.isoformat()
    }


def announcement_id_or_404(announcement_id: str) -> ObjectId:
    """Parse a MongoDB object ID without exposing implementation details."""
    if not ObjectId.is_valid(announcement_id):
        raise HTTPException(status_code=404, detail="Announcement not found")
    return ObjectId(announcement_id)


@router.get("")
@router.get("/")
def get_active_announcements() -> list[Dict[str, Any]]:
    """Get announcements that have started and have not expired."""
    today = date.today().isoformat()
    query = {
        "expiration_date": {"$gte": today},
        "$or": [
            {"start_date": None},
            {"start_date": {"$exists": False}},
            {"start_date": {"$lte": today}}
        ]
    }
    try:
        return [
            serialize_announcement(item)
            for item in announcements_collection.find(query).sort("expiration_date", 1)
        ]
    except PyMongoError:
        logger.exception("Failed to load active announcements")
        raise HTTPException(status_code=500, detail="Failed to load announcements")


@router.get("/manage")
def get_all_announcements(
    session_token: Optional[str] = Query(None)
) -> list[Dict[str, Any]]:
    """Get all announcements for an authenticated teacher."""
    require_teacher(session_token)
    try:
        return [
            serialize_announcement(item)
            for item in announcements_collection.find().sort("expiration_date", -1)
        ]
    except PyMongoError:
        logger.exception("Failed to load announcements for management")
        raise HTTPException(status_code=500, detail="Failed to load announcements")


@router.post("", status_code=status.HTTP_201_CREATED)
def create_announcement(
    announcement: AnnouncementInput,
    session_token: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """Create an announcement as an authenticated teacher."""
    require_teacher(session_token)
    document = validated_document(announcement)
    try:
        result = announcements_collection.insert_one(document)
        return serialize_announcement({"_id": result.inserted_id, **document})
    except PyMongoError:
        logger.exception("Failed to create announcement")
        raise HTTPException(status_code=500, detail="Failed to create announcement")


@router.put("/{announcement_id}")
def update_announcement(
    announcement_id: str,
    announcement: AnnouncementInput,
    session_token: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """Update an announcement as an authenticated teacher."""
    require_teacher(session_token)
    object_id = announcement_id_or_404(announcement_id)
    document = validated_document(announcement)
    try:
        result = announcements_collection.update_one(
            {"_id": object_id}, {"$set": document}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Announcement not found")
        return serialize_announcement({"_id": object_id, **document})
    except PyMongoError:
        logger.exception("Failed to update announcement %s", announcement_id)
        raise HTTPException(status_code=500, detail="Failed to update announcement")


@router.delete("/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_announcement(
    announcement_id: str,
    session_token: Optional[str] = Query(None)
) -> None:
    """Delete an announcement as an authenticated teacher."""
    require_teacher(session_token)
    object_id = announcement_id_or_404(announcement_id)
    try:
        result = announcements_collection.delete_one({"_id": object_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Announcement not found")
    except PyMongoError:
        logger.exception("Failed to delete announcement %s", announcement_id)
        raise HTTPException(status_code=500, detail="Failed to delete announcement")