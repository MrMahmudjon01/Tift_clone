from django.contrib.admin.views.decorators import staff_member_required
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import Application
from .serializers import ApplicationCreateSerializer, ApplicationDetailSerializer


class ApplicationCreateAPIView(CreateAPIView):
    serializer_class = ApplicationCreateSerializer
    queryset = Application.objects.all()
    permission_classes = (IsAuthenticated,)
    throttle_scope = 'application'


class ApplicationStatusesListAPIView(ListAPIView):
    """Faqat joriy foydalanuvchining arizalari."""
    serializer_class = ApplicationDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return (Application.objects.filter(user=self.request.user)
                .select_related('direction__faculty', 'district__region'))


class ApplicationContractDownloadAPIView(APIView):
    """Qabul qilingan ariza shartnomasini (PDF) faqat ariza egasiga beradi."""
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        application = get_object_or_404(Application, pk=pk, user=request.user)
        path = application.contract_path
        if not path or not path.is_file():
            raise Http404("Shartnoma hali tayyor emas.")
        return FileResponse(open(path, 'rb'), as_attachment=True,
                            filename=f"shartnoma-{application.pk}.pdf", content_type='application/pdf')


@method_decorator(staff_member_required, name='dispatch')
class StudentApplicationTemplateview(TemplateView):
    """Shartnoma shablonini ko'rish (faqat xodimlar uchun).

    Avval bu sahifa login talab qilmasdi: ?application_id=1,2,3... deb har qanday
    arizachining pasport ma'lumotlarini ko'rish mumkin edi.
    """
    template_name = "application.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application_id = self.request.GET.get("application_id")
        context['application'] = get_object_or_404(Application, pk=application_id) if application_id else None
        return context
