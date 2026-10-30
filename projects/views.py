from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User
from .forms import ProjectForm
from .models import Project


def visible_projects(user):
    if user.is_superuser or user.role == User.Role.ADMIN:
        return Project.objects.all()

    if user.role == User.Role.MANAGER:
        return Project.objects.filter(manager=user)

    if user.role == User.Role.CLIENT:
        return Project.objects.filter(client=user)

    return Project.objects.none()



@login_required
def project_list(request):
    projects = visible_projects(request.user)
    return render( request, "projects/project_list.html", {"projects": projects}, )


@login_required
def project_detail(request, pk):
    project = get_object_or_404( visible_projects(request.user), pk=pk, )
    return render( request, "projects/project_detail.html", {"project": project}, )


@login_required
def project_create(request):
    user = request.user

    if not (
        user.is_superuser
        or user.role in [User.Role.ADMIN, User.Role.MANAGER]
    ):
        messages.error(request, "You cannot create projects.")
        return redirect("accounts:dashboard")

    form = ProjectForm(request.POST or None)

    if user.role == User.Role.MANAGER and not user.is_superuser:
        form.fields["manager"].queryset = User.objects.filter(pk=user.pk)
        form.fields["manager"].initial = user

    if request.method == "POST" and form.is_valid():
        project = form.save(commit=False)

        if user.role == User.Role.MANAGER and not user.is_superuser:
            project.manager = user

        project.save()
        messages.success(request, "Project created successfully.")
        return redirect("projects:project_list")

    return render(request, "projects/project_form.html", {"form": form})



@login_required
def project_update(request, pk):
    user = request.user

    if not (
        user.is_superuser
        or user.role in [User.Role.ADMIN, User.Role.MANAGER]
    ):
        messages.error(request, "You cannot update projects.")
        return redirect("projects:project_list")

    project = get_object_or_404(visible_projects(user), pk=pk)
    form = ProjectForm(request.POST or None, instance=project)

    if user.role == User.Role.MANAGER and not user.is_superuser:
        form.fields["manager"].queryset = User.objects.filter(pk=user.pk)

    if request.method == "POST" and form.is_valid():
        project = form.save(commit=False)

        if user.role == User.Role.MANAGER and not user.is_superuser:
            project.manager = user

        project.save()
        messages.success(request, "Project updated successfully.")
        return redirect("projects:project_detail", pk=project.pk)

    return render(request, "projects/project_form.html", {"form": form})



@login_required
def project_delete(request, pk):
    user = request.user

    if not (
        user.is_superuser
        or user.role in [User.Role.ADMIN, User.Role.MANAGER]
    ):
        messages.error(request, "You cannot delete projects.")
        return redirect("projects:project_list")

    project = get_object_or_404(visible_projects(user), pk=pk)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project deleted successfully.")
        return redirect("projects:project_list")

    return render(
        request,
        "projects/project_confirm_delete.html",
        {"project": project},
    )
