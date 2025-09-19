from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path("api/", include("api.urls")),
]

if settings.DEBUG:
    urlpatterns += static("/", document_root=settings.BASE_DIR)
