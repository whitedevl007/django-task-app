from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'assigned_to', 'due_date', 'status', 'completion_report', 'worked_hours']
        read_only_fields = ['assigned_to']  # Only user can change their own task

    def validate_status(self, value):
        # Example of a simple validation for status
        if value not in dict(Task.STATUS_CHOICES).keys():
            raise serializers.ValidationError("Invalid status value.")
        return value

    def update(self, instance, validated_data):
        # Handle status change validation here
        status = validated_data.get('status', None)
        
        if status:
            # You can define additional logic if needed to restrict certain transitions (e.g., from 'Completed' back to 'Pending')
            if instance.status == 'Completed' and status != 'Completed':
                raise serializers.ValidationError("Cannot change the status of a completed task.")
            
        return super().update(instance, validated_data)


class TaskCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['completion_report', 'worked_hours']

    def update(self, instance, validated_data):
        # Handle logic for task completion here if needed (e.g., restrict certain actions)
        return super().update(instance, validated_data)
