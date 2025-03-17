from itertools import count
import logging
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from account.serializers import SendPasswordResetEmailSerializer, UserChangePasswordSerializer, UserLoginSerializer, UserPasswordResetSerializer, UserProfileSerializer, UserRegistrationSerializer
from django.contrib.auth import authenticate
from account.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from silk.profiling.profiler import silk_profile
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Avg
import json
from django.http import JsonResponse
from silk.models import Request, Profile
from django.db.models import Avg
from .models import User
from collections import defaultdict
from rest_framework.decorators import api_view



logger = logging.getLogger(__name__)

# Generate Token Manually
def get_tokens_for_user(user):
  refresh = RefreshToken.for_user(user)
  return {
      'refresh': str(refresh),
      'access': str(refresh.access_token),
  }

class UserRegistrationView(APIView):
  renderer_classes = [UserRenderer]

  @silk_profile(name='User Registration Profiling')
  def post(self, request, format=None):
    serializer = UserRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    token = get_tokens_for_user(user)

    logger.info(f"User Registration: {request.data} - Response: {token}")
    return Response({'token':token, 'msg':'Registration Successful'}, status=status.HTTP_201_CREATED)

class UserLoginView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data.get('email')
    password = serializer.data.get('password')

    with silk_profile(name="User Authentication Block"):  # Block profiling starts here
            user = authenticate(email=email, password=password)
    
    if user is not None:
      token = get_tokens_for_user(user)
      logger.info(f"User Login Successful: Email={email}")
      return Response({'token':token, 'msg':'Login Success'}, status=status.HTTP_200_OK)
    else:
      logger.warning(f"User Login Failed: Email={email}")
      return Response({'errors':{'non_field_errors':['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)

class UserProfileView(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated]

  @silk_profile(name='User Profile View')
  def get(self, request, format=None):
    serializer = UserProfileSerializer(request.user)
    logger.info(f"User Profile Accessed: {request.user.email}")
    return Response(serializer.data, status=status.HTTP_200_OK)

class UserChangePasswordView(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated]
  throttle_classes = [UserRateThrottle]
  def post(self, request, format=None):
    serializer = UserChangePasswordSerializer(data=request.data, context={'user':request.user})
    serializer.is_valid(raise_exception=True)
    logger.info(f"Password Change: User={request.user.email}")
    return Response({'msg':'Password Changed Successfully'}, status=status.HTTP_200_OK)

class SendPasswordResetEmailView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    serializer = SendPasswordResetEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    logger.info(f"Password Reset Email Sent: {request.data.get('email')}")
    return Response({'msg':'Password Reset link send. Please check your Email'}, status=status.HTTP_200_OK)

class UserPasswordResetView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, uid, token, format=None):
    serializer = UserPasswordResetSerializer(data=request.data, context={'uid':uid, 'token':token})
    serializer.is_valid(raise_exception=True)
    logger.info(f"Password Reset Success: UID={uid}")
    return Response({'msg':'Password Reset Successfully'}, status=status.HTTP_200_OK)
  

def silk_chart_view(request):
    return render(request, 'silk/chart.html')


def silk_chart_data(request):
    try:
        # Total number of Silk-captured requests and profiles
        total_requests = Request.objects.count()
        total_profiles = Profile.objects.count()

        # Initialize total metrics
        total_response_time = 0
        total_query_time = 0
        total_query_count = 0

        profiles = Profile.objects.all()

        for profile in profiles:
            # Add total response time
            total_response_time += profile.time_taken or 0

            # Get all DB queries associated with this profile
            queries = profile.queries.all()
            total_query_count += queries.count()

            # Sum DB query time per profile
            total_query_time += sum(q.time_taken for q in queries)

        # Compute averages (safely avoiding division by zero)
        avg_response_time = total_response_time / total_profiles if total_profiles else 0
        avg_query_time = total_query_time / total_profiles if total_profiles else 0
        avg_num_queries = total_query_count / total_profiles if total_profiles else 0

        # Return final data (multiplied by 1000 to convert seconds to ms)
        data = {
            'requests': total_requests,
            'profiles': total_profiles,
            'avg_response_time': round(avg_response_time * 1000, 2),  # ms
            'avg_query_time': round(avg_query_time * 1000, 2),        # ms
            'avg_num_queries': round(avg_num_queries, 2)
        }

        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def most_time_chart_page(request):
    return render(request, 'silk/chart_most_time_overall.html')

def most_time_overall_data(request):
    data = []
    requests = Request.objects.order_by('-time_taken')[:10]  # top 10 most time-consuming requests
    for req in requests:
        data.append({
            'path': req.path,
            'time_taken': round(req.time_taken, 2)  # in ms
        })
    return JsonResponse(data, safe=False)


def most_db_time_chart_view(request):
    return render(request, 'silk/most_db_chart.html')


@api_view(['GET'])
def most_db_time_api(request):
    try:
        top_requests = Request.objects.exclude(meta_time_spent_queries=None).order_by('-meta_time_spent_queries')[:10]
        data = [
            {
                'url': r.path,
                'db_time': round(r.meta_time_spent_queries, 2)
            } for r in top_requests
        ]
        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

def most_queries_chart_page(request):
    return render(request, 'silk/most_queries_chart.html')

def most_queries_chart_api(request):
    data = Request.objects.all().order_by('-num_sql_queries')[:10]
    response = [
        {
            "view_name": r.view_name,
            "num_queries": r.num_sql_queries
        } for r in data
    ]
    return JsonResponse(response, safe=False)

def silk_charts_page(request):
   return render(request, 'silk/requests_chart.html')
   
def silk_metrics_api(request):
    http_methods = defaultdict(int)
    time_per_path = defaultdict(float)
    db_queries_per_path = defaultdict(int)
    view_requests = defaultdict(int)

    requests = Request.objects.all()

    for req in requests:
        http_methods[req.method] += 1
        time_per_path[req.path] += req.time_taken or 0
        db_queries_per_path[req.path] += req.num_sql_queries or 0
        view_requests[req.view_name or "Unknown View"] += 1

    data = {
        'http_methods': dict(http_methods),
        'time_per_path': dict(time_per_path),
        'db_queries_per_path': dict(db_queries_per_path),
        'view_requests': dict(view_requests),
    }
    return JsonResponse(data)

def silk_profiling_page(request):
   return render(request, 'silk/profiling_chart.html')

def silk_profiling_data(request):
    profiling_data = []

    profiles = Profile.objects.select_related('request').prefetch_related('queries')

    for profile in profiles:
        func_name = profile.func_name
        module = profile.name
        total_time = profile.time_taken or 0.0

        queries = profile.queries.all()
        db_time = sum(query.time_taken for query in queries if query.time_taken)
        num_queries = queries.count()

        profiling_data.append({
            'func_name': func_name,
            'module': module,
            'total_time': total_time,
            'db_time': db_time,
            'num_queries': num_queries
        })

    return JsonResponse(profiling_data, safe=False)