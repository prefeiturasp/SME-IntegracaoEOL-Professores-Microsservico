"""Rotas da API do domínio de cargos."""

from django.urls import path

from apps.cargos.api.views import CargosView

urlpatterns = [
    path("professores/cargos/", CargosView.as_view(), name="cargos-listar"),
]
