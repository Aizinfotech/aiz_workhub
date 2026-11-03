from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from accounts.models import User
from .models import Task

from django.contrib import messages
from django.shortcuts import redirect
from .forms import TaskForm

from django.shortcuts import get_object_or_404

from django.core.exceptions import PermissionDenied
from .forms import TaskCommentForm, TaskAttachmentForm


@login_required
def task_list(request):

    if request.user.is_superuser or request.user.role == User.Role.ADMIN:
        tasks = Task.objects.all()

    elif request.user.role == User.Role.MANAGER:
        tasks = Task.objects.filter(
            project__manager=request.user
        )

    elif request.user.role == User.Role.EMPLOYEE:
        tasks = Task.objects.filter(
            assigned_to=request.user
        )

    else:
        tasks = Task.objects.filter(
            project__client=request.user
        )

    return render(
        request,
        "tasks/task_list.html",
        {"tasks": tasks},
    )




@login_required
def task_create(request):

    if not (
        request.user.is_superuser
        or request.user.role in [
            User.Role.ADMIN,
            User.Role.MANAGER,
        ]
    ):
        return redirect("tasks:list")

    if request.method == "POST":
        form = TaskForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Task created successfully."
            )
            return redirect("tasks:list")

    else:
        form = TaskForm()

    return render(
        request,
        "tasks/task_form.html",
        {"form": form},
    )


@login_required
def task_detail(request, pk):

    task = get_object_or_404(Task, pk=pk)

    return render(
        request,
        "tasks/task_detail.html",
        {"task": task},
    )


@login_required
def task_update(request, pk):

    task = get_object_or_404(Task, pk=pk)

    if request.method == "POST":
        form = TaskForm(
            request.POST,
            instance=task,
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Task updated successfully."
            )
            return redirect("tasks:detail", pk=task.pk)

    else:
        form = TaskForm(instance=task)

    return render(
        request,
        "tasks/task_form.html",
        {
            "form": form,
            "task": task,
        },
    )


@login_required
def task_delete(request, pk):

    task = get_object_or_404(Task, pk=pk)

    if not (
        request.user.is_superuser
        or request.user.role in [
            User.Role.ADMIN,
            User.Role.MANAGER,
        ]
    ):
        return redirect("tasks:list")

    if request.method == "POST":
        task.delete()

        messages.success(
            request,
            "Task deleted successfully."
        )

        return redirect("tasks:list")

    return render(
        request,
        "tasks/task_confirm_delete.html",
        {"task": task},
    )



def can_access_task(user, task):
    if user.is_superuser or user.role == User.Role.ADMIN:
        return True

    if user.role == User.Role.MANAGER:
        return task.project.manager == user

    if user.role == User.Role.EMPLOYEE:
        return task.assigned_to == user

    if user.role == User.Role.CLIENT:
        return task.project.client == user

    return False



@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if not can_access_task(request.user, task):
        raise PermissionDenied

    context = {
        "task": task,
        "comment_form": TaskCommentForm(),
        "attachment_form": TaskAttachmentForm(),
    }

    return render(
        request,
        "tasks/task_detail.html",
        context,
    )




@login_required
def add_comment(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if not can_access_task(request.user, task):
        raise PermissionDenied

    if request.method == "POST":
        form = TaskCommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()

    return redirect("tasks:detail", pk=task.pk)



@login_required
def add_attachment(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if not can_access_task(request.user, task):
        raise PermissionDenied

    if request.method == "POST":
        form = TaskAttachmentForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.task = task
            attachment.uploaded_by = request.user
            attachment.save()

    return redirect("tasks:detail", pk=task.pk)
