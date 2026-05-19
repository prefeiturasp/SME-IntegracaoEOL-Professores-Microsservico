"""Rotas da API do domínio de turmas."""

from django.urls import path

from apps.turmas.api.views import TurmasHistoricasAnoProfessorView

urlpatterns = [
    path(
        "professores/turmas/anos-letivos/<int:ano_letivo>/"
        "professor/<str:professor_rf>/turmas-historicas-geral/",
        TurmasHistoricasAnoProfessorView.as_view(),
        name="turmas-historicas-professor",
    ),
]
