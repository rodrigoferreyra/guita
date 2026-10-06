# Guita

Local-first CLI for manually tracking personal savings.

Guita records money added to, removed from, and transferred between accounts. It keeps an auditable ledger so you can see balances, history, fees, and how savings change over time.

It is intentionally **not** a budgeting app, expense tracker, or bank aggregator.

```bash
guita + 80 wise
guita - 80 wise
guita transfer 500 wise wallbit
guita transfer 500 wise wallbit --fee 5
```

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

This installs the `guita` command.

## Quick start

```bash
guita account add Wise
guita account add Wallbit
guita + 1000 wise
guita transfer 500 wise wallbit --fee 5
guita
```

## Concepts

| Concept | Meaning |
|---------|---------|
| **Account** | A place money is held (e.g. Wise, Wallbit). Names are case-insensitive. |
| **Addition (`+`)** | Money added to savings. |
| **Removal (`-`)** | Money removed from savings. |
| **Transfer** | Move money from one account to another. Does not change total savings unless there is a fee. |
| **Fee** | Optional cost tied to a transaction. Always reduces total savings. |
| **Snapshot** | A manually recorded real-world balance. Does **not** change the ledger. |

### Money rules (v0.1)

- Currency is **USD only**
- Amounts use up to **2 decimal places** (no silent rounding)
- Amounts must be **positive**; direction comes from the command
- Account balances cannot go negative
- Transfer fee is paid by the **destination** account
- Transfer syntax: `guita transfer <amount> <sender> <recipient> [--fee <amount>]`

### Amount input

Monetary values (amounts, fees, snapshots, goals) accept **`.` or `,` as the decimal separator**:

```bash
guita + 42.5 upwork
guita + 42,5 upwork
guita + 42,5 297,5 upwork
guita transfer 500 wise wallbit --fee 2,5
guita snapshot wise 1820,00
```

If both separators appear in one number, the **last** one is the decimal and the other is treated as thousands grouping:

| Input | Meaning |
|-------|---------|
| `42,5` / `42.5` | 42.50 |
| `1000,50` / `1000.50` | 1000.50 |
| `1.234,56` | 1234.56 |
| `1,234.56` | 1234.56 |

Output is always shown with a dot decimal and US-style grouping (e.g. `$1,234.56`).

Fee examples:

| Command | Effect |
|---------|--------|
| `guita + 100 wise --fee 2` | Wise +$98 net; total savings +$98 |
| `guita - 100 wise --fee 2` | Wise -$102 net; total savings -$102 |
| `guita transfer 100 wise wallbit --fee 2` | Wise -$100; Wallbit +$98; total savings -$2 |

## Storage

- Default database: `~/.local/share/guita/guita.db` (or `$XDG_DATA_HOME/guita/guita.db`)
- Override with `GUITA_DATABASE=/path/to/file.db`
- All data stays local; nothing is sent over the network

Check location anytime:

```bash
guita info
```

## Commands

Every command supports `-h` / `--help`.

### `guita` / `guita balance`

Show current balances for all accounts and the total.

```bash
guita
guita balance
```

### `guita +`

Add money to an account. Multiple amounts before the account name are summed into one addition.

```bash
guita + <amount> [<amount> ...] <account> [--fee <amount>]
```

Examples:

```bash
guita + 80 wise
guita + 42.5 297.5 upwork
guita + 42,5 297,5 upwork
guita + 100 wise --fee 2
guita + 100 wise --fee 2,5
```

### `guita -`

Remove money from an account. Multiple amounts before the account name are summed into one removal.

```bash
guita - <amount> [<amount> ...] <account> [--fee <amount>]
```

Examples:

```bash
guita - 80 wise
guita - 20 15.5 wise
guita - 20 15,5 wise
guita - 100 wise --fee 2
```

### `guita transfer`

Move money from a sender account to a recipient account.

```bash
guita transfer <amount> <source> <destination> [--fee <amount>]
```

- First account = **sender**
- Second account = **recipient**
- Optional `--fee` is paid by the **destination**

Examples:

```bash
guita transfer 500 wise wallbit
guita transfer 500 wise wallbit --fee 5
guita transfer 500,50 wise wallbit --fee 2,5
```

### `guita history`

Show transaction history, or historical totals.

```bash
guita history [--account <name>] [--from YYYY-MM-DD] [--to YYYY-MM-DD] [--type addition|removal|transfer] [--balances]
```

Examples:

```bash
guita history
guita history --account wise
guita history --from 2026-10-01 --to 2026-10-31
guita history --type transfer
guita history --balances
```

`--balances` shows how total savings changed by day.

### `guita snapshot`

Record the observed real-world balance of an account. This does not alter ledger balances; it is for reconciliation.

```bash
guita snapshot <account> <actual-balance>
```

Example:

```bash
guita snapshot wise 1820
guita snapshot wise 1820,50
```

Shows ledger balance, actual balance, and the difference.

### `guita stats`

Show savings statistics for **this month** and **all time**, with simple bar graphs and a savings-over-time chart.

```bash
guita stats
```

Transfers do not affect net savings except through fees.

Positive amounts are shown in green and negative amounts in red when the terminal supports color. Set `NO_COLOR=1` to disable.

### `guita goal`

Set or show an informational savings goal.

```bash
guita goal [amount]
```

Examples:

```bash
guita goal 10000
guita goal
```

### `guita export`

Export the transaction ledger to CSV or JSON.

```bash
guita export [path]
```

- Default path: `transactions.csv`
- Use a `.json` suffix for JSON

Examples:

```bash
guita export
guita export transactions.csv
guita export ledger.json
```

### `guita backup`

Copy the SQLite database to a backup file.

```bash
guita backup [path]
```

If `path` is omitted, a timestamped file is written next to the database.

Examples:

```bash
guita backup
guita backup ~/backups/guita.db
```

### `guita info`

Show version and database path.

```bash
guita info
```

### `guita account`

Manage accounts.

#### `guita account add`

Create an account. Currency defaults to USD (currently the only supported currency).

```bash
guita account add <name> [currency]
```

Examples:

```bash
guita account add Wise
guita account add Wallbit USD
guita account add Binance
guita account add Cash
```

#### `guita account list`

List all accounts and whether each is active or inactive.

```bash
guita account list
```

#### `guita account deactivate`

Deactivate an account. Deactivated accounts remain visible in balances/history but cannot receive new transactions.

```bash
guita account deactivate <name>
```

Example:

```bash
guita account deactivate Upwork
```

## Corrections

Guita does not delete or rewrite history. To fix a mistake, record a corrective transaction (for example, remove the excess amount). The original entry stays in the ledger.

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Product requirements live in [`.cursor/docs/srs.md`](.cursor/docs/srs.md).
