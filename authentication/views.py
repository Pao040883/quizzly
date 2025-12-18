"""
Views for authentication app.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from django.conf import settings

from .serializers import (
    RegisterSerializer, 
    LoginSerializer, 
    UserSerializer
)


def set_auth_cookies(response, access_token, refresh_token):
    """
    Helper function to set authentication cookies.
    """
    response.set_cookie(
        key='access_token',
        value=str(access_token),
        httponly=settings.JWT_COOKIE_HTTP_ONLY,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        max_age=settings.JWT_COOKIE_MAX_AGE
    )
    response.set_cookie(
        key='refresh_token',
        value=str(refresh_token),
        httponly=settings.JWT_COOKIE_HTTP_ONLY,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        max_age=settings.JWT_COOKIE_MAX_AGE
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Register a new user.
    """
    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(
            {'detail': 'User created successfully!'}, 
            status=status.HTTP_201_CREATED
        )
    
    return Response(
        serializer.errors, 
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login user and set auth cookies.
    """
    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    username = serializer.validated_data['username']
    password = serializer.validated_data['password']
    
    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response(
            {'detail': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    refresh = RefreshToken.for_user(user)
    
    response = Response(
        {
            'detail': 'Login successfully!',
            'user': UserSerializer(user).data
        },
        status=status.HTTP_200_OK
    )
    
    set_auth_cookies(response, refresh.access_token, refresh)
    
    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout user and blacklist tokens.
    """
    try:
        refresh_token = request.COOKIES.get('refresh_token')
        
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        response = Response(
            {
                'detail': 'Log-Out successfully! All Tokens will be deleted. '
                         'Refresh token is now invalid.'
            },
            status=status.HTTP_200_OK
        )
        
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        
        return response
        
    except TokenError:
        return Response(
            {'detail': 'Invalid or expired token'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request):
    """
    Refresh access token using refresh token from cookie.
    """
    refresh_token = request.COOKIES.get('refresh_token')
    
    if not refresh_token:
        return Response(
            {'detail': 'Refresh token not found'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        token = RefreshToken(refresh_token)
        access_token = token.access_token
        
        response = Response(
            {
                'detail': 'Token refreshed',
                'access': str(access_token)
            },
            status=status.HTTP_200_OK
        )
        
        response.set_cookie(
            key='access_token',
            value=str(access_token),
            httponly=settings.JWT_COOKIE_HTTP_ONLY,
            secure=settings.JWT_COOKIE_SECURE,
            samesite=settings.JWT_COOKIE_SAMESITE,
            max_age=settings.JWT_COOKIE_MAX_AGE
        )
        
        return response
        
    except TokenError:
        return Response(
            {'detail': 'Invalid or expired refresh token'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
