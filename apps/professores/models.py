"""Models do domínio de professores."""

from django.db import models

_HELP_UE = "ID da UnidadeEducacional neste DB."
_HELP_TURMA = "ID da turma escolar neste DB."
_HELP_STG = "ID da serie-grade neste DB."
_HELP_GRADE = "ID da escola_grade — ref. domínio pedagógico."
_HELP_COMP = "ID do componente curricular — ref. domínio curricular."
_HELP_TERR = "ID do território do saber — ref. domínio pedagógico."
_HELP_EXP = "ID da experiência pedagógica — ref. domínio pedagógico."


class UnidadeEducacional(models.Model):
    """Representa uma unidade educacional."""

    codigo_ue = models.CharField(max_length=20, primary_key=True)
    codigo_dre = models.CharField(max_length=20, null=True, blank=True)
    codigo_tipo_escola = models.IntegerField(null=True, blank=True)

    class Meta:
        app_label = "professores"
        db_table = "unidade_educacional"
        managed = False


class TurmaEscolaGradePrograma(models.Model):
    """Representa grade de programa vinculada a uma turma."""

    codigo = models.BigIntegerField(primary_key=True)
    codigo_turma = models.BigIntegerField(help_text=_HELP_TURMA)
    codigo_escola_grade = models.IntegerField(help_text=_HELP_GRADE)
    dt_fim = models.DateField(null=True, blank=True)

    class Meta:
        app_label = "professores"
        db_table = "turma_escola_grade_programa"
        managed = False


class TurmaGradeTerritorioExperiencia(models.Model):
    """Vínculo entre série-grade, componente, território e experiência."""

    id = models.BigAutoField(primary_key=True)
    codigo_serie_grade = models.IntegerField(help_text=_HELP_STG)
    codigo_componente_curricular = models.IntegerField(help_text=_HELP_COMP)
    codigo_territorio_saber = models.IntegerField(help_text=_HELP_TERR)
    codigo_experiencia_pedagogica = models.IntegerField(help_text=_HELP_EXP)
    dt_inicio = models.DateField(null=True, blank=True)

    class Meta:
        app_label = "professores"
        db_table = "turma_grade_territorio_experiencia"
        managed = False


class AgrupamentoAtribuicaoTerritorioSaber(models.Model):
    """Agrupamento de atribuição do programa Território do Saber."""

    codigo_agrupamento = models.BigIntegerField(primary_key=True)
    codigo_territorio_saber = models.IntegerField(null=True, blank=True)
    codigo_experiencia_pedagogica = models.IntegerField(null=True, blank=True)
    dt_inicio_atribuicao = models.DateField(null=True, blank=True)
    ano_atribuicao = models.IntegerField(null=True, blank=True)
    dt_fim_atribuicao = models.DateField(null=True, blank=True)
    dt_fim_turma = models.DateField(null=True, blank=True)
    rf_professor = models.CharField(max_length=20, null=True, blank=True)
    codigo_turma = models.BigIntegerField(null=True, blank=True)
    codigos_componentes_curriculares = models.TextField(null=True, blank=True)
    ano_letivo = models.IntegerField(null=True, blank=True)
    codigo_motivo_disponibilizacao = models.IntegerField(null=True, blank=True)
    encerramento_atribuicao_agrupamento_atualizado = models.BooleanField(
        null=True, blank=True
    )
    criado_em = models.DateTimeField(null=True, blank=True)
    alterado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "professores"
        db_table = "agrupamento_atribuicao_territorio_saber"
        managed = False


class Professor(models.Model):
    """Servidor público com perfil de professor na rede municipal."""

    codigo_rf = models.CharField(max_length=20, primary_key=True)
    nome = models.CharField(max_length=200)
    nome_social = models.CharField(max_length=200, null=True, blank=True)
    cpf = models.CharField(max_length=14, null=True, blank=True)

    class Meta:
        app_label = "professores"
        db_table = "professor"
        managed = False

    def __str__(self) -> str:
        return f"{self.codigo_rf} - {self.nome}"


class CargoBaseServidor(models.Model):
    """Representa nomeação ou cargo base do servidor."""

    id = models.BigAutoField(primary_key=True)
    professor = models.ForeignKey(
        Professor,
        on_delete=models.CASCADE,
        related_name="cargos_base",
        db_column="codigo_rf",
        db_constraint=False,
    )
    codigo_cargo = models.IntegerField()
    descricao_cargo = models.CharField(max_length=100)
    situacao_funcional = models.IntegerField(null=True, blank=True)
    dt_posse = models.DateField(null=True, blank=True)
    dt_fim_nomeacao = models.DateField(null=True, blank=True)
    dt_cancelamento = models.DateField(null=True, blank=True)

    class Meta:
        app_label = "professores"
        db_table = "cargo_base_servidor"
        managed = False


class LotacaoServidor(models.Model):
    """Lotação do servidor em unidade educacional."""

    id = models.BigAutoField(primary_key=True)
    cargo_base = models.ForeignKey(
        CargoBaseServidor,
        on_delete=models.CASCADE,
        related_name="lotacoes",
        db_constraint=False,
    )
    codigo_unidade_educacao = models.CharField(max_length=20)
    codigo_dre = models.CharField(max_length=20, null=True, blank=True)
    dt_inicio = models.DateField(null=True, blank=True)
    dt_fim = models.DateField(null=True, blank=True)

    class Meta:
        app_label = "professores"
        db_table = "lotacao_servidor"
        managed = False


class FuncionarioUnidadeEducacional(models.Model):
    """Funcionario consolidado para consulta por unidade educacional."""

    codigo_rf = models.CharField(max_length=20, primary_key=True)
    nome = models.CharField(max_length=200)
    nome_social = models.CharField(max_length=200, null=True, blank=True)
    cpf = models.CharField(max_length=14, null=True, blank=True)
    codigo_ue = models.CharField(max_length=20)
    codigo_dre = models.CharField(max_length=20, null=True, blank=True)
    data_inicio = models.DateTimeField(null=True, blank=True)
    data_fim = models.DateTimeField(null=True, blank=True)
    dt_fim_nomeacao = models.DateTimeField(null=True, blank=True)
    dt_fim_funcao_atividade = models.DateTimeField(null=True, blank=True)
    origem_vinculo = models.CharField(max_length=30, null=True, blank=True)
    codigo_cargo = models.CharField(max_length=20, null=True, blank=True)
    cargo = models.CharField(max_length=100, null=True, blank=True)
    codigo_tipo_funcao_atividade = models.IntegerField(
        null=True,
        blank=True,
    )
    eh_professor = models.BooleanField(default=False)
    esta_afastado = models.BooleanField(default=False)
    funcao_externo = models.IntegerField(default=0)
    tipo_funcao_externo = models.IntegerField(default=0)
    nome_ue = models.CharField(max_length=200, null=True, blank=True)
    tipo_funcionario_externo = models.CharField(
        max_length=100, null=True, blank=True
    )
    dc_funcao_externo = models.CharField(max_length=100, null=True, blank=True)
    pessoa = models.ForeignKey(
        "Pessoa",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        db_constraint=False,
    )
    supervisor_dre = models.BooleanField(default=False)

    class Meta:
        app_label = "professores"
        db_table = "funcionario_unidade_educacional"
        verbose_name = "funcionario"
        verbose_name_plural = "funcionarios"
        managed = False
        indexes = [
            models.Index(fields=["codigo_ue"], name="idx_funcionario_ue"),
            models.Index(fields=["codigo_dre"], name="idx_funcionario_dre"),
            models.Index(
                fields=["codigo_cargo"], name="idx_funcionario_cargo"
            ),
            models.Index(fields=["codigo_rf"], name="idx_funcionario_rf"),
            models.Index(
                fields=["codigo_ue", "codigo_cargo"],
                name="idx_funcionario_ue_cargo",
            ),
            models.Index(
                fields=["codigo_dre", "codigo_cargo"],
                name="idx_funcionario_dre_cargo",
            ),
        ]


class FuncionarioCargo(models.Model):
    """Funcionário por cargo."""

    id = models.BigAutoField(primary_key=True)
    codigo_rf = models.CharField(max_length=20)
    nome = models.CharField(max_length=200)
    data_inicio = models.DateTimeField(null=True, blank=True)
    data_fim = models.DateTimeField(null=True, blank=True)
    cargo = models.CharField(max_length=100)
    codigo_cargo = models.IntegerField()

    class Meta:
        app_label = "professores"
        db_table = "funcionario_cargo"
        managed = False


class TurmaAtribuidaUe(models.Model):
    """Turma atribuída por vínculo do funcionário com UE."""

    id = models.BigAutoField(primary_key=True)
    codigo_escola = models.CharField(max_length=6)
    codigo_turma = models.BigIntegerField()
    ano_letivo = models.IntegerField()
    modalidade = models.CharField(max_length=15, null=True, blank=True)
    semestre = models.IntegerField(null=True, blank=True)
    codigo_modalidade = models.IntegerField(null=True, blank=True)
    codigo_dre = models.CharField(max_length=6, null=True, blank=True)
    dre = models.CharField(max_length=60, null=True, blank=True)
    dre_abreviacao = models.CharField(max_length=60, null=True, blank=True)
    ue = models.CharField(max_length=60, null=True, blank=True)
    ue_abreviacao = models.CharField(max_length=60, null=True, blank=True)
    nome_turma = models.CharField(max_length=15, null=True, blank=True)
    ano = models.CharField(max_length=18, null=True, blank=True)
    tipo_ue = models.CharField(max_length=25, null=True, blank=True)
    codigo_tipo_ue = models.IntegerField(null=True, blank=True)
    codigo_tipo_escola = models.IntegerField(null=True, blank=True)
    tipo_escola = models.CharField(max_length=12, null=True, blank=True)
    duracao_turno = models.IntegerField(null=True, blank=True)
    tipo_turno = models.IntegerField(null=True, blank=True)
    usuario_rf = models.CharField(max_length=10)
    cargo = models.IntegerField(null=True, blank=True)
    cargo_sobreposto = models.IntegerField(null=True, blank=True)

    class Meta:
        app_label = "professores"
        db_table = "turma_atribuida_ue"
        managed = False


class DisciplinaTurmaAtribuidaUe(models.Model):
    """Disciplina atribuída por vínculo do funcionário com UE."""

    id = models.BigAutoField(primary_key=True)
    codigo_escola = models.CharField(max_length=6)
    codigo_turma = models.BigIntegerField()
    ano_letivo = models.IntegerField()
    usuario_rf = models.CharField(max_length=10)
    codigo_componente_curricular = models.IntegerField()
    descricao_componente_curricular = models.CharField(max_length=200)
    codigo_componente_curricular_pai = models.IntegerField(
        null=True,
        blank=True,
    )
    regencia = models.BooleanField(default=False)
    codigo_componente_territorio_saber = models.IntegerField(
        null=True,
        blank=True,
    )
    territorio_saber = models.BooleanField(default=False)
    codigo_dre = models.CharField(max_length=6, null=True, blank=True)
    codigo_tipo_escola = models.IntegerField(null=True, blank=True)
    tipo_escola = models.CharField(max_length=12, null=True, blank=True)
    cargo = models.IntegerField(null=True, blank=True)
    cargo_sobreposto = models.IntegerField(null=True, blank=True)

    class Meta:
        app_label = "professores"
        db_table = "disciplina_turma_atribuida_ue"
        managed = False


class CargoSobrepostoServidor(models.Model):
    """Cargo sobreposto exercido sobre o cargo base."""

    id = models.BigAutoField(primary_key=True)
    cargo_base = models.ForeignKey(
        CargoBaseServidor,
        on_delete=models.CASCADE,
        related_name="cargos_sobrepostos",
        db_constraint=False,
    )
    codigo_cargo = models.IntegerField()
    codigo_unidade_local_servico = models.CharField(max_length=20)
    dt_fim_cargo_sobreposto = models.DateField(null=True, blank=True)

    class Meta:
        app_label = "professores"
        db_table = "cargo_sobreposto_servidor"
        managed = False


class FuncaoAtividadeCargoServidor(models.Model):
    """Função de atividade exercida pelo servidor em determinada unidade."""

    id = models.BigAutoField(primary_key=True)
    cargo_base = models.ForeignKey(
        CargoBaseServidor,
        on_delete=models.CASCADE,
        related_name="funcoes_atividade",
        db_constraint=False,
    )
    codigo_unidade_local_servico = models.CharField(max_length=20)
    dt_fim_funcao_atividade = models.DateField(null=True, blank=True)

    class Meta:
        app_label = "professores"
        db_table = "funcao_atividade_cargo_servidor"
        managed = False


class LaudoMedico(models.Model):
    """Registro de laudo médico do servidor."""

    id = models.BigAutoField(primary_key=True)
    cargo_base = models.ForeignKey(
        CargoBaseServidor,
        on_delete=models.CASCADE,
        related_name="laudos_medicos",
        db_constraint=False,
    )

    class Meta:
        app_label = "professores"
        db_table = "laudo_medico"
        managed = False


class Pessoa(models.Model):
    """Pessoa física que atua como professor contratado (externo)."""

    codigo_pessoa = models.BigIntegerField(primary_key=True)
    cpf = models.CharField(max_length=14, unique=True)
    nome = models.CharField(max_length=200)
    nome_social = models.CharField(max_length=200, null=True, blank=True)
    nome_pai = models.CharField(max_length=200, null=True, blank=True)
    nome_mae = models.CharField(max_length=200, null=True, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    rg = models.CharField(max_length=30, null=True, blank=True)
    titulo_eleitoral = models.CharField(max_length=30, null=True, blank=True)
    pis_pasep = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        app_label = "professores"
        db_table = "pessoa"
        managed = False

    def __str__(self) -> str:
        return f"{self.cpf} - {self.nome}"


class ContratoExterno(models.Model):
    """Representa contrato de professor externo."""

    codigo_contrato = models.BigIntegerField(primary_key=True)
    pessoa = models.ForeignKey(
        Pessoa,
        on_delete=models.CASCADE,
        related_name="contratos",
        db_constraint=False,
    )
    codigo_tipo_funcao = models.IntegerField()
    codigo_unidade_educacao = models.CharField(max_length=20)
    dt_cancelamento = models.DateField(null=True, blank=True)
    codigo_motivo_desligamento = models.IntegerField(null=True, blank=True)

    class Meta:
        app_label = "professores"
        db_table = "contrato_externo"
        managed = False


class AtribuicaoAula(models.Model):
    """Atribuição de aulas ao professor efetivo."""

    id = models.BigAutoField(primary_key=True)
    cargo_base = models.ForeignKey(
        CargoBaseServidor,
        on_delete=models.CASCADE,
        related_name="atribuicoes",
        db_constraint=False,
    )
    codigo_unidade_educacao = models.CharField(max_length=20)
    codigo_turma_escola = models.BigIntegerField(null=True, blank=True)
    descricao_turma_escola = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Descrição da turma escolar.",
    )
    codigo_turma_escola_grade_programa = models.BigIntegerField(
        null=True, blank=True
    )
    codigo_grade = models.IntegerField()
    codigo_componente_curricular = models.IntegerField()
    descricao_componente_curricular = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Descrição do componente curricular.",
    )
    codigo_serie_grade = models.IntegerField(null=True, blank=True)
    ano_escolar = models.CharField(max_length=5, null=True, blank=True)
    ano_atribuicao = models.IntegerField()
    codigo_etapa_ensino = models.IntegerField(null=True, blank=True)
    dt_atribuicao_aula = models.DateField()
    dt_disponibilizacao_aulas = models.DateField(null=True, blank=True)
    dt_inicio_turma = models.DateField(null=True, blank=True)
    dt_fim_turma = models.DateField(null=True, blank=True)
    codigo_motivo_disponibilizacao = models.IntegerField(null=True, blank=True)
    dt_cancelamento = models.DateField(null=True, blank=True)
    codigo_dre = models.CharField(max_length=20, null=True, blank=True)
    nome_dre = models.CharField(max_length=200, null=True, blank=True)
    abreviacao_dre = models.CharField(max_length=100, null=True, blank=True)
    nome_unidade_educacional = models.CharField(
        max_length=200, null=True, blank=True
    )
    codigo_tipo_escola = models.IntegerField(null=True, blank=True)
    codigo_tipo_turma = models.IntegerField(null=True, blank=True)
    modalidade = models.CharField(max_length=50, null=True, blank=True)
    codigo_modalidade = models.IntegerField(null=True, blank=True)
    semestre = models.IntegerField(null=True, blank=True)
    duracao_turno = models.IntegerField(null=True, blank=True)
    tipo_turno = models.IntegerField(null=True, blank=True)

    class Meta:
        app_label = "professores"
        db_table = "atribuicao_aula"
        managed = False


class AtribuicaoExterno(models.Model):
    """Atribuição de aulas ao professor externo/contratado."""

    id = models.BigAutoField(primary_key=True)
    contrato_externo = models.ForeignKey(
        ContratoExterno,
        on_delete=models.CASCADE,
        related_name="atribuicoes",
        db_constraint=False,
    )
    codigo_unidade_educacao = models.CharField(max_length=20)
    codigo_turma_escola = models.BigIntegerField(null=True, blank=True)
    descricao_turma_escola = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Descrição da turma escolar.",
    )
    codigo_grade = models.IntegerField()
    codigo_componente_curricular = models.IntegerField()
    descricao_componente_curricular = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Descrição do componente curricular.",
    )
    codigo_serie_grade = models.IntegerField(null=True, blank=True)
    codigo_turma_escola_grade_programa = models.BigIntegerField(
        null=True, blank=True
    )
    ano_escolar = models.CharField(max_length=5, null=True, blank=True)
    ano_atribuicao = models.IntegerField()
    codigo_etapa_ensino = models.IntegerField(null=True, blank=True)
    dt_atribuicao = models.DateField()
    dt_disponibilizacao = models.DateField(null=True, blank=True)
    dt_inicio_turma = models.DateField(null=True, blank=True)
    dt_fim_turma = models.DateField(null=True, blank=True)
    codigo_motivo_disponibilizacao_externo = models.IntegerField(
        null=True, blank=True
    )
    dt_cancelamento = models.DateField(null=True, blank=True)

    class Meta:
        app_label = "professores"
        db_table = "atribuicao_externo"
        managed = False


class AdministradorEscola(models.Model):
    """Administradores SGP vinculados a unidades educacionais.
    """

    codigo_ue = models.CharField(max_length=20, db_index=True)
    rf_login = models.CharField(max_length=50)
    data_sincronizacao = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "professores"
        db_table = "administrador_escola"
        managed = False

    def __str__(self) -> str:
        return f"{self.rf_login} @ {self.codigo_ue}"
