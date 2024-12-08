from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    TYPE_CHOICES = [
        ('wedding', 'Wedding'),
        ('birthday', 'Birthday Party'),
        ('corporate', 'Corporate Event'),
        # Add more event types as needed
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    event_type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.name


class Vendor(models.Model):
    VENDOR_TYPES = [
        ('caterer', 'Caterer'),
        ('photographer', 'Photographer'),
        ('decorator', 'Decorator'),
    ]
    name = models.CharField(max_length=100)
    vendor_type = models.CharField(max_length=20, choices=VENDOR_TYPES)
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.get_vendor_type_display()}"


class VendorProfile(models.Model):
    # Links VendorProfile to a User account
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vendor = models.OneToOneField(
        Vendor, on_delete=models.CASCADE, related_name='profile')
    company_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.company_name} - {self.vendor.get_vendor_type_display()}"


class Service(models.Model):
    VENDOR_TYPES = [
        ('caterer', 'Caterer'),
        ('photographer', 'Photographer'),
        ('decorator', 'Decorator'),
    ]
    # Links Service to the Vendor
    vendor = models.ForeignKey(User, on_delete=models.CASCADE)
    service_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    vendor_type = models.CharField(choices=VENDOR_TYPES, max_length=20)

    def __str__(self):
        return self.service_name


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    vendors = models.ManyToManyField(Vendor, blank=True)

    def total_cost(self):
        vendor_cost = sum(vendor.cost for vendor in self.vendors.all())
        return self.event.cost + vendor_cost

    def __str__(self):
        return f"{self.user.username} booked {self.event.name} on {self.booking_date}"

# Add a method to check if a user is a vendor


def is_vendor(self):
    return hasattr(self, 'vendorprofile')


# Attach the method to the User model
User.add_to_class("is_vendor", is_vendor)

##### Feedback model to get a feedback from customer##


class Feedback(models.Model):
    customer_name = models.CharField(max_length=100)
    email = models.EmailField()
    event = models.CharField(max_length=100)
    rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)], help_text="Rating (1 to 5)")
    feedback_message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Feedback from {self.customer_name} ({self.event})'
