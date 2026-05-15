"""Firebase Storage utility — per-module folder isolation."""
from datetime import datetime, timezone
from typing import Optional

from utils.secrets import settings

MODULE_PATHS = {
    "profiles":      "customers/profiles",
    "staff":         "staff/photos",
    "services":      "services/images",
    "locations":     "locations/photos",
    "bookings":      "bookings/attachments",
    "soulskin":      "soulskin/analysis",
    "before_after":  "before_after",
    "quality":       "quality/reports",
    "loyalty":       "loyalty/assets",
    "consultations": "consultations/forms",
    "voice":         "voice/recordings",
    "twin":          "twin/timeline",
    "general":       "general",
}


def _object_name(module: str, file_name: str) -> str:
    folder = MODULE_PATHS.get(module, f"modules/{module}")
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"{folder}/{ts}_{file_name}"


def _bucket():
    try:
        import firebase_admin
        from firebase_admin import storage as fb_storage, credentials
    except ImportError:
        raise RuntimeError("firebase-admin not installed. Run: pip install firebase-admin")

    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(
            cred, {"storageBucket": settings.FIREBASE_STORAGE_BUCKET}
        )
    return fb_storage.bucket()


async def upload_file(
    file_data: bytes,
    file_name: str,
    module: str = "general",
    content_type: str = "image/jpeg",
) -> str:
    object_name = _object_name(module, file_name)
    blob = _bucket().blob(object_name)
    blob.upload_from_string(file_data, content_type=content_type)
    blob.make_public()
    return blob.public_url


async def get_signed_url(object_name: str, expires_secs: int = 3600) -> Optional[str]:
    try:
        from datetime import timedelta
        return _bucket().blob(object_name).generate_signed_url(
            expiration=timedelta(seconds=expires_secs)
        )
    except Exception:
        return None


async def delete_file(object_name: str) -> bool:
    try:
        _bucket().blob(object_name).delete()
        return True
    except Exception:
        return False


# ── per-module helpers ────────────────────────────────────────────────────────

async def upload_profile_image(data: bytes, filename: str) -> str:
    return await upload_file(data, filename, module="profiles")

async def upload_staff_photo(data: bytes, filename: str) -> str:
    return await upload_file(data, filename, module="staff")

async def upload_service_image(data: bytes, filename: str) -> str:
    return await upload_file(data, filename, module="services")

async def upload_soulskin_image(data: bytes, filename: str) -> str:
    return await upload_file(data, filename, module="soulskin")

async def upload_before_after(data: bytes, filename: str) -> str:
    return await upload_file(data, filename, module="before_after")

async def upload_location_photo(data: bytes, filename: str) -> str:
    return await upload_file(data, filename, module="locations")

async def upload_quality_report(data: bytes, filename: str, content_type: str = "application/pdf") -> str:
    return await upload_file(data, filename, module="quality", content_type=content_type)
