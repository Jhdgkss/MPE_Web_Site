from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render


def _is_customer(user) -> bool:
    # Change this to match your customer identity logic
    if not user.is_authenticated:
        return False
    if user.groups.filter(name="Customers").exists():
        return True
    return hasattr(user, "customer")


@login_required
def dashboard(request):
    if not _is_customer(request.user):
        return HttpResponseForbidden("Customer access only")
    return render(request, "customers/dashboard.html")


@login_required
def documents(request):
    if not _is_customer(request.user):
        return HttpResponseForbidden("Customer access only")
    return render(request, "customers/documents.html")
