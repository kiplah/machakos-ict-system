from .models import AuditLog

def log_action(user, action, description):
    AuditLog.objects.create(
        action=action,
        performed_by=user,
        description=description
    )
