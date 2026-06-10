from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path


IS_FROZEN = getattr(sys, "frozen", False)
BASE_DIR = Path(sys.executable).resolve().parent if IS_FROZEN else Path(__file__).resolve().parent
ASSET_DIR = BASE_DIR / "auracade_assets"
COVER_DIR = ASSET_DIR / "covers"
CATALOG_PATH = BASE_DIR / "auracade_games.json"
GAME_RUNNER_PATH = BASE_DIR / "auracade_game_runner.py"


@dataclass(frozen=True)
class Theme:
    window_size: tuple[int, int] = (1366, 768)
    fps: int = 60
    bg_top: tuple[int, int, int] = (10, 16, 28)
    bg_bottom: tuple[int, int, int] = (31, 19, 17)
    panel: tuple[int, int, int] = (18, 24, 38)
    panel_alt: tuple[int, int, int] = (28, 35, 52)
    text: tuple[int, int, int] = (236, 244, 255)
    text_soft: tuple[int, int, int] = (157, 182, 205)
    accent: tuple[int, int, int] = (0, 232, 192)
    accent_alt: tuple[int, int, int] = (255, 170, 56)
    warn: tuple[int, int, int] = (255, 103, 103)
    line: tuple[int, int, int] = (54, 74, 105)
    glow: tuple[int, int, int] = (59, 255, 224)


THEME = Theme()
APP_TITLE = "AuRaCADE 3BTLC"
APP_SUBTITLE = "Cabinato console per i progetti Pygame della 3BTLC"
DEFAULT_STATUS = "ENTER: avvia | P: scheda | O: PDF esterno | F: cartella | C: credits | M: musica | ESC: esci"
SHORTCUTS_HINT = "ENTER avvia  |  P apre la scheda del gioco  |  O apre la relazione PDF fuori da AuRaCADE"
ABOUT_HINT = "C: About  |  ESC: chiudi / esci"

ABOUT_PARAGRAPHS = (
    "AuRaCADE 3BTLC raccoglie i progetti finali Pygame della classe in un cabinet unico.",
)

CURATION_CREDITS = (
    "Prof. Mirto Musci - idea e curatela del cabinet",
)

STUDENT_CREDITS = (
    "M Tashriful Alom",
    "Diego Anostini",
    "Christian Cipriano",
    "Roberto Carlo Apeno Cisneros",
    "Samuel Alvaro Baldeon Obregon",
    "Polina Bondar",
    "Alessandro Chiloti",
    "Angelo Alessio Condori Lopez",
    "Giulia Anna Di Canio",
    "Mohamed El Sayed Ahmed El Halawti",
    "Massimo Epifani",
    "Davide Geroli",
    "Sofiia Grygoryshena",
    "Nimmi Natasha Liyanage Perera",
    "Andrea Lopez",
    "Federico Marku",
    "Tharuth Deshan Perera Mathota Arachchige",
    "Samuele Quirino",
    "Lorenzo Rondi",
    "Rameen Sohail",
    "Valerio Zago",
)