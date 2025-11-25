from rest_framework.routers import DefaultRouter
from .api_views import LeaveTypeViewSet ,ApplyLeaveViewSet ,LeaveHistoryViewSet ,LeaveBalanceViewSet 
from django.urls import path, include
router = DefaultRouter()
router.register(r"leave-types", LeaveTypeViewSet, basename="leave-types")
router.register(r"apply-leave", ApplyLeaveViewSet, basename="apply-leave")
router.register(r'my-leave-history', LeaveHistoryViewSet, basename='my-leave-history')
router.register(r'leave-balance', LeaveBalanceViewSet, basename='leave-balance')
# router.register(r'leave-actions', LeaveActionViewSet, basename='leave-actions')


urlpatterns = router.urls


