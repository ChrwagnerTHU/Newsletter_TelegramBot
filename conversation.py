from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from utilities.config_manager import speichere_config

FIELDS = ["name", "place", "calendar"]

FRAGEN = {
    "name": "👤 Wie heißt du?",
    "place": "📍 Für welche Stadt soll ich den Newsletter zusammenstellen?",
    "calendar": "📅 Gib bitte die URL zu deinem Kalender an ('nein').",
}

def parse_wert(feld, eingabe):
    if feld in ["name", "place"]:
        if eingabe.strip() == "":
            return "INVALID"
        return eingabe.strip()
    if feld in ["calendar"]:
            if eingabe.strip() == "nein":
                return None
            return eingabe.strip()

    return eingabe.strip()

async def start_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["config"] = {}
    context.user_data["zustand"] = 0
    feld = FIELDS[0]
    await update.message.reply_text(FRAGEN[feld])
    return 1  # Zustand REGISTERING

async def eingabe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    zustand = context.user_data.get("zustand", 0)
    config = context.user_data.get("config", {})
    feld = FIELDS[zustand]

    wert = parse_wert(feld, text)
    if wert == "INVALID":
        await update.message.reply_text(f"⚠️ Ungültige Eingabe. Bitte erneut:\n{FRAGEN[feld]}")
        return 1

    config[feld] = wert
    context.user_data["config"] = config

    zustand += 1
    if zustand >= len(FIELDS):
        user_id = str(update.effective_user.id)
        speichere_config(user_id, config)
        await update.message.reply_text("✅ Deine Konfiguration wurde gespeichert!")
        return ConversationHandler.END

    context.user_data["zustand"] = zustand
    next_feld = FIELDS[zustand]
    await update.message.reply_text(FRAGEN[next_feld])
    return 1

async def abbrechen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Vorgang abgebrochen.")
    return ConversationHandler.END
