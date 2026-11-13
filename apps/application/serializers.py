import re

from rest_framework import serializers

from apps.common.serializer import DistrictsSerializer
from .models import Application


class ApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ("id", "first_name", "last_name", "passport", "pinfl", "gender",
                  "direction", "district", "birth_date")
        read_only_fields = ("id",)
        extra_kwargs = {
            "direction": {"required": True, "allow_null": False},
            "district": {"required": True, "allow_null": False},
        }

    def validate_passport(self, value):
        value = value.strip().upper()
        if not re.fullmatch(r"[A-Z]{2}\d{7}", value):
            raise serializers.ValidationError("Pasport AA1234567 formatida bo'lishi kerak.")
        if Application.objects.filter(passport=value).exists():
            raise serializers.ValidationError("Bu pasport bilan ariza allaqachon topshirilgan.")
        return value

    def validate_pinfl(self, value):
        if not re.fullmatch(r"\d{14}", value.strip()):
            raise serializers.ValidationError("JSHSHIR (PINFL) 14 ta raqamdan iborat bo'lishi kerak.")
        return value.strip()

    def validate(self, attrs):
        user = self.context['request'].user
        if Application.objects.filter(user=user).exists():
            raise serializers.ValidationError("Siz allaqachon ariza topshirgansiz.")
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ApplicationDirectionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    faculty = serializers.CharField(source="faculty.title")


class ApplicationDetailSerializer(serializers.ModelSerializer):
    # Avval yo'nalish DistrictsSerializer bilan chiqarilardi (noto'g'ri serializer)
    direction = ApplicationDirectionSerializer()
    district = DistrictsSerializer()
    status = serializers.CharField(source="get_status_display")
    status_code = serializers.CharField(source="status")
    gender = serializers.CharField(source="get_gender_display")
    has_contract = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = ("id", "first_name", "last_name", "passport", "pinfl", "gender",
                  "direction", "district", "birth_date", "status", "status_code",
                  "accepted_at", "created", "has_contract")

    def get_has_contract(self, obj):
        path = obj.contract_path
        return bool(path and path.is_file())
