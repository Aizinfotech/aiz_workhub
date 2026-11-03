from django import forms
from accounts.models import User
from .models import Task, TaskComment, TaskAttachment


class TaskForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = [
            "project",
            "title",
            "description",
            "assigned_to",
            "status",
            "priority",
            "due_date",
        ]

        widgets = {
            "due_date": forms.DateInput(
                attrs={"type": "date"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["assigned_to"].queryset = (
            User.objects.filter(
                role=User.Role.EMPLOYEE
            )
        )






class TaskCommentForm(forms.ModelForm):
    class Meta:
        model = TaskComment
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(
                attrs={"rows": 3}
            )
        }




class TaskAttachmentForm(forms.ModelForm):
    class Meta:
        model = TaskAttachment
        fields = ["file"]
