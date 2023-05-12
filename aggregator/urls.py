from django.urls import path

from aggregator.views import index, keep_user_logged_in, Register, Login, FindFlight, BookFlight, Logout, \
    PaymentMethods, PayForBooking, OrderView, BookingStatus, CancelBooking

urlpatterns = [
    path('', index, name="index"),
    path('keep_user_logged_in', keep_user_logged_in.as_view()),
    path('register', Register.as_view()),
    path('login', Login.as_view()),
    path('logout', Logout.as_view()),
    path('findflight', FindFlight.as_view()),
    path('bookflight', BookFlight.as_view()),
    path('paymentmethod', PaymentMethods.as_view()),
    path('payforbooking', PayForBooking.as_view()),
    path('orders', OrderView.as_view()),
    path('orders/<str:order_number>', OrderView.as_view()),
    path('bookingstatus',BookingStatus.as_view()),
    path('cancelbooking',CancelBooking.as_view())
]
