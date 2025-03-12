from django.contrib import admin
from django.urls import path, include
from account.views import silk_chart_data, silk_chart_view
# from django.contrib.admin.views.decorators import staff_member_required

# Import Silk's default view
# from silk.views.requests import RequestView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("silk/", include("silk.urls", namespace="silk")),    
    path('api/user/', include('account.urls')),
    path('silk-chart/', silk_chart_view, name='silk_chart'),
    path('api/silk-data/', silk_chart_data, name='silk_chart_data'),


]
