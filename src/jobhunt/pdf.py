from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

BINARY_NAMES = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "msedge"]

PLATFORM_PATHS = {
    "darwin": [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    ],
    "win32": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ],
}


class PdfError(Exception):
    pass


def find_chrome() -> str | None:
    env = os.environ.get("JOBHUNT_CHROME")
    if env:
        return env if Path(env).exists() or shutil.which(env) else None
    for name in BINARY_NAMES:
        found = shutil.which(name)
        if found:
            return found
    for candidate in PLATFORM_PATHS.get(sys.platform, []):
        if Path(candidate).exists():
            return candidate
    return None


def html_to_pdf(html_path: Path, pdf_path: Path, chrome: str | None = None) -> None:
    chrome = chrome or find_chrome()
    if not chrome:
        raise PdfError("No Chrome/Chromium/Edge found. Install one or set JOBHUNT_CHROME=/path/to/browser.")
    args = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        html_path.resolve().as_uri(),
    ]
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        args.insert(1, "--no-sandbox")
    try:
        subprocess.run(args, check=True, capture_output=True, timeout=90)
    except subprocess.CalledProcessError as exc:
        raise PdfError(
            f"Browser failed to print {html_path.name}: {exc.stderr.decode(errors='ignore')[:400]}"
        ) from exc
    except subprocess.TimeoutExpired:
        raise PdfError(f"Browser timed out printing {html_path.name}") from None
    if not pdf_path.exists():
        raise PdfError(f"Browser exited without writing {pdf_path}")


def page_count(pdf_path: Path) -> int:
    if shutil.which("pdfinfo"):
        out = subprocess.run(["pdfinfo", str(pdf_path)], capture_output=True, text=True).stdout
        for line in out.splitlines():
            if line.startswith("Pages:"):
                return int(line.split()[-1])
    data = pdf_path.read_bytes()
    counts = [int(n) for n in re.findall(rb"/Type\s*/Pages\b[^>]*?/Count\s+(\d+)", data)]
    if counts:
        return max(counts)
    return len(re.findall(rb"/Type\s*/Page(?![a-zA-Z])", data))
