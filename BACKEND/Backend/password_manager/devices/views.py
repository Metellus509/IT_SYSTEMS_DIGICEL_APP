from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Device, DeviceAccount, DeviceType, DeviceStatus
from .serializers import (
    DeviceSerializer, DeviceCreateSerializer, 
    DeviceUpdateSerializer, DeviceAccountSerializer
)
from django.contrib.auth import authenticate
from django.core.exceptions import PermissionDenied
from django.utils import timezone 

# Create your views here.



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def device_list(request):
    """
    Get all devices with accessible accounts only
    Optional filters: type, status
    """
    devices = Device.objects.all()
    
    # Filtres optionnels
    device_type = request.GET.get('type')
    status_filter = request.GET.get('status')
    search = request.GET.get('search')
    
    if device_type:
        devices = devices.filter(device_type=device_type)
    if status_filter:
        devices = devices.filter(status=status_filter)
    if search:
        devices = devices.filter(
            Q(hostname__icontains=search) |
            Q(ip_address__icontains=search) |
            Q(location__icontains=search)
        )
    
    serializer = DeviceSerializer(
        devices, 
        many=True,
        context={'request': request}
    )


    return Response({
        'devices': serializer.data
        #'count': devices.count()
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def device_create(request):
    """
    Create a new device
    """
    serializer = DeviceCreateSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        device = serializer.save()
        
        # Retourner les données complètes
        full_serializer = DeviceSerializer(
            device, 
            context={'request': request}
        )
        return Response({
            'message': 'Device created successfully',
            'device': full_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def device_detail(request, device_id):
    """
    Get specific device details with accessible accounts
    """
    device = get_object_or_404(Device, id=device_id)
    
    serializer = DeviceSerializer(
        device, 
        context={'request': request}
    )
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def device_update(request, device_id):
    """
    Update a device (PUT for full update, PATCH for partial)
    """
    device = get_object_or_404(Device, id=device_id)
    
    serializer = DeviceUpdateSerializer(
        device, 
        data=request.data,
        partial=(request.method == 'PATCH'),
        context={'request': request}
    )
    
    if serializer.is_valid():
        serializer.save()
        
        # Retourner les données complètes mises à jour
        full_serializer = DeviceSerializer(
            device, 
            context={'request': request}
        )
        return Response({
            'message': 'Device updated successfully',
            'device': full_serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def device_delete(request, device_id):
    """
    Delete a device
    """
    device = get_object_or_404(Device, id=device_id)
    
    # Sauvegarder les infos pour la réponse
    device_info = {
        'id': device.id,
        'hostname': device.hostname,
        'ip_address': device.ip_address
    }
    
    device.delete()
    
    return Response({
        'message': 'Device deleted successfully',
        'deleted_device': device_info
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def device_add_account(request, device_id):
    """
    Add an account to a device (shared or personal)
    """
    device = get_object_or_404(Device, id=device_id)
    
    serializer = DeviceAccountSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        account = serializer.save(device=device)

        # Sérialiser sans le password
        account_data = DeviceAccountSerializer(
            account, 
            context={'request': request}
        ).data
        account_data.pop('password', None)

        return Response({
            'message': 'Account added successfully',
            'account': account_data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_accounts(request):
    """
    Get all accounts accessible to current user:
    - All shared accounts
    - Personal accounts where username MATCHES current user's username
    """
    current_username = request.user.username
    
    # Shared accounts + personal accounts où le username MATCHE l'utilisateur connecté
    accounts = DeviceAccount.objects.filter(
        Q(is_shared=True) | 
        Q(username=current_username, is_shared=False)
    ).select_related('device')
    
    serializer = DeviceAccountSerializer(
        accounts, 
        many=True,
        context={'request': request}
    )
    
    return Response({
        'accounts': serializer.data,
        'count': accounts.count()
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_accounts(request):
    """
    Get ALL accounts (admin only) - pour la gestion complète
    """
    if not request.user.is_superuser:
        return Response({
            'error': 'Only administrators can view all accounts'
        }, status=status.HTTP_403_FORBIDDEN)
    
    accounts = DeviceAccount.objects.all().select_related('device', 'owner')
    
    serializer = DeviceAccountSerializer(
        accounts, 
        many=True,
        context={'request': request}
    )
    
    return Response({
        'accounts': serializer.data,
        'count': accounts.count()
    }, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request, account_id):
    """
    Delete an account (only if owner or admin)
    """
    account = get_object_or_404(DeviceAccount, id=account_id)
    
    # Vérifier les permissions
    if not (account.owner == request.user or request.user.is_superuser):
        return Response({
            'error': 'You can only delete your own accounts'
        }, status=status.HTTP_403_FORBIDDEN)
    
    account_info = {
        'id': account.id,
        'username': account.username,
        'device': account.device.hostname
    }
    
    account.delete()
    
    return Response({
        'message': 'Account deleted successfully',
        'deleted_account': account_info
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def device_types(request):
    """
    Get available device types
    """
    types = [{'value': value, 'display': display} for value, display in DeviceType.choices]
    return Response({
        'device_types': types
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def device_statuses(request):
    """
    Get available device statuses
    """
    statuses = [{'value': value, 'display': display} for value, display in DeviceStatus.choices]
    return Response({
        'device_statuses': statuses
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_devices(request):
    """
    Search devices by hostname, IP, or location
    """
    search_query = request.GET.get('q', '').strip()
    
    if not search_query:
        return Response({
            'error': 'Search query is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    devices = Device.objects.filter(
        Q(hostname__icontains=search_query) |
        Q(ip_address__icontains=search_query) |
        Q(location__icontains=search_query)
    )
    
    serializer = DeviceSerializer(
        devices, 
        many=True,
        context={'request': request}
    )
    
    return Response({
        'devices': serializer.data,
        'count': devices.count(),
        'search_query': search_query
    }, status=status.HTTP_200_OK)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_account(request, account_id):
    """
    Update an account (only if owner or admin)
    """
    account = get_object_or_404(DeviceAccount, id=account_id)
    
    # Vérifier les permissions
    if not (account.owner == request.user or request.user.is_superuser):
        return Response({
            'error': 'You can only update your own accounts'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = DeviceAccountSerializer(
        account,
        data=request.data,
        partial=(request.method == 'PATCH'),
        context={'request': request}
    )
    
    if serializer.is_valid():
        # Pour les comptes personnels, empêcher la modification du owner
        if not account.is_shared and 'owner' in serializer.validated_data:
            return Response({
                'error': 'Cannot change owner of personal account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        
        return Response({
            'message': 'Account updated successfully',
            'account': serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def device_stats(request):
    """
    Get statistics about devices and accounts
    """
    total_devices = Device.objects.count()
    active_devices = Device.objects.filter(status=DeviceStatus.ACTIVE).count()
    inactive_devices = Device.objects.filter(status=DeviceStatus.INACTIVE).count()
    
    total_accounts = DeviceAccount.objects.count()
    shared_accounts = DeviceAccount.objects.filter(is_shared=True).count()
    personal_accounts = DeviceAccount.objects.filter(is_shared=False).count()
    
    # Comptes accessibles à l'utilisateur connecté
    current_username = request.user.username
    my_accessible_accounts = DeviceAccount.objects.filter(
        Q(is_shared=True) | 
        Q(username=current_username, is_shared=False)
    ).count()
    
    device_types_count = {}
    for device_type in DeviceType.values:
        device_types_count[device_type] = Device.objects.filter(device_type=device_type).count()
    
    return Response({
        'devices': {
            'total': total_devices,
            'active': active_devices,
            'inactive': inactive_devices,
            'by_type': device_types_count
        },
        'accounts': {
            'total': total_accounts,
            'shared': shared_accounts,
            'personal': personal_accounts,
            'my_accessible': my_accessible_accounts
        }
    }, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reveal_account_password(request, account_id):
    """
    Simple password confirmation endpoint
    Returns success status without the password (frontend already has it)
    """
    user_password = request.data.get('password')
    
    if not user_password:
        return Response({
            'error': 'Password confirmation is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Vérifier le mot de passe de l'utilisateur
    user = authenticate(username=request.user.username, password=user_password)
    
    if not user:
        return Response({
            'error': 'Invalid password'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Récupérer le compte spécifique
    account = get_object_or_404(DeviceAccount, id=account_id)
    
    # Vérifier que l'utilisateur a accès à ce compte
    current_username = request.user.username
    if not (account.is_shared or account.username == current_username):
        return Response({
            'error': 'You do not have access to this account'
        }, status=status.HTTP_403_FORBIDDEN)
    
    return Response({
        'message': 'Password access granted',
        'access_granted': True,
        'account_id': account_id,
        'granted_at': timezone.now().isoformat(),
        'expires_at': (timezone.now() + timezone.timedelta(seconds=30)).isoformat()
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reveal_passwords(request, device_id=None):
    """
    Reveal passwords for accounts after password confirmation
    Can be used for a specific device or all devices
    """
    user_password = request.data.get('password')
    
    if not user_password:
        return Response({
            'error': 'Password confirmation is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Vérifier le mot de passe de l'utilisateur
    user = authenticate(username=request.user.username, password=user_password)
    
    if not user:
        return Response({
            'error': 'Invalid password'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Si device_id est fourni, récupérer seulement ce device
    if device_id:
        device = get_object_or_404(Device, id=device_id)
        devices = [device]
    else:
        # Sinon récupérer tous les devices
        devices = Device.objects.all()
    
    # Marquer la requête pour afficher les mots de passe
    request.show_passwords = True
    
    # Sérialiser les données avec les mots de passe visibles
    serializer = DeviceSerializer(
        devices, 
        many=True,
        context={'request': request}
    )
    
    return Response({
        'message': 'Passwords revealed successfully',
        'devices': serializer.data,
        'revealed_at': timezone.now().isoformat(),
        'expires_at': (timezone.now() + timezone.timedelta(seconds=30)).isoformat()
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reveal_my_accounts_passwords(request):
    """
    Reveal passwords for all my accessible accounts
    """
    user_password = request.data.get('password')
    
    if not user_password:
        return Response({
            'error': 'Password confirmation is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Vérifier le mot de passe de l'utilisateur
    user = authenticate(username=request.user.username, password=user_password)
    
    if not user:
        return Response({
            'error': 'Invalid password'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    current_username = request.user.username
    accounts = DeviceAccount.objects.filter(
        Q(is_shared=True) | 
        Q(username=current_username, is_shared=False)
    ).select_related('device')
    
    # Marquer la requête pour afficher les mots de passe
    request.show_passwords = True
    
    serializer = DeviceAccountSerializer(
        accounts, 
        many=True,
        context={'request': request}
    )
    
    return Response({
        'message': 'Passwords revealed successfully',
        'accounts': serializer.data,
        'count': accounts.count(),
        'revealed_at': timezone.now().isoformat(),
        'expires_at': (timezone.now() + timezone.timedelta(seconds=30)).isoformat()
    }, status=status.HTTP_200_OK)