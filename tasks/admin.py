from django.contrib import admin
from .models import Task, TaskComment, TaskAttachment

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "project",
        "assigned_to",
        "status",
        "priority",
        "due_date",
    )

    list_filter = (
        "status",
        "priority",
        "project",
    )

    search_fields = (
        "title",
        "assigned_to__username",
        "project__name",
    )




admin.site.register(TaskComment)
admin.site.register(TaskAttachment)