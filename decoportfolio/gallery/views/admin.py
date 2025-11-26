from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
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


class PortfolioImageAdminViewSet(ModelViewSet):
    queryset = PortfolioImage.objects.select_related("portfolio_item")
    serializer_class = PortfolioImageSerializer
    authentication_classes = [FamilyMemberTokenAuthentication]
    permission_classes = [IsFamilyMember]


class PortfolioVideoAdminViewSet(ModelViewSet):
    queryset = PortfolioVideo.objects.select_related("portfolio_item")
    serializer_class = PortfolioVideoSerializer
    authentication_classes = [FamilyMemberTokenAuthentication]
    permission_classes = [IsFamilyMember]


class CategoryAdminViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = [FamilyMemberTokenAuthentication]
    permission_classes = [IsFamilyMember]


class ServiceAdminViewSet(ModelViewSet):
    queryset = Service.objects.select_related("category")
    serializer_class = ServiceSerializer
    authentication_classes = [FamilyMemberTokenAuthentication]
    permission_classes = [IsFamilyMember]


class BusinessInfoAdminViewSet(ModelViewSet):
    queryset = BusinessInfo.objects.all()
    serializer_class = BusinessInfoSerializer
    authentication_classes = [FamilyMemberTokenAuthentication]
    permission_classes = [IsFamilyMember]
