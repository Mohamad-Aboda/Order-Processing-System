from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.decorators import api_view
import logging
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
# Local imports goes here!
from .serializers import UserSerializer

logger = logging.getLogger(__name__)

@api_view(["POST"])
def signup_view(request):
    if request.method != "POST":
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    try:
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            logger.error('Error occurred during user signup: Invalid serializer data')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f'Error occurred during user signup: {str(e)}')
        return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def login_view(request):
    if request.method != "POST":
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    try:
        email = request.data.get("email")
        password = request.data.get("password")
        if email is None or password is None:
            logger.error('Login failed: Email or password not provided')
            return Response(
                {"error": "Please provide both email and password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(email=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            login(request, user)
            return Response(
                {
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                status=status.HTTP_200_OK,
            )
        else:
            logger.error('Login failed: Invalid credentials')
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except Exception as e:
        logger.error(f'Error occurred during user login: {str(e)}')
        return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def logout_view(request):
    if request.method != "POST":
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    try:
        token = request.data.get("token")
        if token is None:
            logger.error('Logout failed: Token not provided')
            return Response(
                {"error": "Please provide a token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        refresh = RefreshToken(token)
        refresh.blacklist()
        logout(request)

        return Response(
            {"message": "Logout successful"},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f'Error occurred during user logout: {str(e)}')
        return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
