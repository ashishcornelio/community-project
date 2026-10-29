# LearnSphere AI

LearnSphere is a Flask web application for Karnataka DSERT school learning in Classes 8, 9, and 10. Students can browse curriculum topics, read multi-format notes, practise quizzes, view learning progress, use study plans and bookmarks, and search local textbook PDFs for answers. Teacher and administrator accounts have additional classroom and governance views.

## How the application is structured

The project has a small server-rendered Flask layer and a browser-based single-page interface:

```text
Browser
  templates/login.html ── sign-in and registration
  templates/index.html ── page structure and authenticated user data
  static/css/            ── layout, theme, and component styling
  static/js/             ── navigation, API calls, quizzes, progress, and visual lab
          │
          │ HTTP pages and JSON API requests
          ▼
app.py ── Flask routes, login/session checks, role checks, and application logic
   ├── database.py ── SQLite connection, schema creation, migrations, and seed data
   ├── seed_curriculum.py ── school topics and related learning content
   ├── ai_engine.py ── learning feedback and textbook-grounded doubt answering
   └── textbook_search.py ── PDF extraction, full-text index, and page-level search
          │
          ├── data/learnsphere.db
          └── data/textbook_index.db
```

The frontend uses HTML templates, CSS, and vanilla JavaScript; it does not use a separate frontend build system. `templates/index.html` contains the main application views. JavaScript modules load content from the Flask JSON endpoints and update the selected view without navigating to a separate page.

## Database design

LearnSphere uses two SQLite databases with different purposes.

### `data/learnsphere.db`: application data

`database.py` defines and initializes the application database. `get_db()` opens a SQLite connection with named-column rows. On application startup, `init_db()` creates missing tables, runs small schema migrations, seeds initial reference data, synchronizes curriculum content, and removes obsolete non-school curriculum records. Database files and their containing directory are kept under `data/`.

The main tables are:

| Table | What it stores |
|---|---|
| `users` | Student, teacher, and administrator profiles, role, grade, and password hash. |
| `subjects` | School subjects such as Mathematics, Science, Social Science, English, Hindi, and Kannada. |
| `topics` | Topics connected to subjects, including grade, explanations, notes, examples, language versions, and visual references. |
| `topic_prerequisites` | Prerequisite concepts and recommended preparation for topics. |
| `quizzes` | Multiple-choice questions and explanations linked to topics. |
| `quiz_hints` | Progressive hints linked to quiz questions. |
| `mistake_detective` | Feedback and follow-up guidance for selected wrong answers. |
| `quiz_attempts` | Per-user quiz scores and completion history. |
| `confidence_records` | Per-user confidence rating and correctness classification for quiz answers. |
| `learning_gaps` | Per-user, per-topic mastery estimate, status, and recommended next action. |
| `flashcards` | Topic revision cards and their repetition interval. |
| `teach_back_prompts` | Topic prompts, expected concepts, example answers, and rubrics. |
| `study_tasks` | Per-user study-plan tasks and completion state. |
| `textbooks` | Textbook catalogue information, PDF filename, class, subject, and availability. |
| `exam_materials` | Class- and subject-specific exam preparation materials. |
| `bookmarks` | Per-user saved topics, textbooks, formulas, or other learning items. |

Most curriculum data is shared reference data: subjects, topics, quizzes, and textbook catalogue records. User accounts and learning activity are stored separately and reference those records using IDs. Progress, quiz history, confidence, study tasks, and bookmarks are associated with the signed-in user.

When a student submits a quiz, the server derives the user ID from the Flask session rather than trusting a user ID supplied by the browser. The server stores the attempt, calculates a percentage, updates that student's learning-gap record for the topic, and may add a revision task when the score is below 70%. The progress screen reads these records to summarize mastery and topic gaps.

### `data/textbook_index.db`: searchable PDF content

This separate database supports the textbook doubt solver. `textbook_search.py` extracts text and page metadata from PDF files in `text books/`, records indexed books and pages, and maintains a SQLite FTS5 full-text index. A question is matched against indexed textbook passages, with class, subject, and book filters where available. Results can point back to the source textbook page.

The index is derived from the PDF library and can be rebuilt or updated without replacing the main application database. `build_textbook_index.py` is the command-line entry point for indexing.

## Authentication and request flow

1. A visitor opens `/login` or `/register`.
2. Registration creates a student account, validates the requested grade, hashes the password, and starts a signed Flask session.
3. Login verifies the stored password hash. Legacy SHA-256 password records are upgraded to Werkzeug's password-hash format after a successful login.
4. The `before_request` handler requires a session for application pages and APIs, except login, registration, and static assets. Unauthenticated page requests redirect to login; unauthenticated API requests receive HTTP 401.
5. Student data endpoints use the session user ID. Teacher analytics require a teacher or administrator role; administrator APIs require the administrator role.
6. `/logout` clears the session.

Set `LEARNSPHERE_SECRET_KEY` to a stable, private value when running the app persistently or with multiple workers. If it is not set, the app generates a random key at startup, which means sessions do not survive a restart and separate workers will not share sessions.

## Frontend views

The main interface is served by `templates/index.html`. Its navigation switches between sections of that page; the scripts load data from `/api/...` endpoints as needed.

| View | What it does |
|---|---|
| Dashboard | Shows school subjects and topics for the selected grade. |
| Textbooks | Filters the textbook catalogue and opens available local PDFs. |
| Learn & Notes | Displays topic explanations, multi-format notes, prerequisites, and revision features. |
| Exam Prep | Presents available exam materials for the selected class and subject. |
| Adaptive Quiz | Loads topic questions, hints, mistake feedback, and confidence prompts; quiz outcomes are submitted to the server. |
| AI Doubt Solver | Searches textbook content and shows source information with the answer. |
| Short Notes | Requests concise or structured study notes for a selected school topic. |
| Progress & Gaps | Displays the signed-in student's quiz-based progress and topic recommendations. |
| Visual Lab | Runs browser-side school-level math and science simulations. |
| Study Plan | Shows and updates the signed-in student's study tasks. |
| Bookmarks | Lists and toggles the signed-in student's saved items. |
| Teacher View | Provides classroom-level student and quiz analytics for authorized roles. |
| Admin | Shows administrator statistics for authorized users. |

`static/js/app.js` handles navigation, selected grade, dashboard/topic data, textbooks, exam materials, notes, and bookmarks. `static/js/quiz.js` handles quiz interactions. `static/js/progress.js` handles progress and study tasks. `static/js/doubt_solver.js` handles the doubt-solver interface, and `static/js/visual_lab.js` handles simulations.

The grade selector supports Classes 8, 9, and 10. Its selected class is passed to the relevant API requests so the subject, topic, textbook, quiz, and exam screens can display grade-relevant content.

## Run locally on Windows

From the project directory, create and activate a virtual environment if you do not already have one:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

Install the runtime packages:

```powershell
python -m pip install Flask PyMuPDF
```

Flask provides the web server and Werkzeug password hashing. PyMuPDF enables PDF text extraction for building the textbook index. The textbook search module can import either `pymupdf` or the legacy `fitz` module name.

Set a local session secret and start the app:

```powershell
$env:LEARNSPHERE_SECRET_KEY = "replace-with-a-long-random-local-secret"
python app.py
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000). On first startup, the app initializes `data/learnsphere.db` and loads its seed data.

To index all available textbook PDFs:

```powershell
python build_textbook_index.py
```

Optional filters restrict indexing to one class or subject:

```powershell
python build_textbook_index.py --class 10 --subject Science
python build_textbook_index.py --force
```

The PDF files and `manifest.csv` are expected in `text books/`. If PDFs are missing, the catalogue can still be present, but those books cannot be searched or opened locally.

## Demo accounts

On a database that is seeded with the demo accounts, the login credentials are:

| Role | Username | Password |
|---|---|---|
| Student | `arjun_student` | `student123` |
| Student | `ananya_student` | `student123` |
| Teacher | `pooja_teacher` | `teacher123` |
| Administrator | `admin_svh` | `admin123` |

These are development/demo credentials only. Change or remove them before making the application accessible to other users. New registrations create student accounts; teacher and administrator accounts should be provisioned by a trusted administrator.

## Project files

```text
app.py                         Flask app, routes, authentication, and API
database.py                    Main SQLite schema, migrations, and seed routines
seed_curriculum.py             School curriculum and topic learning content
ai_engine.py                   Learning feedback and doubt-solving orchestration
textbook_search.py             PDF indexing and textbook search
build_textbook_index.py        Textbook index command-line utility
download_karnataka_textbooks.py Textbook download helper
templates/                     Flask/Jinja HTML templates
static/css/                    Application styles
static/js/                     Frontend modules
text books/                    Textbook PDFs and manifest
data/                           SQLite databases
```

## Notes

- The application is scoped to Karnataka school curriculum for Classes 8–10.
- `data/learnsphere.db` is the source of truth for application accounts, curriculum, and learning activity.
- `data/textbook_index.db` is a rebuildable search index derived from local textbook PDFs.
- Keep both database files private. The main database contains account and learning records.
- `LEARNSPHERE_SECRET_KEY` should be private and stable in deployments. The built-in Flask development server is intended for local development, not production hosting.
