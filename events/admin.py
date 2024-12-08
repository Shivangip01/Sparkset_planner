# from django.contrib import admin

# Register your models here.
# from django.contrib import admin
# from .models import Event

# admin.site.register(Event)
from django.contrib import admin
from .models import Event, Booking, Vendor
from .models import VendorProfile
from .models import Feedback

# Register the VendorProfile model
admin.site.register(VendorProfile)

admin.site.register(Event)
admin.site.register(Booking)
admin.site.register(Vendor)
admin.site.register(Feedback)
