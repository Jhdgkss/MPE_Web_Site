from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render


def staff_login(request):
    """Staff login at /staff/login/"""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("staffarea:home")

    error = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            login(request, user)
            return redirect("staffarea:home")
        error = "Login failed"

    return render(request, "staffarea/login.html", {"error": error})


@user_passes_test(lambda u: u.is_authenticated and u.is_staff)
def staff_home(request):
    return render(request, "staffarea/home.html")
