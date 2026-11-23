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

## Case study

**The problem.** Prices change constantly, and nobody wants to re-check a
product page every day to catch a drop.

**Technologies.** Pure Python 3. Prices are pulled from the page HTML with
regular expressions that understand common formats (£, $, €), every check is
recorded with a UTC timestamp in a JSON history file, and the network call
is injected so the tests never touch the internet.

**The result.** `check` reports the current price, the lowest price ever
seen and your target for every tracked product, and flags `PRICE ALERT` the
moment a price falls to your target or below. `history` shows the full price
timeline for any product.

**Limits (being upfront).** It checks when you tell it to - run `check`
yourself or schedule it with cron or Task Scheduler (hourly or daily is
plenty, and kinder to the shop). There is no built-in email or phone
notification yet; alerts print to the terminal, and wiring them to an email
or messaging service is the natural next step. It reads prices from the page
HTML, so a site that hides prices behind JavaScript needs a different
extractor.
