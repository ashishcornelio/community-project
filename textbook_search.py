"""
LearnSphere AI - Grounded Textbook Answer Engine

The AI Doubt Solver only answers from the official PDF textbooks stored in the
local "text books" library. Every answer is extracted verbatim from a specific
book, chapter and page, and includes a direct link to that PDF page.

No generated/guessed answer is returned. If the relevant passage cannot be
found in the prescribed textbooks, the engine says so explicitly.
"""

import csv
import math
import os
import re
import sqlite3
import threading
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEXTBOOKS_DIR = os.path.join(BASE_DIR, "text books")
MAIN_DB_PATH = os.path.join(BASE_DIR, "data", "learnsphere.db")
INDEX_DB_PATH = os.path.join(BASE_DIR, "data", "textbook_index.db")
INDEX_VERSION = "6"

try:
    import pymupdf as _pdf
except ImportError:  # older installs expose the module as fitz
    try:
        import fitz as _pdf
    except ImportError:
        _pdf = None


STOPWORDS = set("""
a an the is are was were be been being am i me my we our you your he she it they
them this that these those what which who whom whose why how when where do does
did done can could should would will shall may might must please explain describe
tell give show define definition define meaning means about with without from into
onto of for to in on at by as and or but if then than so very simple words word
step steps question questions answer answers doubt doubts topic topics also using
use find calculate write state mention list name called class textbook chapter
page no number following true false correct incorrect option
""".split())

SUBJECT_KEYWORDS = {
    "Science": [
        "photosynthesis", "chlorophyll", "leaf", "leaves", "plant", "cell", "tissue",
        "organ", "life", "reproduction", "heredity", "evolution", "environment",
        "ecosystem", "newton", "force", "motion", "inertia", "gravity", "friction",
        "electricity", "current", "voltage", "resistance", "ohm", "magnet", "magnetic",
        "light", "reflection", "refraction", "lens", "mirror", "human", "eye", "colour",
        "color", "chemical", "reaction", "acid", "base", "salt", "metal", "nonmetal",
        "carbon", "compound", "atom", "molecule", "periodic", "energy", "heat", "sound",
        "science", "physics", "chemistry", "biology",
    ],
    "Maths": [
        "mathematics", "maths", "math", "number", "real", "irrational", "rational",
        "polynomial", "equation", "linear", "quadratic", "arithmetic", "progression",
        "triangle", "similar", "circle", "tangent", "coordinate", "geometry", "area",
        "volume", "surface", "statistics", "probability", "mean", "median", "mode",
        "trigonometry", "sine", "cosine", "tangent", "angle", "algebra", "factor",
        "theorem", "graph", "slope", "percent", "ratio", "fraction", "solve",
    ],
    "English": [
        "english", "poem", "poetry", "prose", "story", "author", "poet", "literature",
        "grammar", "tense", "verb", "noun", "pronoun", "adjective", "adverb",
        "sentence", "paragraph", "essay", "letter", "comprehension", "summary",
        "first flight", "supplementary", "reader",
    ],
    "Hindi": ["hindi", "कविता", "पाठ", "गद्य", "व्याकरण", "निबंध"],
    "Kannada": ["kannada", "ಕನ್ನಡ", "ಪಾಠ", "ಕವನ", "ವ್ಯಾಕರಣ"],
}

SUBJECT_ALIASES = {
    "mathematics": "Maths", "math": "Maths", "maths": "Maths",
    "science": "Science", "physics": "Science", "chemistry": "Science", "biology": "Science",
    "english": "English", "hindi": "Hindi", "kannada": "Kannada",
}

CHAPTER_RE = re.compile(r"(?i)\b(?:chapter|unit)\s*[-–—:.]?\s*(\d{1,2})\b")
TOC_PATTERNS = [
    # CHAPTER 3 \n Metals and Non-metals \n 01
    re.compile(r"(?im)^\s*chapter\s+(\d{1,2})\s*[:.\-–—]?\s*\n\s*([^\n]{2,90})\n\s*(\d{1,3})\s*$"),
    # 1. \n Real Numbers \n 1
    re.compile(r"(?m)^\s*(\d{1,2})\.\s*\n\s*([A-Z][^\n]{2,90})\n\s*(\d{1,3})\s*$"),
    # 1. A Letter to God \n 1   /   10. Circles \n 32
    re.compile(r"(?m)^\s*(\d{1,2})\.\s+([A-Z][^\n]{2,90}?)\s*\n\s*(\d{1,3})\s*$"),
    # 1 \n A Wrong Man in Workers' Paradise \n Author \n 1-16
    re.compile(
        r"(?m)^\s*(\d{1,2})\s*\n\s*([A-Z][^\n]{2,90})\s*\n"
        r"(?:[^\n]{0,90}\n)?\s*(\d{1,3})(?:\s*[-–]\s*\d{1,3})?\s*$"
    ),
]


def _is_contents_page(text):
    if re.search(r"(?i)\bcontents?\b", text):
        return True
    matches = 0
    for regex in TOC_PATTERNS:
        matches += len(regex.findall(text))
        if matches >= 2:
            return True
    return False


def _norm(text):
    return re.sub(r"[^a-z0-9]", "", (text or "").lower())


def _ascii_letter_ratio(text):
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    ascii_letters = sum(1 for c in letters if c.isascii())
    return ascii_letters / len(letters)


COMMON_ENGLISH_WORDS = set("""
the and of to in is are was were this that with for as by on it from be or an we
you your can will would which their these those has have had not but at its into
more other such than then when where all any each also may use used using made make
one two what how why who whose do does did about over under between through during
because while both same some many most only very our they them he she his her
""".split())


def _english_word_ratio(text):
    words = re.findall(r"[A-Za-z]{2,}", text.lower())
    if not words:
        return 0.0
    common = sum(1 for word in words if word in COMMON_ENGLISH_WORDS)
    return common / len(words)


def _is_english_page(text):
    words = re.findall(r"[A-Za-z]{2,}", text)
    if len(words) < 30:
        return False
    return _english_word_ratio(text) >= 0.18


def _clean_page_text(raw):
    if not raw:
        return ""
    text = raw.replace("\x00", " ").replace("\u00a0", " ")
    text = "".join(
        ch for ch in text
        if not (0xE000 <= ord(ch) <= 0xF8FF)  # private-use glyphs used by some PDFs
    )
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _printed_page(text):
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return None
    for line in lines[:3] + lines[-4:]:
        if re.fullmatch(r"\d{1,3}", line):
            return line
    return None


def _parse_toc(doc, max_pages=20):
    """Return a list of {number, title} entries parsed from contents pages."""
    entries = []
    seen = set()
    toc_pages_left = 0

    for i in range(min(max_pages, doc.page_count)):
        text = _clean_page_text(doc[i].get_text())
        if re.search(r"(?i)\bcontents?\b", text):
            toc_pages_left = 3

        if toc_pages_left <= 0:
            continue
        toc_pages_left -= 1

        for regex in TOC_PATTERNS:
            for match in regex.finditer(text):
                number = int(match.group(1))
                title = re.sub(r"\s+", " ", match.group(2)).strip(" .:-–—")
                if not title:
                    continue
                if re.fullmatch(r"(?i)(chapter|unit)\s*\d+", title):
                    continue
                if re.fullmatch(r"(?i)contents?", title):
                    continue
                key = (number, _norm(title))
                if key in seen:
                    continue
                seen.add(key)
                entries.append({"number": number, "title": title})

    return entries


def _chapter_from_page(text, toc, current_number, current_title):
    head = text[:500]
    norm_head = _norm(head)

    best = None
    for entry in toc:
        norm_title = _norm(entry["title"])
        if len(norm_title) < 4:
            continue
        pos = norm_head.find(norm_title)
        if 0 <= pos <= 180:
            if best is None or pos < best[0]:
                best = (pos, entry["number"], entry["title"])

    if best:
        pos, number, title = best
        if pos <= 60 or "chapter" in norm_head[: pos + 40] or current_number is None:
            return number, title

    match = CHAPTER_RE.search(head)
    if match:
        number = int(match.group(1))
        for entry in toc:
            if entry["number"] == number:
                return number, entry["title"]

    return current_number, current_title


def extract_keywords(query):
    query = (query or "").lower()
    tokens = re.findall(r"[a-z][a-z0-9']{1,}", query)
    keywords = []

    for token in tokens:
        token = token.strip("'")
        if token.endswith("'s"):
            token = token[:-2]
        if not token or token in STOPWORDS or len(token) < 2:
            continue
        if token.endswith("ies") and len(token) > 4:
            token = token[:-3] + "y"
        elif token.endswith("es") and len(token) > 4 and not token.endswith("sses"):
            token = token[:-2]
        elif token.endswith("s") and len(token) > 3 and not token.endswith("ss"):
            token = token[:-1]
        if token not in keywords:
            keywords.append(token)

    for token in re.findall(r"\d+[a-z]+|[a-z]+\d+", query):
        if token not in keywords:
            keywords.append(token)

    if ("=" in query or "solve" in query) and re.search(r"\d", query):
        for extra in ("linear", "equation", "variable"):
            if extra not in keywords:
                keywords.append(extra)

    return keywords[:12]


def infer_subject(query):
    lowered = (query or "").lower()
    scores = {}
    for subject, words in SUBJECT_KEYWORDS.items():
        score = sum(1 for word in words if word in lowered)
        if score:
            scores[subject] = score
    if not scores:
        return None
    return max(scores, key=scores.get)


def infer_class(query):
    lowered = (query or "").lower()
    if re.search(r"\bsslc\b|\bclass\s*10\b|\b10th\b|\bstd\s*10\b", lowered):
        return 10
    if re.search(r"\bclass\s*9\b|\b9th\b|\bstd\s*9\b", lowered):
        return 9
    if re.search(r"\bclass\s*8\b|\b8th\b|\bstd\s*8\b", lowered):
        return 8
    match = re.search(r"\b(8|9|10)\b", lowered)
    if match:
        return int(match.group(1))
    return None


def normalize_subject(subject):
    if not subject or str(subject).strip().lower() in ("", "general", "auto", "all"):
        return None
    return SUBJECT_ALIASES.get(str(subject).strip().lower(), str(subject).strip())


def _fts_term(keyword):
    keyword = re.sub(r"[^a-z0-9]", "", keyword.lower())
    if not keyword:
        return None
    if len(keyword) >= 4:
        return keyword + "*"
    return keyword


def _coverage(text, keywords):
    lowered = text.lower()
    compact = re.sub(r"\s+", "", lowered)
    hits = 0
    for keyword in keywords:
        stem = keyword[: max(3, len(keyword) - 1)]
        if keyword in lowered or stem in compact:
            hits += 1
    return hits / len(keywords) if keywords else 0.0


def _best_excerpt(text, keywords, max_chars=1100):
    flat = re.sub(r"\s+", " ", text).strip()
    if len(flat) <= max_chars:
        return flat

    sentences = re.split(r"(?<=[.!?])\s+", flat)
    if len(sentences) < 2:
        return flat[:max_chars].rsplit(" ", 1)[0] + "..."

    best_index = 0
    best_score = -1
    for index, sentence in enumerate(sentences):
        score = sum(1 for keyword in keywords if keyword in sentence.lower())
        if score > best_score:
            best_score = score
            best_index = index

    start = best_index
    end = best_index + 1
    while start > 0 and len(" ".join(sentences[start - 1:end])) < max_chars * 0.65:
        start -= 1
    while end < len(sentences) and len(" ".join(sentences[start:end + 1])) <= max_chars:
        end += 1

    excerpt = " ".join(sentences[start:end]).strip()
    if start > 0:
        excerpt = "... " + excerpt
    if end < len(sentences):
        excerpt = excerpt + " ..."
    return excerpt


class TextbookSearchEngine:
    def __init__(self):
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Index database
    # ------------------------------------------------------------------
    def _connect(self):
        os.makedirs(os.path.dirname(INDEX_DB_PATH), exist_ok=True)
        conn = sqlite3.connect(INDEX_DB_PATH, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _ensure_schema(self, conn):
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS index_meta (
            key TEXT PRIMARY KEY,
            value TEXT
        );

        CREATE TABLE IF NOT EXISTS indexed_books (
            book_id INTEGER PRIMARY KEY,
            filename TEXT NOT NULL,
            title TEXT,
            class_num INTEGER,
            subject TEXT,
            medium TEXT,
            page_count INTEGER DEFAULT 0,
            english_pages INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            indexed_at TEXT
        );

        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            page_no INTEGER NOT NULL,
            printed_page TEXT,
            chapter_no TEXT,
            chapter_title TEXT,
            text TEXT NOT NULL,
            UNIQUE(book_id, page_no)
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(
            text,
            chapter_title,
            content='pages',
            content_rowid='id',
            tokenize='unicode61 remove_diacritics 2'
        );

        CREATE TRIGGER IF NOT EXISTS pages_ai AFTER INSERT ON pages BEGIN
            INSERT INTO pages_fts(rowid, text, chapter_title)
            VALUES (new.id, new.text, new.chapter_title);
        END;

        CREATE TRIGGER IF NOT EXISTS pages_ad AFTER DELETE ON pages BEGIN
            INSERT INTO pages_fts(pages_fts, rowid, text, chapter_title)
            VALUES ('delete', old.id, old.text, old.chapter_title);
        END;

        CREATE TRIGGER IF NOT EXISTS pages_au AFTER UPDATE ON pages BEGIN
            INSERT INTO pages_fts(pages_fts, rowid, text, chapter_title)
            VALUES ('delete', old.id, old.text, old.chapter_title);
            INSERT INTO pages_fts(rowid, text, chapter_title)
            VALUES (new.id, new.text, new.chapter_title);
        END;
        """)

        row = conn.execute(
            "SELECT value FROM index_meta WHERE key = 'version'"
        ).fetchone()
        if not row or row["value"] != INDEX_VERSION:
            # Indexing rules changed (e.g. language detection); rebuild cleanly.
            conn.execute("DELETE FROM pages")
            conn.execute("DELETE FROM indexed_books")
            conn.execute(
                "INSERT OR REPLACE INTO index_meta (key, value) VALUES ('version', ?)",
                (INDEX_VERSION,),
            )
        conn.commit()

    # ------------------------------------------------------------------
    # Book metadata
    # ------------------------------------------------------------------
    def _books_from_main_db(self):
        books = []
        if os.path.exists(MAIN_DB_PATH):
            try:
                conn = sqlite3.connect(MAIN_DB_PATH, timeout=10)
                conn.row_factory = sqlite3.Row
                rows = conn.execute("""
                    SELECT id AS book_id, filename, title, class_num, subject, medium
                    FROM textbooks
                """).fetchall()
                conn.close()
                books = [dict(row) for row in rows]
            except sqlite3.Error:
                books = []

        if not books:
            books = self._books_from_manifest()
        return books

    def _books_from_manifest(self):
        manifest = os.path.join(TEXTBOOKS_DIR, "manifest.csv")
        books = []
        if not os.path.exists(manifest):
            return books
        with open(manifest, encoding="utf-8-sig") as handle:
            for index, row in enumerate(csv.DictReader(handle), start=1):
                books.append({
                    "book_id": index,
                    "filename": row.get("filename", "").strip(),
                    "title": row.get("title", "").strip(),
                    "class_num": int(row.get("class", "0") or 0),
                    "subject": row.get("subject", "").strip(),
                    "medium": row.get("medium", "").strip(),
                })
        return books

    def _candidate_books(self, class_num=None, subject=None, book_id=None):
        books = self._books_from_main_db()
        candidates = []
        for book in books:
            if book_id is not None and int(book["book_id"]) != int(book_id):
                continue
            if class_num is not None and book.get("class_num") != class_num:
                continue
            if subject and (book.get("subject") or "").lower() != subject.lower():
                continue
            full_path = os.path.join(TEXTBOOKS_DIR, book.get("filename") or "")
            if not os.path.exists(full_path):
                continue
            book["full_path"] = full_path
            candidates.append(book)
        return candidates

    # ------------------------------------------------------------------
    # Indexing
    # ------------------------------------------------------------------
    def _probe_book(self, full_path):
        if _pdf is None:
            return False
        try:
            doc = _pdf.open(full_path)
        except Exception:
            return False

        total = doc.page_count
        if total == 0:
            doc.close()
            return False

        sample = sorted(set([
            min(total - 1, max(0, int(total * 0.10))),
            min(total - 1, max(0, int(total * 0.25))),
            min(total - 1, max(0, int(total * 0.45))),
            min(total - 1, max(0, int(total * 0.65))),
            min(total - 1, max(0, int(total * 0.85))),
        ]))

        good = 0
        for page_no in sample:
            text = _clean_page_text(doc[page_no].get_text())
            if len(text) > 180 and _is_english_page(text):
                good += 1
        doc.close()
        return good >= 2

    def index_book(self, book, force=False):
        if _pdf is None:
            return {"success": False, "error": "PyMuPDF is not installed. Run: pip install pymupdf"}

        book_id = int(book["book_id"])
        full_path = book.get("full_path") or os.path.join(TEXTBOOKS_DIR, book.get("filename") or "")

        with self._lock:
            conn = self._connect()
            self._ensure_schema(conn)

            existing = conn.execute(
                "SELECT status FROM indexed_books WHERE book_id = ?", (book_id,)
            ).fetchone()
            if existing and existing["status"] == "indexed" and not force:
                conn.close()
                return {"success": True, "status": "already_indexed", "book_id": book_id}

            if not os.path.exists(full_path):
                conn.execute("""
                    INSERT INTO indexed_books (book_id, filename, title, class_num, subject, medium, status, indexed_at)
                    VALUES (?, ?, ?, ?, ?, ?, 'missing', ?)
                    ON CONFLICT(book_id) DO UPDATE SET status = 'missing', indexed_at = excluded.indexed_at
                """, (
                    book_id, book.get("filename"), book.get("title"), book.get("class_num"),
                    book.get("subject"), book.get("medium"), datetime.now().isoformat(timespec="seconds"),
                ))
                conn.commit()
                conn.close()
                return {"success": False, "status": "missing", "book_id": book_id}

            if not force and not self._probe_book(full_path):
                conn.execute("""
                    INSERT INTO indexed_books (book_id, filename, title, class_num, subject, medium, status, indexed_at)
                    VALUES (?, ?, ?, ?, ?, ?, 'skipped', ?)
                    ON CONFLICT(book_id) DO UPDATE SET status = 'skipped', indexed_at = excluded.indexed_at
                """, (
                    book_id, book.get("filename"), book.get("title"), book.get("class_num"),
                    book.get("subject"), book.get("medium"), datetime.now().isoformat(timespec="seconds"),
                ))
                conn.commit()
                conn.close()
                return {"success": True, "status": "skipped", "book_id": book_id}

            try:
                doc = _pdf.open(full_path)
            except Exception as exc:
                conn.close()
                return {"success": False, "status": "error", "error": str(exc)}

            toc = _parse_toc(doc)
            page_rows = []
            current_number = None
            current_title = None
            english_pages = 0

            for page_index in range(doc.page_count):
                page = doc[page_index]
                text = _clean_page_text(page.get_text())
                if len(text) < 40:
                    continue
                if not _is_english_page(text):
                    continue
                if page_index < 20 and _is_contents_page(text):
                    continue

                english_pages += 1
                current_number, current_title = _chapter_from_page(
                    text, toc, current_number, current_title
                )
                page_rows.append((
                    book_id,
                    page_index + 1,
                    _printed_page(text),
                    str(current_number) if current_number is not None else None,
                    current_title,
                    text,
                ))

            page_count = doc.page_count
            doc.close()

            has_chapters = any(row[4] for row in page_rows)
            if len(page_rows) < 20 or (not has_chapters and len(page_rows) < 60):
                conn.execute("""
                    INSERT INTO indexed_books
                        (book_id, filename, title, class_num, subject, medium, page_count, english_pages, status, indexed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'skipped', ?)
                    ON CONFLICT(book_id) DO UPDATE SET
                        page_count = excluded.page_count,
                        english_pages = excluded.english_pages,
                        status = 'skipped',
                        indexed_at = excluded.indexed_at
                """, (
                    book_id, book.get("filename"), book.get("title"), book.get("class_num"),
                    book.get("subject"), book.get("medium"), page_count, english_pages,
                    datetime.now().isoformat(timespec="seconds"),
                ))
                conn.commit()
                conn.close()
                return {
                    "success": True,
                    "status": "skipped",
                    "book_id": book_id,
                    "reason": "no usable chapter text",
                }

            conn.execute("DELETE FROM pages WHERE book_id = ?", (book_id,))
            conn.executemany("""
                INSERT INTO pages (book_id, page_no, printed_page, chapter_no, chapter_title, text)
                VALUES (?, ?, ?, ?, ?, ?)
            """, page_rows)
            conn.execute("""
                INSERT INTO indexed_books
                    (book_id, filename, title, class_num, subject, medium, page_count, english_pages, status, indexed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'indexed', ?)
                ON CONFLICT(book_id) DO UPDATE SET
                    filename = excluded.filename,
                    title = excluded.title,
                    class_num = excluded.class_num,
                    subject = excluded.subject,
                    medium = excluded.medium,
                    page_count = excluded.page_count,
                    english_pages = excluded.english_pages,
                    status = 'indexed',
                    indexed_at = excluded.indexed_at
            """, (
                book_id, book.get("filename"), book.get("title"), book.get("class_num"),
                book.get("subject"), book.get("medium"), page_count, english_pages,
                datetime.now().isoformat(timespec="seconds"),
            ))
            conn.commit()
            conn.close()

        return {
            "success": True,
            "status": "indexed",
            "book_id": book_id,
            "pages_indexed": len(page_rows),
            "page_count": page_count,
        }

    def _search_index(self, conn, keywords, book_ids=None, class_num=None, subject=None):
        match_and = " AND ".join(filter(None, (_fts_term(k) for k in keywords)))
        match_or = " OR ".join(filter(None, (_fts_term(k) for k in keywords)))
        if not match_and:
            return []

        filters = []
        params = []
        if book_ids:
            filters.append("p.book_id IN (%s)" % ",".join("?" for _ in book_ids))
            params.extend(book_ids)
        if class_num is not None:
            filters.append("ib.class_num = ?")
            params.append(class_num)
        if subject:
            filters.append("LOWER(ib.subject) = ?")
            params.append(subject.lower())

        filter_sql = (" AND " + " AND ".join(filters)) if filters else ""
        base_sql = f"""
            SELECT p.id, p.book_id, p.page_no, p.printed_page, p.chapter_no, p.chapter_title,
                   p.text, ib.title, ib.class_num, ib.subject, ib.medium,
                   bm25(pages_fts) AS rank
            FROM pages_fts
            JOIN pages p ON p.id = pages_fts.rowid
            JOIN indexed_books ib ON ib.book_id = p.book_id
            WHERE pages_fts MATCH ? {filter_sql}
            ORDER BY rank
            LIMIT 100
        """

        rows = []
        seen = set()
        for match_query in (match_and, match_or):
            try:
                found = conn.execute(base_sql, [match_query] + params).fetchall()
            except sqlite3.Error:
                found = []
            for row in found:
                if row["id"] in seen:
                    continue
                seen.add(row["id"])
                rows.append(dict(row))
            if len(rows) >= 12:
                break
        return rows

    def _select_results(self, rows, keywords, limit=3):
        if not keywords:
            return []
        needed = 1 if len(keywords) <= 2 else max(2, math.ceil(len(keywords) * 0.4))

        scored = []
        for row in rows:
            coverage = _coverage(row["text"], keywords)
            if coverage <= 0:
                continue
            hits = round(coverage * len(keywords))
            if hits < needed:
                continue

            chapter_norm = _norm(row.get("chapter_title"))
            title_hits = 0
            for keyword in keywords:
                stem = _norm(keyword)[:8]
                if stem and stem in chapter_norm:
                    title_hits += 1

            # Short queries must match the chapter/topic heading. This rejects
            # incidental mentions (e.g. a metals chapter page that only says
            # the word "electricity" in passing).
            if len(keywords) <= 2 and title_hits == 0:
                continue

            rank_bonus = max(0.0, -float(row.get("rank") or 0.0))
            score = coverage * 20.0 + title_hits * 15.0 + min(rank_bonus, 10.0)
            row["coverage"] = coverage
            row["title_hits"] = title_hits
            row["score"] = score
            scored.append(row)

        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:limit]

    def _candidate_keywords(self, keywords):
        """Remove repeated very short/generic words that hurt FTS precision."""
        useful = [k for k in keywords if len(k) >= 3]
        return useful or keywords

    def search(self, query, class_num=None, subject=None, medium=None, book_id=None):
        keywords = self._candidate_keywords(extract_keywords(query))
        if not keywords:
            return self._format_search_result(query, [], [], [])

        subject = normalize_subject(subject)
        if subject is None and book_id is None:
            subject = infer_subject(query)
        if class_num is None:
            class_num = infer_class(query)
        if class_num is None:
            class_num = 10

        conn = self._connect()
        self._ensure_schema(conn)

        if subject is None and book_id is None:
            # No subject could be inferred: limit automatic indexing to the core
            # subjects instead of opening every language/literature PDF.
            candidates = []
            for core_subject in ("Science", "Maths"):
                candidates.extend(
                    self._candidate_books(class_num=class_num, subject=core_subject)
                )
        else:
            candidates = self._candidate_books(
                class_num=class_num, subject=subject, book_id=book_id
            )

        indexed_ids = {
            row["book_id"] for row in conn.execute(
                "SELECT book_id FROM indexed_books WHERE status = 'indexed'"
            ).fetchall()
        }

        # Search already indexed books first. Only index on-demand when needed.
        candidate_ids = [int(book["book_id"]) for book in candidates]
        if candidate_ids:
            rows = self._search_index(
                conn,
                keywords,
                book_ids=candidate_ids,
                class_num=None,
                subject=None,
            )
            results = self._select_results(rows, keywords)
            if results:
                conn.close()
                return self._format_search_result(query, keywords, results, candidates)

        # Index missing candidate textbooks (skip PDFs without extractable English text).
        for book in candidates:
            book_id_int = int(book["book_id"])
            if book_id_int in indexed_ids:
                continue
            self.index_book(book)
            indexed_ids.add(book_id_int)

        rows = self._search_index(
            conn,
            keywords,
            book_ids=candidate_ids or None,
            class_num=class_num if not candidate_ids else None,
            subject=subject if not candidate_ids else None,
        )
        results = self._select_results(rows, keywords)

        conn.close()
        return self._format_search_result(query, keywords, results, candidates)

    def _format_search_result(self, query, keywords, results, candidates):
        if not results:
            subject = infer_subject(query)
            scope = f"Class {candidates[0].get('class_num')} {subject or 'textbooks'}" if candidates else "the prescribed textbooks"
            return {
                "success": True,
                "found": False,
                "query": query,
                "keywords": keywords,
                "results": [],
                "search_scope": scope,
                "response": (
                    f"### Not found in the prescribed textbooks\n\n"
                    f"I searched {scope} but could not find a passage that answers: "
                    f"**{query}**\n\n"
                    "To avoid giving you an incorrect or invented answer, I will not guess. "
                    "Try rephrasing with a chapter/topic keyword, or choose the correct "
                    "Class and Subject above."
                ),
            }

        citations = []
        blocks = []
        for result in results:
            printed = result.get("printed_page")
            pdf_page = result.get("page_no")
            page_label = printed or str(pdf_page)
            chapter_no = result.get("chapter_no")
            chapter_title = result.get("chapter_title") or "Chapter not detected"
            if chapter_no:
                chapter_label = f"Chapter {chapter_no}: {chapter_title}"
            else:
                chapter_label = chapter_title

            excerpt = _best_excerpt(result["text"], keywords)
            read_url = f"/api/textbooks/read/{result['book_id']}#page={pdf_page}"
            citation = {
                "book_id": result["book_id"],
                "book_title": result.get("title"),
                "class_num": result.get("class_num"),
                "subject": result.get("subject"),
                "medium": result.get("medium"),
                "chapter_no": chapter_no,
                "chapter_title": result.get("chapter_title"),
                "page_no": pdf_page,
                "printed_page": printed,
                "page_label": page_label,
                "excerpt": excerpt,
                "read_url": read_url,
            }
            citations.append(citation)

            page_line = f"Page {page_label}"
            if printed and str(printed) != str(pdf_page):
                page_line += f" (PDF page {pdf_page})"
            blocks.append(
                f"**{result.get('title')}**\n"
                f"*{chapter_label}* | **{page_line}**\n\n"
                f"> {excerpt}\n\n"
                f"[Open this textbook page]({read_url})"
            )

        response = (
            "### Answer found in your textbook\n\n"
            + "\n\n---\n\n".join(blocks)
            + "\n\n*This answer is quoted directly from the prescribed Karnataka State Board "
              "textbook shown above. I only answer from the textbooks in your library, so no "
              "invented answer is given.*"
        )

        return {
            "success": True,
            "found": True,
            "query": query,
            "keywords": keywords,
            "results": citations,
            "primary_source": citations[0],
            "response": response,
            "topic": citations[0].get("chapter_title") or query,
            "related_actions": ["Take Practice Quiz", "Generate Short Notes", "View Visual Simulation"],
        }

    def stats(self):
        conn = self._connect()
        self._ensure_schema(conn)
        row = conn.execute("""
            SELECT
                COUNT(*) AS books,
                SUM(CASE WHEN status = 'indexed' THEN 1 ELSE 0 END) AS indexed,
                SUM(CASE WHEN status = 'skipped' THEN 1 ELSE 0 END) AS skipped,
                SUM(CASE WHEN status = 'missing' THEN 1 ELSE 0 END) AS missing,
                SUM(english_pages) AS pages
            FROM indexed_books
        """).fetchone()
        conn.close()
        return dict(row)

    def index_all(self, class_num=None, subject=None, force=False):
        candidates = self._candidate_books(class_num=class_num, subject=normalize_subject(subject))
        summary = []
        for book in candidates:
            outcome = self.index_book(book, force=force)
            summary.append({
                "book_id": book["book_id"],
                "title": book.get("title"),
                "status": outcome.get("status"),
                "pages_indexed": outcome.get("pages_indexed"),
                "error": outcome.get("error"),
            })
        return summary


textbook_search_engine = TextbookSearchEngine()
