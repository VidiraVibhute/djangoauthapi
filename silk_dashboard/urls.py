from django.urls import path
from silk_dashboard.views import user_profiles_view, demo_profiles_view, method_details, demo_method_details 


urlpatterns = [
    path('user_prof/', user_profiles_view, name ='user_profiling'),
    path('demo_prof/', demo_profiles_view, name = 'demo_profiling'),
    path('method-details/<str:method_name>/', method_details, name='method_details'),
    path('demo-method-details/<str:method_name>/', demo_method_details, name='demo_method_details'),
    
]