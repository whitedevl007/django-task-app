from django.urls import path
from .views import register, login, get_tasks, update_task, create_task
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import TaskReportView

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('tasks/', get_tasks, name='get_tasks'),  # GET request to fetch tasks
    path('tasks/create/', create_task, name='create_task'),  # POST request to create a task
    path('tasks/<int:pk>/', update_task, name='update_task'),  # PUT/PATCH request to update a task
    
    path('tasks/<int:pk>/report/', TaskReportView.as_view(), name='task_report'),  # POST request to submit a task report
    # ✅ JWT endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
