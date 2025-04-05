from silk.middleware import SilkyMiddleware
from django.conf import settings

class CustomSilkMiddleware(SilkyMiddleware):
    """
    Custom middleware to log Silk data to different databases based on IS_LIVE setting.
    """

    def process_request(self, request):
        """
        Override Silk's request processing to store data in the correct database.
        """
        response = super().process_request(request)

        if hasattr(request, 'silk_request') and request.silk_request:
            request.silk_request.save(using="silk_live" if settings.IS_LIVE else "silk_dev")

        return response

    def process_response(self, request, response):
        """
        Override Silk's response processing to store data in the correct database.
        """
        if hasattr(request, 'silk_request') and request.silk_request:
            request.silk_request.save(using="silk_live" if settings.IS_LIVE else "silk_dev")

        return super().process_response(request, response)
