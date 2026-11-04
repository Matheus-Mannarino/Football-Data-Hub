<div align="center">
  <img src="backend/core/static/core/img/logo.png" alt="Football Data Hub" width="180">

# Football Data Hub

**Explore os números. Entenda o jogo.**

Plataforma acadêmica para consultar resultados, acompanhar campanhas e comparar jogadores do Brasileirão Série A de 2026.

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black)

</div>

## Sobre o projeto

O Football Data Hub reúne informações da API Highlightly em um banco PostgreSQL e as apresenta em uma aplicação web desenvolvida com Django. O projeto integra coleta, validação, modelagem relacional e visualização de dados para facilitar a exploração da competição.

O recorte atual é o **Campeonato Brasileiro Série A de 2026**. A aplicação possui nove páginas implementadas e utiliza uma base atualizada por scripts e comandos executados manualmente.

## Funcionalidades

| Página | O que permite explorar |
| --- | --- |
| Início | Visão geral da competição e acesso aos jogos |
| Classificação | Posição, pontos, resultados e indicadores das campanhas |
| Partidas | Confrontos com filtros por rodada e status |
| Detalhe da partida | Resultado e atuações individuais disponíveis |
| Detalhe do clube | Campanha e jogadores com atuação registrada pelo clube |
| Jogadores | Busca e acesso aos perfis dos atletas |
| Detalhe do jogador | Estatísticas e histórico de atuações disponíveis |
| Comparação | Seleção de dois atletas, filtros por nome, clube e posição, tabela e gráficos |
| Sobre | Objetivo, origem dos dados, critérios das métricas, limitações e equipe |

Os clubes podem ser acessados pelas páginas da competição e das partidas, sem uma listagem independente.

### Comparação de jogadores

A comparação apresenta jogos, minutos, gols, assistências, finalizações, passes-chave, desarmes e nota média. Para os indicadores de produção, também são calculados valores por 90 minutos:

```text
Indicador por 90 minutos = (total do indicador / minutos registrados) × 90
```

As estatísticas consideram atuações disponíveis em partidas com status `Finished` e minutos jogados maiores que zero. A nota média é a média aritmética das notas disponíveis, sem ponderação pelo tempo de jogo.

## Tecnologias

| Camada | Tecnologias |
| --- | --- |
| Coleta e tratamento | Python, Requests e JSON |
| Banco de dados | PostgreSQL, SQL e Psycopg |
| Backend | Django e Django ORM |
| Interface | Django Templates, HTML, CSS e JavaScript |
| Configuração | python-dotenv |
| Versionamento | Git e GitHub |
| Fonte dos dados | API Highlightly |

As versões das dependências estão em [requirements.txt](requirements.txt).

## Fluxo dos dados

1. Scripts Python consultam a API e salvam respostas em arquivos JSON.
2. Rotinas de validação verificam os dados coletados.
3. O importador insere ou atualiza os registros no PostgreSQL.
4. O Django consulta as tabelas existentes e apresenta as informações na interface.

A classificação possui um processo próprio: é obtida do endpoint de classificação da API e armazenada no banco. **Ela não é calculada a partir das partidas coletadas.**

### Modelo de dados

| Tabela | Responsabilidade |
| --- | --- |
| `competicoes` | Identificação da competição |
| `temporadas` | Associação entre competição e ano |
| `clubes` | Identificação dos clubes |
| `jogadores` | Identificação e posição principal dos atletas |
| `partidas` | Confrontos, rodada, data, status e placar |
| `jogador_partida` | Atuação de um jogador em uma partida por um clube |
| `classificacao` | Posição e campanha de cada clube na temporada |

Os modelos de futebol usam `managed = False`: a estrutura dessas tabelas é administrada por SQL, fora das migrations do Django.

## Organização do repositório

| Caminho | Conteúdo |
| --- | --- |
| [backend/config/](backend/config/) | Configurações e rotas principais do Django |
| [backend/core/](backend/core/) | Início, página Sobre e estrutura visual compartilhada |
| [backend/futebol/](backend/futebol/) | Modelos, consultas, páginas e recursos da competição |
| [backend/futebol/management/commands/](backend/futebol/management/commands/) | Comando de atualização da classificação |
| [poc/](poc/) | Scripts de coleta, importação, inspeção e validação |
| [poc/dados/](poc/dados/) | Arquivos JSON incluídos no repositório |
| [poc/sql/](poc/sql/) | Criação das tabelas, consultas de validação e índices |

## Executar localmente

### 1. Preparar o ambiente

É necessário ter Python compatível com as dependências de `requirements.txt`, PostgreSQL e Git instalados. Para novas coletas, também é necessária uma chave da API Highlightly.

```bash
git clone https://github.com/Matheus-Mannarino/Football-Data-Hub.git
cd Football-Data-Hub
python -m venv .venv
```

Ative o ambiente virtual:

**Windows — PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

### 2. Iniciar a aplicação

```bash
cd backend
python manage.py runserver
```

Acesse **http://127.0.0.1:8000/**.

A configuração atual é destinada ao desenvolvimento local.

## Critérios e limitações

- **Sem atualização em tempo real:** os dados refletem a última execução dos processos de coleta e importação.
- **Momentos de atualização diferentes:** classificação e partidas são atualizadas separadamente.
- **Cobertura parcial:** algumas partidas podem não possuir estatísticas individuais coletadas; os totais dos jogadores podem estar incompletos.
- **Ausência não equivale a zero:** a falta de dados não demonstra ausência de produção do atleta.
- **Clubes dos jogadores:** os vínculos representam atuações registradas na temporada, não necessariamente o elenco atual.
- **Comparações:** métricas por 90 minutos devem ser interpretadas considerando posição e tamanho da amostra.
- **Dependência da fonte:** datas, resultados, status e disponibilidade das estatísticas dependem da API e podem sofrer alterações.

## Equipe

Projeto acadêmico desenvolvido por:

- Matheus Mannarino
- João Loss
- Giovanni Vilela
- Pedro Torres
- Antonio Vieira

---

Dados obtidos pela **API Highlightly**. O projeto tem finalidade acadêmica e reúne práticas de banco de dados, desenvolvimento web e análise de dados aplicadas ao futebol.

