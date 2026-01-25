from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render


@user_passes_test(lambda u: u.is_authenticated and u.is_superuser)
def home(request):
    return render(request, "siteadmin/home.html")
