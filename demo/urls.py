from django.urls import path
from demo.views import SendPasswordResetEmailView, UserChangePasswordView, UserLoginView, UserProfileView, UserRegistrationView, UserPasswordResetView
from demo.views import silk_chart_data, silk_chart_view, most_time_overall_data, most_time_chart_page, most_db_time_api, most_db_time_chart_view, most_queries_chart_api, most_queries_chart_page, silk_charts_page, silk_metrics_api, silk_profiling_data, silk_profiling_page

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('changepassword/', UserChangePasswordView.as_view(), name='changepassword'),
    path('send-reset-password-email/', SendPasswordResetEmailView.as_view(), name='send-reset-password-email'),
    path('reset-password/<uid>/<token>/', UserPasswordResetView.as_view(), name='reset-password'),

    path('silk-chart/', silk_chart_view, name='silk_chart'),
    path('api/silk-data/', silk_chart_data, name='silk_chart_data'),
    path('api/silk-most-time-overall/', most_time_overall_data, name='most_time_overall_chart_data'),
    path('most-time-chart/', most_time_chart_page, name='most_time_chart_page'),
    path("api/silk-most-db/", most_db_time_api, name="silk-most-db"),
    path("silk-mosttime-db/", most_db_time_chart_view, name="most_db_time_chart_view"),
    path("api/silk-most-queries/", most_queries_chart_api, name="silk-most-queries-api"),
    path("most-queries-chart/", most_queries_chart_page, name="most_queries_chart_page"),
    path('silk-charts-page/', silk_charts_page, name='silk_charts_page'),
    path('api/silk-metrics/', silk_metrics_api, name='silk_metrics_api'),
    path('api/silk-profiling-data/', silk_profiling_data, name='silk_profiling_data'),
    path('silk-profiling-page/', silk_profiling_page, name='silk_profiling_page'),
    

]