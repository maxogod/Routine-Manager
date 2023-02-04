from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from django.contrib.auth import authenticate, login, logout

from .serializers import CreateUserSerializer, UserSerializer
from .models import User


class SessionView(APIView):
    """
    Api to see current session user and Login/Logout
    """

    # Get current session data
    def get(self, request, format=None):
        try:
            user = User.objects.get(id=request.user.id)
        except:
            user = {'id': None, 'username': None, 'email': None, }

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Update current session (Login/Logout)
    def post(self, request, format=None):

        # Logout
        if 'email' in request.data.keys() and request.data['email'] is None:
            logout(request)
            return Response('logged out', status=status.HTTP_200_OK)

        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():

            # Auth and Login
            user = authenticate(
                request, email=request.data['email'], password=request.data['password'])

            if user is not None:
                login(request, user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response('Wrong information', status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    """
    Api to register a new user
    """

    # Create new User (Sign up)
    def post(self, request, format=None):
        serializer = CreateUserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()  # Create User
            login(request, user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)