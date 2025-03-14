from django.contrib import admin
from django.urls import path, include
from account.views import silk_chart_data, silk_chart_view, most_time_overall_data, most_time_chart_page, most_db_time_api, most_db_time_chart_view, most_queries_chart_api, most_queries_chart_page
# from django.contrib.admin.views.decorators import staff_member_required

# Import Silk's default view
# from silk.views.requests import RequestView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("silk/", include("silk.urls", namespace="silk")),    
    path('api/user/', include('account.urls')),
    path('silk-chart/', silk_chart_view, name='silk_chart'),
    path('api/silk-data/', silk_chart_data, name='silk_chart_data'),
    path('api/silk-most-time-overall/', most_time_overall_data, name='most_time_overall_chart_data'),
    path('silk/most-time-chart/', most_time_chart_page, name='most_time_chart_page'),
    path("api/silk-most-db/", most_db_time_api, name="silk-most-db"),
    path("silk/silk-mosttime-db/", most_db_time_chart_view, name="most_db_time_chart_view"),
    path("api/silk-most-queries/", most_queries_chart_api, name="silk-most-queries-api"),
    path("silk/most-queries-chart/", most_queries_chart_page, name="most_queries_chart_page"),

]

