# price-watch

Watch product prices and get alerted when they drop to your target. Track as
many products as you like; every check is recorded so you can see the full
price history. Pure Python 3, no packages to install.

## What it does

- Tracks products by URL, each with your own target price
- Checks every tracked product with one command and prints alerts
- Records every price it sees, so you can review the history
- Understands common price formats (£, $, €) out of the box

## Usage

```bash
# Track a book on the practice shop, alert at 40 or below
python price_watch.py add "A Light in the Attic" \
    --url https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html \
    --target 40

# Check everything you track (run it daily, or from a scheduler)
python price_watch.py check

# See every price recorded so far
python price_watch.py history "A Light in the Attic"
```

Example check output:

```
A Light in the Attic: 51.77 (lowest seen 48.5, target 40) - no alert
```

## Running the tests

```bash
python -m unittest test_price_watch.py -v
```

The tests use saved sample pages, so they run offline.

## What I learned building this

- Fetching pages and extracting data with regular expressions
- Keeping a time-stamped history in JSON
- Designing for testability: the network call is injected, so tests never
  touch the internet
- Building a CLI with subcommands (`add`, `check`, `history`)
