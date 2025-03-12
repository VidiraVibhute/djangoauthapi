from django.shortcuts import redirect
from django.conf import settings

class SilkAdminOnlyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only restrict access to Silk, allow everything else
        if request.path.startswith("/silk/") and not (request.user.is_authenticated and request.user.is_staff):
            return redirect(settings.LOGIN_URL)  # Redirect to admin login

        response = self.get_response(request)
        return response
