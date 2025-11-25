from django import forms
from .models import Leave

# Employee form to apply for leave
class LeaveApplicationForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Short reason...'}),
        }

    def clean_leave_type(self):
        lt = self.cleaned_data.get('leave_type')
        if lt is None:
            raise forms.ValidationError("Please choose a leave type.")
        return lt

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')

        if start and end and end < start:
            raise forms.ValidationError("End date cannot be earlier than start date.")

        return cleaned_data



#Manager form to approve/reject leave
class ManagerDecisionForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['status', 'manager_comment']
        widgets = {
            'manager_comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add comment here...'}),
        }


# for registration 
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

