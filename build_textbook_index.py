"""
Build the searchable textbook index used by the AI Doubt Solver.
The SQLite index is stored in data/textbook_index.db.

Examples:
    python build_textbook_index.py
    python build_textbook_index.py --class 10 --subject Science
    python build_textbook_index.py --force
"""

import argparse

from textbook_search import textbook_search_engine


def main():
    parser = argparse.ArgumentParser(description="Index textbook PDFs for grounded doubt solving.")
    parser.add_argument("--class", dest="class_num", type=int, choices=[8, 9, 10], default=None)
    parser.add_argument("--subject", default=None, help="Maths, Science, English, Hindi, or Kannada")
    parser.add_argument("--force", action="store_true", help="Re-index books already in the index")
    args = parser.parse_args()

    summary = textbook_search_engine.index_all(
        class_num=args.class_num,
        subject=args.subject,
        force=args.force,
    )

    indexed = sum(1 for item in summary if item["status"] == "indexed")
    skipped = sum(1 for item in summary if item["status"] == "skipped")
    for item in summary:
        pages = f" ({item['pages_indexed']} pages)" if item.get("pages_indexed") else ""
        print(f"[{item['status']}] {item['title']}{pages}")
        if item.get("error"):
            print(f"    error: {item['error']}")

    print(f"\nDone: {indexed} indexed, {skipped} skipped (no extractable text).")
    print("Index stats:", textbook_search_engine.stats())


if __name__ == "__main__":
    main()
