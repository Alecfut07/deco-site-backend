from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import (
    PortfolioItemViewSet,
    CategoryViewSet,
    ServiceViewSet,
    BusinessInfoViewSet,
)
from .views.admin import (
    PortfolioItemAdminViewSet,
    PortfolioImageAdminViewSet,
    PortfolioVideoAdminViewSet,
    CategoryAdminViewSet,
    ServiceAdminViewSet,
    BusinessInfoAdminViewSet,
)
from .views.auth import FamilyLoginView, FamilyLogoutView, UserView

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r"portfolio-items", PortfolioItemViewSet, basename="portfolioitem")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"services", ServiceViewSet, basename="service")
router.register(r"business-info", BusinessInfoViewSet, basename="businessinfo")

# Add the Family-only endpoints
router.register(
    r"admin/portfolio-items", PortfolioItemAdminViewSet, basename="admin-portfolioitem"
)
router.register(
    r"admin/portfolio-images",
    PortfolioImageAdminViewSet,
    basename="admin-portfolioimage",
)
router.register(
    r"admin/portfolio-videos",
    PortfolioVideoAdminViewSet,
    basename="admin-portfoliovideo",
)
router.register(r"admin/categories", CategoryAdminViewSet, basename="admin-category")
router.register(r"admin/services", ServiceAdminViewSet, basename="admin-service")
# router.register(
#     r"admin/business-info", BusinessInfoAdminViewSet, basename="admin-businessinfo"
# )

app_name = "gallery"

urlpatterns = [
    # Custom routes for BusinessInfo singleton (must come BEFORE router to take precedence)
    path(
        "api/admin/business-info/",
        BusinessInfoAdminViewSet.as_view(
            {
                "get": "list",
                "patch": "update_singleton",
                "put": "update_singleton",
            }
        ),
        name="admin-businessinfo-singleton",
    ),
    # Include the router URLs
    path("api/", include(router.urls)),
    path("api/auth/login/", FamilyLoginView.as_view(), name="family-login"),
    path("api/auth/logout/", FamilyLogoutView.as_view(), name="family-logout"),
    path("api/auth/user/", UserView.as_view(), name="current-user"),
    # Keep your existing endpoints for backward compatibility
    path(
        "api/gallery/",
        PortfolioItemViewSet.as_view({"get": "list"}),
        name="portfolio_list",
    ),
    path(
        "api/gallery/<int:pk>/",
        PortfolioItemViewSet.as_view({"get": "retrieve"}),
        name="portfolio_detail",
    ),
    path(
        "api/gallery/search/",
        PortfolioItemViewSet.as_view({"get": "search"}),
        name="portfolio_search",
    ),
    path(
        "api/gallery/filter/",
        PortfolioItemViewSet.as_view({"get": "filter"}),
        name="portfolio_filter",
    ),
    path(
        "api/gallery/combined/",
        PortfolioItemViewSet.as_view({"get": "combined"}),
        name="portfolio_combined",
    ),
    path(
        "api/gallery/category/<str:category>/",
        PortfolioItemViewSet.as_view({"get": "by_category"}),
        name="portfolio_by_category",
    ),
]
