from django.conf import settings
from silk.models import Request
from django.shortcuts import redirect
import time

class SilkAdminOnlyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Restrict access to Silk dashboard
        user = getattr(request, "user", None)
        if request.path.startswith("/silk/") and not (user and user.is_authenticated and user.is_staff):
            return redirect(settings.LOGIN_URL)

        # Start profiling
        start_time = time.time()

        response = self.get_response(request)

        # Measure total time taken
        total_time = (time.time() - start_time) * 1000  # Convert to ms

        # Determine which app the request belongs to
        app_name = None
        if request.path.startswith("/api/user/"):
            app_name = "account"
        elif request.path.startswith("/api/demo/"):
            app_name = "demo"

        # Log request only if profiling is enabled
        if settings.ENABLE_DYNAMIC_SILK_PROFILING and app_name:
            Request.objects.create(
            path=request.path,
            method=request.method,
            time_taken=total_time,
            meta_time=total_time,  # Keep this as a number
            view_name=app_name  # Store app name in another field if needed
        )

        return response
