from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pygame

from auracade_audio import LauncherMusic
from auracade_game_runner import main as runner_main
from auracade_config import ABOUT_HINT
from auracade_config import ABOUT_PARAGRAPHS
from auracade_config import APP_SUBTITLE
from auracade_config import APP_TITLE
from auracade_config import BASE_DIR
from auracade_config import CATALOG_PATH
from auracade_config import COVER_DIR
from auracade_config import CURATION_CREDITS
from auracade_config import DEFAULT_STATUS
from auracade_config import GAME_RUNNER_PATH
from auracade_config import IS_FROZEN
from auracade_config import SHORTCUTS_HINT
from auracade_config import STUDENT_CREDITS
from auracade_config import THEME


RUN_GAME_FLAG = "--run-game"


@dataclass(frozen=True)
class GameInfo:
    slug: str
    title: str
    authors_label: str
    authors_full: tuple[str, ...]
    genre: str
    script: Path
    doc: Path
    cover: Path
    description: str
    summary: tuple[str, ...]
    features: tuple[str, ...]
    controls: tuple[str, ...]


def load_games() -> tuple[GameInfo, ...]:
    raw_catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8-sig"))
    games: list[GameInfo] = []
    for entry in raw_catalog:
        games.append(
            GameInfo(
                slug=str(entry["slug"]),
                title=str(entry["title"]),
                authors_label=str(entry["authors_label"]),
                authors_full=tuple(str(value) for value in entry["authors_full"]),
                genre=str(entry["genre"]),
                script=BASE_DIR / str(entry["script"]),
                doc=BASE_DIR / str(entry["doc"]),
                cover=COVER_DIR / str(entry["cover"]),
                description=str(entry["description"]),
                summary=tuple(str(value) for value in entry["summary"]),
                features=tuple(str(value) for value in entry["features"]),
                controls=tuple(str(value) for value in entry["controls"]),
            )
        )
    return tuple(games)


def draw_text(
    surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    color: tuple[int, int, int],
    pos: tuple[int, int],
    *,
    center: bool = False,
) -> pygame.Rect:
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surface.blit(rendered, rect)
    return rect


def wrap_text(font: pygame.font.Font, text: str, width: int) -> list[str]:
    words = text.replace("\r", " ").replace("\n", " \n ").split()
    lines: list[str] = []
    current = ""
    for word in words:
        if word == "\\n":
            if current.strip():
                lines.append(current.rstrip())
            current = ""
            continue
        test = word if not current else f"{current} {word}"
        if font.size(test)[0] <= width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return [line for line in lines if line.strip()]


def draw_gradient(surface: pygame.Surface) -> None:
    width, height = surface.get_size()
    for y in range(height):
        t = y / max(1, height - 1)
        color = (
            int(THEME.bg_top[0] + (THEME.bg_bottom[0] - THEME.bg_top[0]) * t),
            int(THEME.bg_top[1] + (THEME.bg_bottom[1] - THEME.bg_top[1]) * t),
            int(THEME.bg_top[2] + (THEME.bg_bottom[2] - THEME.bg_top[2]) * t),
        )
        pygame.draw.line(surface, color, (0, y), (width, y))


def draw_stars(surface: pygame.Surface, stars: list[dict[str, float]], elapsed: float) -> None:
    for star in stars:
        blink = 0.35 + 0.65 * abs(math.sin(elapsed * star["speed"] + star["phase"]))
        color = (
            int(40 + 110 * blink),
            int(100 + 120 * blink),
            int(130 + 110 * blink),
        )
        pygame.draw.circle(surface, color, (int(star["x"]), int(star["y"])), int(star["size"]))


def draw_scanline_overlay(surface: pygame.Surface) -> None:
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    for y in range(0, surface.get_height(), 4):
        pygame.draw.line(overlay, (0, 0, 0, 20), (0, y), (surface.get_width(), y))
    surface.blit(overlay, (0, 0))


def load_cover_image(cache: dict[Path, pygame.Surface], path: Path, size: tuple[int, int]) -> pygame.Surface | None:
    if path in cache:
        return cache[path]
    if not path.exists():
        return None
    try:
        image = pygame.image.load(str(path)).convert_alpha()
        image = pygame.transform.smoothscale(image, size)
        cache[path] = image
        return image
    except Exception:
        return None


def draw_cover_panel(
    surface: pygame.Surface,
    current: GameInfo,
    cover_cache: dict[Path, pygame.Surface],
    body_font: pygame.font.Font,
    small_font: pygame.font.Font,
) -> None:
    cover_rect = pygame.Rect(940, 146, 348, 196)
    pygame.draw.rect(surface, (12, 16, 26), cover_rect, border_radius=16)
    pygame.draw.rect(surface, THEME.line, cover_rect, 2, border_radius=16)
    image = load_cover_image(cover_cache, current.cover, (cover_rect.width - 12, cover_rect.height - 12))
    if image is not None:
        surface.blit(image, (cover_rect.x + 6, cover_rect.y + 6))
    else:
        draw_text(surface, body_font, "Copertina non disponibile", THEME.text_soft, (cover_rect.x + 34, cover_rect.y + 80))
        draw_text(surface, small_font, current.cover.name, THEME.text_soft, (cover_rect.x + 34, cover_rect.y + 112))


def draw_overlay_frame(surface: pygame.Surface, title_font: pygame.font.Font, small_font: pygame.font.Font, title: str, subtitle: str) -> pygame.Rect:
    veil = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    veil.fill((4, 8, 16, 210))
    surface.blit(veil, (0, 0))
    frame = pygame.Rect(84, 58, 1198, 648)
    pygame.draw.rect(surface, THEME.panel, frame, border_radius=18)
    pygame.draw.rect(surface, THEME.accent, frame, 2, border_radius=18)
    draw_text(surface, title_font, title, THEME.text, (112, 88))
    draw_text(surface, small_font, subtitle, THEME.text_soft, (114, 130))
    return frame


def draw_splash_screen(
    surface: pygame.Surface,
    elapsed: float,
    title_font: pygame.font.Font,
    section_font: pygame.font.Font,
    body_font: pygame.font.Font,
    small_font: pygame.font.Font,
) -> None:
    draw_gradient(surface)
    glow = 0.55 + 0.45 * abs(math.sin(elapsed * 1.8))
    center_x = surface.get_width() // 2
    center_y = surface.get_height() // 2
    halo = pygame.Surface((640, 320), pygame.SRCALPHA)
    pygame.draw.ellipse(halo, (0, 232, 192, int(70 * glow)), halo.get_rect())
    surface.blit(halo, (center_x - 320, center_y - 160))

    frame = pygame.Rect(170, 120, 1026, 500)
    pygame.draw.rect(surface, (12, 18, 28), frame, border_radius=28)
    pygame.draw.rect(surface, THEME.accent, frame, 3, border_radius=28)

    draw_text(surface, title_font, APP_TITLE, THEME.text, (center_x, 218), center=True)
    draw_text(surface, section_font, "Cabinet arcade della 3BTLC", THEME.accent_alt, (center_x, 282), center=True)
    draw_text(surface, body_font, "Launcher curato per mostrare, avviare e contestualizzare i progetti finali Pygame della classe.", THEME.text_soft, (center_x, 340), center=True)
    draw_text(surface, body_font, "I giochi partono in finestra normale e la musica del launcher si sospende durante l'esecuzione.", THEME.text_soft, (center_x, 376), center=True)
    draw_text(surface, small_font, "ENTER o SPAZIO per entrare  |  C per credits  |  ESC per uscire", THEME.text, (center_x, 466), center=True)
    draw_text(surface, small_font, APP_SUBTITLE, THEME.text_soft, (center_x, 542), center=True)


def draw_active_game_badge(
    surface: pygame.Surface,
    body_font: pygame.font.Font,
    small_font: pygame.font.Font,
    game_title: str,
    elapsed: float,
) -> None:
    pulse = 0.55 + 0.45 * abs(math.sin(elapsed * 2.6))
    badge = pygame.Rect(894, 62, 392, 58)
    fill = (int(28 + 18 * pulse), int(74 + 50 * pulse), int(56 + 22 * pulse))
    pygame.draw.rect(surface, fill, badge, border_radius=16)
    pygame.draw.rect(surface, THEME.accent, badge, 2, border_radius=16)
    draw_text(surface, small_font, "IN ESECUZIONE", THEME.text, (badge.x + 18, badge.y + 10))
    title = game_title if len(game_title) <= 32 else f"{game_title[:29]}..."
    draw_text(surface, body_font, title, THEME.text, (badge.x + 18, badge.y + 28))
    indicator_x = badge.right - 34
    indicator_y = badge.y + badge.height // 2
    pygame.draw.circle(surface, (16, 26, 18), (indicator_x, indicator_y), 11)
    pygame.draw.circle(surface, (120, 255, 170), (indicator_x, indicator_y), int(5 + 3 * pulse))


def draw_summary_overlay(
    surface: pygame.Surface,
    title_font: pygame.font.Font,
    body_font: pygame.font.Font,
    small_font: pygame.font.Font,
    current: GameInfo,
    scroll: int,
) -> int:
    frame = draw_overlay_frame(surface, title_font, small_font, f"Scheda gioco: {current.title}", "Su/giu scorri  |  O apre il PDF esterno  |  ESC chiude")
    text_area = pygame.Rect(frame.x + 24, frame.y + 118, frame.width - 48, frame.height - 150)
    pygame.draw.rect(surface, (12, 18, 28), text_area, border_radius=12)
    pygame.draw.rect(surface, THEME.line, text_area, 1, border_radius=12)

    lines: list[tuple[str, tuple[int, int, int]]] = []
    lines.append((current.genre, THEME.accent_alt))
    lines.append(("", THEME.text))
    for paragraph in current.summary:
        for line in wrap_text(body_font, paragraph, text_area.width - 36):
            lines.append((line, THEME.text))
        lines.append(("", THEME.text))

    lines.append(("Autori riconosciuti:", THEME.accent))
    for author in current.authors_full:
        lines.append((f"- {author}", THEME.text))
    lines.append(("", THEME.text))
    lines.append(("Percorso di uscita uniformato:", THEME.accent))
    lines.append(("- X finestra: chiusura standard Pygame", THEME.text))
    lines.append(("- Esc: il wrapper del launcher forza un evento di uscita", THEME.text))
    lines.append(("- Il launcher muta la musica finche il gioco resta aperto", THEME.text))

    visible_lines = 18
    max_scroll = max(0, len(lines) - visible_lines)
    scroll = max(0, min(scroll, max_scroll))
    for index, (line, color) in enumerate(lines[scroll : scroll + visible_lines]):
        draw_text(surface, body_font, line, color, (text_area.x + 18, text_area.y + 16 + index * 28))

    if max_scroll > 0:
        draw_text(surface, small_font, f"Righe {scroll + 1}-{min(scroll + visible_lines, len(lines))} di {len(lines)}", THEME.accent_alt, (text_area.right - 190, text_area.bottom - 30))
    return max_scroll


def draw_about_overlay(
    surface: pygame.Surface,
    title_font: pygame.font.Font,
    body_font: pygame.font.Font,
    small_font: pygame.font.Font,
    scroll: int,
) -> int:
    frame = draw_overlay_frame(surface, title_font, small_font, "About / Credits", "ESC chiude")
    text_area = pygame.Rect(frame.x + 24, frame.y + 118, frame.width - 48, frame.height - 150)
    pygame.draw.rect(surface, (12, 18, 28), text_area, border_radius=12)
    pygame.draw.rect(surface, THEME.line, text_area, 1, border_radius=12)

    intro_y = text_area.y + 18
    for paragraph in ABOUT_PARAGRAPHS:
        for line in wrap_text(body_font, paragraph, text_area.width - 40):
            draw_text(surface, body_font, line, THEME.text, (text_area.x + 18, intro_y))
            intro_y += 26
        intro_y += 8

    divider_y = intro_y + 4
    pygame.draw.line(surface, THEME.line, (text_area.x + 18, divider_y), (text_area.right - 18, divider_y), 1)

    student_title_y = divider_y + 22
    draw_text(surface, title_font, "I protagonisti", THEME.accent_alt, (text_area.x + 18, student_title_y))

    left_x = text_area.x + 24
    right_x = text_area.centerx + 18
    list_y = student_title_y + 50
    row_height = 22
    half = (len(STUDENT_CREDITS) + 1) // 2
    left_students = STUDENT_CREDITS[:half]
    right_students = STUDENT_CREDITS[half:]

    for index, item in enumerate(left_students):
        draw_text(surface, body_font, f"- {item}", THEME.text, (left_x, list_y + index * row_height))
    for index, item in enumerate(right_students):
        draw_text(surface, body_font, f"- {item}", THEME.text, (right_x, list_y + index * row_height))

    cur_y = text_area.bottom - 82
    pygame.draw.line(surface, THEME.line, (text_area.x + 18, cur_y - 18), (text_area.right - 18, cur_y - 18), 1)
    draw_text(surface, small_font, "Curatela", THEME.accent, (text_area.x + 18, cur_y))
    for index, item in enumerate(CURATION_CREDITS):
        draw_text(surface, small_font, item, THEME.text, (text_area.x + 18, cur_y + 24 + index * 20))
    draw_text(surface, small_font, ABOUT_HINT, THEME.text_soft, (text_area.right - 410, text_area.bottom - 30))
    return 0


def status_color(message: str) -> tuple[int, int, int]:
    lowered = message.lower()
    if "avviato" in lowered or "aperto" in lowered or "attive" in lowered or "tornato" in lowered:
        return THEME.accent
    if "fall" in lowered or "manc" in lowered or "non disponibile" in lowered or "gia in esecuzione" in lowered:
        return THEME.warn
    return THEME.text_soft


def open_path(path: Path) -> str:
    if not path.exists():
        return f"Percorso mancante: {path.name}"
    try:
        os.startfile(path)  # type: ignore[attr-defined]
        return f"Aperto: {path.name}"
    except Exception as exc:
        return f"Apertura fallita: {exc}"


def launch_game(entry: GameInfo) -> tuple[subprocess.Popen[str] | None, str]:
    if not entry.script.exists():
        return None, f"File non trovato: {entry.script.name}"
    if not IS_FROZEN and not GAME_RUNNER_PATH.exists():
        return None, "Runner giochi mancante: auracade_game_runner.py"

    try:
        command = [sys.executable, RUN_GAME_FLAG, str(entry.script)] if IS_FROZEN else [sys.executable, str(GAME_RUNNER_PATH), str(entry.script)]
        process = subprocess.Popen(
            command,
            cwd=str(entry.script.parent),
            text=True,
        )
        return process, f"Avviato: {entry.title}"
    except Exception as exc:
        return None, f"Avvio fallito: {exc}"


def main() -> None:
    games = load_games()

    pygame.init()
    pygame.display.set_caption(APP_TITLE)
    screen = pygame.display.set_mode(THEME.window_size)
    clock = pygame.time.Clock()

    title_font = pygame.font.SysFont("consolas", 50, bold=True)
    section_font = pygame.font.SysFont("consolas", 24, bold=True)
    body_font = pygame.font.SysFont("consolas", 19)
    small_font = pygame.font.SysFont("consolas", 15)

    music = LauncherMusic()

    stars = []
    for i in range(120):
        stars.append(
            {
                "x": (i * 113) % THEME.window_size[0],
                "y": ((i * 197) % (THEME.window_size[1] - 100)) + 30,
                "size": 1 + (i % 3),
                "phase": (i % 17) * 0.37,
                "speed": 0.5 + (i % 7) * 0.11,
            }
        )

    cover_cache: dict[Path, pygame.Surface] = {}
    selected = 0
    summary_open = False
    about_open = False
    summary_scroll = 0
    about_scroll = 0
    active_process: subprocess.Popen[str] | None = None
    active_game_title = ""
    last_status = DEFAULT_STATUS
    splash_open = True
    running = True

    while running:
        clock.tick(THEME.fps)
        elapsed = pygame.time.get_ticks() / 1000.0
        current = games[selected]

        if active_process is not None and active_process.poll() is not None:
            exit_code = active_process.returncode or 0
            active_process = None
            music.resume_after_game()
            last_status = f"Tornato al launcher da {active_game_title} (codice {exit_code})"
            active_game_title = ""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if splash_open:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        splash_open = False
                        last_status = DEFAULT_STATUS
                    elif event.key == pygame.K_c:
                        splash_open = False
                        about_open = True
                        about_scroll = 0
                        last_status = "About / Credits aperti"
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                elif about_open:
                    max_scroll = draw_about_overlay(screen, section_font, body_font, small_font, about_scroll)
                    if event.key == pygame.K_ESCAPE:
                        about_open = False
                        about_scroll = 0
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        about_scroll = max(0, about_scroll - 1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        about_scroll = min(max_scroll, about_scroll + 1)
                elif summary_open:
                    max_scroll = draw_summary_overlay(screen, section_font, body_font, small_font, current, summary_scroll)
                    if event.key == pygame.K_ESCAPE:
                        summary_open = False
                        summary_scroll = 0
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        summary_scroll = max(0, summary_scroll - 1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        summary_scroll = min(max_scroll, summary_scroll + 1)
                    elif event.key == pygame.K_o:
                        last_status = open_path(current.doc)
                else:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        selected = (selected + 1) % len(games)
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        selected = (selected - 1) % len(games)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if active_process is not None and active_process.poll() is None:
                            last_status = "Un gioco e gia in esecuzione: chiudilo prima di avviarne un altro."
                        else:
                            process, status = launch_game(current)
                            last_status = status
                            if process is not None:
                                active_process = process
                                active_game_title = current.title
                                music.suspend_for_game()
                    elif event.key == pygame.K_o:
                        last_status = open_path(current.doc)
                    elif event.key == pygame.K_p:
                        summary_open = True
                        summary_scroll = 0
                        last_status = f"Scheda aperta: {current.title}"
                    elif event.key == pygame.K_f:
                        last_status = open_path(current.script.parent)
                    elif event.key == pygame.K_m:
                        last_status = music.toggle()
                    elif event.key == pygame.K_c:
                        about_open = True
                        about_scroll = 0
                        last_status = "About / Credits aperti"

        music.tick()

        current = games[selected]
        draw_gradient(screen)
        draw_stars(screen, stars, elapsed)

        left_panel = pygame.Rect(40, 118, 450, 580)
        right_panel = pygame.Rect(520, 118, 806, 580)
        pygame.draw.rect(screen, THEME.panel, left_panel, border_radius=18)
        pygame.draw.rect(screen, THEME.panel_alt, right_panel, border_radius=18)
        pygame.draw.rect(screen, THEME.line, left_panel, 2, border_radius=18)
        pygame.draw.rect(screen, THEME.line, right_panel, 2, border_radius=18)

        draw_text(screen, title_font, APP_TITLE, THEME.text, (40, 32))
        draw_text(screen, small_font, APP_SUBTITLE, THEME.text_soft, (44, 88))
        draw_text(screen, small_font, f"Curati nel launcher: {len(games)} giochi finali", THEME.accent_alt, (1040, 44))

        draw_text(screen, section_font, "Collezione", THEME.accent, (62, 140))

        list_top = 166
        item_h = 36
        for index, entry in enumerate(games):
            y = list_top + index * item_h
            row_rect = pygame.Rect(58, y - 3, 414, 30)
            if index == selected:
                pygame.draw.rect(screen, (20, 78, 88), row_rect, border_radius=8)
                pygame.draw.rect(screen, THEME.glow, row_rect, 2, border_radius=8)
                draw_text(screen, body_font, f"> {entry.title}", THEME.text, (70, y))
            else:
                draw_text(screen, body_font, f"  {entry.title}", THEME.text_soft, (70, y))

        draw_text(screen, section_font, current.title, THEME.text, (548, 146))
        draw_text(screen, body_font, current.authors_label, THEME.accent_alt, (550, 184))
        draw_text(screen, small_font, current.genre, THEME.text_soft, (550, 214))
        draw_cover_panel(screen, current, cover_cache, body_font, small_font)

        desc_y = 260
        draw_text(screen, small_font, "Mini descrizione", THEME.accent, (550, desc_y))
        for line_index, line in enumerate(wrap_text(body_font, current.description, 350)):
            draw_text(screen, body_font, line, THEME.text, (550, desc_y + 28 + line_index * 24))

        feat_y = 404
        draw_text(screen, small_font, "Caratteristiche", THEME.accent, (550, feat_y))
        for idx, item in enumerate(current.features):
            wrapped = wrap_text(body_font, item, 350)
            for sub_index, line in enumerate(wrapped):
                prefix = "- " if sub_index == 0 else "  "
                draw_text(screen, body_font, prefix + line, THEME.text, (550, feat_y + 26 + idx * 54 + sub_index * 22))

        ctrl_y = 368
        draw_text(screen, small_font, "Tasti / input", THEME.accent_alt, (940, ctrl_y))
        for idx, item in enumerate(current.controls):
            wrapped = wrap_text(body_font, item, 330)
            for sub_index, line in enumerate(wrapped):
                prefix = "- " if sub_index == 0 else "  "
                draw_text(screen, body_font, prefix + line, THEME.text, (940, ctrl_y + 28 + idx * 48 + sub_index * 22))

        footer_y = 630
        draw_text(screen, small_font, f"Script: {current.script.relative_to(BASE_DIR)}", THEME.text_soft, (550, footer_y))
        draw_text(screen, small_font, f"Relazione PDF: {current.doc.relative_to(BASE_DIR)}", THEME.text_soft, (550, footer_y + 22))
        draw_text(screen, small_font, SHORTCUTS_HINT, THEME.text_soft, (550, footer_y + 44))
        draw_text(screen, small_font, last_status, status_color(last_status), (44, 724))

        if active_process is not None and active_process.poll() is None:
            draw_text(screen, small_font, "Musica launcher mutata fino alla chiusura del gioco", THEME.accent_alt, (44, 702))
            draw_active_game_badge(screen, body_font, small_font, active_game_title, elapsed)
        else:
            draw_text(screen, small_font, ABOUT_HINT, THEME.text_soft, (44, 702))

        draw_scanline_overlay(screen)

        bar_x = 58 + (math.sin(elapsed * 3.8) * 6)
        pygame.draw.rect(screen, THEME.accent_alt, (bar_x, 197 + selected * item_h, 4, 24), border_radius=3)

        if summary_open:
            draw_summary_overlay(screen, section_font, body_font, small_font, current, summary_scroll)
        if about_open:
            draw_about_overlay(screen, section_font, body_font, small_font, about_scroll)
        if splash_open:
            draw_splash_screen(screen, elapsed, title_font, section_font, body_font, small_font)

        pygame.display.flip()

    music.shutdown()
    pygame.quit()


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == RUN_GAME_FLAG:
        raise SystemExit(runner_main([sys.argv[2]]))
    main()
