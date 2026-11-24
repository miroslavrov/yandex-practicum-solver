"""Shared helpers for Practicum browser automation."""
import json, os

COOKIES_FILE = os.environ.get("PRACTICUM_COOKIES", "practicum_cookies.txt")
STATE_FILE = os.environ.get("PRACTICUM_STATE", "practicum_state.json")


def netscape_to_playwright(path=COOKIES_FILE):
    cookies = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 7:
            continue
        domain, flag, path_, secure, expiry, name, value = parts[:7]
        c = {
            "name": name,
            "value": value,
            "path": path_,
            "domain": domain,
            "secure": secure.upper() == "TRUE",
            "httpOnly": False,
            "sameSite": "Lax",
        }
        try:
            exp = int(expiry)
            if exp > 0:
                c["expires"] = exp
        except ValueError:
            pass
        cookies.append(c)
    return cookies


def save_state(context, path=STATE_FILE):
    context.storage_state(path=path)


def new_context(browser, viewport=(1400, 900)):
    """Fresh context pre-loaded with the Yandex session cookies."""
    ctx = browser.new_context(viewport={"width": viewport[0], "height": viewport[1]},
                              locale="ru-RU")
    ctx.add_cookies(netscape_to_playwright())
    return ctx
