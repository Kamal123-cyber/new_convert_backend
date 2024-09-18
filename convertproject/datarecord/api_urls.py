from django.urls import path
from .api_views import ConversionAPIView, RecordListAPIView

urlpatterns = [
    path('convert/<str:conversion_type>/', ConversionAPIView.as_view(), name='convert'),
    path('records/', RecordListAPIView.as_view(), name='record_list'),
]