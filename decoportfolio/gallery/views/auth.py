from django.contrib.auth import authenticate
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework import status, permissions, exceptions
from gallery.models import FamilyMember
from gallery.serializers import FamilyLoginSerializer


class FamilyMemberTokenAuthentication(TokenAuthentication):
    """
    Custom token authentication that only works with FamilyMember users.
    Django Admin users won't be authenticated by this.
    """

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related("user").get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid token.")

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed("User inactive or deleted.")

        # Only allow FamilyMember users
        if not isinstance(token.user, FamilyMember):
            raise exceptions.AuthenticationFailed("Invalid user type.")

        return (token.user, token)


class FamilyLoginView(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = FamilyLoginSerializer
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]
        user = authenticate(request, username=username, password=password)

        if user is None:
            return Response(
                {"detail": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST
            )

        if not (user.is_superuser or user.groups.filter(name="Family").exists()):
            return Response(
                {"detail": "Access restricted to family members."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get or create token for the user (Token Authentication)
        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {
                "detail": "Login successful.",
                "token": token.key,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            }
        )


class FamilyLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Require token authentication

    def post(self, request):
        # Delete the token to logout (Token Authentication)
        # This doesn't affect Django admin session at all
        try:
            request.user.auth_token.delete()
        except:
            pass  # Token might not exist

        return Response({"detail": "Logout successful."}, status=status.HTTP_200_OK)


class UserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

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
