from typing import Any, Dict

from services.api_client import get_request, post_request

# ── Engineer verification ────────────────────────────────────────────────────
async def get_pending_verifications() -> Dict[str, Any]:
    """GET /admin/pending-verifications → {success, verifications: [...]}"""
    return await get_request("/admin/pending-verifications")


async def approve_verification(
    public_id: str,
    engineer_id: str,
) -> Dict[str, Any]:
    """POST /admin/approve-verification"""
    return await post_request(
        "/admin/approve-verification",
        {"public_id": public_id, "engineer_id": engineer_id},
    )


async def decline_verification(
    public_id: str, engineer_id: str, reason: str
) -> Dict[str, Any]:
    """POST /admin/decline-verification"""
    return await post_request(
        "/admin/decline-verification",
        {"public_id": public_id, "engineer_id": engineer_id, "reason": reason},
    )


# # ── Cracks ───────────────────────────────────────────────────────────────────

# async def fetch_all_cracks(token: str) -> Dict[str, Any]:
#     """POST /cracks/fetch → {success, cracks: [...]}"""
#     return await post_request("/cracks/fetch", {}, headers=_auth(token))


# async def delete_crack(crack_id: Any, token: str) -> Dict[str, Any]:
#     """POST /cracks/delete"""
#     return await post_request(
#         "/cracks/delete",
#         {"id": crack_id},
#         headers=_auth(token),
#     )
