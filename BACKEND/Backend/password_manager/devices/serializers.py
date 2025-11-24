from rest_framework import serializers
from django.db.models import Q
from .models import Device, DeviceAccount, DeviceType, DeviceStatus

class DeviceAccountSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True, allow_null=True)
    is_owned_by_me = serializers.SerializerMethodField()
    is_my_personal_account = serializers.SerializerMethodField()
    device_hostname = serializers.CharField(source='device.hostname', read_only=True)
    device_ip = serializers.CharField(source='device.ip_address', read_only=True)
    #password = serializers.SerializerMethodField() 

    class Meta:
        model = DeviceAccount
        fields = [
            'id', 'username', 'password', 'description', 
            'is_shared', 'owner', 'owner_username', 
            'is_owned_by_me', 'is_my_personal_account',
            'device_hostname', 'device_ip',
            'created_by', 'created_at'
        ]
        extra_kwargs = {
            #'password': {'write_only': True},
            'owner': {'read_only': True},
        }

    # def get_password_visible(self, obj):
    #     """
    #     Retourne le mot de passe seulement si explicitement demandé
    #     """
    #     request = self.context.get('request')
    #     if request and hasattr(request, 'show_passwords') and request.show_passwords:
    #         # Ici vous pouvez déchiffrer le mot de passe si nécessaire
    #         # password = decrypt_password(obj.password)
    #         # return password
    #         return obj.password  # Retourne le mot de passe en clair
    #     return None  # Ou "********" pour masquer

    def get_is_owned_by_me(self, obj):
        """
        Vérifie si le compte appartient à l'utilisateur connecté
        - Pour les comptes personnels : seulement si owner == user connecté
        - Pour les comptes partagés : JAMAIS True (car ils n'ont pas de propriétaire spécifique)
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if obj.is_shared:
                return False  # ← CORRECTION : Les shared accounts n'appartiennent à personne
            return obj.owner == request.user
        return False

    def get_is_my_personal_account(self, obj):
        """
        Vérifie si c'est un compte personnel qui matche le username de l'utilisateur connecté
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if not obj.is_shared and obj.username == request.user.username:
                return True
        return False

    def create(self, validated_data):
        # Définir automatiquement le propriétaire et le créateur
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if not validated_data.get('is_shared'):
                validated_data['owner'] = request.user
            validated_data['created_by'] = request.user
        
        # Ici vous pouvez ajouter le chiffrement du mot de passe si nécessaire
        # password = validated_data['password']
        # validated_data['password'] = encrypt_password(password)
        
        return super().create(validated_data)

    # def to_representation(self, instance):
    #     """Masquer le mot de passe dans la représentation"""
    #     representation = super().to_representation(instance)
        
    #     # Masquer le mot de passe même s'il est chiffré
    #     if 'password' in representation:
    #         representation['password'] = '********'
        
    #     return representation

class DeviceSerializer(serializers.ModelSerializer):
    accounts = serializers.SerializerMethodField()
    created_by = serializers.StringRelatedField(read_only=True)
    #accounts_count = serializers.SerializerMethodField()
    #accessible_accounts_count = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = [
            'id', 'hostname', 'ip_address', 'location', 
            'device_type', 'status', 'created_by', 
            'created_at', 'updated_at', 'accounts', 
            #'accounts_count', 'accessible_accounts_count'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def get_accounts(self, obj):
        """
        Retourne seulement les comptes accessibles à l'utilisateur connecté :
        - Tous les shared accounts
        - Personal accounts où le username matche exactement l'utilisateur connecté
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            current_username = request.user.username
            
            # Utiliser la méthode du modèle si elle existe
            if hasattr(obj, 'get_accessible_accounts'):
                accessible_accounts = obj.get_accessible_accounts(request.user)
            else:
                # Fallback: filtrer directement
                accessible_accounts = obj.accounts.filter(
                    Q(is_shared=True) | 
                    Q(username=current_username, is_shared=False)
                )
            
            return DeviceAccountSerializer(
                accessible_accounts, 
                many=True,
                context=self.context
            ).data
        return []

    # def get_accounts_count(self, obj):
    #     """Nombre total de comptes sur le device"""
    #     return obj.accounts.count()

    # def get_accessible_accounts_count(self, obj):
    #     """Nombre de comptes accessibles à l'utilisateur connecté"""
    #     request = self.context.get('request')
    #     if request and request.user.is_authenticated:
    #         current_username = request.user.username
    #         if hasattr(obj, 'get_accessible_accounts'):
    #             return obj.get_accessible_accounts(request.user).count()
    #         else:
    #             return obj.accounts.filter(
    #                 Q(is_shared=True) | 
    #                 Q(username=current_username, is_shared=False)
    #             ).count()
    #     return 0

class DeviceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = [
            'hostname', 'ip_address', 'location', 
            'device_type', 'status'
        ]

    def validate_hostname(self, value):
        """Validation personnalisée pour le hostname"""
        if Device.objects.filter(hostname=value).exists():
            raise serializers.ValidationError("A device with this hostname already exists.")
        return value

    def validate_ip_address(self, value):
        """Validation personnalisée pour l'adresse IP"""
        if Device.objects.filter(ip_address=value).exists():
            raise serializers.ValidationError("A device with this IP address already exists.")
        return value

    def create(self, validated_data):
        # Ajouter l'utilisateur connecté comme créateur
        device = Device.objects.create(
            **validated_data,
            created_by=self.context['request'].user
        )
        return device

class DeviceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = [
            'hostname', 'ip_address', 'location', 
            'device_type', 'status'
        ]
        extra_kwargs = {
            'hostname': {'required': False},
            'ip_address': {'required': False},
        }

    def validate_hostname(self, value):
        """Validation du hostname lors de la mise à jour"""
        if Device.objects.filter(hostname=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("A device with this hostname already exists.")
        return value

    def validate_ip_address(self, value):
        """Validation de l'IP lors de la mise à jour"""
        if Device.objects.filter(ip_address=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("A device with this IP address already exists.")
        return value

# Sérialiseurs pour les choix (enums)
class DeviceTypeSerializer(serializers.Serializer):
    value = serializers.CharField()
    display = serializers.CharField()

class DeviceStatusSerializer(serializers.Serializer):
    value = serializers.CharField()
    display = serializers.CharField()