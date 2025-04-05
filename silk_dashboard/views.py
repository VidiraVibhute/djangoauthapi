from django.shortcuts import render
from django.db.models import Avg
from silk.models import Request, Profile

# Create your views here.
def user_profiles_view(request):
    methods = ["GET", "POST", "PUT", "DELETE"]
    method_data = []

    for method in methods:
        requests = Request.objects.filter(method=method, path__startswith="/api/user").order_by('-start_time')

        avg_time = requests.aggregate(avg_time=Avg('time_taken'))['avg_time'] or 0  

        overall_avg_result = Request.objects.filter(method=method, time_taken__isnull=False).exclude(time_taken=0).aggregate(avg_time=Avg('time_taken'))
        overall_avg_time = overall_avg_result['avg_time'] if overall_avg_result['avg_time'] is not None else 0  

        method_data.append({
            "method": method,
            "requests": requests[:5],  # Limit recent requests to 5
            "total_requests": requests.count(),
            "avg_time": round(avg_time, 2),
            "overall_avg_time": round(overall_avg_time, 2),
        })

    return render(request, "silk/user_profiling.html", {"method_data": method_data})

def method_details(request, method_name):
    requests = Request.objects.filter(method=method_name, path__startswith="/api/user").order_by('-start_time')

    return render(request, "silk/method_details.html", {
        "method_name": method_name,
        "recent_requests": requests,
    })

def demo_profiles_view(request):
    methods = ["GET", "POST", "PUT", "DELETE"]
    method_data = []

    for method in methods:
        requests = Request.objects.filter(method=method, path__startswith="/api/demo").order_by('-start_time')

        avg_time = requests.aggregate(avg_time=Avg('time_taken'))['avg_time'] or 0  

        overall_avg_result = Request.objects.filter(method=method, time_taken__isnull=False).exclude(time_taken=0).aggregate(avg_time=Avg('time_taken'))
        overall_avg_time = overall_avg_result['avg_time'] if overall_avg_result['avg_time'] is not None else 0  

        method_data.append({
            "method": method,
            "requests": requests[:5],  # Limit recent requests to 5
            "total_requests": requests.count(),
            "avg_time": round(avg_time, 2),
            "overall_avg_time": round(overall_avg_time, 2),
        })

    return render(request, "silk/demo_profiling.html", {"method_data": method_data})

def demo_method_details(request, method_name):
    requests = Request.objects.filter(method=method_name, path__startswith="/api/demo").order_by('-start_time')

    return render(request, "silk/demo_method_details.html", {
        "method_name": method_name,
        "recent_requests": requests,
    })

