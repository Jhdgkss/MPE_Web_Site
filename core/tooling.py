from django.shortcuts import render


def tooling(request):
    """Tooling landing page.

    Purpose:
    - Gives you a stable /tooling/ route today (for Railway + links)
    - Later becomes the entry point for a tooling specification generator form

    No database changes. No dependencies.
    """
    return render(request, "core/tooling.html")
