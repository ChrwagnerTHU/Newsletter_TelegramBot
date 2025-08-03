# Personalisiertes Telegram Newsletter Bot

Dieses Projekt stellt einen Telegram‑Bot bereit, der dir jeden Morgen einen persönlichen Newsletter zusendet. Der Bot kombiniert verschiedene Informationsquellen wie Wetter, Kalendertermine, Veranstaltungen, zufällige Wikipedia‑Artikel und Rezeptvorschläge.

## Funktionen

- 💬 **Interaktive Konfiguration** über den Bot (`/register`, `/edit`)
- 📰 **Newsletter** sofort anfordern (`/newsletter`) oder automatisch täglich um 05:30 Uhr erhalten
- ☀️ **Wettervorhersage** für einen gewählten Ort
- 📅 **Kalendertermine** aus einer angegebenen ICS‑URL
- 🎉 **Veranstaltungen** in deiner Stadt
- 📚 **Zufällige Wikipedia‑Artikel**
- 🍽️ **Rezeptvorschläge**

## Voraussetzungen

- Python 3.8 oder höher
- Telegram Bot Token und OpenWeatherMap API‑Key

## Installation

1. Repository klonen:
   ```bash
   git clone <repository-url>
   cd Newsletter_TelegramBot
   ```
2. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```
3. Konfigurationsdatei anpassen:
   Ersetze in `utilities/configs/config.json` die Platzhalter `TOKEN`, `TOKEN_DEV` und `WEATHER_API` durch deine eigenen Tokens.

## Nutzung

Starte den Bot mit:
```bash
python bot.py
```

Im Telegram‑Chat stehen folgende Befehle zur Verfügung:

| Befehl       | Beschreibung |
|--------------|--------------|
| `/start`     | Begrüßung und Hinweis auf verfügbare Befehle |
| `/help`      | Hilfe mit allen Befehlen |
| `/register`  | Neue Konfiguration anlegen |
| `/edit`      | Bestehende Konfiguration bearbeiten |
| `/newsletter`| Newsletter sofort senden |
| `/cancel`    | Aktuellen Vorgang abbrechen |

