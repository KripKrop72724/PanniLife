from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings


class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = response.data['access']
        refresh_token = response.data['refresh']
        response.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE'],
            value=token,
            expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            httponly=True,
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
        )
        response.set_cookie(
            key=settings.SIMPLE_JWT['REFRESH_COOKIE'],
            value=refresh_token,
            expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            httponly=True,
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
        )
        return response


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['REFRESH_COOKIE'])
        if refresh_token is None:
            return Response({"detail": "Refresh token not found in cookies."}, status=status.HTTP_401_UNAUTHORIZED)
        request.data['refresh'] = refresh_token
        response = super().post(request, *args, **kwargs)
        new_access_token = response.data['access']
        new_refresh_token = response.data['refresh']
        response.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE'],
            value=new_access_token,
            expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            httponly=True,
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
        )
        response.set_cookie(
            key=settings.SIMPLE_JWT['REFRESH_COOKIE'],
            value=new_refresh_token,
            expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            httponly=True,
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
        )

        # Blacklist the old refresh token
        try:
            old_refresh_token = RefreshToken(refresh_token)
            old_refresh_token.blacklist()
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return response


class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['REFRESH_COOKIE'])
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        response = Response({"detail": "Logout successful."}, status=status.HTTP_200_OK)
        response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
        response.delete_cookie(settings.SIMPLE_JWT['REFRESH_COOKIE'])
        return response
