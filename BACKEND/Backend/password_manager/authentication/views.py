from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer
from rest_framework_simplejwt.exceptions import TokenError
from .models import *

# Create your views here.

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # ← CHANGEMENT ICI : De AllowAny à IsAuthenticated
def register_user(request):
    """
    Vue pour l'inscription d'un nouvel utilisateur
    SEULEMENT pour les utilisateurs connectés
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
                
        return Response({
            'message': 'User account created successfully',
            'user': UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Vue pour la connexion d'un utilisateur
    """
    serializer = UserLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(username=username, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Connection Successful',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid Credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    View for user logout - blacklist the refresh token
    """
    try:
        refresh_token = request.data.get('refresh_token')
        
        if not refresh_token:
            return Response({
                'error': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
        
    except TokenError as e:
        return Response({
            'error': 'Invalid or expired token'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'error': 'Logout failed'
        }, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
def get_current_user(request):
    """
    Vue pour récupérer les informations de l'utilisateur connecté
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request, user_id):
    """
    Soft delete user account (mark as deleted instead of actual deletion)
    """
    try:
        # Empêcher un utilisateur de se supprimer lui-même
        if request.user.id == user_id:
            return Response({
                'error': 'You cannot delete your own account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Trouver l'utilisateur à supprimer
        user_to_delete = CustomUser.objects.get(id=user_id)
        
        # Vérifier les permissions admin
        if not request.user.is_superuser:
            return Response({
                'error': 'Only administrators can delete user accounts'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Soft delete au lieu de supprimer
        user_to_delete.soft_delete()
        
        return Response({
            'message': 'User account deleted successfully',
            'deleted_user': {
                'id': user_to_delete.id,
                'username': user_to_delete.username,
                'email': user_to_delete.email,
                'deleted_at': user_to_delete.deleted_at
            }
        }, status=status.HTTP_200_OK)
        
    except CustomUser.DoesNotExist:
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)