"""AWS SNS Service — WhatsApp Business + Push Notification delivery.

Used by: Stylist cancellation alerts (F4), Scheduler confirmations (F8),
         Birthday reminders (F12), Post-visit homecare (F13), Inventory alerts (F9).
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def _get_sns_client():
    """Lazy-import boto3 so the app starts without AWS credentials in dev."""
    try:
        import boto3
        from app.config import settings
        return boto3.client(
            "sns",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
    except Exception as exc:
        logger.warning("AWS SNS client unavailable: %s", exc)
        return None


async def send_whatsapp(phone: str, message: str, template_name: Optional[str] = None) -> bool:
    """Send WhatsApp message via AWS SNS.

    Phone must be E.164 format: +919876543210
    Falls back to logging when SNS is unconfigured (dev mode).
    """
    from app.config import settings

    if not settings.AWS_SNS_WHATSAPP_SENDER_ID:
        logger.info("[SNS-DEV] WhatsApp to %s: %s", phone, message[:80])
        return True

    client = _get_sns_client()
    if not client:
        return False

    try:
        client.publish(
            PhoneNumber=phone,
            Message=message,
            MessageAttributes={
                "AWS.SNS.SMS.SMSType": {"DataType": "String", "StringValue": "Transactional"},
                "AWS.MM.SMS.OriginationNumber": {
                    "DataType": "String",
                    "StringValue": settings.AWS_SNS_WHATSAPP_SENDER_ID,
                },
            },
        )
        logger.info("[SNS] WhatsApp sent to %s", phone)
        return True
    except Exception as exc:
        logger.error("[SNS] WhatsApp failed for %s: %s", phone, exc)
        return False


async def send_push(push_token: str, title: str, body: str, data: Optional[dict] = None) -> bool:
    """Send mobile push notification via AWS SNS."""
    from app.config import settings

    if not settings.AWS_SNS_PLATFORM_ARN:
        logger.info("[SNS-DEV] Push to %s: %s — %s", push_token[:20], title, body)
        return True

    client = _get_sns_client()
    if not client:
        return False

    try:
        import json
        endpoint_response = client.create_platform_endpoint(
            PlatformApplicationArn=settings.AWS_SNS_PLATFORM_ARN,
            Token=push_token,
        )
        endpoint_arn = endpoint_response["EndpointArn"]

        payload = {
            "default": body,
            "GCM": json.dumps({
                "notification": {"title": title, "body": body},
                "data": data or {},
            }),
            "APNS": json.dumps({
                "aps": {"alert": {"title": title, "body": body}, "sound": "default"},
                **(data or {}),
            }),
        }
        client.publish(
            TargetArn=endpoint_arn,
            Message=json.dumps(payload),
            MessageStructure="json",
        )
        logger.info("[SNS] Push sent to token %s...", push_token[:20])
        return True
    except Exception as exc:
        logger.error("[SNS] Push failed: %s", exc)
        return False


async def send_sms(phone: str, message: str) -> bool:
    """Send SMS via AWS SNS (fallback when WhatsApp unavailable)."""
    from app.config import settings

    if not settings.AWS_ACCESS_KEY_ID:
        logger.info("[SNS-DEV] SMS to %s: %s", phone, message[:80])
        return True

    client = _get_sns_client()
    if not client:
        return False

    try:
        client.publish(
            PhoneNumber=phone,
            Message=message,
            MessageAttributes={
                "AWS.SNS.SMS.SMSType": {"DataType": "String", "StringValue": "Transactional"},
            },
        )
        return True
    except Exception as exc:
        logger.error("[SNS] SMS failed for %s: %s", phone, exc)
        return False
