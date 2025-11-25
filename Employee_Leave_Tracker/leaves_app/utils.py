from datetime import date
from django.db.models import Sum
from .models import Leave, LeaveType

def get_remaining_leaves(user):
    """Returns a list of leave types with remaining leave counts for the given user."""
    leave_summary = []

    for lt in LeaveType.objects.all():
        # Sum up approved leaves of this type in the current year
        approved_days = (
            Leave.objects.filter(
                applicant=user,
                leave_type=lt,
                status='APPROVED',
                start_date__year=date.today().year
            ).aggregate(total_days=Sum('end_date') - Sum('start_date'))
        )

        # Alternatively, sum using your duration_days property:
        approved_qs = Leave.objects.filter(
            applicant=user,
            leave_type=lt,
            status='APPROVED',
            start_date__year=date.today().year
        )
        used_days = sum([l.duration_days for l in approved_qs])

        remaining = max(lt.max_days_allowed - used_days, 0)
        leave_summary.append({
            'type': lt.name,
            'max': lt.max_days_allowed,
            'used': used_days,
            'remaining': remaining
        })
    return leave_summary
