
# from django.urls import path
# from .views import SignupView, SigninView, LogoutView


# urlpatterns = [
#     path('register/', SignupView.as_view(), name='register'),
#     path('login/', SigninView.as_view(), name='login'),
#     path('logout/', LogoutView.as_view(), name='logout'),
# ]

from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('signin/', views.login_view, name='signin'),  # Alias for login
    path('logout/', views.logout_view, name='logout'),
]
