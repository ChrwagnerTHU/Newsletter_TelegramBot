from urllib.parse import quote

import requests

import config_manager

RANDOM_SUMMARY_URL = "https://de.wikipedia.org/api/rest_v1/page/random/summary"
DEFAULT_USER_AGENT = "NewsletterTelegramBot/1.0 (contact: example@example.com)"


def _get_user_agent():
    meta_config = config_manager.get_meta_config()
    return meta_config.get("WIKI_USER_AGENT", DEFAULT_USER_AGENT)

def main():
    headers = {"User-Agent": _get_user_agent()}
    try:
        response = requests.get(RANDOM_SUMMARY_URL, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception:
        return None

    title = data.get("title")
    content_urls = data.get("content_urls", {})
    desktop_urls = content_urls.get("desktop", {})
    link = desktop_urls.get("page")

    if not link and title:
        title_url = quote(title.replace(" ", "_"))
        link = f"https://de.wikipedia.org/wiki/{title_url}"

    if not title or not link:
        return None

    return {"Link": link, "Header": title}

if __name__ == '__main__':
    main()
