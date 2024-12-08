from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import user_dashboard  # Import the user_dashboard view

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='events/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('', views.index, name='index'),
    path('book/<int:event_id>/', views.book_event, name='book_event'),
    path('payment/<int:booking_id>/', views.process_payment,
         name='process_payment'),  # URL for payment processing
    path('booking_confirmation/<int:booking_id>/', views.booking_confirmation,
         name='booking_confirmation'),  # URL for booking confirmation
    path('vendor/signup/', views.vendor_signup,
         name='vendor_signup'),  # vendor signup
    path('vendor/login/', views.vendor_login,
         name='vendor_login'),  # vendor login
    path('vendor/dashboard/', views.vendor_dashboard,
         name='vendor_dashboard'),  # Add this line
    path('vendor/add_service/', views.add_service, name='add_service'),
    path('vendor/service/delete/<int:service_id>/', views.delete_service,
         name='delete_service'),  # To delete service from vendor's end##
    path('vendor/notifications/', views.vendor_notifications,
         name='vendor_notifications'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='events/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='events/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='events/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='events/password_reset_complete.html'), name='password_reset_complete'),
    # New URL path for About Us page
    path('about/', views.about_us, name='about_us'),
    path('user/dashboard/', views.user_dashboard,
         name='user_dashboard'),  # New path for user dashboard
    # path('services/', views.services, name='services'),  # New path for Services page
    # Updated to use feedback_view
    path('feedback/', views.feedback_view, name='feedback'),
    path('delete_booking/<int:booking_id>/',
         views.delete_booking, name='delete_booking'),

]
