"""
Firebase Cloud Messaging utilities using FCM HTTP v1 API (firebase-admin).

Replaces legacy https://fcm.googleapis.com/fcm/send with service account auth.
Configure via .env — see .env.example.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_firebase_app = None


def _get_base_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def _resolve_service_account_path() -> Path:
    env_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_FILE", "").strip()
    if env_path:
        path = Path(env_path)
        if not path.is_absolute():
            path = _get_base_dir() / path
        return path
    return _get_base_dir() / "credentials" / "firebase-service-account.json"


def init_firebase():
    """Initialize firebase-admin once. Safe to call multiple times."""
    global _firebase_app
    if _firebase_app is not None:
        return _firebase_app

    import firebase_admin
    from firebase_admin import credentials

    if firebase_admin._apps:
        _firebase_app = firebase_admin.get_app()
        return _firebase_app

    sa_path = _resolve_service_account_path()
    if not sa_path.exists():
        raise FileNotFoundError(
            f"Firebase service account not found at {sa_path}. "
            "Set FIREBASE_SERVICE_ACCOUNT_FILE in .env"
        )

    cred = credentials.Certificate(str(sa_path))
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    options = {"projectId": project_id} if project_id else None
    _firebase_app = firebase_admin.initialize_app(cred, options)
    logger.info("Firebase Admin initialized for project %s", project_id or cred.project_id)
    return _firebase_app


def send_fcm_message(device_token: str, msg: str, title: str, data: dict[str, Any] | None = None) -> bool:
    """
    Send push notification via FCM HTTP v1.

    device_token may use __colon__ encoding from mobile clients.
    """
    from firebase_admin import messaging

    if not device_token:
        logger.warning("Empty device token — skipping FCM send")
        return False

    token = device_token.replace("__colon__", ":")
    init_firebase()

    payload_data = {str(k): str(v) for k, v in (data or {}).items()}

    message = messaging.Message(
        notification=messaging.Notification(title=title, body=msg),
        data=payload_data,
        token=token,
        android=messaging.AndroidConfig(priority="high"),
    )

    try:
        response = messaging.send(message)
        logger.info("FCM v1 sent: %s", response)
        return True
    except Exception as exc:
        logger.exception("FCM v1 send failed: %s", exc)
        return False


# Backward-compatible alias used across Django views
def sendFMCMsg(deviceToken, msg, title, data):
    if isinstance(data, str):
        try:
            data = json.loads(data) if data else {}
        except json.JSONDecodeError:
            data = {"payload": data}
    elif data is None:
        data = {}
    return send_fcm_message(deviceToken, msg, title, data)
