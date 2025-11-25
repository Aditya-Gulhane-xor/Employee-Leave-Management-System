from django.contrib import admin
from .models import Profile, LeaveType, Leave , Notification

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_manager', 'manager', 'department', 'designation')
    list_filter = ('is_manager', 'department')
    search_fields = ('user__username', 'manager__username', 'department', 'designation')
    list_editable = ('is_manager',)

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_days_allowed')
    search_fields = ('name',)

@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'leave_type', 'start_date', 'end_date', 'status', 'manager', 'applied_at')
    list_filter = ('status', 'leave_type')
    search_fields = ('applicant__username', 'reason', 'manager__username')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('recipient__username', 'message')
    ordering = ('-created_at',)


