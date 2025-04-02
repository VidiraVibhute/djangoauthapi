from django.contrib import admin
from django.urls import path, include
from account.views import user_profiles_view, method_details
from demo.views import demo_profiles_view, demo_method_details

urlpatterns = [
    path('admin/', admin.site.urls),

    # API paths
    path('api/user/', include('account.urls')),
    path('api/demo/', include('demo.urls')),
    path('', include('account.urls')),
  
    path('silk/', include('silk.urls', namespace='silk')),

    path('silk/user_prof/', user_profiles_view, name ='user_profiling'),
    path('silk/demo_prof/', demo_profiles_view, name = 'demo_profiling'),
    path('method-details/<str:method_name>/', method_details, name='method_details'),
    path('demo-method-details/<str:method_name>/', demo_method_details, name='demo_method_details'),

]
