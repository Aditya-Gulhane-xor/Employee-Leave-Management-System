from rest_framework.views import APIView
from rest_framework.response import Response 
from  rest_framework import status , permissions 
from django.utils import timezone
from datetime import date 
from django.shortcuts import get_object_or_404
from .models import LeaveType , Leave
# from .serializers import LeaveTypeSerializer , LeaveSerializer
from .permissions import IsManager ,IsEmployee


# #just a testing api
# class HelloAPIView(APIView):
#     def get(self,request):
#         return Response({"message":"Hello, Setting up the DRF"})

# #view for leavetype
# class LeaveTypeListAPIView(APIView):
#     permissions_classes = [permissions.IsAuthenticated]

#     def get(self,request):
#         leave_type = LeaveType.objects.all()
#         serializer = LeaveTypeSerializer(leave_types,many=True)
#         return Response(serializer.data,ststus=status.HTTP_200_ok)


# #Show leaves applied by current user
# class MyLeavesAPIView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get (self , request):
#         leaves = Leave.objects.filter(applicant=request.user).order_by('-applied_at')
#         serializer = LeaveSerializer(leaves,many=True)
#         return Response(serializer.data , status=status.HTTP_200_OK)

# class ApplyLeaveAPIView(APIView):

#     permission_classes =[permissions.IsAuthenticated, IsEmployee]


#     def post(self,request):
#         user = request.user
#         serializer = LeaveSerializer(data=request.data)

#         if serializer.is_valid():
#             start = serializer.validated_data['start_date']
#             end = serializer.validated_data['end_date']
#             leave_type= serializer.validate_data['leave_type']

#             if start > end:
#                 return Response ({"error":"End date cannot be ealier than start date"},status=status.HTTP_400_BAD_REQUEST)

#             if start < date.today():
#                 return Response({"error": "Start date cannot be in the past."},status=status.HTTP_400_BAD_REQUEST)

#             overlap=Leave.objects.filter(applicant=user).exclude(status__in=['REJECTED','CANCELLED']).filter(start_date_lte=end,end_date__gte=start)
            

#             if overlap.exists():
#                 return Response({"error":"You have a leave during this period"},status=status.HTTP_400_BAD_REQUEST)

#             profile = getattr(user,'profile',None)

#             if profile and profile.manager:
#                 leave.manager=profile.manager
#                 leave.save()

#             return response({ "message": "Leave applied successfully. Awaiting manager approval.",
#                 "data": LeaveSerializer(leave).data
#             }, status=status.HTTP_201_CREATED)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# from rest_framework import viewsets

# class LeaveViewSet(viewsets.ModelViewSet):
#     queryset = Leave.objects.all()
#     serializer_class = LeaveSerializer


# restart 

from rest_framework import viewsets ,status ,response
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import LeaveType ,Leave
from .serializers import LeaveTypeSerializer , LeaveApplySerializer ,LeaveListSerializer ,LeaveBalanceSerializer
from .utils import get_remaining_leaves
from .permissions import IsManager ,IsEmployee ,IsAdmin
from django_filters.rest_framework import DjangoFilterBackend
class LeaveTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class=LeaveTypeSerializer
    permission_classes = [IsAdmin]



    def list(self, request, *args, **kwargs):
        print(">>>>> PERMISSION CHECK TRIGGERED <<<<<")
        return super().list(request, *args, **kwargs)


class ApplyLeaveViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveApplySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Leave.objects.filter(applicant=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        profile = getattr(user, 'profile', None)
        manager = profile.manager if profile else None

        start = serializer.validated_data["start_date"]
        end = serializer.validated_data["end_date"]
        leave_type = serializer.validated_data["leave_type"]

        #  Overlapping leave check ---
        overlap = Leave.objects.filter(
            applicant=user
        ).exclude(status__in=["REJECTED", "CANCELLED"]).filter(
            start_date__lte=end,
            end_date__gte=start
        )

        if overlap.exists():
            raise serializers.ValidationError(
                {"detail": "You already have a leave request overlapping these dates."}
            )

        # --- Leave Balance Check using your function ---
        from leaves_app.utils import get_remaining_leaves
        remaining = get_remaining_leaves(user)[leave_type.name]["remaining"]
        requested_days = (end - start).days + 1

        if requested_days > remaining:
            raise serializers.ValidationError(
                {"detail": f"Insufficient {leave_type.name} balance. Only {remaining} days left."}
            )

        # --- SAVE Leave ---
        serializer.save(
            applicant=user,
            manager=manager
        )


# API for seeing view history 

class LeaveHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LeaveApplySerializer
    permission_classes = [IsEmployee]

    # Add ANY queryset to satisfy DRF (it will be overridden anyway)
    queryset = Leave.objects.none()

    filter_backends = [DjangoFilterBackend]

    filterset_fields = {
        'status': ['exact']

    }

    def get_queryset(self):
        return Leave.objects.filter(
            applicant=self.request.user
        ).order_by('-applied_at')


    

# Api for leave Baance 

class LeaveBalanceViewSet(viewsets.ViewSet):
    permission_classes = [IsEmployee]

    def list(self, request):
        user = request.user
        leave_types = LeaveType.objects.all()

        results = []

        for lt in leave_types:
            used = Leave.objects.filter(
                applicant=user,
                leave_type=lt,
                status="APPROVED"
            ).count()

            remaining = max(lt.max_days_allowed- used, 0)

            results.append({
                "type": lt.name,
                "max": lt.max_days_allowed,
                "used": used,
                "remaining": remaining
            })

        serializer = LeaveBalanceSerializer(results, many=True)
        return response.Response(serializer.data)

#Api for cancle leave request 
