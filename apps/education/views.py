from django.db.models import Count
from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import Faculty
from .serializers import FacultyDetailSerializer, FacultyListSerializer


class FacultyListAPIView(ListAPIView):
    serializer_class = FacultyListSerializer

    def get_queryset(self):
        qs = Faculty.objects.annotate(directions_count=Count("directions")).order_by("id")
        degree = self.request.query_params.get("degree")
        return qs.filter(degree=degree) if degree else qs


class FacultyDetailAPIView(RetrieveAPIView):
    queryset = Faculty.objects.select_related("director").prefetch_related("directions")
    serializer_class = FacultyDetailSerializer
