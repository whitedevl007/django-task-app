from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from .serializers import TaskSerializer, TaskCompletionSerializer
from .models import Task
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .permissions import IsAdminOrSuperAdmin

User = get_user_model()

# Serializers for User registration and login
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'role']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            role=validated_data.get('role', 'user')
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

# Register API
@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Login API to get JWT token
@api_view(['POST'])
def login(request):
    print("Login request received:", request.data)  # Debugging line
    if request.method == 'POST':
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            print("Serializer is valid.")  # Debugging line
            user = User.objects.filter(username=serializer.validated_data['username']).first()
            if user and user.check_password(serializer.validated_data['password']):
                print(f"User {user.username} authenticated.")  # Debugging line
                refresh = RefreshToken.for_user(user)
                print(f"Generated refresh token: {str(refresh)}")  # Debugging line
                print(f"Generated access token: {str(refresh.access_token)}")  # Debugging line
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            print("Invalid credentials.")  # Debugging line
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        print("Serializer errors:", serializer.errors)  # Debugging line
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Create a new task
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_task(request):
    if request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            # Assign the logged-in user as the task owner
            serializer.save(assigned_to=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Fetch all tasks for the logged-in user
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_tasks(request):
    tasks = Task.objects.filter(assigned_to=request.user)
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)

# Update task status (Mark as completed) and submit completion report
@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_task(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.data.get('status'):  # If the request contains 'status'
        serializer = TaskSerializer(task, data=request.data, partial=True)
    else:
        serializer = TaskCompletionSerializer(task, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Allow all authenticated users

    def get(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({"detail": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is the task owner or an admin
        if request.user == task.assigned_to or request.user.is_staff or request.user.is_superuser:
            serializer = TaskCompletionSerializer(task)
            return Response(serializer.data)
        return Response({"detail": "You do not have permission to view this report."}, status=status.HTTP_403_FORBIDDEN)
