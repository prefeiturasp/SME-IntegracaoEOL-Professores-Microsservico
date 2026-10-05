"""Rotas principais do projeto Django."""

from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny

from apps.core.health import HealthView

_API = "api/v1/"

urlpatterns = [
    path(f"{_API}professores/health/", HealthView.as_view(), name="health"),
    path(
        f"{_API}schema/",
        SpectacularAPIView.as_view(
            authentication_classes=[],
            permission_classes=[AllowAny],
        ),
        name="schema",
    ),
    path(
        f"{_API}docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema",
            authentication_classes=[],
            permission_classes=[AllowAny],
        ),
        name="swagger-ui",
    ),
    path(_API, include("apps.cargos.api.urls")),
    path(_API, include("apps.professores.api.urls")),
    path(_API, include("apps.turmas.api.urls")),
    path(_API, include("apps.funcionarios.api.urls")),
]
