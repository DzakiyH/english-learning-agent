import os
import re
import json
import sqlite3
import urllib.request

HTML_CACHE = r"C:\Users\INTEL\.gemini\antigravity-cli\brain\a51bd638-5f21-4254-a1b4-0babe80c0b3d\.system_generated\steps\68\content.md"
URL = "https://www.oxfordlearnersdictionaries.com/wordlists/oxford3000-5000"
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vocab.db")
JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "oxford_words.json")

def get_html():
    if os.path.exists(HTML_CACHE):
        with open(HTML_CACHE, "r", encoding="utf-8") as f:
            return f.read()
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8")

def seed():
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        conn = sqlite3.connect(DB_PATH)
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
        for item in data:
            conn.execute("""
                INSERT INTO words (word, status, times_practiced, notes)
                VALUES (?, 'NEW', 0, ?)
                ON CONFLICT(word) DO NOTHING;
            """, (item["word"], item["notes"]))
        conn.commit()
        total = conn.execute("SELECT COUNT(*) FROM words;").fetchone()[0]
        conn.close()
        print(f"Seeded from oxford_words.json. Total words in DB: {total}")
        return

    html = get_html()
    pattern = re.compile(
        r'<li\s+data-hw="([^"]+)"(?:[^>]*data-ox3000="([^"]*)")?(?:[^>]*data-ox5000="([^"]*)")?[^>]*>(.*?)</li>',
        re.DOTALL
    )

    words = {}
    for m in pattern.finditer(html):
        hw = m.group(1).strip()
        ox3 = (m.group(2) or "").strip().upper()
        ox5 = (m.group(3) or "").strip().upper()
        body = m.group(4)

        level = ox5 if ox5 in ("B1", "B2", "C1") else ox3
        if level not in ("B1", "B2", "C1"):
            continue

        pos_match = re.search(r'<span class="pos">([^<]+)</span>', body)
        pos = pos_match.group(1).strip() if pos_match else ""

        if hw not in words:
            words[hw] = {"level": level, "pos": [pos] if pos else []}
        else:
            if pos and pos not in words[hw]["pos"]:
                words[hw]["pos"].append(pos)

    # Insert into SQLite vocab.db
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS words (
            word TEXT PRIMARY KEY COLLATE NOCASE,
            status TEXT DEFAULT 'NEW',
            times_practiced INTEGER DEFAULT 0,
            last_practiced TEXT,
            notes TEXT
        );
    """)

    inserted = 0
    for hw, info in words.items():
        pos_str = ", ".join(info["pos"])
        notes = f"{info['level']} | {pos_str}" if pos_str else info["level"]
        cur = conn.execute("""
            INSERT INTO words (word, status, times_practiced, notes)
            VALUES (?, 'NEW', 0, ?)
            ON CONFLICT(word) DO NOTHING;
        """, (hw, notes))
        if cur.rowcount > 0:
            inserted += cur.rowcount

    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM words;").fetchone()[0]
    conn.close()

    print(f"Extracted: {len(words)} unique B1/B2/C1 words from Oxford 3000/5000.")
    print(f"Inserted: {inserted} new words into vocab.db (Total in DB: {total}).")

if __name__ == "__main__":
    seed()
