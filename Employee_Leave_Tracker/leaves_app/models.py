from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_manager = models.BooleanField(default=False)
    department = models.CharField(max_length=100 , blank=True , null=True)
    designation =models.CharField(max_length=100 , blank=True , null=True)
    # 🔹 NEW FIELD: Each employee has one manager (who is also a User)
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='team_members'
    )
    
    def __str__(self):
        return self.user.username


class LeaveType(models.Model):
    name=models.CharField(max_length=50,unique=True)
    description =models.TextField(blank=True,null=True)
    max_days_allowed = models.IntegerField(default=30)

    def __str__(self):
        return self.name

class Leave(models.Model):
    STATUS_CHOICES =[
        ('PENDING','Pending'),
        ('APPROVED','Approved'),
        ('REJECTED','Rejected'),
        ('CANCELLED','Cancelled')

    ]
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.SET_NULL, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True)
    applied_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    manager_comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.applicant.username} - {self.leave_type} ({self.status})"

    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days + 1


class Notification(models.Model):
    recipient = models.ForeignKey(User,on_delete=models.CASCADE , related_name='notifications')
    message =models.TextField()
    created_at=models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)


    def __str__(self):
        return f"To: {self.recipient.username} | {self.message[:50]}"
    