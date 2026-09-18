"""Lab07: retrospective P/E comparison using frozen case inputs.

Run: python3 ComparablePolicy_2026-09-15_Lab07.py
Prices are December 31, 2024 closes; FY2024 earnings were reported later.
This is not a point-in-time investment analysis. Keep price and EPS on the
same stock-split basis. Use total GAAP diluted EPS, not adjusted EPS.
"""

# EDITABLE INPUTS: use ticker symbols as company identifiers.
# Numeric strings preserve the exact input decimals; None means missing.
TARGET = {"ticker": "ABG", "name": "Asbury Automotive",
          "price": "243.03", "eps": "21.50"}
PEERS = [
    {"ticker": "AN", "name": "AutoNation", "price": "169.84", "eps": "16.92",
     "policy": "Use with caveat: AutoNation Finance adds lending exposure."},
    {"ticker": "GPI", "name": "Group 1 Automotive", "price": "421.48", "eps": "36.81",
     "policy": "Qualified: U.S./U.K. geography and 54 Inchcape dealerships acquired in 2024."},
]

from fractions import Fraction
from statistics import median


def positive_number(value):
    """Return an exact rational number, or None for unusable inputs."""
    if isinstance(value, bool):
        return None
    try:
        number = Fraction(str(value))
    except (ValueError, TypeError, ZeroDivisionError):
        return None
    return number if number > 0 else None


def ticker(company):
    return str(company.get("ticker") or "").strip().upper()


def pe(company):
    price = positive_number(company.get("price"))
    eps = positive_number(company.get("eps"))
    return price / eps if price is not None and eps is not None else None


def formatted(value, digits=2, signed=False):
    """Round only for display, using exact integer arithmetic (half-even)."""
    scale = 10 ** digits
    whole, remainder = divmod(abs(value.numerator) * scale, value.denominator)
    if remainder * 2 > value.denominator or (
        remainder * 2 == value.denominator and whole % 2
    ):
        whole += 1
    prefix = "-" if value < 0 else ("+" if signed else "")
    return f"{prefix}{whole // scale:,}.{whole % scale:0{digits}d}"


def main(target=None, peers=None):
    target = TARGET if target is None else target
    peers = PEERS if peers is None else peers
    # Show the case peers first, using the same first-occurrence policy below.
    for symbol, name in (("AN", "AutoNation"), ("GPI", "Group 1 Automotive")):
        company = next((item for item in peers if ticker(item) == symbol), None)
        multiple = pe(company) if company is not None and symbol != ticker(target) else None
        result = (formatted(multiple, 6) + "x" if multiple is not None
                  else "not meaningful (missing/invalid inputs or excluded peer)")
        print(f"{name} P/E: {result}")
    print()
    print("ComparablePolicy | 2026-09-15 | Lab07")
    print("Retrospective training comparison: 2024-12-31 prices and subsequently")
    print("reported FY2024 total GAAP diluted EPS; matching stock-split bases.")
    print("P/E is equity-to-equity: no cash/debt bridge.\n")

    # Deduplicate by normalized ticker; the first occurrence wins.
    unique = []
    seen = set()
    for company in peers:
        symbol = ticker(company)
        if not symbol:
            print("Excluded peer without a ticker: cannot identify/deduplicate.")
        elif symbol == ticker(target):
            print(f"Excluded target from peers: {symbol}")
        elif symbol in seen:
            print(f"Removed duplicate peer: {symbol} (first occurrence retained)")
        else:
            seen.add(symbol)
            unique.append(company)

    target_eps = positive_number(target.get("eps"))
    target_pe = pe(target)
    print(f"Target: {ticker(target)} — {target.get('name', '')}")
    print("Target P/E: " + (formatted(target_pe, 6) + "x" if target_pe is not None
                              else "not meaningful (missing, invalid, or nonpositive price/EPS)"))
    if target_eps is None:
        print("All implied target prices: not meaningful (invalid target EPS).")
    print()

    valid = {}
    for company in unique:
        symbol = ticker(company)
        multiple = pe(company)
        print(f"{symbol}: {company.get('policy', 'Candidate peer')}")
        if multiple is None:
            print("  P/E and peer-implied price: not meaningful "
                  "(missing, invalid, or nonpositive price/EPS).")
        else:
            valid[symbol] = multiple
            implied = ("$" + formatted(multiple * target_eps)
                       if target_eps is not None else "not meaningful")
            print(f"  P/E: {formatted(multiple, 6)}x; implied target price: {implied}")

    print(f"\nValid unique peers: {len(valid)}")
    full_estimate = None
    if not valid:
        print("No usable peers. No estimate.")
    else:
        multiples = list(valid.values())
        midpoint = median(multiples)
        print(f"Median peer P/E: {formatted(midpoint, 6)}x")
        if target_eps is not None:
            full_estimate = midpoint * target_eps
        if len(valid) == 1:
            estimate = ("$" + formatted(full_estimate)
                        if full_estimate is not None else "not meaningful")
            print(f"One valid peer: reference estimate {estimate}; no range.")
        else:
            for label, multiple in (("Minimum", min(multiples)),
                                    ("Median", midpoint),
                                    ("Maximum", max(multiples))):
                implied = ("$" + formatted(multiple * target_eps)
                           if target_eps is not None else "not meaningful")
                print(f"{label}: {formatted(multiple, 6)}x -> {implied}")

    baseline_label = "two-peer midpoint" if len(valid) == 2 else "full-peer median estimate"
    print(f"\nPeer-removal sensitivity (change from {baseline_label}):")
    if full_estimate is not None:
        print(f"Baseline {baseline_label}: ${formatted(full_estimate)}")
    if not unique:
        print("No peers to remove.")
    for company in unique:
        symbol = ticker(company)
        remaining_symbols = [key for key in valid if key != symbol]
        remaining = [value for key, value in valid.items() if key != symbol]
        if not remaining:
            print(f"Remove {symbol}: no usable peers remain; no estimate or dollar change.")
        elif target_eps is None:
            print(f"Remove {symbol}: implied price and dollar change not meaningful "
                  "(invalid target EPS).")
        else:
            estimate = median(remaining) * target_eps
            change = estimate - full_estimate
            note = "; one-peer reference, no range" if len(remaining) == 1 else ""
            sign = "-" if change < 0 else "+"
            print(f"Remove {symbol}: {target.get('name', ticker(target))} "
                  f"({ticker(target)}) target + {', '.join(remaining_symbols)} peer(s) remain.")
            print(f"  Remaining median P/E: {formatted(median(remaining), 6)}x")
            print(f"  Implied target price: ${formatted(estimate)}{note}")
            print(f"  Change from {baseline_label}: {sign}${formatted(abs(change))} "
                  "(calculated before rounding)")


if __name__ == "__main__":
    main()
