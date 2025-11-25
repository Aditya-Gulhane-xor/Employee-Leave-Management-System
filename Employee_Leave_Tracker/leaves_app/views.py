from django.shortcuts import render,redirect 
from django.contrib.auth.decorators import login_required
from datetime import date , timedelta
from django.contrib import messages
from django.db.models import Q
from .forms import LeaveApplicationForm
from .models import Leave, Notification ,Profile
from django.views.decorators.cache import never_cache
from .utils import get_remaining_leaves
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import UserRegisterForm
from datetime import date, timedelta
from django.utils.timezone import now
from django.core.paginator import Paginator

def index(request):
    return render(request, 'leaves_app/index.html')

from django.http import HttpResponse
@never_cache
@login_required
def emp_dashboard(request):
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.is_manager:
        return redirect('leaves_app:manager-dashboard')

    # Fetch latest 2 leaves for this employee
    recent_leaves = Leave.objects.filter(applicant=request.user).order_by('-applied_at')[:2]

    # Fetch unread notifications
    unread_notifications = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).order_by('-created_at')


    context = {
        'unread_notifications': unread_notifications,
        "recent_leaves": recent_leaves,
    }
    return render(request, 'leaves_app/emp_dashboard.html', context)


@login_required
def mark_notifications_read(request):
    if request.method == "POST":
        Notification.objects.filter(
            recipient=request.user, is_read=False
        ).update(is_read=True)
        messages.info(request, "All notifications marked as read.")
    return redirect('leaves_app:emp-dashboard')



# this is view for apply leave so that employee can apply for the leave
@login_required
def apply_leave(request):
    profile = getattr(request.user, 'profile', None)

    if not profile.manager:
        messages.error(request, "No manager assigned. Contact admin.")
        return redirect('leaves_app:emp-dashboard')

    form = LeaveApplicationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        leave = form.save(commit=False)
        leave.applicant = request.user
        leave.manager = profile.manager

        #  Date validation
        if leave.start_date > leave.end_date:
            form.add_error('end_date', "End date cannot be before start date.")
        elif leave.start_date < date.today():
            form.add_error('start_date', "Start date cannot be in the past.")
        else:
            #  Overlapping check
            overlap = Leave.objects.filter(
                applicant=request.user
            ).exclude(
                status__in=['REJECTED', 'CANCELLED']
            ).filter(
                start_date__lte=leave.end_date,
                end_date__gte=leave.start_date
            )

            if overlap.exists():
                form.add_error(None, "You already have a leave overlapping these dates.")
            else:
                #  Leave balance check 
                requested_days = (leave.end_date - leave.start_date).days + 1
                remaining_data = get_remaining_leaves(request.user)
                remaining = next(
                    (item['remaining'] for item in remaining_data if item['type'] == leave.leave_type.name),
                    0
                )

                if remaining < requested_days:
                    form.add_error(
                        None,
                        f"Insufficient {leave.leave_type.name} balance: "
                        f"{remaining} day(s) left, requested {requested_days}."
                    )
                else:
                    # All checks passed
                    leave.save()
                    messages.success(request, "Leave applied successfully. Awaiting manager approval.")
                    return redirect('leaves_app:emp-dashboard')

    return render(request, 'leaves_app/apply_leave.html', {'form': form})



@login_required
def view_history(request):

    user = request.user
    today = date.today()

    # Get filter from query params
    filter_option = request.GET.get('filter', 'all')  # default to 'all'

    # Compute date range based on filter
    if filter_option == 'week':
        start_date = today - timedelta(days=today.weekday())  # Monday of this week
        end_date = today
    elif filter_option == 'month':
        start_date = today.replace(day=1)
        end_date = today
    elif filter_option == 'year':
        start_date = today.replace(month=1, day=1)
        end_date = today
    elif filter_option == 'all':
        first_leave = Leave.objects.filter(applicant=user).order_by('start_date').first()
        start_date = first_leave.start_date if first_leave else today
        end_date = today
    else:
        start_date = today.replace(day=1)
        end_date = today

    # Filter leaves within range (unless 'all' is selected)
    if filter_option == 'all':
        leaves = Leave.objects.filter(applicant=user).order_by('-start_date')
    else:
        leaves = Leave.objects.filter(
            applicant=user,
            start_date__gte=start_date,
            start_date__lte=end_date
        ).order_by('-start_date')

    context = {
        'leaves': leaves,
        'filter_option': filter_option,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'leaves_app/view_history.html', context)


@login_required 
def cancel_leave(request,leave_id):
    leave=get_object_or_404(Leave ,id=leave_id,applicant=request.user)

    if leave.status != 'PENDING':
        messages.error(request,"Only pending leave requests can be cancelled.")
        return redirect('leaves_app:view-history')
    else:
        leave.status ='CANCELLED'
        leave.save()
        messages.success(request,"Leave request cancelled succesfully.")
    return redirect('leaves_app:view-history')


@login_required
def view_leave_balance(request):
    profile = getattr(request.user, 'profile', None)
    if profile and profile.is_manager:
        return redirect('leaves_app:manager-dashboard')

    leave_data = get_remaining_leaves(request.user)
    return render(request, 'leaves_app/leave_balance.html', {'leave_data': leave_data})




#############################MANAGER-DASHBOARD###########################################
@never_cache
@login_required
def manager_dashboard(request):
    # Pending 
    pending_leaves = Leave.objects.filter(manager=request.user, status="PENDING")
    pending_count = pending_leaves.count()
    approved_count = Leave.objects.filter(manager=request.user, status="APPROVED").count()
    rejected_count = Leave.objects.filter(manager=request.user, status="REJECTED").count()

    # Profiles
    profiles = Profile.objects.filter(manager=request.user)
    name_query = request.GET.get("name", "").strip()
    if name_query:
        profiles = profiles.filter(user__username__icontains=name_query)
    profile_paginator = Paginator(profiles, 10)
    profile_page = profile_paginator.get_page(request.GET.get("profile_page"))

    # History filtering 
    # Acceptable explicit status values
    VALID_STATUS = {"APPROVED", "REJECTED"}  

    
    status_filter = request.GET.get("status")  # could be 'APPROVED', 'REJECTED', '' or None
    if status_filter is not None:
        status_filter = status_filter.strip().upper() or None

    # Employee name filter for history
    emp_name_query = request.GET.get("emp_name", "").strip()

    # Start from all leaves actioned by this manager 
    history_qs = Leave.objects.filter(manager=request.user).exclude(status__in=["PENDING", "CANCELLED"])

    # Apply status filter only if it's a valid specific status
    if status_filter in VALID_STATUS:
        history_qs = history_qs.filter(status=status_filter)
    

    # Apply employee name filter if provided
    if emp_name_query:
        history_qs = history_qs.filter(applicant__username__icontains=emp_name_query)

    history_paginator = Paginator(history_qs.order_by('-applied_at'), 10)
    history_page = history_paginator.get_page(request.GET.get("history_page"))

    # Active tab control (keep dashboard on right tab after filtering)
    active_tab = request.GET.get("tab", "pending")

    # Employees on leave today
    today = date.today()
    employees_on_leave_today = Leave.objects.filter(manager=request.user,status="APPROVED",start_date__lte=today,end_date__gte=today).select_related("applicant", "leave_type")

    context = {
        "pending_leaves": pending_leaves,
        "profile_page": profile_page,
        "history_page": history_page,
        "active_tab": active_tab,
        #sending count in the dashboard 
        "pending_count": pending_count,
        "approved_count": approved_count,
        "rejected_count": rejected_count,
        
        # pass back current filters for template to show them
        "name_query": name_query,
        "status_filter": status_filter,
        "emp_name_query": emp_name_query,
        #employee on leave today
        "employees_on_leave_today": employees_on_leave_today,
    }
    return render(request, "leaves_app/manager_dashboard.html", context)
    

@never_cache
@login_required
def approve_leave(request, leave_id):
    leave = get_object_or_404(Leave, id=leave_id, manager=request.user)

    if leave.status != 'PENDING':
        messages.error(request, "This leave request is not pending.")
    else:
        leave.status = 'APPROVED'
        leave.manager_comment = "Approved by manager."
        leave.save()

        
        Notification.objects.create(
            recipient=leave.applicant,
            message=f"Your {leave.leave_type.name} from {leave.start_date} to {leave.end_date} has been APPROVED."
        )

        messages.success(request, f"Leave approved for {leave.applicant.username}.")

    return redirect('leaves_app:manager-dashboard')


@never_cache
@login_required
def reject_leave(request, leave_id):
    """Manager rejects a pending leave and notifies the employee."""
    leave = get_object_or_404(Leave, id=leave_id, manager=request.user)

    if leave.status != 'PENDING':
        messages.error(request, "This leave request is not pending.")
    else:
        leave.status = 'REJECTED'
        leave.manager_comment = "Rejected by manager."
        leave.save()

        
        Notification.objects.create(
            recipient=leave.applicant,
            message=f"Your {leave.leave_type.name} from {leave.start_date} to {leave.end_date} has been REJECTED."
        )

        messages.warning(request, f"Leave rejected for {leave.applicant.username}.")

    return redirect('leaves_app:manager-dashboard')








# to redirect the after the login we have this function and we have given the url of this function in the settings.py file 
@never_cache
@login_required
def dashboard_redirect(request):
    """Redirect user to their respective dashboard based on role."""
    profile = getattr(request.user, 'profile', None)

    if profile and profile.is_manager:
        return redirect('leaves_app:manager-dashboard')  # Manager dashboard
    else:
        return redirect('leaves_app:emp-dashboard')  # Employee dashboard

# for registration 
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Your account has been created successfully! You can now log in.")
            return redirect('login')  # built-in Django login page
    else:
        form = UserRegisterForm()
    return render(request, 'leaves_app/register.html', {'form': form})

