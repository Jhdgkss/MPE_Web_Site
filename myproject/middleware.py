from django.http import HttpResponsePermanentRedirect


class WwwRedirectMiddleware:
    """
    Permanently redirect the apex domain to the canonical www domain.

    This only redirects the live production host so local development and
    Railway preview domains continue to work normally.
    """

    SOURCE_HOST = "mpe-uk.com"
    TARGET_HOST = "www.mpe-uk.com"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(":", 1)[0].lower()

        if host == self.SOURCE_HOST:
            return HttpResponsePermanentRedirect(
                f"https://{self.TARGET_HOST}{request.get_full_path()}"
            )

        return self.get_response(request)
