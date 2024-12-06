from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Event, Booking, Vendor, VendorProfile, Service, Feedback  # Import Feedback model
from django.contrib.auth.models import User
from .forms import BookingForm, VendorSignUpForm, ServiceForm, FeedbackForm  # Import FeedbackForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.http import HttpResponse
from datetime import date
#from .models import Feedback
from django.urls import reverse
from django.http import HttpResponseRedirect
from datetime import datetime
from django.utils import timezone

def index(request):
    """
    Renders the index page with all available events, vendors, and feedback.
    """
    events = Event.objects.all()
    vendors = Vendor.objects.all()
    services = Service.objects.all()
    feedbacks = Feedback.objects.all()[:5]  # Fetch the latest 5 feedbacks
    print("Feedbacks:", feedbacks)  # Add this to check data
    
    return render(request, 'events/index.html', {
        'events': events,
        'vendors': vendors,
        'services': services,
        'feedbacks': feedbacks  # Add feedbacks to the context
    })
##


def signup(request):
    """
    Handles user signup with username, email, and password.
    After successful signup, the user is logged in automatically.
    """
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        # Form Validation
        if password != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('signup')

        # Create User
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        # Automatically log the user in after signup
        login(request, user)
        messages.success(request, f"Account created successfully! Welcome, {user.username}!")
        return redirect('index')
    
    return render(request, 'events/signup.html')

def vendor_signup(request):
    """
    Handles vendor signup with company information and vendor-specific details.
    After successful signup, the vendor is logged in automatically.
    """
    if request.method == 'POST':
        form = VendorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # This also creates the Vendor and VendorProfile
            login(request, user)  # Log the user in after successful registration
            messages.success(request, "Vendor account created successfully!")
            return redirect('vendor_dashboard')  # Redirect to a vendor dashboard or desired page
    else:
        form = VendorSignUpForm()
    return render(request, 'events/vendor_signup.html', {'form': form})

def vendor_login(request):
    """
    Handles vendor login.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('vendor_dashboard')  # Redirect to vendor dashboard
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'events/vendor_login.html', {'form': form})

class VendorLoginView(LoginView):
    """
    Custom login view for vendors, redirecting to the vendor dashboard on success.
    """
    template_name = 'events/vendor_login.html'
    redirect_authenticated_user = True  # Redirect already logged-in users

    def get_success_url(self):
        return reverse_lazy('vendor_dashboard')


#@login_required
#def vendor_dashboard(request):
#return render(request, 'events/vendor_dashboard.html')

#@login_required
#def vendor_notifications(request):
    
    #vendor = request.user.vendorprofile.vendor  # Assume VendorProfile links User to Vendor
    #bookings = Booking.objects.filter(vendors=vendor)  # Find bookings linked to this vendor
    #return render(request, 'events/vendor_notifications.html', {'bookings': bookings})
    


@login_required
def vendor_notifications(request):
    """
    Allows a vendor to view bookings related to their services and manage them.
    """
    # Get current vendor profile
    vendor_profile = request.user.vendorprofile

    # Get current date and time
    current_date = timezone.now()

    # Get all bookings involving the vendor
    bookings = Booking.objects.filter(vendors=vendor_profile.vendor)

    # Separate bookings into past and future based on both date and time
    future_bookings = bookings.filter(start_date__gte=current_date.date(), start_time__gte=current_date.time())
    past_bookings = bookings.exclude(id__in=future_bookings)

    # Debug output to confirm past bookings
    print("Future Bookings:", future_bookings)
    print("Past Bookings:", past_bookings)

    context = {
        'future_bookings': future_bookings,
        'past_bookings': past_bookings,
    }

    return render(request, 'events/vendor_notifications.html', context)
    
@login_required
def vendor_dashboard(request):
   
    services = Service.objects.filter(vendor=request.user)  # Get services for the logged-in vendor
    return render(request, 'events/vendor_dashboard.html', {'services': services})
    
    
@login_required
def user_dashboard(request):
    user = request.user
    bookings = Booking.objects.filter(user=user)

    if bookings.exists():
        greeting_message = "Welcome back, {}! Here are your upcoming and past bookings:".format(user.username)
    else:
        greeting_message = "Hello, {}! You have no bookings yet. Start planning your next event with us!".format(user.username)
    
    context = {
        'greeting_message': greeting_message,
        'bookings': bookings,
    }
    return render(request, 'events/user_dashboard.html', context)
    
@login_required
def delete_service(request, service_id):
    """
    Allows a vendor to delete one of their services.
    """
    service = get_object_or_404(Service, id=service_id, vendor=request.user)  # Ensure service belongs to the vendor
    if request.method == 'POST':
        service.delete()
        messages.success(request, "Service deleted successfully!")
        return redirect('vendor_dashboard')
    return render(request, 'events/delete_service_confirm.html', {'service': service})


@login_required
def add_service(request):
    """
    Allows vendors to add a specific service.
    """
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.vendor = request.user
            service.save()
            messages.success(request, "Service added successfully!")
            return redirect('vendor_dashboard')
    else:
        form = ServiceForm()
    return render(request, 'events/add_service.html', {'form': form})

@login_required
def book_event(request, event_id):
   
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.event = event
            booking.start_date = form.cleaned_data['start_date']
            booking.end_date = form.cleaned_data['end_date']
            booking.start_time = form.cleaned_data['start_time']
            booking.end_time = form.cleaned_data['end_time']
            booking.save()
            form.save_m2m()  # Save the many-to-many field 'vendors'

            # Redirect to the payment page after booking is confirmed
            return redirect('process_payment', booking_id=booking.id)
    else:
        form = BookingForm()

    # Pass event object to the template for event-specific customization
    return render(request, 'events/book_event.html', {'form': form, 'event': event})
    

   
@login_required
def process_payment(request, booking_id):
    """
    Handles the payment processing.
    """
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Placeholder for payment logic (can be replaced with real payment gateway integration)
    if request.method == 'POST':
        # Simulating successful payment
        messages.success(request, f"Payment for {booking.event.name} was successful!")
        return redirect('booking_confirmation', booking_id=booking.id)

    return render(request, 'events/process_payment.html', {'booking': booking})



@login_required
def booking_confirmation(request, booking_id):
    """
    Renders the booking confirmation page after an event is booked successfully.
    Sends an email confirmation to the user and notifies vendors if applicable.
    """
    booking = get_object_or_404(Booking, id=booking_id)

    # Send booking confirmation email to the user
    subject = f'Booking Confirmation: {booking.event.name}'
    message = (
        f'Dear {booking.user.username},\n\n'
        f'Thank you for booking with us! Your event "{booking.event.name}" has been confirmed.\n\n'
        f'Event Details:\nStart Date: {booking.start_date}\nEnd Date: {booking.end_date}\n'
        f'Start Time: {booking.start_time}\nEnd Time: {booking.end_time}\n\n'
        'We look forward to making your event special!\n\nBest Regards,\nSparkset Planner Team'
    )
    recipient_list = [booking.user.email]
    send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)

    # Notify Vendors
    vendor_subject = f'Your Service has been Booked for {booking.event.name}'
    for vendor in booking.vendors.all():
        try:
            vendor_message = (
                f'Dear {vendor.name} Team,\n\n'
                f'Your service has been booked for the event "{booking.event.name}" by {booking.user.username}.\n\n'
                f'Event Details:\nStart Date: {booking.start_date}\nEnd Date: {booking.end_date}\n'
                f'Start Time: {booking.start_time}\nEnd Time: {booking.end_time}\n\n'
                'Thank you for being a part of our team!\n\nBest Regards,\nSparkset Planner Team'
            )
            vendor_recipient_list = [vendor.profile.user.email]  # Assuming each vendor has a linked user email

            send_mail(vendor_subject, vendor_message, settings.EMAIL_HOST_USER, vendor_recipient_list)
        except ObjectDoesNotExist:
            # Log or handle the missing VendorProfile as needed
            print(f"Vendor {vendor.name} has no profile, skipping email notification.")

    return render(request, 'events/booking_confirmation.html', {'booking': booking})


def my_view(request):
    """
    Redirects to the event list with a success message.
    """
    messages.success(request, "Event created successfully!")
    return redirect('event_list')
    
    
class VendorLoginView(LoginView):
    """
    Custom login view for vendors, redirecting to the vendor dashboard on success.
    """
    template_name = 'events/vendor_login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('vendor_dashboard')
    
def about_us(request):
    return render(request, 'events/about_us.html')
    
    
def services(request):
    all_services = Service.objects.all()  # Fetch all services (optional, adjust based on your needs)
    return render(request, 'events/services.html', {'services': all_services})
    
    
    
##def feedback_view(request):
    #if request.method == 'POST':
        #form = FeedbackForm(request.POST)
        #if form.is_valid():
            #form.save()
            #messages.success(request, 'Thank you for your feedback!')
            #return redirect('index')  # Redirect to the homepage or any other page after submission
    #else:
        #form = FeedbackForm()

    #return render(request, 'events/feedback.html', {'form': form})
    
#def feedback_view(request):
    #if request.method == 'POST':
        #form = FeedbackForm(request.POST)
        #if form.is_valid():
           #feedback = form.save()

            # Send Thank You Email
            #send_mail(
                #subject='Your Experience Matters to Us—Thank You!',
                #message=f"Dear {feedback.customer_name},\n\nThank you for your feedback about {feedback.event}. We truly appreciate your thoughts and value your input. \n We strive for perfection, and your insights bring us closer to that goal.\n\nBest regards,\nThe SparkSet Team",
               # from_email=settings.EMAIL_HOST_USER,
                #recipient_list=[feedback.email],
                #fail_silently=False,
            #)

            #messages.success(request, 'Your Experience Matters to Us—Thank You!')
            #return redirect('index')  # Redirect to the homepage or any other page after submission
    #else:
        #form = FeedbackForm()

   # return render(request, 'events/feedback.html', {'form': form})
    
def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save()

            # Debug: Check feedback data
            print("Feedback Saved:", feedback.comment, feedback.customer_name)

            # Send Thank You Email
            send_mail(
                subject='Your Experience Matters to Us—Thank You!',
                message=f"Dear {feedback.customer_name},\n\nThank you for your feedback about {feedback.event}. We truly appreciate your thoughts and value your input. \n We strive for perfection, and your insights bring us closer to that goal.\n\nBest regards,\nThe SparkSet Team",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[feedback.email],
                fail_silently=False,
            )

            messages.success(request, 'Your Experience Matters to Us—Thank You!')
            return redirect('index')  # Redirect to the homepage or any other page after submission
        else:
            # Debug: Form errors
            print("Form Errors:", form.errors)
    else:
        form = FeedbackForm()

    return render(request, 'events/feedback.html', {'form': form})
    
    
@login_required
def delete_booking(request, booking_id):
    """
    Allows a vendor to delete a past booking.
    """
    try:
        print(f"Attempting to delete booking with ID: {booking_id}")

        # Fetch booking with provided ID
        booking = get_object_or_404(Booking, id=booking_id)
        print(f"Booking found: {booking}")

        # Ensure the logged-in user is allowed to delete the booking
        if request.user.vendorprofile.vendor in booking.vendors.all():
            booking.delete()
            messages.success(request, "Booking deleted successfully!")
            print("Booking deleted successfully!")
        else:
            messages.error(request, "You do not have permission to delete this booking.")
            print("User does not have permission to delete the booking.")

    except Exception as e:
        print(f"Error occurred: {e}")
        messages.error(request, "An error occurred while deleting the booking.")

    return HttpResponseRedirect(reverse('vendor_notifications'))

