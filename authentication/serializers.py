from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User, Abonnement


class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    role      = serializers.ChoiceField(choices=User.ROLE_CHOICES, default="etudiant")

    class Meta:
        model  = User
        fields = ("username", "email", "first_name", "last_name", "password", "password2", "role")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        user     = User(**validated_data)
        user.set_password(password)
        user.save()
        Abonnement.objects.create(user=user, type="free")
        return user


class UserSerializer(serializers.ModelSerializer):
    abonnement_type = serializers.SerializerMethodField()
    is_premium      = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()


    class Meta:
        model  = User
        fields = ("id", "username", "email", "first_name", "last_name", "role", "avatar","avatar_url", "abonnement_type", "is_premium", "created_at")

    def get_abonnement_type(self, obj):
        try:
            return obj.abonnement.type
        except:
            return "free"

    def get_is_premium(self, obj):
        return obj.is_premium
    
    def get_avatar_url(self, obj):

        request = self.context.get("request")

        if obj.avatar:
            if request:
                return request.build_absolute_uri(
                obj.avatar.url
                )
            return obj.avatar.url

            

        return None