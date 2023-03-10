from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from django.contrib.auth import authenticate, login, logout

from . import serializers
import json
from django.core.serializers.json import DjangoJSONEncoder

from .models import User, Routine, Task


# User Auth
class SessionView(APIView):
    """
    Api to see current session user and Login/Logout
    """

    # Get current session data
    def get(self, request, format=None):
        try:
            user = User.objects.get(id=request.user.id)
            routines = Routine.objects.filter(user=user)
        except:
            user = {
                "id": None,
                "email": None,
                "username": None,
                "avatar": None,
            }
            routines = []

        serializer = serializers.UserSerializer(user)
        routineSerializer = serializers.RoutineSerializer(routines, many=True)
        return Response({'user': serializer.data, 'schedules': routineSerializer.data}, status=status.HTTP_200_OK)

    # Update current session (Login/Logout)
    def post(self, request, format=None):

        # Logout
        if 'email' in request.data.keys() and request.data['email'] is None:
            logout(request)
            return Response('logged out', status=status.HTTP_200_OK)

        serializer = serializers.UserSerializer(data=request.data)

        if serializer.is_valid():

            # Auth and Login
            user = authenticate(
                request, email=request.data['email'], password=request.data['password'])

            if user is not None:
                login(request, user)
                return Response({'success': True}, status=status.HTTP_200_OK)
            else:
                return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    """
    Api to register a new user
    """

    # Create new User (Sign up)
    def post(self, request, format=None):
        serializer = serializers.CreateUserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()  # Create User
            login(request, user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GoogleOauth(APIView):
    """
    API to register/login a user after it is authenticated by google.
    """

    def post(self, request, format=None):
        serializer = serializers.GoogleOauthSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # Create/Get User
            login(request, user)
            return Response({'success': True}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Routine Creation
class RoutineGet(APIView):

    def get(self, request, pk, format=None):
        try:
            routine = Routine.objects.get(id=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if routine is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif routine.user != request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        tasks = Task.objects.filter(routine=routine)
        serializer = serializers.RoutineSerializer(routine)
        task_serializer = serializers.TaskSerializer(tasks, many=True)
        return Response({'scheduleOptions': serializer.data, 'taskList': task_serializer.data}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        try:
            routine = Routine.objects.get(id=pk)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if (routine.user == request.user):
            routine.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class RoutineCreate(APIView):

    def post(self, request, format=None):
        serializer = serializers.RoutineSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(request.user, request.data['tasks'])
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
