"""Account naming, short codes, and aliases."""

from __future__ import annotations

from guita.domain.models import Account

SHORT_CODE_LEN = 3


def normalize_alias(alias: str) -> str:
    return alias.strip()


def validate_alias_format(alias: str) -> str:
    """Return a cleaned alias or raise ValueError with a user-facing message."""
    cleaned = normalize_alias(alias)
    if len(cleaned) < SHORT_CODE_LEN:
        raise ValueError(
            f"Error: alias must be at least {SHORT_CODE_LEN} characters "
            f'(got "{alias}").'
        )
    return cleaned


def default_short_code(name: str) -> str | None:
    """First three letters of the account name, if long enough."""
    cleaned = name.strip()
    if len(cleaned) < SHORT_CODE_LEN:
        return None
    return cleaned[:SHORT_CODE_LEN].casefold()


def effective_short_code(account: Account) -> str | None:
    """Alias if set, otherwise the default three-letter code from the name."""
    if account.alias:
        return account.alias.casefold()
    return default_short_code(account.name)


def account_short_code(name: str) -> str | None:
    """Backward-compatible helper for name-based short codes."""
    return default_short_code(name)


def matches_account_query(account: Account, query: str) -> bool:
    """True if *query* should resolve to *account* as a non-exact reference.

    Exact name/alias equality is handled by the caller first.
    Accounts with a custom alias do not claim their name's default 3-letter
    code; that prevents overlap with another account that still uses it.
    """
    q = query.strip().casefold()
    if not q or len(q) < SHORT_CODE_LEN:
        return False

    name = account.name.casefold()

    if account.alias:
        alias = account.alias.casefold()
        if alias == q or alias.startswith(q):
            return True
        # Longer name prefixes remain available (not the colliding 3-letter code).
        if len(q) >= SHORT_CODE_LEN + 1 and name.startswith(q):
            return True
        return False

    code = default_short_code(account.name)
    if code and code == q:
        return True
    return name.startswith(q)
