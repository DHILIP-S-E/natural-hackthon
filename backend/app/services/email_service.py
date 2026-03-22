"""AURA Email Service — SMTP-based email sending (works with Gmail, Outlook, any SMTP)."""
import asyncio
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from app.config import settings


def _send_smtp(to_email: str, subject: str, html_body: str, text_body: str = "") -> bool:
    """Send email via SMTP (synchronous — run in executor for async)."""
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        print(f"[Email] SMTP not configured — would send to {to_email}: {subject}")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL or settings.SMTP_USER}>"
    msg["To"] = to_email

    if text_body:
        msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        if settings.SMTP_USE_TLS:
            context = ssl.create_default_context()
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls(context=context)
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(msg["From"], to_email, msg.as_string())
        else:
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(msg["From"], to_email, msg.as_string())
        print(f"[Email] Sent to {to_email}: {subject}")
        return True
    except Exception as e:
        print(f"[Email] Failed to send to {to_email}: {e}")
        return False


async def send_email(to_email: str, subject: str, html_body: str, text_body: str = "") -> bool:
    """Send email asynchronously via SMTP."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _send_smtp, to_email, subject, html_body, text_body)


# ── Pre-built email templates ──

async def send_otp_email(to_email: str, otp: str, purpose: str = "password reset") -> bool:
    """Send OTP email with AURA branding."""
    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 480px; margin: 0 auto; padding: 32px;">
        <div style="text-align: center; margin-bottom: 24px;">
            <h1 style="color: #C9A96E; font-size: 28px; margin: 0;">AURA</h1>
            <p style="color: #888; font-size: 12px; margin: 4px 0 0;">Beauty Intelligence Platform</p>
        </div>
        <div style="background: #f9f9f9; border-radius: 12px; padding: 32px; text-align: center;">
            <p style="color: #333; font-size: 14px; margin: 0 0 16px;">Your {purpose} OTP is:</p>
            <div style="font-size: 36px; font-weight: 700; letter-spacing: 8px; color: #C9A96E; padding: 16px; background: #fff; border-radius: 8px; border: 2px dashed #C9A96E; display: inline-block;">
                {otp}
            </div>
            <p style="color: #888; font-size: 12px; margin: 16px 0 0;">This code expires in 10 minutes. Do not share it with anyone.</p>
        </div>
        <p style="color: #aaa; font-size: 11px; text-align: center; margin-top: 24px;">
            If you didn't request this, please ignore this email.<br>
            &copy; 2026 Naturals AURA
        </p>
    </div>
    """
    return await send_email(to_email, f"AURA — Your {purpose} OTP: {otp}", html, f"Your AURA {purpose} OTP is: {otp}")


async def send_booking_reminder(to_email: str, customer_name: str, service: str, scheduled_at: str, location: str = "") -> bool:
    """Send booking reminder email."""
    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 480px; margin: 0 auto; padding: 32px;">
        <div style="text-align: center; margin-bottom: 24px;">
            <h1 style="color: #C9A96E; font-size: 28px; margin: 0;">AURA</h1>
        </div>
        <div style="background: #f9f9f9; border-radius: 12px; padding: 24px;">
            <p style="color: #333; font-size: 16px; margin: 0 0 8px;">Hi {customer_name},</p>
            <p style="color: #555; font-size: 14px; line-height: 1.6;">
                This is a reminder for your upcoming appointment:
            </p>
            <div style="background: #fff; border-radius: 8px; padding: 16px; margin: 16px 0; border-left: 4px solid #C9A96E;">
                <p style="margin: 0; font-weight: 600; color: #333;">{service}</p>
                <p style="margin: 4px 0 0; color: #888; font-size: 13px;">{scheduled_at}{f' · {location}' if location else ''}</p>
            </div>
            <p style="color: #555; font-size: 13px;">We look forward to seeing you!</p>
        </div>
    </div>
    """
    return await send_email(to_email, f"AURA — Appointment Reminder: {service}", html)


async def send_quality_alert_email(to_email: str, manager_name: str, session_score: float, details: str = "") -> bool:
    """Send quality flag alert to manager."""
    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 480px; margin: 0 auto; padding: 32px;">
        <div style="text-align: center; margin-bottom: 24px;">
            <h1 style="color: #C9A96E; font-size: 28px; margin: 0;">AURA</h1>
        </div>
        <div style="background: #fff3f3; border-radius: 12px; padding: 24px; border: 1px solid #ffcccc;">
            <p style="color: #cc3333; font-weight: 600; font-size: 16px; margin: 0 0 8px;">Quality Alert</p>
            <p style="color: #555; font-size: 14px;">
                A service session scored <strong>{session_score:.1f}%</strong> — below the quality threshold.
            </p>
            {f'<p style="color: #888; font-size: 13px;">{details}</p>' if details else ''}
            <p style="color: #555; font-size: 13px; margin-top: 12px;">Please review this session in the AURA dashboard.</p>
        </div>
    </div>
    """
    return await send_email(to_email, f"AURA — Quality Alert: Score {session_score:.1f}%", html)
