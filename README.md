# Guita

**Guita** is a CLI application for manually tracking personal savings. Guita stores an auditable **ledger** of additions, removals, transfers, and fees. It shows current balances, history, and how total savings change over time. It is not a budgeting tool, expense categorizer, bank aggregator, or investment tracker.

```bash
guita + 80 wise
guita - 80 wise
guita transfer 500 wise wallbit
guita transfer 500 wise wallbit --fee 5
```

## How it works

Guita treats savings as money held in named **accounts**. You record movements yourself. The application calculates balances from the ledger and keeps history intact.

Each **account** has a name and a currency. In the current version, currency is **USD** only. Account names are matched case-insensitively and stored with the capitalization you enter.

A **transaction** is one of:

- **Addition** (`+`): money added to savings in an account
- **Removal** (`-`): money removed from savings in an account
- **Transfer**: money moved from a **sender** account to a **recipient** account

A **fee** is an optional cost tied to a transaction. Fees always reduce total savings. For transfers, the **destination** account pays the fee.

A **snapshot** is a manually recorded real-world balance for an account. Snapshots do not change the ledger. They exist so you can compare calculated balances with what you observe outside Guita.

Corrections stay append-only. To fix a mistake, record another transaction rather than editing or deleting history.

## Key features

- Record additions, removals, and transfers from the terminal
- Attach optional fees that reduce total savings
- Sum several amounts in one `+` or `-` command
- Accept `.` or `,` as the decimal separator on input
- List balances, history, monthly and all-time statistics, and a savings goal
- Export the ledger and back up the local database
- Keep all data on your machine with no network requirement for normal use

## Main benefits

- Answers “how much money do I have, where is it, and how has it changed?” without categories or budgets
- Keeps an auditable history suitable for later review
- Uses exact decimal arithmetic so monetary values are not stored as binary floating-point

**Note:** Positive amounts appear in green and negative amounts in red when the terminal supports color. Set `NO_COLOR=1` to disable color.

## Install Guita

Install Guita in a Python virtual environment so the `guita` command is available on your path.

1. Create and activate a virtual environment in the project directory.
2. Install the package in editable mode with development dependencies.
3. Confirm the command is available.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
guita info
```

`guita info` prints the version and the database path. The default database location is `~/.local/share/guita/guita.db`, or `$XDG_DATA_HOME/guita/guita.db` when `XDG_DATA_HOME` is set. Override the path with the `GUITA_DATABASE` environment variable.

## Get started with your first balances

Create accounts, record an addition, move money between accounts, then view balances.

1. Add the accounts you use.
2. Add money to an account.
3. Transfer money to another account, with an optional fee.
4. Display balances.

```bash
guita account add Wise
guita account add Wallbit
guita + 1000 wise
guita transfer 500 wise wallbit --fee 5
guita
```

Running `guita` with no subcommand shows the same balance summary as **`guita balance`**.

## Manage accounts

Accounts are the places where Guita holds balances. Create them before you record transactions.

### Add an account

1. Run **`guita account add`** with the account name.
2. Optionally pass the currency. The default is *USD*, which is the only supported currency in this version.

```bash
guita account add Wise
guita account add Wallbit USD
guita account add Binance
guita account add Cash
```

### List accounts

Run **`guita account list`** to show each account, its currency, and whether it is active or inactive.

```bash
guita account list
```

### Deactivate an account

Run **`guita account deactivate`** with the account name. Inactive accounts remain visible in balances and history, but they reject new transactions.

```bash
guita account deactivate Upwork
```

## Record money movements

Amounts must be positive. The command chooses the direction. Values use at most two decimal places and are not silently rounded.

### Add money

Run **`guita +`** with one or more amounts, then the account name. Multiple amounts are summed into one addition.

```bash
guita + 80 wise
guita + 42.5 297.5 upwork
guita + 42,5 297,5 upwork
guita + 100 wise --fee 2
guita + 100 wise --fee 2,5
```

### Remove money

Run **`guita -`** with one or more amounts, then the account name. Multiple amounts are summed into one removal.

```bash
guita - 80 wise
guita - 20 15.5 wise
guita - 20 15,5 wise
guita - 100 wise --fee 2
```

### Transfer money

Run **`guita transfer`** with the amount, the **sender**, and the **recipient**. The first account is always the sender. The second is always the recipient. An optional **`--fee`** is paid by the destination account.

```bash
guita transfer 500 wise wallbit
guita transfer 500 wise wallbit --fee 5
guita transfer 500,50 wise wallbit --fee 2,5
```

A transfer without a fee does not change total savings. A transfer with a fee reduces total savings by the fee amount.

## Review history and statistics

### Show transaction history

Run **`guita history`** to list recorded movements. Filter with **`--account`**, **`--from`**, **`--to`**, and **`--type`**. Use **`--balances`** to show how total savings changed by day.

```bash
guita history
guita history --account wise
guita history --from 2026-10-01 --to 2026-10-31
guita history --type transfer
guita history --balances
```

Valid **`--type`** values are *addition*, *removal*, and *transfer*.

### Record a snapshot

Run **`guita snapshot`** with the account name and the observed balance. Guita prints the ledger balance, the actual balance, and the difference. The ledger itself does not change.

```bash
guita snapshot wise 1820
guita snapshot wise 1820,50
```

### Show statistics

Run **`guita stats`** to see this month’s figures, all-time figures since the first transaction, bar graphs for the period breakdown, and a savings-over-time chart.

```bash
guita stats
```

Transfer principal does not affect net savings. Fees do.

### Set or show a savings goal

Run **`guita goal`** with an amount to set a goal, or without an amount to show progress.

```bash
guita goal 10000
guita goal
```

The goal is informational only. Guita does not create budgets or recommendations from it.

## Export and back up your data

### Export the ledger

Run **`guita export`** with an optional path. The default file is *transactions.csv*. Use a `.json` suffix for JSON output.

```bash
guita export
guita export transactions.csv
guita export ledger.json
```

### Back up the database

Run **`guita backup`** to copy the SQLite database. If you omit the path, Guita writes a timestamped file next to the database.

```bash
guita backup
guita backup ~/backups/guita.db
```

## Show version and database location

Run **`guita info`** to print the product name, version, and database path.

```bash
guita info
```

## Get command help

Every command accepts **`-h`** or **`--help`**.

```bash
guita -h
guita transfer -h
guita account -h
```

## Reference

### Core concepts

| Concept | Meaning |
|---------|---------|
| **Account** | A named place where money is held. Names are case-insensitive. |
| **Addition** | Money added to an account (`guita +`). |
| **Removal** | Money removed from an account (`guita -`). |
| **Transfer** | Money moved from sender to recipient. Does not change total savings unless a fee is present. |
| **Fee** | Optional cost tied to a transaction. Always reduces total savings. On transfers, paid by the destination. |
| **Snapshot** | Observed real-world balance. Does not alter the ledger. |
| **Ledger** | Append-oriented history of transactions used to calculate balances. |

### Money rules

- Currency is **USD** only in this version.
- Amounts use up to **2** decimal places. Excess precision is rejected.
- Entered amounts must be **positive**. Direction comes from the command.
- Account balances cannot go negative.
- Transfer fee is paid by the **destination** account.

### Amount input

Monetary values for amounts, fees, snapshots, and goals accept **`.`** or **`,`** as the decimal separator.

| Input | Meaning |
|-------|---------|
| `42,5` / `42.5` | 42.50 |
| `1000,50` / `1000.50` | 1000.50 |
| `1.234,56` | 1234.56 |
| `1,234.56` | 1234.56 |

When both separators appear in one number, the **last** separator is the decimal and the other is thousands grouping. Display output uses a conventional format such as `$1,234.56`.

### Fee effects

| Command | Effect |
|---------|--------|
| `guita + 100 wise --fee 2` | Wise +$98 net; total savings +$98 |
| `guita - 100 wise --fee 2` | Wise -$102 net; total savings -$102 |
| `guita transfer 100 wise wallbit --fee 2` | Wise -$100; Wallbit +$98; total savings -$2 |

### Command synopsis

| Command | Purpose |
|---------|---------|
| `guita` / `guita balance` | Show account balances and total |
| `guita +` *amounts…* *account* `[--fee` *amount*`]` | Add money (sum multiple amounts) |
| `guita -` *amounts…* *account* `[--fee` *amount*`]` | Remove money (sum multiple amounts) |
| `guita transfer` *amount* *source* *destination* `[--fee` *amount*`]` | Transfer from sender to recipient |
| `guita history` | Show history; optional filters and `--balances` |
| `guita snapshot` *account* *balance* | Record an observed balance |
| `guita stats` | Show month and all-time stats with graphs |
| `guita goal` [*amount*] | Set or show a savings goal |
| `guita export` [*path*] | Export ledger to CSV or JSON |
| `guita backup` [*path*] | Copy the database file |
| `guita info` | Show version and database path |
| `guita account add` *name* [*currency*] | Create an account |
| `guita account list` | List accounts |
| `guita account deactivate` *name* | Deactivate an account |

### Storage

- Default database: `~/.local/share/guita/guita.db` (or `$XDG_DATA_HOME/guita/guita.db`)
- Override with `GUITA_DATABASE=/path/to/file.db`
- Data stays local; normal operation does not require a network connection

### Develop and test

1. Activate the virtual environment.
2. Install editable dependencies if needed.
3. Run the test suite.

```bash
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Product requirements are defined in the [software requirements specification](.cursor/docs/srs.md). Documentation writing conventions are defined in the [software product documentation style guide](docs/style-guide.md).
