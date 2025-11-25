from django.urls import path
from . import views

app_name = 'leaves_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('dashboard-redirect/', views.dashboard_redirect, name='dashboard-redirect'), #just to redirect for emp or manger 
    path('emp-dashboard/', views.emp_dashboard, name='emp-dashboard'),#AAAA
    path('apply-leave/', views.apply_leave, name='apply-leave'), #A
    path('view-history/', views.view_history, name='view-history'),#A
    path('leave-balance/', views.view_leave_balance, name='leave-balance'),#A
    path('cancel-leave/<int:leave_id>/', views.cancel_leave, name='cancel-leave'),#A
    path('manager-dashboard/', views.manager_dashboard, name='manager-dashboard'),#MM
    path('approve-leave/<int:leave_id>/', views.approve_leave, name='approve-leave'),#M
    path('reject-leave/<int:leave_id>/', views.reject_leave, name='reject-leave'),#M


    path('mark-notifications-read/', views.mark_notifications_read, name='mark-notifications-read'),
    

]