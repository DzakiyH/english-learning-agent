import sys
import os
import sqlite3
import argparse
from datetime import datetime, timedelta

DEFAULT_DB = os.getenv("VOCAB_DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "vocab.db"))

STATUS_CHOICES = ["NEW", "PRACTICING", "REVIEW", "LEARNED", "DIFFICULT", "REQUESTED"]
ACTION_MAP = {
    "done": "LEARNED",
    "practice again": "PRACTICING",
    "practice_again": "PRACTICING",
    "practice": "PRACTICING",
    "difficult": "DIFFICULT",
    "review": "REVIEW",
    "new": "NEW",
    "requested": "REQUESTED",
}

def get_conn(db_path=DEFAULT_DB):
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path=DEFAULT_DB):
    with get_conn(db_path) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS words (
            word TEXT PRIMARY KEY COLLATE NOCASE,
            status TEXT DEFAULT 'NEW',
            times_practiced INTEGER DEFAULT 0,
            last_practiced TEXT,
            next_review TEXT,
            notes TEXT
        );
        """)
        try:
            conn.execute("ALTER TABLE words ADD COLUMN next_review TEXT;")
        except sqlite3.OperationalError:
            pass
        conn.commit()

def add_words(words, notes=None, status="REQUESTED", db_path=DEFAULT_DB):
    init_db(db_path)
    added = []
    with get_conn(db_path) as conn:
        for w in words:
            w = w.strip()
            if not w:
                continue
            cur = conn.execute(
                "INSERT INTO words (word, status, notes) VALUES (?, ?, ?) "
                "ON CONFLICT(word) DO UPDATE SET status = ?, notes = COALESCE(excluded.notes, notes);",
                (w, status, notes, status)
            )
            if cur.rowcount > 0:
                added.append(w)
        conn.commit()
    return added

def calculate_next_review(status, times_practiced, now=None):
    if now is None:
        now = datetime.utcnow()
    if status == "DIFFICULT":
        return now.strftime("%Y-%m-%d %H:%M:%S")
    elif status == "PRACTICING":
        intervals = [1, 3, 7, 14]
        days = intervals[min(max(times_practiced - 1, 0), len(intervals) - 1)]
        return (now + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    elif status == "REVIEW":
        return (now + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    elif status == "LEARNED":
        return (now + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    elif status == "REQUESTED":
        return now.strftime("%Y-%m-%d %H:%M:%S")
    return None

def update_word(word, action, notes=None, db_path=DEFAULT_DB):
    init_db(db_path)
    word = word.strip()
    action_clean = action.strip().lower()

    if action_clean == "remove":
        with get_conn(db_path) as conn:
            cur = conn.execute("DELETE FROM words WHERE word = ? COLLATE NOCASE;", (word,))
            conn.commit()
            return cur.rowcount > 0

    new_status = ACTION_MAP.get(action_clean, action_clean.upper())
    if new_status not in STATUS_CHOICES:
        raise ValueError(f"Invalid status or action '{action}'. Valid: {list(ACTION_MAP.keys())} or {STATUS_CHOICES}")

    now = datetime.utcnow()
    now_iso = now.strftime("%Y-%m-%d %H:%M:%S")
    with get_conn(db_path) as conn:
        row = conn.execute("SELECT times_practiced FROM words WHERE word = ? COLLATE NOCASE;", (word,)).fetchone()
        new_times = (row["times_practiced"] + 1) if row else 1
        next_review_iso = calculate_next_review(new_status, new_times, now)

        cur = conn.execute("""
            UPDATE words
            SET status = ?,
                times_practiced = ?,
                last_practiced = ?,
                next_review = ?,
                notes = COALESCE(?, notes)
            WHERE word = ? COLLATE NOCASE;
        """, (new_status, new_times, now_iso, next_review_iso, notes, word))
        if cur.rowcount == 0:
            conn.execute("""
                INSERT INTO words (word, status, times_practiced, last_practiced, next_review, notes)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (word, new_status, new_times, now_iso, next_review_iso, notes))
        conn.commit()
    return True

def get_next(limit=5, due_only=True, db_path=DEFAULT_DB):
    init_db(db_path)
    now_iso = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    due_clause = "AND (next_review IS NULL OR next_review <= ?)" if due_only else ""
    params = (now_iso, limit) if due_only else (limit,)
    query = f"""
    SELECT word, status, times_practiced, last_practiced, next_review, notes
    FROM words
    WHERE status != 'LEARNED'
      {due_clause}
    ORDER BY
        CASE status
            WHEN 'REQUESTED' THEN 0
            WHEN 'DIFFICULT' THEN 1
            WHEN 'REVIEW' THEN 2
            WHEN 'PRACTICING' THEN 3
            WHEN 'NEW' THEN 4
            ELSE 5
        END,
        CASE WHEN next_review IS NULL THEN 0 ELSE 1 END,
        next_review ASC,
        RANDOM()
    LIMIT ?;
    """
    with get_conn(db_path) as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

def list_words(status=None, db_path=DEFAULT_DB):
    init_db(db_path)
    with get_conn(db_path) as conn:
        if status:
            rows = conn.execute(
                "SELECT word, status, times_practiced, last_practiced, next_review, notes FROM words WHERE status = ? COLLATE NOCASE ORDER BY word ASC;",
                (status.upper(),)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT word, status, times_practiced, last_practiced, next_review, notes FROM words ORDER BY word ASC;"
            ).fetchall()
        return [dict(r) for r in rows]

def get_stats(db_path=DEFAULT_DB):
    init_db(db_path)
    with get_conn(db_path) as conn:
        rows = conn.execute("SELECT status, COUNT(*) as count FROM words GROUP BY status;").fetchall()
        total = conn.execute("SELECT COUNT(*) FROM words;").fetchone()[0]
        counts = {r["status"]: r["count"] for r in rows}
        return {"total": total, "by_status": counts}

def run_tests():
    test_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_vocab.db")
    if os.path.exists(test_db):
        os.remove(test_db)
    try:
        init_db(test_db)
        # Add
        add_words(["reluctant", "subtle", "overwhelming"], db_path=test_db)
        words = list_words(db_path=test_db)
        assert len(words) == 3, f"Expected 3 words, got {len(words)}"
        assert words[0]["status"] == "REQUESTED"

        # Update
        update_word("reluctant", "done", db_path=test_db)
        update_word("subtle", "practice again", db_path=test_db)
        update_word("overwhelming", "difficult", db_path=test_db)

        # Spaced repetition check:
        # 'subtle' has next_review tomorrow (+1 day), so with due_only=True it should NOT be due!
        # 'overwhelming' is DIFFICULT so next_review is now (due immediately)
        nxt_due = get_next(limit=5, due_only=True, db_path=test_db)
        assert len(nxt_due) == 1
        assert nxt_due[0]["word"].lower() == "overwhelming"

        # With due_only=False, subtle is returned
        nxt_all = get_next(limit=5, due_only=False, db_path=test_db)
        assert len(nxt_all) == 2

        # Remove
        update_word("subtle", "remove", db_path=test_db)
        assert len(list_words(db_path=test_db)) == 2

        # Stats
        stats = get_stats(db_path=test_db)
        assert stats["total"] == 2
        print("All tests passed successfully.")
    finally:
        if os.path.exists(test_db):
            os.remove(test_db)

def main():
    parser = argparse.ArgumentParser(description="Minimal vocabulary store CLI")
    subparsers = parser.add_subparsers(dest="command")

    # add
    p_add = subparsers.add_parser("add", help="Add one or more words")
    p_add.add_argument("words", nargs="+", help="Words to add")
    p_add.add_argument("--notes", help="Optional notes")

    # update
    p_up = subparsers.add_parser("update", help="Update a word status")
    p_up.add_argument("word", help="Word to update")
    p_up.add_argument("action", help="Action/Status (done, practice again, difficult, review, remove)")
    p_up.add_argument("--notes", help="Optional notes")

    # next
    p_next = subparsers.add_parser("next", help="Get next batch of words to practice")
    p_next.add_argument("--limit", type=int, default=5, help="Number of words (default: 5)")
    p_next.add_argument("--all", action="store_true", help="Ignore spaced repetition intervals and show all words")

    # list
    p_list = subparsers.add_parser("list", help="List words")
    p_list.add_argument("--status", help="Filter by status (NEW, PRACTICING, REVIEW, LEARNED, DIFFICULT)")

    # stats
    subparsers.add_parser("stats", help="Show vocabulary statistics")

    # test
    subparsers.add_parser("test", help="Run internal self-tests")

    args = parser.parse_args()

    if args.command == "add":
        added = add_words(args.words, notes=args.notes)
        print(f"Added {len(added)} words: {', '.join(args.words)}")
    elif args.command == "update":
        update_word(args.word, args.action, notes=args.notes)
        print(f"Updated '{args.word}' -> {args.action}")
    elif args.command == "next":
        items = get_next(limit=args.limit, due_only=not getattr(args, "all", False))
        if not items:
            print("No words currently due for practice. Add new words or use: python vocab.py next --all")
        else:
            for item in items:
                print(f"- {item['word']} [{item['status']}] (practiced: {item['times_practiced']}x)")
    elif args.command == "list":
        items = list_words(status=args.status)
        if not items:
            print("Vocabulary is empty.")
        for item in items:
            due_str = item['next_review'] or 'now'
            print(f"{item['word']:<18} {item['status']:<12} practiced: {item['times_practiced']}x  due: {due_str:<20} last: {item['last_practiced'] or '-'}")
    elif args.command == "stats":
        s = get_stats()
        print(f"Total vocabulary: {s['total']}")
        for st, cnt in s["by_status"].items():
            print(f"  {st:<12}: {cnt}")
    elif args.command == "test":
        run_tests()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
