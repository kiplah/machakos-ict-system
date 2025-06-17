from django.urls import path
from .views import RegisterUserView, list_pending_users, approve_user, asset_list_create, assign_asset, asset_maintenance_logs, get_audit_logs

urlpatterns = [
    path('auth/register/', RegisterUserView.as_view(), name='register'),
    path('users/pending/', list_pending_users, name='pending-users'),
    path('users/<int:user_id>/approve/', approve_user, name='approve-user'),
    path('assets/', asset_list_create, name='assets'),
    path('assets/<int:asset_id>/assign/', assign_asset, name='assign-asset'),
    path('assets/<int:asset_id>/maintenance/', asset_maintenance_logs, name='asset-maintenance'),
    path('logs/', get_audit_logs, name='audit-logs'),
]
# This file defines the URL patterns for the core application, including user registration and management endpoints.
# It maps URLs to views that handle user registration, listing pending users, and approving users.