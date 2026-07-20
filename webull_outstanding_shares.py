"""
Webull: get a stock's outstanding shares — even though the SDK doesn't expose it.

WHY THIS FILE EXISTS
--------------------
Webull Support confirmed (ticket, 2026-07-13) that their market-data *snapshot*
already returns the number of outstanding shares in a field literally named:

    out_standing_shares      <-- note the extra underscore; that's their spelling

...but their official Python SDK and documentation were not updated to expose it.
So if you look for a tidy `.outstanding_shares` property, you won't find one.

The fix is simple: read the value straight out of the raw response the API sends
back. This file does exactly that, in a way that keeps working no matter how
Webull nests the data or (mis)spells the field.

You do NOT need to be an expert to use this:
  1. Fill in your Webull developer credentials in the CONFIG section below.
  2. Run:  python3 webull_outstanding_shares.py AAPL
  3. It prints the outstanding-shares number.

If you just want to SEE that the extraction logic works without any credentials,
run it with no arguments -- it runs a built-in self-test on sample data:
     python3 webull_outstanding_shares.py
"""

from __future__ import annotations

import sys
from typing import Any, Optional


# ---------------------------------------------------------------------------
# CONFIG  --  fill these in with your own Webull developer credentials.
# Get them at https://developer.webull.com  (App Key / App Secret).
# Leaving them blank is fine if you only want to run the self-test.
# ---------------------------------------------------------------------------
APP_KEY = ""      # e.g. "abcd1234..."
APP_SECRET = ""   # e.g. "wxyz9876..."
REGION_ID = "us"  # "us", "hk", or "jp"
CATEGORY = "US_STOCK"


# ---------------------------------------------------------------------------
# The important part: pulling the value out no matter where Webull hides it.
# ---------------------------------------------------------------------------

# All the spellings/aliases we're willing to accept for "outstanding shares".
# `out_standing_shares` is the confirmed one; the rest are defensive so this
# keeps working if/when Webull "fixes" the name in a future update.
_OUTSTANDING_KEYS = (
    "out_standing_shares",   # confirmed field name from Webull support
    "outstanding_shares",
    "outstandingShares",
    "outStandingShares",
    "totalShares",
    "total_shares",
)


def extract_outstanding_shares(snapshot: Any) -> Optional[float]:
    """Find the outstanding-shares value anywhere inside a snapshot response.

    Webull's snapshot may come back as a dict, a list of dicts, or a nested
    mix of both. Rather than guessing the exact path, we walk the whole
    structure and return the first value whose key matches one of the known
    outstanding-shares names.

    Returns the number as a float, or None if it genuinely isn't there.
    """
    match = _find_first_by_key(snapshot, _OUTSTANDING_KEYS)
    return _to_number(match) if match is not None else None


def _find_first_by_key(node: Any, keys: tuple[str, ...]) -> Any:
    """Depth-first search for the first dict value under any of `keys`."""
    if isinstance(node, dict):
        # Direct hit at this level takes priority.
        for k in keys:
            if k in node and node[k] not in (None, ""):
                return node[k]
        # Otherwise recurse into the values.
        for value in node.values():
            found = _find_first_by_key(value, keys)
            if found is not None:
                return found
    elif isinstance(node, (list, tuple)):
        for item in node:
            found = _find_first_by_key(item, keys)
            if found is not None:
                return found
    return None


def _to_number(value: Any) -> Optional[float]:
    """Best-effort convert Webull's value (often a string) to a number."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace(",", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


# ---------------------------------------------------------------------------
# Talking to Webull. This is isolated so the extraction logic above can be
# tested/used on its own. The SDK is imported lazily so this file still runs
# (and self-tests) even if the SDK isn't installed.
# ---------------------------------------------------------------------------

def get_snapshot(symbol: str) -> Any:
    """Fetch the raw snapshot for `symbol` from Webull's official SDK.

    Install the SDK first:
        pip install webull-python-sdk-core webull-python-sdk-mdata

    If your SDK version arranges things slightly differently, the only line
    you'd adjust is the `api.market_data.get_snapshot(...)` call -- everything
    else (credentials, extraction) stays the same.
    """
    if not APP_KEY or not APP_SECRET:
        raise RuntimeError(
            "Webull APP_KEY / APP_SECRET are not set. Edit the CONFIG section "
            "at the top of this file. (Run with no arguments to try the "
            "credential-free self-test instead.)"
        )

    # Lazy import so the file loads even without the SDK installed.
    from webullsdkcore.client import ApiClient          # type: ignore
    from webullsdkmdata.api import API                   # type: ignore

    api_client = ApiClient(APP_KEY, APP_SECRET, REGION_ID)
    api = API(api_client)

    response = api.market_data.get_snapshot(symbols=symbol, category=CATEGORY)

    # The SDK usually returns an HTTP-response-like object; get the parsed JSON.
    if hasattr(response, "json"):
        return response.json()
    return response


def outstanding_shares_for(symbol: str) -> Optional[float]:
    """Convenience: fetch the snapshot and pull outstanding shares out of it."""
    snapshot = get_snapshot(symbol)
    return extract_outstanding_shares(snapshot)


# ---------------------------------------------------------------------------
# Self-test: proves the extraction works on data shaped like Webull's response,
# without needing any credentials or network access.
# ---------------------------------------------------------------------------

def _self_test() -> None:
    print("Running self-test (no credentials needed)...\n")

    # A snapshot shaped roughly like Webull's, with the field buried in a list.
    sample_response = {
        "code": 200,
        "data": [
            {
                "symbol": "AAPL",
                "close": "227.52",
                "out_standing_shares": "15204137000",  # the confirmed field
                "volume": "41000000",
            }
        ],
    }

    result = extract_outstanding_shares(sample_response)
    assert result == 15204137000.0, f"unexpected: {result}"
    print(f"  AAPL outstanding shares: {result:,.0f}   OK")

    # Works even if a future SDK renames it to the 'correct' spelling.
    renamed = {"data": {"outstandingShares": 900000000}}
    assert extract_outstanding_shares(renamed) == 900000000.0
    print("  handles the renamed/fixed field too            OK")

    # Returns None cleanly when the value simply isn't present.
    assert extract_outstanding_shares({"data": {"close": "10"}}) is None
    print("  returns None when the field is absent           OK")

    print("\nSelf-test passed. Add your credentials up top, then run:")
    print("  python3 webull_outstanding_shares.py AAPL")


def main() -> None:
    args = sys.argv[1:]
    if not args:
        _self_test()
        return

    symbol = args[0].upper()
    try:
        shares = outstanding_shares_for(symbol)
    except RuntimeError as err:
        # Friendly message (e.g. missing credentials) instead of a scary traceback.
        print(err)
        sys.exit(1)
    except ImportError:
        print(
            "The Webull SDK isn't installed. Install it with:\n"
            "  pip install webull-python-sdk-core webull-python-sdk-mdata"
        )
        sys.exit(1)
    if shares is None:
        print(f"{symbol}: outstanding shares not found in the snapshot response.")
    else:
        print(f"{symbol}: {shares:,.0f} outstanding shares")


if __name__ == "__main__":
    main()
