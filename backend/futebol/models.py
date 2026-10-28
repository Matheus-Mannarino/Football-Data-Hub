from django.db import models

class Clubes(models.Model):
    id = models.BigAutoField(primary_key=True)
    api_id = models.BigIntegerField(unique=True)
    nome = models.CharField(max_length=100)
    logo = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'clubes'


class Competicoes(models.Model):
    id = models.BigAutoField(primary_key=True)
    api_id = models.BigIntegerField(unique=True)
    nome = models.CharField(max_length=50)
    logo = models.TextField(blank=True, null=True)
    pais_codigo = models.CharField(max_length=2)
    pais_nome = models.CharField(max_length=50)
    pais_logo = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'competicoes'


class JogadorPartida(models.Model):
    id = models.BigAutoField(primary_key=True)
    jogador = models.ForeignKey('Jogadores', models.DO_NOTHING)
    partida = models.ForeignKey('Partidas', models.DO_NOTHING)
    clube = models.ForeignKey(Clubes, models.DO_NOTHING)
    numero_camisa = models.SmallIntegerField()
    posicao_partida = models.CharField(max_length=50)
    nota = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    capitao = models.BooleanField()
    minutos_jogados = models.SmallIntegerField()
    titular = models.BooleanField()
    impedimentos = models.SmallIntegerField()
    gols = models.SmallIntegerField()
    defesas = models.SmallIntegerField()
    gols_sofridos = models.SmallIntegerField()
    assistencias = models.SmallIntegerField()
    dribles_total = models.SmallIntegerField()
    dribles_bem_sucedidos = models.SmallIntegerField()
    faltas_sofridas = models.SmallIntegerField()
    faltas_cometidas = models.SmallIntegerField()
    desarmes = models.SmallIntegerField()
    interceptacoes = models.SmallIntegerField()
    finalizacoes_total = models.SmallIntegerField()
    finalizacoes_no_alvo = models.SmallIntegerField()
    penaltis_cobrados = models.SmallIntegerField()
    penaltis_convertidos = models.SmallIntegerField()
    passes_total = models.SmallIntegerField()
    passes_certos = models.SmallIntegerField()
    passes_chave = models.SmallIntegerField()
    cartoes_amarelos = models.SmallIntegerField()
    cartoes_vermelhos = models.SmallIntegerField()
    segundos_amarelos = models.SmallIntegerField()
    duelos_total = models.SmallIntegerField()
    duelos_vencidos = models.SmallIntegerField()
    xa = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True)
    xg = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True)
    xg_no_alvo = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True)
    xg_no_alvo_sofrido = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True)
    gols_evitados_esperados = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'jogador_partida'
        unique_together = (('jogador', 'partida'),)


class Jogadores(models.Model):
    id = models.BigAutoField(primary_key=True)
    api_id = models.BigIntegerField(unique=True)
    nome = models.CharField(max_length=150)
    logo = models.TextField(blank=True, null=True)
    posicao_principal = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'jogadores'


class Partidas(models.Model):
    id = models.BigAutoField(primary_key=True)
    api_id = models.BigIntegerField(unique=True)
    rodada = models.SmallIntegerField()
    data_hora = models.DateTimeField()
    clube_mandante = models.ForeignKey(Clubes, models.DO_NOTHING)
    clube_visitante = models.ForeignKey(Clubes, models.DO_NOTHING, related_name='partidas_clube_visitante_set')
    gols_mandante = models.SmallIntegerField(blank=True, null=True)
    gols_visitante = models.SmallIntegerField(blank=True, null=True)
    penaltis_mandante = models.SmallIntegerField(blank=True, null=True)
    penaltis_visitante = models.SmallIntegerField(blank=True, null=True)
    minuto = models.SmallIntegerField(blank=True, null=True)
    status_partida = models.CharField(max_length=30)
    temporada = models.ForeignKey('Temporadas', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'partidas'


class Temporadas(models.Model):
    id = models.BigAutoField(primary_key=True)
    ano = models.SmallIntegerField()
    competicao = models.ForeignKey(Competicoes, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'temporadas'
        unique_together = (('competicao', 'ano'),)

class Classificacao(models.Model):
    id = models.BigAutoField(primary_key=True)

    temporada = models.ForeignKey(
        Temporadas,
        models.DO_NOTHING,
    )
    clube = models.ForeignKey(
        Clubes,
        models.DO_NOTHING,
    )

    posicao = models.SmallIntegerField()
    pontos = models.SmallIntegerField()
    jogos = models.SmallIntegerField()
    vitorias = models.SmallIntegerField()
    empates = models.SmallIntegerField()
    derrotas = models.SmallIntegerField()
    gols_pro = models.SmallIntegerField()
    gols_contra = models.SmallIntegerField()
    atualizado_em = models.DateTimeField()

    @property
    def saldo_gols(self):
        return self.gols_pro - self.gols_contra

    @property
    def aproveitamento(self):
        if self.jogos == 0:
            return 0
        return self.pontos / (self.jogos * 3) * 100

    def __str__(self):
        return f"{self.posicao} - {self.clube.nome}"

    class Meta:
        managed = False
        db_table = "classificacao"
        unique_together = (("temporada", "clube"),)
        ordering = ["posicao", "clube_id"]