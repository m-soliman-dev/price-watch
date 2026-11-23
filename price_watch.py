#!/usr/bin/env python3
"""price-watch - watch product prices and get alerted when they drop.

Track products by URL, record every price you check, and get an alert the
moment a price falls to (or below) your target. Ships with a ready-made
extractor for the books.toscrape.com practice shop, and a regex mode that
works with any page.

Usage:
    python price_watch.py add "A Light in the Attic" \
        --url https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html \
        --target 40
    python price_watch.py check          # check every tracked product once
    python price_watch.py history "A Light in the Attic"
"""

import argparse
import json
from html import unescape
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

STORE = Path.home() / ".price_watch.json"
USER_AGENT = "price-watch/1.0 (+https://github.com/m-soliman-dev/price-watch)"

# Price patterns: first match wins. The practice shop uses pounds.
PRICE_PATTERNS = [
    re.compile(r'class="price_color"[^>]*>\s*[£$€]?\s*([0-9]+(?:\.[0-9]{1,2})?)'),
    re.compile(r'[£$€]\s*([0-9]+(?:\.[0-9]{1,2})?)'),
]


def fetch(url):
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=15) as response:
        return response.read().decode("utf-8", errors="replace")


def extract_price(html):
    """Pull the first recognisable price out of a page's HTML."""
    html = unescape(html)
    for pattern in PRICE_PATTERNS:
        match = pattern.search(html)
        if match:
            return float(match.group(1))
    return None


def load_store(path=STORE):
    path = Path(path)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def save_store(store, path=STORE):
    Path(path).write_text(json.dumps(store, indent=2), encoding="utf-8")


def check_product(name, product, fetcher=fetch):
    """Fetch the current price for one product and record it.

    Returns (current_price, alert) where alert is True when the price is at
    or below the target.
    """
    html = fetcher(product["url"])
    price = extract_price(html)
    if price is None:
        raise ValueError(f"no price found on the page for {name!r}")
    product.setdefault("history", []).append(
        {"date": datetime.now(timezone.utc).isoformat(timespec="seconds"),
         "price": price})
    return price, price <= product["target"]


def cmd_add(args):
    store = load_store()
    store[args.name] = {"url": args.url, "target": args.target,
                        "history": []}
    save_store(store)
    print(f"tracking {args.name!r} - alert at {args.target:g} or below")
    return 0


def cmd_check(args):
    store = load_store()
    if not store:
        print("nothing tracked yet - use: price_watch.py add ...")
        return 0
    exit_code = 0
    for name, product in store.items():
        try:
            price, alert = check_product(name, product)
        except (OSError, ValueError) as error:
            print(f"{name}: error: {error}", file=sys.stderr)
            exit_code = 1
            continue
        lowest = min(h["price"] for h in product["history"])
        status = "*** PRICE ALERT ***" if alert else "no alert"
        print(f"{name}: {price:g} (lowest seen {lowest:g}, "
              f"target {product['target']:g}) - {status}")
    save_store(store)
    return exit_code


def cmd_history(args):
    store = load_store()
    product = store.get(args.name)
    if product is None:
        print(f"not tracked: {args.name!r}", file=sys.stderr)
        return 1
    for entry in product["history"]:
        print(f"{entry['date']}  {entry['price']:g}")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add", help="track a product")
    add.add_argument("name")
    add.add_argument("--url", required=True)
    add.add_argument("--target", type=float, required=True,
                     help="alert when the price drops to this or lower")
    add.set_defaults(func=cmd_add)

    check = commands.add_parser("check", help="check all tracked products")
    check.set_defaults(func=cmd_check)

    history = commands.add_parser("history", help="show recorded prices")
    history.add_argument("name")
    history.set_defaults(func=cmd_history)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
