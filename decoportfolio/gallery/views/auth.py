from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.authentication import BaseAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework import status, permissions, exceptions
from gallery.models import FamilyMember, FamilyMemberToken
from gallery.serializers import FamilyLoginSerializer


class FamilyMemberTokenAuthentication(BaseAuthentication):
    """
    Custom token authentication that only works with FamilyMember users.
    Django Admin users won't be authenticated by this.
    """

    keyword = "Token"

    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        # Debug logging
        print(f"DEBUG: Authorization header: {auth_header}")
        print(f"DEBUG: All headers: {[k for k in request.META.keys() if 'HTTP' in k]}")

        # Also check for lowercase 'authorization' header (some clients send it lowercase)
        if not auth_header:
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        if not auth_header:
            print("DEBUG: No Authorization header found")
            return None

        # Handle both "Token <key>" and "Bearer <key>" formats
        parts = auth_header.split()
        if len(parts) != 2:
            return None

        auth_type, token_key = parts

        # Accept both "Token" and "Bearer" keywords
        if auth_type.lower() not in (self.keyword.lower(), "bearer"):
            return None

        if not token_key:
            return None

        try:
            token = FamilyMemberToken.objects.select_related("user").get(key=token_key)
        except FamilyMemberToken.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid token.")

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed("User inactive or deleted.")

        return (token.user, token)


@method_decorator(csrf_exempt, name="dispatch")
class FamilyLoginView(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = (
        []
    )  # Disable all authentication (including SessionAuth which triggers CSRF)
    serializer_class = FamilyLoginSerializer
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        # Authenticate using FamilyMember model
        try:
            user = FamilyMember.objects.get(username=username)
            if not user.check_password(password):
                user = None
        except FamilyMember.DoesNotExist:
            user = None

        if user is None:
            return Response(
                {"detail": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST
            )

        if not user.is_active:
            return Response(
                {"detail": "Account is inactive."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get or create token for the user (Token Authentication)
        token, created = FamilyMemberToken.objects.get_or_create(user=user)

        return Response(
            {
                "detail": "Login successful.",
                "token": token.key,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
            }
        )


class FamilyLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [FamilyMemberTokenAuthentication]

    def post(self, request):
        # Delete the token to logout
        try:
            request.user.auth_token.delete()
        except:
            pass  # Token might not exist

        return Response({"detail": "Logout successful."}, status=status.HTTP_200_OK)


class UserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [FamilyMemberTokenAuthentication]

    def get(self, request):
        user = request.user
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        )
