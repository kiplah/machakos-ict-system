from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import CustomUser, Asset, Maintenance, AuditLog
from .serializers import UserRegistrationSerializer, AssetSerializer, MaintenanceSerializer, AuditLogSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from datetime import date

def log_action(user, action, description):
    # Implement your logging logic here, e.g., save to a database or print to console
    print(f"User: {user}, Action: {action}, Description: {description}")

class RegisterUserView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_pending_users(request):
    users = CustomUser.objects.filter(is_approved=False)
    serializer = UserRegistrationSerializer(users, many=True)
    return Response(serializer.data)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_approved_users(request):
    users = CustomUser.objects.filter(is_approved=True)
    serializer = UserRegistrationSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def approve_user(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        user.is_approved = True
        user.save()
        
        log_action(request.user, 'user_approved', f"Approved user {user.username}")

        return Response({"message": "User approved successfully."})
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found."}, status=404)
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def asset_list_create(request):
    if request.method == 'POST':
        if not request.user.is_staff:
            return Response({'error': 'Only admins can add assets.'}, status=403)
        serializer = AssetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            log_action(request.user, 'asset_created', f"Created asset {serializer.validated_data['name']}")
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    assets = Asset.objects.all()
    serializer = AssetSerializer(assets, many=True)
    return Response(serializer.data)
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def asset_maintenance_logs(request, asset_id):
    try:
        asset = Asset.objects.get(id=asset_id)
    except Asset.DoesNotExist:
        return Response({'error': 'Asset not found.'}, status=404)

    if request.method == 'POST':
        if not request.user.is_staff:
            return Response({'error': 'Only admins can log maintenance.'}, status=403)

        data = request.data.copy()
        data['asset'] = asset.id
        data['performed_by'] = request.user.id

        serializer = MaintenanceSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            log_action(request.user, 'maintenance_logged', f"Logged maintenance for asset {asset.name}")
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    elif request.method == 'GET':
        logs = Maintenance.objects.filter(asset=asset)
        serializer = MaintenanceSerializer(logs, many=True)
        return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([permissions.IsAdminUser])
def assign_asset(request, asset_id):
    try:
        asset = Asset.objects.get(id=asset_id)
        user_id = request.data.get('user_id')
        department = request.data.get('department')
        user = CustomUser.objects.get(id=user_id)

        asset.assigned_to = user
        asset.department = department
        asset.assigned_date = date.today()
        asset.status = 'assigned'
        asset.save()
        log_action(request.user, 'asset_assigned', f"Assigned asset {asset.name} to user {user.username}")
        user.is_approved = True  # Automatically approve user when assigning an asset

        return Response({'message': 'Asset assigned successfully.'})
    except Asset.DoesNotExist:
        return Response({'error': 'Asset not found.'}, status=404)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found.'}, status=404)
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def get_audit_logs(request):
    logs = AuditLog.objects.all().order_by('-timestamp')
    serializer = AuditLogSerializer(logs, many=True)
    return Response(serializer.data)
