import os
import sys
import json
import logging
import urllib.request
import urllib.error

# Import our local vocabulary engine
import vocab

# Try loading .env file if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import telebot

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Credentials
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ALLOWED_USER_ID = os.getenv("ALLOWED_USER_ID")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")

if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN not found! Please set it in your .env file or environment.")
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not found! Please set it in your .env file or environment.")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else None

# Helper: Call Google Gemini (using official google-genai or direct REST fallback)
def call_gemini(prompt, system_instruction=None, json_mode=False):
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured.")

    # 1. Try google-genai SDK if installed
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=GEMINI_API_KEY)
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json" if json_mode else "text/plain"
        )
        resp = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=config
        )
        return resp.text
    except ImportError:
        pass

    # 2. Lean REST fallback (standard library urllib)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    if system_instruction:
        payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
    if json_mode:
        payload["generationConfig"] = {"responseMimeType": "application/json"}

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        logger.error(f"Gemini API error: {err_msg}")
        raise RuntimeError(f"Gemini API Error: {err_msg}")

# System prompt for study material generation
MATERIAL_RULES = """
You are an expert English language learning content generator following strict material guidelines.

For each target word provided:
1. Header block:
   - Pronunciation: IPA transcription + plain sound approximation (e.g. /beər/ — sounds like "bair" (rhymes with hair, care)).
   - Word forms: list all verb forms if a verb (base → past → past participle | -ing | 3rd person) or noun/adj forms.
2. Paragraphs:
   - One paragraph per DISTINCT meaning/use of the word.
   - Each paragraph must use the word in a DIFFERENT way (different meaning or pattern).
   - Priority: Different USAGE > different TOPIC.
   - Include noun/verb senses naturally.
   - After each paragraph, include an italic note: *Pattern note: ...* showing collocations or usage traps.
3. Closing blocks per word:
   - Fixed expressions (common idioms/phrases with short meaning and example).
   - Quick recap table (one row per form/sense with a model sentence).

At the very end of the session, scan the generated text and output:
### 💡 Candidate Words Discovered in This Session
- **[word]** (IPA) — short definition (from [target word] paragraph [N])
- **[word]** (IPA) — short definition (from [target word] paragraph [N])

Tone: Clean, natural English, context makes meaning obvious, no dictionary-like stiff sentences.
"""

def is_authorized(message):
    if not ALLOWED_USER_ID:
        return True
    return str(message.from_user.id) == str(ALLOWED_USER_ID).strip()

def send_long_message(chat_id, text):
    """Safely send messages that might exceed Telegram 4096 character limit."""
    max_len = 4000
    if len(text) <= max_len:
        bot.send_message(chat_id, text, parse_mode="Markdown")
        return

    # Split by markdown headers or dividers
    chunks = text.split("\n---\n")
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        if len(chunk) <= max_len:
            try:
                bot.send_message(chat_id, chunk, parse_mode="Markdown")
            except Exception:
                bot.send_message(chat_id, chunk)
        else:
            # Fallback hard chunking
            for i in range(0, len(chunk), max_len):
                sub = chunk[i:i+max_len]
                try:
                    bot.send_message(chat_id, sub, parse_mode="Markdown")
                except Exception:
                    bot.send_message(chat_id, sub)

def generate_lesson_for_user(chat_id, limit=3, force_all=False):
    items = vocab.get_next(limit=limit, due_only=not force_all)
    if not items:
        # Check if there are any words at all
        all_items = vocab.get_next(limit=limit, due_only=False)
        if all_items:
            bot.send_message(
                chat_id,
                "🎉 You're all caught up on scheduled reviews for today!\n\n"
                "To practice ahead anyway, send `/today all` or type *give me more words*.",
                parse_mode="Markdown"
            )
        else:
            bot.send_message(
                chat_id,
                "Vocabulary list is currently empty. Add words with `/add <word>` or seed with Oxford 3000/5000."
            )
        return

    words_list = [item["word"] for item in items]
    bot.send_message(chat_id, f"📖 Generating today's lesson for: *{', '.join(words_list)}*...", parse_mode="Markdown")

    prompt = f"Generate complete learning materials for the following target words: {', '.join(words_list)}."
    try:
        lesson = call_gemini(prompt, system_instruction=MATERIAL_RULES)
        send_long_message(chat_id, lesson)
        bot.send_message(
            chat_id,
            "💬 *When done, reply naturally:*\n"
            "• `done` (learned)\n"
            "• `practice again` (review soon)\n"
            "• `difficult` (priority review)\n"
            "• `add <word>` (queue a new word)\n\n"
            "_Example: 'rare is done, but let's practice descent again'_",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error generating lesson: {e}")
        bot.send_message(chat_id, f"⚠️ Error generating lesson: {e}")

# Telegram Handlers
if bot:
    @bot.message_handler(commands=["start", "help"])
    def handle_start(message):
        if not is_authorized(message):
            bot.send_message(message.chat.id, "⛔ Access restricted.")
            return

        text = (
            "👋 *Welcome to your English Learning Agent!*\n\n"
            "• `/today` — Start today's study session\n"
            "• `/stats` — Check your vocabulary counts and progress\n"
            "• `/list` — View your words currently in review\n"
            "• `/add <word> <word>...` — Add new target words\n\n"
            "You can also chat with me completely naturally! Just text *give me today's lesson*, or reply *rare was easy, descent was hard*."
        )
        bot.send_message(message.chat.id, text, parse_mode="Markdown")

    @bot.message_handler(commands=["today", "study"])
    def handle_today(message):
        if not is_authorized(message):
            return
        args = message.text.split()
        force_all = len(args) > 1 and args[1].lower() == "all"
        generate_lesson_for_user(message.chat.id, limit=3, force_all=force_all)

    @bot.message_handler(commands=["stats"])
    def handle_stats(message):
        if not is_authorized(message):
            return
        s = vocab.get_stats()
        text = f"📊 *Vocabulary Statistics*\n\n*Total Words:* {s['total']}\n"
        for st, count in s["by_status"].items():
            text += f"• `{st:<12}`: {count}\n"
        bot.send_message(message.chat.id, text, parse_mode="Markdown")

    @bot.message_handler(commands=["list"])
    def handle_list(message):
        if not is_authorized(message):
            return
        practicing = vocab.list_words(status="PRACTICING")
        requested = vocab.list_words(status="REQUESTED")
        difficult = vocab.list_words(status="DIFFICULT")
        words = requested + difficult + practicing

        if not words:
            bot.send_message(message.chat.id, "No words currently active in review queue.")
            return

        lines = ["📚 *Active Review Queue:*"]
        for w in words[:15]:
            due = w["next_review"] or "now"
            lines.append(f"• *{w['word']}* [{w['status']}] (practiced: {w['times_practiced']}x, due: {due[:10]})")
        bot.send_message(message.chat.id, "\n".join(lines), parse_mode="Markdown")

    @bot.message_handler(commands=["add"])
    def handle_add(message):
        if not is_authorized(message):
            return
        words = message.text.split()[1:]
        if not words:
            bot.send_message(message.chat.id, "Usage: `/add <word1> <word2>...`", parse_mode="Markdown")
            return
        added = vocab.add_words(words)
        bot.send_message(message.chat.id, f"✅ Added *{len(added)}* words: {', '.join(words)}", parse_mode="Markdown")

    @bot.message_handler(func=lambda m: True)
    def handle_natural_conversation(message):
        if not is_authorized(message):
            return

        user_text = message.text.strip()
        logger.info(f"Received message: {user_text}")

        # Use Gemini in JSON mode to extract intent & updates
        system_parser = """
        You are the intent parsing engine for a personal English vocabulary assistant.
        Analyze the user's message and determine what actions to execute on the vocabulary database.
        
        Possible actions for a word: "done", "practice again", "difficult", "review", "remove".
        
        Respond with ONLY a JSON object with this exact structure:
        {
          "is_study_request": boolean,      // true if user asks to study, start lesson, get words, etc.
          "evaluations": [                 // word evaluations/status updates from user
            {"word": "word_name", "action": "done"|"practice again"|"difficult"|"remove"}
          ],
          "add_words": ["word1", "word2"], // words the user wants to add to practice
          "reply": "Friendly concise answer or confirmation to the user"
        }
        """

        try:
            raw_json = call_gemini(f"User message: {user_text}", system_instruction=system_parser, json_mode=True)
            # Strip markdown fences if present
            clean_json = raw_json.strip()
            if clean_json.startswith("```"):
                clean_json = clean_json.strip("`").replace("json\n", "", 1).strip()
            data = json.loads(clean_json)

            actions_taken = []

            # 1. Handle evaluations
            if data.get("evaluations"):
                for ev in data["evaluations"]:
                    w, act = ev.get("word"), ev.get("action")
                    if w and act:
                        vocab.update_word(w, act)
                        actions_taken.append(f"• *{w}* → `{act}`")

            # 2. Handle words to add
            if data.get("add_words"):
                vocab.add_words(data["add_words"])
                actions_taken.append(f"• Added to queue: *{', '.join(data['add_words'])}*")

            # 3. Handle study request
            if data.get("is_study_request"):
                if actions_taken:
                    bot.send_message(message.chat.id, "✅ Updates saved:\n" + "\n".join(actions_taken), parse_mode="Markdown")
                generate_lesson_for_user(message.chat.id)
                return

            # 4. Standard conversational reply
            response_text = data.get("reply", "Understood!")
            if actions_taken:
                response_text = "✅ Updates recorded:\n" + "\n".join(actions_taken) + "\n\n" + response_text

            bot.send_message(message.chat.id, response_text, parse_mode="Markdown")

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            bot.send_message(message.chat.id, f"Sorry, I had trouble processing that: {e}")

def main():
    if not bot:
        print("Error: TELEGRAM_BOT_TOKEN is not set. Please configure .env file.")
        sys.exit(1)
    print("🤖 English Learning Telegram Bot is running! Press Ctrl+C to stop.")
    bot.infinity_polling()

if __name__ == "__main__":
    main()
