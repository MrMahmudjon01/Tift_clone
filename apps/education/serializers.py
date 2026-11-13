from rest_framework import serializers

from apps.education.models import Direction, Director, Faculty


class FacultyListSerializer(serializers.ModelSerializer):
    degree_display = serializers.CharField(source="get_degree_display", read_only=True)
    directions_count = serializers.IntegerField(read_only=True)  # view annotate qiladi

    class Meta:
        model = Faculty
        fields = ("id", "title", "degree", "degree_display", "directions_count")


class DirectorModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Director
        fields = ("full_name", "bio", "phone_number", "picture")


class DirectionModelSerializer(serializers.ModelSerializer):
    # id ariza formasida yo'nalishni tanlash uchun kerak (avval yo'q edi)
    language = serializers.CharField(source="get_language_display", read_only=True)
    education_type = serializers.CharField(source="get_education_type_display", read_only=True)

    class Meta:
        model = Direction
        fields = ("id", "title", "language", "body", "education_type")


class FacultyDetailSerializer(serializers.ModelSerializer):
    director = DirectorModelSerializer()
    directions = DirectionModelSerializer(many=True)
    degree = serializers.CharField(source="get_degree_display", read_only=True)

    class Meta:
        model = Faculty
        fields = ("id", "title", "body", "degree", "director", "directions")
