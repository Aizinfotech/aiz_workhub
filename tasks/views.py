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
from django.http import HttpResponseForbidden
from accounts.permissions import can_access_task, is_admin, is_manager, can_manage_task
from .emails import send_task_assignment_email, send_task_status_email



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
        is_admin(request.user)
        or is_manager(request.user)
    ):
        return HttpResponseForbidden(
            "You cannot create tasks."
        )

            # return redirect("tasks:list")

    # if not (
    #     request.user.is_superuser
    #     or request.user.role in [
    #         User.Role.ADMIN,
    #         User.Role.MANAGER,
    #     ]
    # ):

    if request.method == "POST":
        form = TaskForm(request.POST)

        if form.is_valid():
            task = form.save()

            send_task_assignment_email(task)

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



    

# @login_required
# def task_detail(request, pk):

#     task = get_object_or_404(Task, pk=pk)

#     return render(
#         request,
#         "tasks/task_detail.html",
#         {"task": task},
#     )

@login_required
def task_detail(request, pk):

    task = get_object_or_404(Task, pk=pk)

    if not can_access_task(request.user, task):
        return HttpResponseForbidden(
            "You do not have permission to view this task."
        )

    return render(
        request,
        "tasks/task_detail.html",
        {"task": task},
    )



@login_required
def task_update(request, pk):

    task = get_object_or_404(Task, pk=pk)
    old_assigned_to_id = task.assigned_to_id
    old_status = task.status

    if not can_manage_task(request.user, task):
        return HttpResponseForbidden(
            "You cannot edit this task."
        )

    if request.method == "POST":
        form = TaskForm(
            request.POST,
            instance=task,
        )

        if form.is_valid():
            task = form.save()

            if task.assigned_to_id != old_assigned_to_id:
                send_task_assignment_email(task)
                
            if task.status != old_status:
                send_task_status_email(task)

            return redirect(
                "tasks:detail",
                pk=task.pk,
            )
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

    if not can_manage_task(
        request.user,
        task,
    ):
        return HttpResponseForbidden(
            "You cannot delete this task."
        )

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
    old_status = task.status

    if not can_access_task(request.user, task):
        raise PermissionDenied

    if request.method == "POST":
        form = TaskForm(
            request.POST,
            instance=task,
        )

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

    # if not can_access_task(request.user, task):
    #     raise PermissionDenied
    if not can_access_task(request.user, task):
        return HttpResponseForbidden(
            "You cannot comment on this task."
        )

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

    # if not can_access_task(request.user, task):
    #     raise PermissionDenied
    if not can_access_task(request.user, task):
        return HttpResponseForbidden(
            "You cannot upload to this task."
        )


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


def can_manage_tasks(user):
    return (
        user.is_authenticated
        and (
            user.is_superuser
            or user.role in [
                User.Role.ADMIN,
                User.Role.MANAGER,
            ]
        )
    )




    
