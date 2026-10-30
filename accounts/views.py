from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import User



def login_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password,)

        if user is not None:
            login(request, user)
            return redirect("accounts:dashboard")

        messages.error(request, "Invalid username or password.")

    return render(request, "accounts/login.html")


@login_required
def dashboard(request):
    user = request.user

    if user.is_superuser or user.role == User.Role.ADMIN:
        return render(request, "accounts/admin_dashboard.html")

    if user.role == User.Role.MANAGER:
        return render(request, "accounts/manager_dashboard.html")

    if user.role == User.Role.CLIENT:
        return render(request, "accounts/client_dashboard.html")

    return render(request, "accounts/employee_dashboard.html")



@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("accounts:login")
