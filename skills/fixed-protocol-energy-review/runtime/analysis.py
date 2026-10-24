"""Explicit ordinary/conditional ledger review, not conditional-state compute."""
from decimal import Decimal
from .decimal_arithmetic import bounded_decimal, exact_context


def analyze(parameters, data):
    identity_fields = ['protocol_id', 'protocol_version', 'method_id', 'basis_id', 'geometry_id']
    if set(parameters) != set(identity_fields + ['atol_hartree']) or set(data) != {'states', 'comparison_definition'}:
        raise ValueError('Declare protocol/method/basis/geometry identity, tolerance, two states and comparison definition.')
    if not all(isinstance(parameters[k], str) and parameters[k].strip() for k in identity_fields):
        raise ValueError('Protocol and scientific identity cannot be implicit.')
    atol = parameters['atol_hartree']
    if type(atol) not in {int, float} or not 0 <= atol <= 1e-3:
        raise ValueError('Declare finite absolute Hartree tolerance in [0,1e-3].')
    if not isinstance(data['comparison_definition'], str) or not data['comparison_definition'].strip():
        raise ValueError('Comparison meaning is required; no automatic bond-energy interpretation.')
    states = data['states']
    if not isinstance(states, list) or len(states) != 2 or {s.get('role') for s in states} != {'ordinary', 'conditional'}:
        raise ValueError('Exactly ordinary and conditional state receipts are required.')
    checks, energies, records = [], {}, []
    literals = [atol]
    for state in states:
        if not isinstance(state.get('terms'), list) or not 1 <= len(state['terms']) <= 32 or 'reported_total_hartree' not in state:
            raise ValueError('Each endpoint requires1..32 terms and a reported total.')
        literals.append(state['reported_total_hartree'])
        for term in state['terms']:
            if not isinstance(term, dict) or not {'coefficient', 'value_hartree'} <= term.keys():
                raise ValueError('Each ledger term requires a coefficient and value.')
            literals.extend([term['coefficient'], term['value_hartree']])
    with exact_context(literals, max_terms=64) as arithmetic:
        for state in states:
            expected = set(identity_fields + ['role', 'operator_definition', 'occupation_definition', 'converged',
                                            'endpoint_qualified', 'terms', 'reported_total_hartree', 'total_source_id'])
            if set(state) != expected or any(state[k] != parameters[k] for k in identity_fields):
                raise ValueError('Incompatible or incomplete state comparison identity.')
            if any(not isinstance(state[k], str) or not state[k].strip() for k in ['operator_definition', 'occupation_definition', 'total_source_id']):
                raise ValueError('Explicit operator, occupation and total-energy source definitions required.')
            if type(state['converged']) is not bool or type(state['endpoint_qualified']) is not bool:
                raise ValueError('Convergence and endpoint qualification must be explicit Booleans.')
            terms = state['terms']
            if not isinstance(terms, list) or not 1 <= len(terms) <= 32:
                raise ValueError('Provide the defined functional ledger, not an inferred universal decomposition.')
            value, seen = Decimal(0), set()
            for term in terms:
                if set(term) != {'id', 'value_hartree', 'coefficient', 'source_id'} or not term['id'] or term['id'] in seen or not term['source_id']:
                    raise ValueError('Terms need unique IDs, values, signed coefficients and sources.')
                seen.add(term['id'])
                coefficient, energy = bounded_decimal(term['coefficient']), bounded_decimal(term['value_hartree'])
                if not coefficient.is_finite() or not energy.is_finite():
                    raise ValueError('Nonfinite ledger term.')
                value += coefficient * energy
            reported = bounded_decimal(state['reported_total_hartree'])
            if not reported.is_finite():
                raise ValueError('Nonfinite independently reported total.')
            residual = abs(value - reported)
            role = state['role']
            checks.extend([{'name': role + '_ledger_closure', 'passed': residual <= bounded_decimal(atol),
                            'actual': str(residual), 'threshold': atol},
                           {'name': role + '_declared_endpoint_qualification',
                            'passed': state['converged'] and state['endpoint_qualified'],
                            'actual': {'converged': state['converged'], 'qualified': state['endpoint_qualified']},
                            'threshold': 'Both declarations true; actual source evidence still requires review'}])
            energies[role] = value
            records.append({'role': role, 'assembled_hartree': str(value), 'reported_hartree': str(reported),
                            'operator_definition': state['operator_definition'], 'occupation_definition': state['occupation_definition']})
        qualified = all(c['passed'] for c in checks)
        return {'arithmetic': arithmetic, 'scope': 'EXPLICIT_FIXED_PROTOCOL_ENERGY_LEDGER_REVIEW_ONLY', 'checks': checks, 'states': records,
                'conditional_minus_ordinary_hartree': str(energies['conditional'] - energies['ordinary']) if qualified else None,
                'comparison_definition': data['comparison_definition'], 'new_conditional_compute': 'NOT_ACCEPTED',
                'limits': ['No new ordinary/conditional quantum endpoint; source labels and eligibility flags are declarations, not proof.',
                           'The input formula defines the ledger; no universal conditional functional is inferred.',
                           'A conditional-functional difference is not automatically a physical bond energy, excitation or observable.',
                           'Unqualified endpoints do not receive a usable comparison result.']}
