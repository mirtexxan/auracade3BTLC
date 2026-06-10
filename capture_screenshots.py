from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "screenshot"
CATALOG_PATH = ROOT / "auracade_games.json"


SITE_HOOK = r'''
import atexit
import os
import time

try:
    import pygame
except Exception:
    pygame = None

_OUTPUT = os.environ.get("AURACADE_CAPTURE_OUTPUT", "").strip()
_CAPTURE_AFTER_MS = int(os.environ.get("AURACADE_CAPTURE_AFTER_MS", "10000"))
_QUIT_AFTER_MS = int(os.environ.get("AURACADE_QUIT_AFTER_MS", "22000"))

_captured = False
_start = time.time()


def _elapsed_ms() -> int:
    return int((time.time() - _start) * 1000)


def _save_if_possible() -> None:
    global _captured
    if _captured or not _OUTPUT or pygame is None:
        return
    if not pygame.get_init() or not pygame.display.get_init():
        return
    surface = pygame.display.get_surface()
    if surface is None:
        return
    try:
        os.makedirs(os.path.dirname(_OUTPUT), exist_ok=True)
        pygame.image.save(surface, _OUTPUT)
        _captured = True
    except Exception:
        pass


def _request_quit() -> None:
    if pygame is None or not pygame.get_init():
        return
    try:
        pygame.event.post(pygame.event.Event(pygame.QUIT))
    except Exception:
        pass


def _on_frame() -> None:
    if _elapsed_ms() >= _CAPTURE_AFTER_MS:
        _save_if_possible()
    if _elapsed_ms() >= _QUIT_AFTER_MS:
        _save_if_possible()
        _request_quit()


if pygame is not None:
    try:
        _orig_flip = pygame.display.flip

        def _patched_flip(*args, **kwargs):
            result = _orig_flip(*args, **kwargs)
            _on_frame()
            return result

        pygame.display.flip = _patched_flip
    except Exception:
        pass

    try:
        _orig_update = pygame.display.update

        def _patched_update(*args, **kwargs):
            result = _orig_update(*args, **kwargs)
            _on_frame()
            return result

        pygame.display.update = _patched_update
    except Exception:
        pass

atexit.register(_save_if_possible)
'''


@dataclass(frozen=True)
class CaptureTarget:
    slug: str
    title: str
    script: Path
    cover: Path


def load_targets() -> list[CaptureTarget]:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8-sig"))
    targets: list[CaptureTarget] = []
    for entry in catalog:
        slug = str(entry["slug"])
        title = str(entry["title"])
        script = ROOT / str(entry["script"])
        cover = ROOT / "auracade_assets" / "covers" / str(entry["cover"])
        targets.append(CaptureTarget(slug=slug, title=title, script=script, cover=cover))
    return targets


def build_env(hook_dir: Path, output_file: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(hook_dir) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    env["AURACADE_CAPTURE_OUTPUT"] = str(output_file)
    env["AURACADE_CAPTURE_AFTER_MS"] = "10000"
    env["AURACADE_QUIT_AFTER_MS"] = "22000"
    return env


def run_capture(command: list[str], cwd: Path, hook_dir: Path, output_file: Path, timeout_sec: int = 20) -> bool:
    env = build_env(hook_dir, output_file)
    process = None
    try:
        process = subprocess.Popen(
            command,
            cwd=str(cwd),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        process.wait(timeout=timeout_sec)
    except subprocess.TimeoutExpired:
        if process is not None:
            try:
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception:
                process.kill()
    except Exception:
        if process is not None:
            try:
                process.kill()
            except Exception:
                pass
    return output_file.exists() and output_file.stat().st_size > 0


def build_reconstructed_image(target: CaptureTarget, output_file: Path) -> bool:
    try:
        import pygame

        pygame.init()
        pygame.font.init()

        width, height = 1366, 768
        surface = pygame.Surface((width, height))
        surface.fill((14, 20, 33))

        if target.cover.exists():
            cover = pygame.image.load(str(target.cover)).convert_alpha()
            cover_rect = cover.get_rect()
            max_w = int(width * 0.62)
            max_h = int(height * 0.72)
            scale = min(max_w / max(1, cover_rect.width), max_h / max(1, cover_rect.height))
            new_size = (max(1, int(cover_rect.width * scale)), max(1, int(cover_rect.height * scale)))
            cover = pygame.transform.smoothscale(cover, new_size)
            cover_pos = (70, (height - new_size[1]) // 2)
            surface.blit(cover, cover_pos)

        panel = pygame.Rect(int(width * 0.72), 90, int(width * 0.24), int(height * 0.76))
        pygame.draw.rect(surface, (24, 35, 58), panel, border_radius=16)
        pygame.draw.rect(surface, (58, 88, 130), panel, width=2, border_radius=16)

        title_font = pygame.font.SysFont("consolas", 34, bold=True)
        body_font = pygame.font.SysFont("consolas", 24)

        y = 130
        for line in wrap_lines(title_font, target.title, 280):
            text = title_font.render(line, True, (231, 245, 255))
            surface.blit(text, (panel.x + 20, y))
            y += 42

        y += 14
        for line in wrap_lines(body_font, "Schermata ricostruita dal codice", 280):
            text = body_font.render(line, True, (150, 200, 230))
            surface.blit(text, (panel.x + 20, y))
            y += 30

        y += 10
        slug_text = body_font.render(f"slug: {target.slug}", True, (255, 181, 82))
        surface.blit(slug_text, (panel.x + 20, y))

        output_file.parent.mkdir(parents=True, exist_ok=True)
        pygame.image.save(surface, str(output_file))
        pygame.quit()
        return True
    except Exception:
        return False


def wrap_lines(font, text: str, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []

    for word in words:
        trial = " ".join(current + [word])
        if font.size(trial)[0] <= max_width:
            current.append(word)
            continue
        if current:
            lines.append(" ".join(current))
        current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    targets = load_targets()

    python = Path(sys.executable)
    runner = ROOT / "auracade_game_runner.py"

    results: list[dict[str, str]] = []

    with tempfile.TemporaryDirectory(prefix="auracade_capture_") as tmp:
        hook_dir = Path(tmp)
        (hook_dir / "sitecustomize.py").write_text(SITE_HOOK, encoding="utf-8")

        launcher_out = OUTPUT_DIR / "auracade_launcher.png"
        if launcher_out.exists() and launcher_out.stat().st_size > 0:
            launcher_ok = True
        else:
            launcher_ok = run_capture([str(python), str(ROOT / "auracade_3btlc.py")], ROOT, hook_dir, launcher_out, timeout_sec=20)
        results.append({
            "slug": "auracade_launcher",
            "title": "AuRaCADE Launcher",
            "status": "real" if launcher_ok else "failed",
            "file": str(launcher_out.name if launcher_ok else ""),
        })

        for target in targets:
            real_out = OUTPUT_DIR / f"{target.slug}.png"
            if real_out.exists() and real_out.stat().st_size > 0:
                ok = True
            else:
                print(f"Catturo: {target.slug}", flush=True)
                ok = run_capture([str(python), str(runner), str(target.script)], target.script.parent, hook_dir, real_out, timeout_sec=20)
            status = "real"
            final_file = real_out
            if not ok:
                recon_out = OUTPUT_DIR / f"{target.slug}_ricostruito.png"
                rec_ok = build_reconstructed_image(target, recon_out)
                status = "reconstructed" if rec_ok else "failed"
                final_file = recon_out if rec_ok else real_out
            results.append({
                "slug": target.slug,
                "title": target.title,
                "status": status,
                "file": final_file.name if final_file.exists() else "",
            })

    report_lines = [
        "# Report screenshot",
        "",
        "Legenda: real = screenshot vero in esecuzione, reconstructed = schermata ricostruita da codice/asset.",
        "",
    ]
    for item in results:
        report_lines.append(f"- {item['slug']}: {item['status']} -> {item['file']}")

    (OUTPUT_DIR / "REPORT.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    real_count = sum(1 for item in results if item["status"] == "real")
    recon_count = sum(1 for item in results if item["status"] == "reconstructed")
    failed_count = sum(1 for item in results if item["status"] == "failed")

    print(f"Screenshot reali: {real_count}")
    print(f"Ricostruiti: {recon_count}")
    print(f"Falliti: {failed_count}")
    print(f"Output: {OUTPUT_DIR}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
