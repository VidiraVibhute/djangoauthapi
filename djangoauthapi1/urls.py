from django.contrib import admin
from django.urls import path, include
from account.views import (silk_app_selection, filtered_summary, filtered_requests, filtered_profiling)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API paths
    path('api/user/', include('account.urls')),
    path('api/demo/', include('demo.urls')),
    path('', include('account.urls')),



    # Step 1: Show the app selection page
    path('silk_dashboard/', silk_app_selection, name='silk_app_selection'),

    # Step 2: Directly access the filtered Silk dashboard for each app
    path('silk/<str:app_name>/summary/', filtered_summary, name='filtered_summary'),
    path('silk/<str:app_name>/requests/', filtered_requests, name='filtered_requests'),
    path('silk/<str:app_name>/profiling/', filtered_profiling, name='filtered_profiling'),

    path('silk/', include('silk.urls', namespace='silk')),
]
