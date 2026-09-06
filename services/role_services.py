"""Backward-compatible imports for the canonical role service."""

from services.role_service import (
    assign_role,
    get_audit_logs,
    get_user_role,
    log_audit,
)

__all__ = ["assign_role", "get_audit_logs", "get_user_role", "log_audit"]