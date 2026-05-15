"""Storage utilities — MinIO/S3-compatible file storage."""
import io
from datetime import datetime, timezone
from typing import Optional

from utils.secrets import settings


async def get_storage_client():
    if settings.STORAGE_BACKEND == "minio":
        try:
            from minio import Minio
            client = Minio(
                settings.STORAGE_ENDPOINT,
                access_key=settings.STORAGE_ACCESS_KEY,
                secret_key=settings.STORAGE_SECRET_KEY,
                secure=settings.STORAGE_USE_SSL,
            )
            if not client.bucket_exists(settings.STORAGE_BUCKET):
                client.make_bucket(settings.STORAGE_BUCKET)
            return client
        except ImportError:
            raise RuntimeError("minio package not installed. Run: pip install minio")
    return None


async def upload_file(
    file_data: bytes,
    file_name: str,
    folder: str = "uploads",
    content_type: str = "image/jpeg",
) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    object_name = f"{folder}/{timestamp}_{file_name}"

    if settings.STORAGE_BACKEND == "minio":
        client = await get_storage_client()
        if client:
            data_stream = io.BytesIO(file_data)
            client.put_object(
                settings.STORAGE_BUCKET, object_name, data_stream,
                length=len(file_data), content_type=content_type,
            )
            protocol = "https" if settings.STORAGE_USE_SSL else "http"
            return f"{protocol}://{settings.STORAGE_ENDPOINT}/{settings.STORAGE_BUCKET}/{object_name}"

    elif settings.STORAGE_BACKEND == "supabase":
        import httpx
        async with httpx.AsyncClient() as http:
            resp = await http.post(
                f"{settings.SUPABASE_URL}/storage/v1/object/{settings.STORAGE_BUCKET}/{object_name}",
                headers={
                    "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
                    "Content-Type": content_type,
                },
                content=file_data,
            )
            if resp.status_code in (200, 201):
                return f"{settings.SUPABASE_URL}/storage/v1/object/public/{settings.STORAGE_BUCKET}/{object_name}"

    return f"/storage/{object_name}"


async def get_signed_url(object_name: str, expires_secs: int = 3600) -> Optional[str]:
    if settings.STORAGE_BACKEND == "minio":
        client = await get_storage_client()
        if client:
            from datetime import timedelta
            return client.presigned_get_object(
                settings.STORAGE_BUCKET, object_name, expires=timedelta(seconds=expires_secs)
            )
    return None


async def delete_file(object_name: str) -> bool:
    if settings.STORAGE_BACKEND == "minio":
        client = await get_storage_client()
        if client:
            try:
                client.remove_object(settings.STORAGE_BUCKET, object_name)
                return True
            except Exception:
                return False
    return False
