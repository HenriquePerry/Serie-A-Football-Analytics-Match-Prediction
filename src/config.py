"""
Configuração central do projeto: caminhos e parâmetros partilhados por todos
os scripts (data_collection, preprocessing, features, train, predict).

Mantém-se tudo num único sítio para evitar strings "mágicas" espalhadas pelo
código (ex.: "I1", caminhos de pastas) — se algo mudar (ex.: mudar de liga),
muda-se aqui uma vez só.
"""

from pathlib import Path

# --- Caminhos -----------------------------------------------------------
# BASE_DIR = raiz do projeto (pasta que contém src/, data/, etc.).
# Calculado a partir deste ficheiro para funcionar independentemente de onde
# o script é chamado (não depende do "current working directory").
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"
MODELS_DIR = BASE_DIR / "models"

# --- Fonte de dados -------------------------------------------------------
LEAGUE_CODE = "I1"  # Serie A em football-data.co.uk

FOOTBALL_DATA_URL_TEMPLATE = "https://www.football-data.co.uk/mmz4281/{season}/{league}.csv"

# --- Épocas -----------------------------------------------------------
# Formato usado pelo football-data.co.uk: "1516" para a época 2015/16.
def _season_code(start_year: int) -> str:
    """Converte o ano de início da época (ex.: 2015) no código 'AAAA' (ex.: '1516')."""
    end_year = start_year + 1
    return f"{start_year % 100:02d}{end_year % 100:02d}"


# 2015/16 é só "warm-up": serve para calcular rolling stats (ex.: forma das
# equipas nos últimos N jogos) no início da época 2016/17, mas não entra
# como jogos a prever/avaliar no modelo.
WARMUP_SEASON = _season_code(2015)

# 2016/17 a 2025/26: dataset de modelação (~3.800 jogos).
MODEL_SEASONS = [_season_code(year) for year in range(2016, 2026)]

# Todas as épocas a descarregar (warm-up + modelação).
ALL_SEASONS = [WARMUP_SEASON] + MODEL_SEASONS
