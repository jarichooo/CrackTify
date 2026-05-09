from typing import Dict, Any
from .api_client import get_request, post_request


async def verify_engineer(
    user_id: int, license_number: str, document_url: str
) -> Dict[str, Any]:
    return await post_request(
        f"/engineer/verify",
        {
            "user_id": user_id,
            "license_number": license_number,
            "document_url": document_url,
        },
    )


async def get_all_engineer_usernames() -> Dict[str, Any]:
    return await get_request(f"/engineer/usernames")


async def invite_engineer(user_id: int, engineer_username: str) -> Dict[str, Any]:
    return await post_request(
        f"/engineer/invite",
        {
            "user_id": user_id,
            "engineer_username": engineer_username,
        },
    )


async def accept_engineer_invitation(
    inviter_id: str, engineer_id: int
) -> Dict[str, Any]:
    return await post_request(
        f"/engineer/accept_invitation",
        {
            "inviter_id": inviter_id,
            "engineer_id": engineer_id,
        },
    )


async def get_associated_user(user_id: int) -> Dict[str, Any]:
    return await get_request(
        f"/engineer/get_associated_user",
        {
            "user_id": user_id,
        },
    )
