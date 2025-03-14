from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("djoser.urls")),
    path("api/v1/auth/", include("djoser.urls.jwt")),
    path("api/v1/products/", include("product.urls")),
    path("api/v1/orders/", include("order.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
