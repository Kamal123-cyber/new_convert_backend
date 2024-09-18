from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Record
from .serializers import RecordSerializer
import requests
import os
from django.core.files.base import ContentFile
from django.conf import settings

FASTAPI_BASE_URL = "http://127.0.0.1:8000"  # Adjust this to your FastAPI server URL

class ConversionAPIView(APIView):
  #  permission_classes = [IsAuthenticated]

    def get_max_file_size(self, user):
        if not user.is_authenticated:
            return 2 * 1024 * 1024  # 2 MB
        elif user.subscription == 'basic':
            return 5 * 1024 * 1024  # 5 MB
        elif user.subscription == 'standard':
            return 15 * 1024 * 1024  # 15 MB
        elif user.subscription == 'premium':
            return 25 * 1024 * 1024  # 25 MB
        else:
            return 2 * 1024 * 1024  # Default to 2 MB

    def post(self, request, conversion_type):
        if 'file' not in request.FILES:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']
        max_file_size = self.get_max_file_size(request.user)

        if file.size > max_file_size:
            return Response({"error": "File size exceeds the allowed limit"}, status=status.HTTP_400_BAD_REQUEST)

        if conversion_type == 'pdf-to-docx':
            fastapi_endpoint = f"{FASTAPI_BASE_URL}/convert/pdf-to-docx"
            converted_format = 'docx'
        elif conversion_type == 'pdf-to-txt':
            fastapi_endpoint = f"{FASTAPI_BASE_URL}/convert/pdf-to-txt"
            converted_format = 'txt'
        else:
            return Response({"error": "Invalid conversion type"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Call FastAPI for conversion
            response = requests.post(fastapi_endpoint, files={"file": file})
            response.raise_for_status()
            result = response.json()

            # Download the converted file
            converted_file_url = f"{FASTAPI_BASE_URL}{result['download_url']}"
            converted_file_response = requests.get(converted_file_url)
            converted_file_response.raise_for_status()

            # Create the Record instance
            record = Record(
                user=request.user,
                original_file=file,
                original_format=os.path.splitext(file.name)[1][1:],
                original_size=file.size,
                converted_format=converted_format,
                status='completed'
            )

            # Save the converted file to the Record
            converted_filename = os.path.basename(result['download_url'])
            record.converted_file.save(converted_filename, ContentFile(converted_file_response.content), save=False)
            record.converted_size = record.converted_file.size
            record.save()

            serializer = RecordSerializer(record)
            return Response({
                "message": "Conversion successful",
                "record": serializer.data,
                "download_url": settings.MEDIA_URL + record.converted_file.name
            }, status=status.HTTP_200_OK)

        except requests.RequestException as e:
            return Response({"error": f"Error calling FastAPI: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class RecordListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        records = Record.objects.filter(user=request.user)
        serializer = RecordSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)