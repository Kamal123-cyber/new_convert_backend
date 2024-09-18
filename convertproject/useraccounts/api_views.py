from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from allauth.account.adapter import get_adapter
from .serializers import SignUpSerializer, SignInSerializers, ChangePasswordSerializer
from .models import UserAccount

class SignUpAPIView(APIView):
    def post(self, request):
        try:
            serializer = SignUpSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                email = serializer.validated_data['email']
                first_name = serializer.validated_data['first_name']
                last_name = serializer.validated_data['last_name']
                password = serializer.validated_data['password1']
                user_username = get_adapter().generate_unique_username([first_name])
                user_obj = UserAccount.objects.create(
                    email=email,
                    username=user_username,
                    first_name=first_name,
                    last_name=last_name,
                    user_type='basic'
                )
                user_obj.set_password(password)
                user_obj.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SignInAPIView(APIView):
    serializer_class = SignInSerializers

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                token, _ = Token.objects.get_or_create(user=user)
                return Response({
                    "message": "Sign In Successfully",
                    "token": token.key
                }, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid email and password"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)