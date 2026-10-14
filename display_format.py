"""Presentation-only formatting. Raw financial/CSV values remain numeric."""
import math


def money(value, compact=False, decimals=0):
    """US dollars, negative values as -$; preserves sign and sensible precision."""
    value = float(value)
    if not math.isfinite(value):
        return 'N/A'
    sign = '-' if value < 0 else ''
    amount = abs(value)
    if compact and amount >= 1_000_000:
        return f'{sign}${amount / 1_000_000:,.2f}M'
    if compact and amount >= 10_000:
        return f'{sign}${amount / 1_000:,.1f}K'
    return f'{sign}${amount:,.{decimals}f}'


def percentage(value, decimals=1):
    return f'{value:,.{decimals}f}%'


def integer(value):
    return f'{value:,.0f}'


def money_millions(value):
    return money(float(value) * 1_000_000, compact=True)
