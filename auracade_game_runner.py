from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path


def _safe_window_size(requested: tuple[int, int]) -> tuple[int, int]:
    import pygame

    if not pygame.display.get_init():
        pygame.display.init()
    info = pygame.display.Info()
    max_width = max(960, info.current_w - 160)
    max_height = max(540, info.current_h - 160)
    width, height = requested
    if width <= 0 or height <= 0:
        return min(1280, max_width), min(720, max_height)
    if width >= info.current_w or height >= info.current_h:
        return min(width, max_width), min(height, max_height)
    return width, height


def patch_pygame() -> None:
    import pygame

    original_set_mode = pygame.display.set_mode
    original_event_get = pygame.event.get
    original_event_wait = pygame.event.wait
    original_event_poll = pygame.event.poll

    def patched_set_mode(size, flags=0, depth=0, display=0, vsync=0):
        safe_size = _safe_window_size(size)
        cleaned_flags = flags & ~pygame.FULLSCREEN
        return original_set_mode(safe_size, cleaned_flags, depth, display, vsync)

    def add_quit_on_escape(events):
        result = list(events)
        if any(event.type == pygame.KEYDOWN and getattr(event, "key", None) == pygame.K_ESCAPE for event in result):
            result.append(pygame.event.Event(pygame.QUIT))
        return result

    def patched_event_get(*args, **kwargs):
        return add_quit_on_escape(original_event_get(*args, **kwargs))

    def patched_event_wait(*args, **kwargs):
        event = original_event_wait(*args, **kwargs)
        if event.type == pygame.KEYDOWN and getattr(event, "key", None) == pygame.K_ESCAPE:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        return event

    def patched_event_poll(*args, **kwargs):
        event = original_event_poll(*args, **kwargs)
        if event.type == pygame.KEYDOWN and getattr(event, "key", None) == pygame.K_ESCAPE:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        return event

    pygame.display.set_mode = patched_set_mode
    pygame.event.get = patched_event_get
    pygame.event.wait = patched_event_wait
    pygame.event.poll = patched_event_poll


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) < 1:
        print("Uso: auracade_game_runner.py <script_gioco>")
        return 2
    script_path = Path(args[0]).resolve()
    if not script_path.exists():
        print(f"Gioco non trovato: {script_path}")
        return 2

    os.chdir(script_path.parent)
    sys.path.insert(0, str(script_path.parent))
    patch_pygame()

    try:
        runpy.run_path(str(script_path), run_name="__main__")
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 0
        return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())