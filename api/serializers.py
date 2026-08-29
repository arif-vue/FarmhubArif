from rest_framework import serializers

from .models import Cow, CowActivity, Farm, FarmerProfile, MilkRecord


class FarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = ["id", "name", "location", "agent", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]

    def validate_agent(self, value):
        if value.role != "agent":
            raise serializers.ValidationError("Only agent users can manage a farm.")
        return value


class FarmerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmerProfile
        fields = ["id", "user", "farm", "created_at"]
        read_only_fields = ["created_at"]


class CowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cow
        fields = [
            "id",
            "name",
            "tag_number",
            "breed",
            "farm",
            "owner",
            "date_of_birth",
            "notes",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class CowActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CowActivity
        fields = [
            "id",
            "cow",
            "activity_type",
            "occurred_on",
            "description",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["created_by", "created_at"]


class MilkRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MilkRecord
        fields = [
            "id",
            "cow",
            "recorded_on",
            "quantity_liters",
            "notes",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["created_by", "created_at"]
