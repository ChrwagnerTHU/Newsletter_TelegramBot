import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters, ConversationHandler
)
from conversation import FIELDS, FRAGEN, start_add, eingabe, abbrechen
from utilities import config_manager
from newsletter import send_newsletter
import schedule
import asyncio

TELEGRAM_BOT_TOKEN = config_manager.get_telegram_token(True)
MAX_LENGTH = 4096

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EDITING, REGISTERING = range(2)


def split_message(text, max_length=MAX_LENGTH):
    parts = []
    while len(text) > max_length:
        # Split an einem Zeilenumbruch, wenn möglich
        split_index = text.rfind('\n', 0, max_length)
        if split_index == -1:
            split_index = max_length  # Notfalls hart trennen

        parts.append(text[:split_index])
        text = text[split_index:]
    parts.append(text)
    return parts

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Willkommen beim persönlichen Tages-Newsletter!\n"
        "➡️ Nutze /help für alle verfügbaren Befehle.\n"
        "➡️ Starte die Konfiguration mit /register, solltest du das erste mal diesen Service nutzen"
    )

# /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📘 <b>Verfügbare Befehle:</b>\n"
        "/start – Begrüßung\n"
        "/help – Hilfe anzeigen\n"
        "/register – Konfiguration neu anlegen\n"
        "/edit – Bestehende Konfiguration bearbeiten\n"
        "/newsletter – Newsletter sofort erhalten\n"
        "/cancel – Abbrechen eines laufenden Vorgangs",
        parse_mode="HTML"
    )

# /register
async def edit_suche(update, context):
    user_id = str(update.effective_user.id)
    config = config_manager.lade_config(user_id)

    if not config:
        await update.message.reply_text("⚠️ Keine Konfiguration gefunden. Bitte nutze /register.")
        return ConversationHandler.END

    context.user_data["config"] = config
    context.user_data["zustand"] = 0
    feld = FIELDS[0]
    await update.message.reply_text(f"✏️ Neuer Wert für:\n{FRAGEN[feld]}")
    return EDITING

# Eingabe beim Editieren
async def save_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text.strip()
    zustand = context.user_data.get("zustand", 0)
    feld = FIELDS[zustand]

    context.user_data["config"][feld] = text
    zustand += 1

    if zustand >= len(FIELDS):
        config_manager.speichere_config(user_id, context.user_data["config"])
        await update.message.reply_text("✅ Konfiguration aktualisiert.")
        return ConversationHandler.END

    context.user_data["zustand"] = zustand
    nächstes_feld = FIELDS[zustand]
    await update.message.reply_text(FRAGEN[nächstes_feld])
    return EDITING

# /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Abgebrochen.")
    return ConversationHandler.END

# /newsletter
async def send_newsletter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    config = config_manager.lade_config(user_id)
    if not config:
        await update.message.reply_text("⚠️ Keine Konfiguration gefunden. Bitte nutze zuerst /register.")
        return

    await update.message.reply_text("📰 Erstelle deinen Newsletter...")

    try:
        content = send_newsletter(config)
        messages = split_message(content)
        for part in messages:
            await update.message.reply_text(part, parse_mode="HTML", disable_web_page_preview=False)
    except Exception as e:
        await update.message.reply_text(f"❌ Fehler beim Senden des Newsletters:\n{e}")

def schedule_jobs(application):
    async def job():
        for chat_id in config_manager.get_all_user_ids():
            config = config_manager.lade_config(chat_id)
            content = send_newsletter(config)
            messages = split_message(content)
            for part in messages:
                await application.bot.send_message(chat_id=chat_id, text=part, parse_mode="HTML")

    async def scheduler():
        schedule.every().day.at("05:30").do(lambda: asyncio.create_task(job()))
        while True:
            schedule.run_pending()
            await asyncio.sleep(30)

    asyncio.create_task(scheduler())

async def post_init(application):
    schedule_jobs(application)

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("newsletter", send_newsletter_command))

    register_conv = ConversationHandler(
        entry_points=[CommandHandler("register", start_add)],
        states={REGISTERING: [MessageHandler(filters.TEXT & ~filters.COMMAND, eingabe)]},
        fallbacks=[CommandHandler("cancel", abbrechen)],
    )
    app.add_handler(register_conv)

    edit_conv = ConversationHandler(
        entry_points=[CommandHandler("edit", edit_suche)],
        states={EDITING: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_edit)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(edit_conv)

    app.run_polling()

if __name__ == "__main__":
    main()