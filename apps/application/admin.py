from django.contrib import admin
from apps.application.models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "passport", "direction", "status", "created")
    list_editable = ("status", )
    list_filter = ("status", "gender", "direction__faculty")
    search_fields = ("first_name", "last_name", "passport", "pinfl")
    readonly_fields = ("contract_url", "accepted_at", "created")
    list_select_related = ("direction",)
