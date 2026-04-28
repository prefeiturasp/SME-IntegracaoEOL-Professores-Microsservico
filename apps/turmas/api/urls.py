"""Rotas da API do domínio Turmas."""

from django.urls import path

from apps.turmas.api.views import TurmasHistoricasAnoProfessorView

urlpatterns = [
    # EP-24 — Turmas históricas do professor por ano
    path(
        "turmas/anos-letivos/<int:ano_letivo>/professor/<str:professor_rf>/turmas-historicas-geral/",
        TurmasHistoricasAnoProfessorView.as_view(),
        name="turmas-historicas-professor",
    ),
]
