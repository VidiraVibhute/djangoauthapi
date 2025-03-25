import time
from django.shortcuts import redirect
from django.conf import settings
from silk.models import Request

class SilkAdminOnlyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Restrict access to Silk dashboard
        if request.path.startswith("/silk/") and not (request.user.is_authenticated and request.user.is_staff):
            return redirect(settings.LOGIN_URL)

        # Start profiling (time tracking)
        start_time = time.time()

        response = self.get_response(request)

        # Measure time taken
        total_time = (time.time() - start_time) * 1000  # Convert to ms

        # Save profiling data in Silk (excluding Silk requests)
        if not request.path.startswith("/silk/"):
            silk_request = Request.objects.create(
                path=request.path,
                method=request.method,
                time_taken=total_time
            )
            silk_request.save()

        return response
