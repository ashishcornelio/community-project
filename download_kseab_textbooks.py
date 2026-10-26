
import asyncio
import csv
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote

import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from tqdm import tqdm

# ============================================================
# CONFIGURATION
# ============================================================

START_URL = "https://textbooks.karnataka.gov.in/textbooks/en"

OUTPUT_DIR = Path("KSEAB_Textbooks")
MANIFEST = OUTPUT_DIR / "download_manifest.csv"

CLASSES = {"8", "9", "10"}

# Choose: "chrome", "brave", or "auto"
BROWSER = "auto"

# Maximum pages visited during discovery.
MAX_PAGES = 100

# Restrict discovery to the official textbook website.
ALLOWED_HOSTS = {
    "textbooks.karnataka.gov.in",
    "ktbs.kar.nic.in",
}

TIMEOUT_MS = 20000
DOWNLOAD_TIMEOUT = 90
MAX_FILE_MB = 300

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
}


# ============================================================
# HELPERS
# ============================================================

def safe_name(value):
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", value)
    value = re.sub(r"\s+", " ", value).strip(" .")
    return value[:140] or "textbook"


def get_class(text):
    text = unquote(text).lower()

    patterns = [
        r"\bclass[\s:_-]*(8|9|10)\b",
        r"\b(8|9|10)(?:st|nd|rd|th)\s*(?:standard|class|grade)\b",
        r"\b(?:standard|grade)[\s:_-]*(8|9|10)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)

    return None


def allowed_url(url):
    parsed = urlparse(url)

    return (
        parsed.scheme in ("http", "https")
        and parsed.hostname in ALLOWED_HOSTS
    )


def is_pdf_url(url):
    return urlparse(url).path.lower().endswith(".pdf")


def infer_subject(label, url):
    text = unquote(label + " " + url).lower()

    subjects = [
        ("social_science", ["social science", "social_science", "socialscience"]),
        ("mathematics", ["mathematics", "maths", "math"]),
        ("science", ["science"]),
        ("english", ["english"]),
        ("kannada", ["kannada"]),
        ("hindi", ["hindi"]),
        ("urdu", ["urdu"]),
        ("marathi", ["marathi"]),
        ("tamil", ["tamil"]),
        ("telugu", ["telugu"]),
        ("sanskrit", ["sanskrit"]),
        ("computer_science", ["computer science", "computer_science"]),
    ]

    for subject, terms in subjects:
        if any(term in text for term in terms):
            return subject

    return "Other"


def load_existing_manifest():
    if not MANIFEST.exists():
        return []

    try:
        with MANIFEST.open(
            "r", newline="", encoding="utf-8-sig"
        ) as f:
            return list(csv.DictReader(f))
    except OSError:
        return []


def save_manifest(rows):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fields = [
        "status", "class", "subject", "title",
        "url", "file", "error"
    ]

    with MANIFEST.open(
        "w", newline="", encoding="utf-8-sig"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


# ============================================================
# BROWSER LAUNCH
# ============================================================

async def launch_browser(playwright):
    choices = (
        ["chrome", "brave"]
        if BROWSER == "auto"
        else [BROWSER]
    )

    for choice in choices:
        try:
            print(f"Trying browser: {choice}", flush=True)

            if choice == "chrome":
                browser = await playwright.chromium.launch(
                    channel="chrome",
                    headless=True,
                )
            elif choice == "brave":
                # Brave may not be recognised as a Playwright
                # channel. Try standard executable paths below.
                paths = [
                    Path.home()
                    / "AppData/Local/BraveSoftware/Brave-Browser/Application/brave.exe",
                    Path("C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"),
                    Path("C:/Program Files (x86)/BraveSoftware/Brave-Browser/Application/brave.exe"),
                ]

                exe = next(
                    (p for p in paths if p.exists()),
                    None
                )

                if exe is None:
                    continue

                browser = await playwright.chromium.launch(
                    executable_path=str(exe),
                    headless=True,
                )
            else:
                raise ValueError(
                    "BROWSER must be chrome, brave, or auto"
                )

            print(f"Using {choice}.", flush=True)
            return browser

        except Exception as exc:
            print(f"{choice} unavailable: {exc}", flush=True)

    raise RuntimeError(
        "Could not launch Chrome or Brave. "
        "Install Google Chrome, or update the Brave executable "
        "path in this script."
    )


# ============================================================
# DISCOVER PDF LINKS
# ============================================================

async def discover_pdfs(page):
    queue = [(START_URL, "", 0)]
    visited = set()
    found = {}

    while queue and len(visited) < MAX_PAGES:
        url, parent_label, depth = queue.pop(0)

        if url in visited or not allowed_url(url):
            continue

        visited.add(url)

        print(
            f"[{len(visited)}/{MAX_PAGES}] {url}",
            flush=True,
        )

        try:
            response = await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=TIMEOUT_MS,
            )

            if response and response.status >= 400:
                print(f"  HTTP {response.status}", flush=True)
                continue

            # Allow a little time for the page to render.
            await page.wait_for_timeout(500)

            current_url = page.url

            if is_pdf_url(current_url):
                found[current_url] = parent_label or current_url
                continue

            links = await page.locator("a").evaluate_all("""
                els => els.map(a => ({
                    text: (
                        a.innerText ||
                        a.getAttribute('aria-label') ||
                        a.title || ''
                    ).trim(),
                    href: a.href
                }))
            """)

            # Include URLs referenced in rendered HTML attributes.
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")

            for tag in soup.find_all(["iframe", "embed", "object"]):
                value = (
                    tag.get("src")
                    or tag.get("data")
                    or ""
                )

                if value:
                    links.append({
                        "text": tag.get("title", "Textbook PDF"),
                        "href": urljoin(current_url, value),
                    })

            for link in links:
                href = link.get("href", "")
                label = link.get("text") or parent_label

                if not href or not allowed_url(href):
                    continue

                if is_pdf_url(href):
                    combined = label + " " + href
                    cls = get_class(combined)

                    # Store only PDFs that can be associated with
                    # the requested classes.
                    if cls in CLASSES:
                        found[href] = label or href

                    continue

                if depth >= 3:
                    continue

                combined = (label + " " + href).lower()

                relevant = (
                    get_class(combined) in CLASSES
                    or any(word in combined for word in [
                        "textbook", "textbooks", "subject",
                        "class", "medium", "download",
                        "standard", "books"
                    ])
                )

                if relevant and href not in visited:
                    queue.append((href, label, depth + 1))

        except Exception as exc:
            print(f"  Page error: {exc}", flush=True)

    print(
        f"\nDiscovery finished: {len(found)} PDF links found.",
        flush=True,
    )

    return found


# ============================================================
# DOWNLOAD PDF FILES
# ============================================================

def download_pdf(session, url, destination):
    if destination.exists() and destination.stat().st_size > 0:
        with destination.open("rb") as f:
            if f.read(5) == b"%PDF-":
                return "ALREADY_EXISTS"

    temporary = destination.with_suffix(".part")

    with session.get(
        url,
        stream=True,
        timeout=DOWNLOAD_TIMEOUT,
        allow_redirects=True,
    ) as response:
        response.raise_for_status()

        content_length = response.headers.get("content-length")
        if content_length:
            size = int(content_length)

            if size > MAX_FILE_MB * 1024 * 1024:
                raise RuntimeError(
                    f"File exceeds {MAX_FILE_MB} MB limit"
                )

        first = True
        total = 0

        with temporary.open("wb") as f:
            for chunk in response.iter_content(128 * 1024):
                if not chunk:
                    continue

                if first:
                    first = False

                    if not chunk.startswith(b"%PDF-"):
                        raise RuntimeError(
                            "Server did not return a PDF file"
                        )

                total += len(chunk)

                if total > MAX_FILE_MB * 1024 * 1024:
                    raise RuntimeError(
                        f"File exceeds {MAX_FILE_MB} MB limit"
                    )

                f.write(chunk)

    temporary.replace(destination)
    return "DOWNLOADED"


# ============================================================
# MAIN
# ============================================================

async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = load_existing_manifest()
    existing_urls = {
        row.get("url")
        for row in results
        if row.get("status") in ("DOWNLOADED", "ALREADY_EXISTS")
    }

    session = requests.Session()
    session.headers.update(HEADERS)

    async with async_playwright() as p:
        browser = await launch_browser(p)
        page = await browser.new_page()

        try:
            pdfs = await discover_pdfs(page)
        finally:
            await browser.close()

    if not pdfs:
        print(
            "\nNo matching PDFs were discovered.",
            "\nThe portal may use dynamic selectors or another host.",
            "\nOpen the textbook portal manually in Chrome or Brave:",
            f"\n{START_URL}",
            flush=True,
        )
        save_manifest(results)
        return

    for url, title in tqdm(
        pdfs.items(),
        desc="Downloading textbooks",
        unit="file",
    ):
        if url in existing_urls:
            continue

        cls = get_class(title + " " + url)

        if cls not in CLASSES:
            results.append({
                "status": "CLASS_UNKNOWN",
                "class": "",
                "subject": infer_subject(title, url),
                "title": title,
                "url": url,
                "file": "",
                "error": "Could not infer class from label or URL",
            })
            continue

        subject = infer_subject(title, url)
        folder = OUTPUT_DIR / f"Class_{cls}" / subject
        folder.mkdir(parents=True, exist_ok=True)

        filename = safe_name(title)

        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"

        destination = folder / filename

        if destination.exists():
            destination = folder / (
                destination.stem + "_2.pdf"
            )

        try:
            status = download_pdf(session, url, destination)

            results.append({
                "status": status,
                "class": cls,
                "subject": subject,
                "title": title,
                "url": url,
                "file": str(destination),
                "error": "",
            })

            print(f"\n{status}: {destination}", flush=True)

        except Exception as exc:
            results.append({
                "status": "FAILED",
                "class": cls,
                "subject": subject,
                "title": title,
                "url": url,
                "file": "",
                "error": str(exc),
            })

            print(f"\nFAILED: {url}\n  {exc}", flush=True)

        save_manifest(results)
        time.sleep(0.2)

    session.close()

    save_manifest(results)

    print("\nAll tasks finished.")
    print(f"Output folder: {OUTPUT_DIR.resolve()}")
    print(f"Manifest: {MANIFEST.resolve()}")
    print(
        "Review the manifest to identify missing classes, "
        "subjects, or failed downloads."
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(
            "\nStopped by user. Completed downloads are preserved.",
            flush=True,
        )
        sys.exit(1)
    except Exception as exc:
        print(f"\nFatal error: {exc}", flush=True)
        sys.exit(1)
