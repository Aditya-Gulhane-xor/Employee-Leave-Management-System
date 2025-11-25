from rest_framework import serializers 
from django.contrib.auth.models import User
from .models import Profile , LeaveType , Leave

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model =User
        fields=['id','username','first_name','last_name','email']


class ProfileSerializers(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields =['user','is_manager','department','designation','manager']


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model =LeaveType
        fields='__all__'
  

class MyLeaveSerializer(serializers.ModelSerializer):
    applicant = UserSerializer(read_only=True)
    leave_type = LeaveTypeSerializer(read_only=True)

    class Meta:
        model =Leave
        fields = '__all__'


class LeaveApplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
from .models import LeaveType, Leave


#restart 


# 1 Simple serializer for LeaveType (read-only listing)
class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = ["id", "name", "max_days_allowed", "description"]
        read_only_fields = ["id"]

# 2 Serializer used when an employee views their leaves (read-only)
class LeaveListSerializer(serializers.ModelSerializer):
    leave_type = LeaveTypeSerializer(read_only=True)
    applicant_username = serializers.CharField(source="applicant.username", read_only=True)
    manager_username = serializers.CharField(source="manager.username", read_only=True)

    class Meta:
        model = Leave
        fields = [
            "id",
            "applicant_username",
            "leave_type",
            "start_date",
            "end_date",
            "duration_days",
            "status",
            "manager_username",
            "manager_comment",
            "applied_at",
        ]
        read_only_fields = fields



# 3 Serializer for applying a leave (write)
class LeaveApplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = ["leave_type", "start_date", "end_date", "reason"]

    def validate(self, data):
        """
        Cross-field validation:
        - start_date <= end_date
        - start_date not in the past (business rule; optional)
        """
        start = data.get("start_date")
        end = data.get("end_date")

        if start and end and end < start:
            raise serializers.ValidationError({"end_date": "End date cannot be earlier than start date."})

        return data

# serializer for leave balance 

class LeaveBalanceSerializer(serializers.Serializer):
    type = serializers.CharField()
    max = serializers.IntegerField()
    used = serializers.IntegerField()
    remaining = serializers.IntegerField()


# Serializer for cnacel leave request 

