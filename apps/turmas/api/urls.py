"""Rotas da API do domínio Turmas."""

from django.urls import path

from apps.turmas.api.views import TurmasHistoricasAnoProfessorView

urlpatterns = [
    # EP-24 — Turmas históricas do professor por ano
    path(
        "professores/turmas/anos-letivos/<int:anoLetivo>/"
        "professor/<str:professorRf>/turmas-historicas-geral/",
        TurmasHistoricasAnoProfessorView.as_view(),
        name="turmas-historicas-professor",
    ),
]
