"""Real finite linear algebra; explicit tolerances, no physical interpretation."""
import numpy as np


def keys(value, required, optional=()):
    if not isinstance(value, dict) or not set(required).issubset(value) or set(value) - set(required) - set(optional):
        raise ValueError('Required fields: ' + ','.join(required) + '; optional: ' + ','.join(optional))


def require_real_leaves(value):
    """Validate raw numeric leaves before NumPy can promote mixed Booleans."""
    pending = [value]
    visited = 0
    while pending:
        item = pending.pop()
        visited += 1
        if visited > 100000:
            raise ValueError('Numeric input exceeds the bounded traversal budget.')
        if isinstance(item, (list, tuple)):
            pending.extend(item)
        elif isinstance(item, np.ndarray):
            if item.dtype.kind not in 'if':
                raise ValueError('Require real numeric leaves; Boolean/string/null/complex input is not admitted.')
        elif isinstance(item, (bool, np.bool_)) or not isinstance(item, (int, float, np.integer, np.floating)):
            raise ValueError('Require real numeric leaves; Boolean/string/null/complex input is not admitted.')


def array(value, ndim, maximum=128):
    require_real_leaves(value)
    result = np.asarray(value)
    if result.dtype.kind not in 'if' or result.ndim != ndim or not result.size or max(result.shape) > maximum:
        raise ValueError('Require a nonempty real numeric array of the declared bounded shape; no Boolean/string/complex arrays.')
    result = result.astype(float)
    if not np.isfinite(result).all():
        raise ValueError('Nonfinite array.')
    return result


def tolerance(value):
    if type(value) not in {int, float} or not 1e-14 <= value <= 1e-4:
        raise ValueError('Declare absolute tolerance in [1e-14,1e-4]; this is an engineering check, not a scientific uncertainty.')
    return float(value)


def metric(value, atol):
    s = array(value, 2)
    if s.shape[0] != s.shape[1] or np.max(abs(s - s.T)) > atol:
        raise ValueError('Metric must be square symmetric to the explicit tolerance.')
    eigenvalues, vectors = np.linalg.eigh(s)
    if eigenvalues[0] <= 1e-10 or eigenvalues[-1] / eigenvalues[0] > 1e10:
        raise ValueError('Require a positive definite, bounded-condition ambient metric; no silent rank truncation of S.')
    return s, eigenvalues, vectors


def check(name, actual, threshold):
    actual = float(actual)
    return {'name': name, 'actual': actual, 'threshold': threshold,
            'passed': bool(np.isfinite(actual) and actual <= threshold)}


def require_rows(matrix, count, name):
    if matrix.shape[0] != count:
        raise ValueError('Mismatched row dimension: ' + name)


def scope_result(scope, checks, **kwargs):
    return {'scope': scope, 'environment': {'numpy': np.__version__}, 'checks': checks, **kwargs}
