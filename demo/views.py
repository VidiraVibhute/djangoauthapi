from itertools import count
import logging
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from demo.serializers import (
    SendPasswordResetEmailSerializer, UserChangePasswordSerializer,
    UserLoginSerializer, UserPasswordResetSerializer,
    UserProfileSerializer, UserRegistrationSerializer
)
from django.contrib.auth import authenticate
from demo.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from django.shortcuts import render
from django.db.models import Avg
import json
from django.http import JsonResponse
from silk.models import Request, Profile
from .models import User
from collections import defaultdict
from rest_framework.decorators import api_view
from functools import wraps
from django.conf import settings

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

    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = get_tokens_for_user(user)
        logger.info(f"User Registration: {request.data} - Response: {token}")
        return Response({'token': token, 'msg': 'Registration Successful'}, status=status.HTTP_201_CREATED)

class UserLoginView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = authenticate(email=email, password=password)

        if user is not None:
            token = get_tokens_for_user(user)
            logger.info(f"User Login Successful: Email={email}")
            return Response({'token': token, 'msg': 'Login Success'}, status=status.HTTP_200_OK)
        else:
            logger.warning(f"User Login Failed: Email={email}")
            return Response({'errors': {'non_field_errors': ['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)

class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        logger.info(f"User Profile Accessed: {request.user.email}")
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        logger.info(f"Password Change: User={request.user.email}")
        return Response({'msg': 'Password Changed Successfully'}, status=status.HTTP_200_OK)

class SendPasswordResetEmailView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        logger.info(f"Password Reset Email Sent: {request.data.get('email')}")
        return Response({'msg': 'Password Reset link sent. Please check your Email'}, status=status.HTTP_200_OK)

class UserPasswordResetView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, uid, token, format=None):
        serializer = UserPasswordResetSerializer(data=request.data, context={'uid': uid, 'token': token})
        serializer.is_valid(raise_exception=True)
        logger.info(f"Password Reset Success: UID={uid}")
        return Response({'msg': 'Password Reset Successfully'}, status=status.HTTP_200_OK)

def silk_chart_view(request):
    return render(request, 'silk/chart.html')

def silk_chart_data(request):
    try:
        total_requests = Request.objects.count()
        total_profiles = Profile.objects.count()
        total_response_time = sum(p.time_taken or 0 for p in Profile.objects.all())
        total_query_time = sum(sum(q.time_taken for q in p.queries.all()) for p in Profile.objects.all())
        total_query_count = sum(p.queries.count() for p in Profile.objects.all())

        avg_response_time = total_response_time / total_profiles if total_profiles else 0
        avg_query_time = total_query_time / total_profiles if total_profiles else 0
        avg_num_queries = total_query_count / total_profiles if total_profiles else 0

        data = {
            'requests': total_requests,
            'profiles': total_profiles,
            'avg_response_time': round(avg_response_time * 1000, 2),
            'avg_query_time': round(avg_query_time * 1000, 2),
            'avg_num_queries': round(avg_num_queries, 2)
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def most_time_chart_page(request):
    return render(request, 'silk/chart_most_time_overall.html')

def most_time_overall_data(request):
    data = [{'path': r.path, 'time_taken': round(r.time_taken, 2)} for r in Request.objects.order_by('-time_taken')[:10]]
    return JsonResponse(data, safe=False)

def most_db_time_chart_view(request):
    return render(request, 'silk/most_db_chart.html')

@api_view(['GET'])
def most_db_time_api(request):
    try:
        top_requests = Request.objects.exclude(meta_time_spent_queries=None).order_by('-meta_time_spent_queries')[:10]
        data = [{'url': r.path, 'db_time': round(r.meta_time_spent_queries, 2)} for r in top_requests]
        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

def most_queries_chart_page(request):
    return render(request, 'silk/most_queries_chart.html')

def most_queries_chart_api(request):
    data = [{'view_name': r.view_name, 'num_queries': r.num_sql_queries} for r in Request.objects.order_by('-num_sql_queries')[:10]]
    return JsonResponse(data, safe=False)

def silk_charts_page(request):
    return render(request, 'silk/requests_chart.html')

def silk_metrics_api(request):
    http_methods, time_per_path, db_queries_per_path, view_requests = defaultdict(int), defaultdict(float), defaultdict(int), defaultdict(int)
    for req in Request.objects.all():
        http_methods[req.method] += 1
        time_per_path[req.path] += req.time_taken or 0
        db_queries_per_path[req.path] += req.num_sql_queries or 0
        view_requests[req.view_name or "Unknown View"] += 1
    return JsonResponse({
        'http_methods': dict(http_methods),
        'time_per_path': dict(time_per_path),
        'db_queries_per_path': dict(db_queries_per_path),
        'view_requests': dict(view_requests),
    })

def silk_profiling_page(request):
    return render(request, 'silk/profiling_chart.html')

def silk_profiling_data(request):
    data = []
    for p in Profile.objects.select_related('request').prefetch_related('queries'):
        db_time = sum(q.time_taken for q in p.queries.all())
        data.append({
            'func_name': p.func_name,
            'module': p.name,
            'total_time': p.time_taken or 0.0,
            'db_time': db_time,
            'num_queries': p.queries.count()
        })
    return JsonResponse(data, safe=False)
