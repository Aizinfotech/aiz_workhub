from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "manager",
        "client",
        "status",
        "start_date",
        "due_date",
    )
    list_filter = ("status", "manager", "client")
    search_fields = ("title", "description")
