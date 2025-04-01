from django.contrib import admin
from django.urls import path, include
from account.views import user_profiles_view
from demo.views import demo_profiles_view

urlpatterns = [
    path('admin/', admin.site.urls),

    # API paths
    path('api/user/', include('account.urls')),
    path('api/demo/', include('demo.urls')),
    path('', include('account.urls')),
  
    path('silk/', include('silk.urls', namespace='silk')),

    path('silk/user_prof/', user_profiles_view, name ='user_profiling'),
    path('silk/demo_prof/', demo_profiles_view, name = 'demo_profiling'),
]
