"""
Descarrega os CSVs da Serie A a partir de football-data.co.uk, uma época
de cada vez, e guarda-os sem alterações em data/raw/.

Decisões importantes:
- Guardamos os bytes tal como vêm do servidor (sem parsear/decodificar),
  para não arriscar corromper nada antes de sequer olharmos para o schema.
  A limpeza/parsing fica para preprocessing.py (fase seguinte).
- Cada época é tentada de forma isolada (try/except); se uma falhar
  (ex.: época 2025/26 ainda incompleta, ou ainda não publicada), as
  restantes continuam a ser descarregadas.
- Idempotente: se o ficheiro já existe, salta o download (usa --force para
  forçar re-download, útil para atualizar a época em curso).
"""

import sys
from pathlib import Path

import requests

try:
    from src.config import ALL_SEASONS, DATA_RAW_DIR, FOOTBALL_DATA_URL_TEMPLATE, LEAGUE_CODE
except ImportError:
    from config import ALL_SEASONS, DATA_RAW_DIR, FOOTBALL_DATA_URL_TEMPLATE, LEAGUE_CODE

REQUEST_TIMEOUT_SECONDS = 15
# Uma resposta "de erro" do football-data.co.uk costuma ser uma página HTML
# pequena, não um 404 normal. Um CSV real de uma época tem várias centenas
# de jogos, por isso um ficheiro suspeitosamente pequeno é sinal de que a
# época ainda não está disponível.
MIN_VALID_CONTENT_BYTES = 1000


def download_season(
    season: str,
    league: str = LEAGUE_CODE,
    dest_dir: Path = DATA_RAW_DIR,
    force: bool = False,
) -> bool:
    """Descarrega o CSV de uma época. Devolve True em sucesso, False caso contrário."""
    url = FOOTBALL_DATA_URL_TEMPLATE.format(season=season, league=league)
    dest_path = dest_dir / f"{league}_{season}.csv"

    if dest_path.exists() and not force:
        print(f"[skip] {dest_path.name} já existe")
        return True

    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        print(f"[falhou] época {season}: {exc}")
        return False

    if len(response.content) < MIN_VALID_CONTENT_BYTES:
        print(f"[aviso] época {season}: resposta demasiado pequena ({len(response.content)} bytes) — a ignorar")
        return False

    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path.write_bytes(response.content)
    print(f"[ok] {dest_path.name} ({len(response.content)} bytes)")
    return True


def download_all_seasons(force: bool = False) -> dict[str, bool]:
    """Descarrega todas as épocas definidas em config.ALL_SEASONS."""
    results: dict[str, bool] = {}
    for season in ALL_SEASONS:
        results[season] = download_season(season, force=force)
    return results


def main() -> None:
    force = "--force" in sys.argv
    results = download_all_seasons(force=force)

    ok = [s for s, success in results.items() if success]
    failed = [s for s, success in results.items() if not success]

    print("\n--- Resumo ---")
    print(f"Sucesso: {len(ok)}/{len(results)} épocas")
    if failed:
        print(f"Falharam: {failed}")


if __name__ == "__main__":
    main()
