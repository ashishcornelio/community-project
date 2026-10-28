
"""
Download Karnataka State Board textbooks for Classes 8, 9 and 10.

Core subjects:
    Mathematics, Science, Social Science
    -> English, Hindi and Kannada mediums only.

Language subjects:
    English, Kannada and Hindi
    -> First, Second and Third Language books where available.

Output:
    text books/
        class 8th/
        class 9th/
        class 10/
        manifest.csv

Install:
    py -m pip install requests beautifulsoup4
"""

import csv
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

BASE_URL = "https://karnatakatextbooks.in"

OUTPUT_DIR = Path.cwd() / "text books"
MANIFEST_PATH = OUTPUT_DIR / "manifest.csv"

CLASS_PAGES = {
    8: f"{BASE_URL}/class-8/",
    9: f"{BASE_URL}/class-9/",
    10: f"{BASE_URL}/class-10/",
}

# Core subjects must be downloaded in these mediums only.
ALLOWED_CORE_MEDIUMS = {
    "english-medium",
    "hindi-medium",
    "kannada-medium",
}

CORE_SUBJECTS = {
    "Maths": ["MATHEMATICS", "MATHS", "GANITA"],
    "Science": ["SCIENCE", "VIJNAANA", "VIGYAN"],
    "Social": [
        "SOCIAL SCIENCE",
        "SOCIAL STUDIES",
        "SOCIAL SCIENCES",
    ],
}

LANGUAGE_SUBJECTS = {
    "English": ["ENGLISH"],
    "Kannada": ["KANNADA"],
    "Hindi": ["HINDI"],
}

LANGUAGE_LEVELS = [
    "FIRST LANGUAGE",
    "SECOND LANGUAGE",
    "THIRD LANGUAGE",
    "FIRST-LANGUAGE",
    "SECOND-LANGUAGE",
    "THIRD-LANGUAGE",
    "FL",
    "SL",
    "TL",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/130.0.0.0 Safari/537.36"
    )
}

REQUEST_DELAY = 0.3

session = requests.Session()
session.headers.update(HEADERS)


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def normalize(text):
    """Normalize text for matching."""
    return re.sub(r"[^A-Z0-9]+", " ", text.upper()).strip()


def clean_filename(text, max_length=150):
    """Create a Windows-safe filename."""
    text = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", text)
    text = re.sub(r"\s+", "_", text.strip())
    text = re.sub(r"_+", "_", text)
    return text[:max_length].strip(" ._")


def get_soup(url):
    response = session.get(url, timeout=(20, 60))
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def class_folder_name(class_number):
    if class_number == 8:
        return "class 8th"
    if class_number == 9:
        return "class 9th"
    return "class 10"


def get_medium(detail_url):
    """Extract the medium from the textbook URL."""
    parts = [
        part.lower()
        for part in urlparse(detail_url).path.split("/")
        if part
    ]

    for part in parts:
        if part.endswith("-medium"):
            return part

    return "unknown-medium"


def detect_subject(title):
    """
    Return (folder name, subject type).

    Core subjects are checked before language subjects.
    """
    text = normalize(title)

    # Social Science before other possible matches.
    for subject, keywords in CORE_SUBJECTS.items():
        for keyword in keywords:
            if normalize(keyword) in text:
                return subject, "core"

    # Do not accidentally download unrelated subjects.
    for subject, keywords in LANGUAGE_SUBJECTS.items():
        for keyword in keywords:
            if normalize(keyword) in text:
                return subject, "language"

    return None, None


def is_language_book(title):
    """Keep language-course books, including parts."""
    text = normalize(title)

    return any(
        normalize(level) in text
        for level in LANGUAGE_LEVELS
    )


def is_allowed_book(title, detail_url):
    """
    Core books: English/Hindi/Kannada mediums only.
    Language books: English, Kannada and Hindi courses.
    """
    subject, kind = detect_subject(title)

    if subject is None:
        return None

    medium = get_medium(detail_url)

    if kind == "core":
        if medium not in ALLOWED_CORE_MEDIUMS:
            return None

        return {
            "subject": subject,
            "kind": kind,
            "medium": medium,
        }

    # Avoid accidentally classifying core subject books
    # as language textbooks.
    if not is_language_book(title):
        return None

    return {
        "subject": subject,
        "kind": kind,
        "medium": medium,
    }


# ---------------------------------------------------------
# CATALOG DISCOVERY
# ---------------------------------------------------------

def find_textbook_pages(class_number):
    """
    Read the class catalog and collect textbook detail pages.

    The detail pages are deduplicated by URL.
    """
    listing_url = CLASS_PAGES[class_number]
    soup = get_soup(listing_url)
    books = {}

    for anchor in soup.find_all("a", href=True):
        detail_url = urljoin(listing_url, anchor["href"])
        parsed = urlparse(detail_url)

        # Stay on the textbook catalog website.
        if parsed.netloc.lower() not in {
            urlparse(BASE_URL).netloc.lower(),
            "www.karnatakatextbooks.in",
        }:
            continue

        path = parsed.path.lower()

        # Only pages associated with the requested class.
        if f"/class-{class_number}/" not in path:
            continue

        # Skip the class landing page itself.
        if path.rstrip("/") == f"/class-{class_number}":
            continue

        title = anchor.get_text(" ", strip=True)

        if not title:
            continue

        info = is_allowed_book(title, detail_url)

        if info:
            books[detail_url] = {
                "listing_title": title,
                **info,
            }

    return books


# ---------------------------------------------------------
# PDF LINK DISCOVERY
# ---------------------------------------------------------

def find_pdf_url(detail_url):
    """
    Find a PDF link on a textbook detail page.

    Handles ordinary .pdf URLs and catalog download endpoints.
    """
    soup = get_soup(detail_url)

    for anchor in soup.find_all("a", href=True):
        href = urljoin(detail_url, anchor["href"])
        parsed = urlparse(href)
        path = parsed.path.lower()
        label = anchor.get_text(" ", strip=True).lower()

        if parsed.scheme not in {"http", "https"}:
            continue

        is_pdf_link = (
            path.endswith(".pdf")
            or "/api/textbooks/" in path
            or (
                "download" in label
                and "pdf" in label
            )
        )

        if is_pdf_link:
            return href, soup

    return None, soup


def choose_title(soup, fallback):
    """Extract a useful textbook title from the detail page."""
    heading = soup.find("h1")

    if heading:
        title = heading.get_text(" ", strip=True)
        if title:
            return title

    if soup.title and soup.title.string:
        title = soup.title.string.strip()
        if title:
            return title

    return fallback


# ---------------------------------------------------------
# DOWNLOAD AND VALIDATION
# ---------------------------------------------------------

def download_pdf(pdf_url, destination):
    """
    Download a PDF safely.

    A temporary file prevents incomplete downloads being
    mistaken for completed PDFs.
    """
    if destination.exists():
        try:
            with destination.open("rb") as file:
                if (
                    destination.stat().st_size > 1024
                    and file.read(5) == b"%PDF-"
                ):
                    print(f"  SKIP: {destination.name}")
                    return "Already downloaded"
        except OSError:
            pass

    temp_file = destination.with_suffix(".pdf.part")

    try:
        with session.get(
            pdf_url,
            stream=True,
            timeout=(20, 180),
        ) as response:
            response.raise_for_status()

            content_type = response.headers.get(
                "Content-Type", ""
            ).lower()

            first_chunk = True

            with temp_file.open("wb") as file:
                for chunk in response.iter_content(
                    chunk_size=64 * 1024
                ):
                    if not chunk:
                        continue

                    if first_chunk:
                        first_chunk = False

                        if not chunk.startswith(b"%PDF-"):
                            raise ValueError(
                                "Server did not return a PDF. "
                                f"Content-Type: {content_type}"
                            )

                    file.write(chunk)

        if not temp_file.exists():
            raise ValueError("Temporary download file missing")

        if temp_file.stat().st_size < 1024:
            raise ValueError("PDF is unexpectedly small")

        with temp_file.open("rb") as file:
            if file.read(5) != b"%PDF-":
                raise ValueError("Invalid PDF header")

        temp_file.replace(destination)

        print(f"  DOWNLOADED: {destination.name}")
        return "Downloaded"

    except Exception as error:
        print(f"  FAILED: {destination.name}")
        print(f"         {error}")

        temp_file.unlink(missing_ok=True)
        return f"Failed: {error}"


# ---------------------------------------------------------
# MANIFEST
# ---------------------------------------------------------

MANIFEST_FIELDS = [
    "class",
    "subject",
    "kind",
    "medium",
    "title",
    "filename",
    "source_page",
    "pdf_url",
    "status",
]


def save_manifest(rows):
    """Write the results to CSV for the project."""
    with MANIFEST_PATH.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=MANIFEST_FIELDS,
        )
        writer.writeheader()
        writer.writerows(rows)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest_rows = []
    counts = {
        "Downloaded": 0,
        "Already downloaded": 0,
        "Failed": 0,
    }

    for class_number, listing_url in CLASS_PAGES.items():
        class_folder = (
            OUTPUT_DIR / class_folder_name(class_number)
        )
        class_folder.mkdir(parents=True, exist_ok=True)

        print("\n" + "=" * 65)
        print(f"CLASS {class_number}")
        print(f"Catalog: {listing_url}")
        print("=" * 65)

        try:
            textbooks = find_textbook_pages(class_number)

        except Exception as error:
            print(f"Catalog error: {error}")
            manifest_rows.append({
                "class": class_number,
                "subject": "",
                "kind": "",
                "medium": "",
                "title": "",
                "filename": "",
                "source_page": listing_url,
                "pdf_url": "",
                "status": f"Catalog failed: {error}",
            })
            continue

        print(f"Matching textbook entries: {len(textbooks)}")

        if not textbooks:
            print(
                "No matching textbooks found. "
                "The catalog structure may have changed."
            )
            continue

        for detail_url, info in textbooks.items():
            listing_title = info["listing_title"]
            subject = info["subject"]
            medium = info["medium"]
            kind = info["kind"]

            try:
                pdf_url, soup = find_pdf_url(detail_url)

                if not pdf_url:
                    status = "Failed: PDF link not found"
                    print(f"  FAILED: {listing_title}")

                    manifest_rows.append({
                        "class": class_number,
                        "subject": subject,
                        "kind": kind,
                        "medium": medium,
                        "title": listing_title,
                        "filename": "",
                        "source_page": detail_url,
                        "pdf_url": "",
                        "status": status,
                    })
                    counts["Failed"] += 1
                    continue

                title = choose_title(soup, listing_title)

                # The URL slug is used as a fallback to distinguish
                # books when a catalog title is too generic.
                slug = urlparse(detail_url).path.rstrip("/").split("/")[-1]

                filename = clean_filename(
                    f"{title}_{medium}_{slug}"
                ) + ".pdf"

                # Keep language and core subjects in separate folders.
                subject_folder = class_folder / subject
                subject_folder.mkdir(parents=True, exist_ok=True)

                destination = subject_folder / filename

                status = download_pdf(pdf_url, destination)

                if status.startswith("Failed:"):
                    counts["Failed"] += 1
                else:
                    counts[status] += 1

                manifest_rows.append({
                    "class": class_number,
                    "subject": subject,
                    "kind": kind,
                    "medium": medium,
                    "title": title,
                    "filename": str(destination.relative_to(OUTPUT_DIR)),
                    "source_page": detail_url,
                    "pdf_url": pdf_url,
                    "status": status,
                })

                time.sleep(REQUEST_DELAY)

            except Exception as error:
                print(f"  ERROR: {listing_title}: {error}")
                counts["Failed"] += 1

                manifest_rows.append({
                    "class": class_number,
                    "subject": subject,
                    "kind": kind,
                    "medium": medium,
                    "title": listing_title,
                    "filename": "",
                    "source_page": detail_url,
                    "pdf_url": "",
                    "status": f"Failed: {error}",
                })

    save_manifest(manifest_rows)

    print("\n" + "=" * 65)
    print("DOWNLOAD SUMMARY")
    print("=" * 65)
    print(f"Downloaded:        {counts['Downloaded']}")
    print(f"Already present:   {counts['Already downloaded']}")
    print(f"Failed:            {counts['Failed']}")
    print(f"Manifest:          {MANIFEST_PATH}")
    print(f"Textbook folder:   {OUTPUT_DIR.resolve()}")
    print("\nRun the script again to retry missing downloads.")


if __name__ == "__main__":
    main()
