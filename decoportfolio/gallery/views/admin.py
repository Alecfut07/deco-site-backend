from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from gallery.models import (
    PortfolioItem,
    PortfolioImage,
    PortfolioVideo,
    Category,
    Service,
    BusinessInfo,
)
from gallery.serializers import (
    PortfolioItemSerializer,
    PortfolioImageSerializer,
    PortfolioVideoSerializer,
    CategorySerializer,
    ServiceSerializer,
    BusinessInfoSerializer,
)
from gallery.permissions import IsFamilyMember
from gallery.views.auth import FamilyMemberTokenAuthentication


class PortfolioItemAdminViewSet(ModelViewSet):
    queryset = PortfolioItem.objects.all()
    serializer_class = PortfolioItemSerializer
    authentication_classes = [FamilyMemberTokenAuthentication]
    permission_classes = [IsFamilyMember]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        item_title = instance.title
        self.perform_destroy(instance)
        return Response(
            {"detail": f"Portfolio item {item_title} deleted successfully."},
            status=status.HTTP_200_OK,
        )


class PortfolioImageAdminViewSet(ModelViewSet):
    queryset = PortfolioImage.objects.select_related("portfolio_item")
    serializer_class = PortfolioImageSerializer
    authentication_classes = [FamilyMemberTokenAuthentication]
    permission_classes = [IsFamilyMember]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Portfolio image deleted successfully."},
            status=status.HTTP_200_OK,
        )


class PortfolioVideoAdminViewSet(ModelViewSet):
    queryset = PortfolioVideo.objects.select_related("portfolio_item")
    serializer_class = PortfolioVideoSerializer
    authentication_classes = [FamilyMemberTokenAuthentication]
    permission_classes = [IsFamilyMember]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Portfolio video deleted successfully."},
            status=status.HTTP_200_OK,
        )


class CategoryAdminViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = [FamilyMemberTokenAuthentication]
    permission_classes = [IsFamilyMember]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        category_name = instance.name
        self.perform_destroy(instance)
        return Response(
            {"detail": f"Category {category_name} deleted successfully."},
            status=status.HTTP_200_OK,
        )


class ServiceAdminViewSet(ModelViewSet):
    queryset = Service.objects.select_related("category")
    serializer_class = ServiceSerializer
    authentication_classes = [FamilyMemberTokenAuthentication]
    permission_classes = [IsFamilyMember]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        service_name = instance.name
        self.perform_destroy(instance)
        return Response(
            {"detail": f"Service {service_name} deleted successfully."},
            status=status.HTTP_200_OK,
        )


class BusinessInfoAdminViewSet(ModelViewSet):
    queryset = BusinessInfo.objects.all()
    serializer_class = BusinessInfoSerializer
    authentication_classes = [FamilyMemberTokenAuthentication]
    permission_classes = [IsFamilyMember]

    def get_object(self):
        """
        Since BusinessInfo is a singleton, return the first (and only) instance.
        If none exists, create one.
        """
        obj = BusinessInfo.objects.first()
        if obj is None:
            # Create a default instance if none exists.
            obj = BusinessInfo.objects.create(
                company_name="Ortega Reyes Remodeling and Restoration",
                phone="",
            )
        return obj

    def list(self, request, *args, **kwargs):
        """
        Return the single BusinessInfo instance as a list with one item.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response([serializer.data])

    def retrieve(self, request, *args, **kwargs):
        """
        Return the single BusinessInfo instance.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
        Handle PUT request to update BusinessInfo.
        Works with or without ID in URL.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Business info deleted successfully."},
            status=status.HTTP_200_OK,
        )
