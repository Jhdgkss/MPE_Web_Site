from django.shortcuts import render


def home(request):
    """Public home page: /"""
    return render(request, "public/home.html")


def quote(request):
    """Public quote page: /quote/"""
    # Replace this with your existing quote/contact form when ready
    return render(request, "public/quote.html")
