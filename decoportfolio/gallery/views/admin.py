from rest_framework.viewsets import ModalViewSet
from gallery.models import PortfolioItem
from gallery.serializers import PortfolioItemSerializer
from gallery.permissions import IsFamilyMember

class PortfolioItemAdminViewSet(ModalViewSet):
    queryset = PortfolioItem.objects.all()
    serializer_class = PortfolioItemSerializer
    permission_classes = [IsFamilyMember]
    # default create/update/delete logic comes from ModalViewSet