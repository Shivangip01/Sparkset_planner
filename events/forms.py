from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Booking, Vendor, VendorProfile
from .models import Service
from .models import Feedback

class BookingForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Start Date",
        required=True
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="End Date",
        required=True
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label="Start Time",
        required=True
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label="End Time",
        required=True
    )
    vendors = forms.ModelMultipleChoiceField(
        queryset=Vendor.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Additional Services"
    )

    class Meta:
        model = Booking
        fields = ['start_date', 'end_date', 'start_time', 'end_time', 'vendors']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vendors'].label_from_instance = lambda obj: f"{obj.name} (${obj.cost})"


class VendorSignUpForm(UserCreationForm):
    company_name = forms.CharField(max_length=255, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    vendor_type = forms.ChoiceField(choices=Vendor.VENDOR_TYPES, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'company_name', 'phone_number', 'vendor_type', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Create the vendor and vendor profile after user is saved
            vendor = Vendor.objects.create(
                name=self.cleaned_data.get('company_name'),
                vendor_type=self.cleaned_data.get('vendor_type'),
                cost=0  # Set initial cost as 0 or customize if needed
            )
            VendorProfile.objects.create(
                user=user,
                vendor=vendor,
                company_name=self.cleaned_data.get('company_name'),
                phone_number=self.cleaned_data.get('phone_number')
            )
        return user
#from django import forms
#from .models import Service

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['service_name', 'description', 'price', 'vendor_type']
        
        

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['customer_name', 'email', 'event', 'rating', 'feedback_message']