from django.urls import path
from .api_views import SignUpAPIView, SignInAPIView, ChangePasswordAPIView

urlpatterns = [
    path('signup/', SignUpAPIView.as_view(), name='signup'),
    path('signin/', SignInAPIView.as_view(), name='signin'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change_password'),
]