"""Bounded exact decimal ledger arithmetic, policy skill-ledger-decimal-v2.

Only finite literals with <=80 coefficient digits, exponent in [-200,200]
and <=128 characters are admitted. Precision covers sums of two-factor products
and comparisons; rounding is a failure, never a successful closure.
"""
from contextlib import contextmanager
from decimal import Decimal, Inexact, Rounded, InvalidOperation, Overflow, Underflow, localcontext
import math
import re

POLICY = 'skill-ledger-decimal-v2'


def bounded_decimal(value):
    if type(value) not in {int, float, str}:
        raise ValueError('Decimal literals must be int/float/text, never Boolean/null/objects.')
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError('Finite decimal literals are required.')
    # Bound an integer before converting a potentially huge value to text.
    if isinstance(value, int) and value.bit_length() > 266:
        raise ValueError('Decimal literal exceeds80 coefficient digits.')
    text = str(value)
    if len(text) > 128 or not re.fullmatch(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?', text):
        raise ValueError('Require a bounded decimal literal without whitespace or special values.')
    number = Decimal(text)  # Construction is exact, independent of context.prec.
    parts = number.as_tuple()
    if not number.is_finite() or len(parts.digits) > 80 or not -200 <= parts.exponent <= 200:
        raise ValueError('Decimal policy: <=80 coefficient digits and exponent in[-200,200].')
    return number


@contextmanager
def exact_context(literals, max_terms=100):
    if not isinstance(literals, (list, tuple)) or not 1 <= len(literals) <= 1000:
        raise ValueError('Provide1..1000 bounded numeric literals.')
    if type(max_terms) is not int or not 1 <= max_terms <= 100:
        raise ValueError('Provide an explicit ledger term bound in1..100.')
    numbers = [bounded_decimal(value) for value in literals]
    low = min([0] + [value.as_tuple().exponent for value in numbers])
    high = max([0] + [value.adjusted() + 1 for value in numbers if value])
    # Products occupy at most [2*low,2*high); add carries for100 terms,
    # a reference subtraction and an ordinary/conditional difference.
    precision = max(34, 2 * (high - low) + len(str(max_terms)) + 4)
    if precision > 1024:
        raise ValueError('Exact arithmetic exceeds the1024-digit budget.')
    with localcontext() as context:
        context.prec = precision
        context.Emin, context.Emax = -1000, 1000
        for signal in (Inexact, Rounded, InvalidOperation, Overflow, Underflow):
            context.traps[signal] = True
        yield {'id': POLICY, 'precision_digits': precision, 'coefficient_digits_max': 80,
               'literal_exponent_min': -200, 'literal_exponent_max': 200,
               'literal_characters_max': 128, 'precision_digits_max': 1024,
               'rounding_policy': 'TRAP_INEXACT_AND_ROUNDED', 'max_terms': max_terms}
