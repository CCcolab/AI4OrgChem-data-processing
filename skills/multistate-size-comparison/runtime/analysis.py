"""Explicit state-set completeness and fixed-weight arithmetic within each size."""
import numpy as np
from .support import check, keys, scope_result, tolerance


def analyze(parameters, data):
    keys(parameters, ['protocol_id', 'method_id', 'basis_id', 'weight_atol', 'expected_states', 'comparison_definition'])
    keys(data, ['states'])
    atol = tolerance(parameters['weight_atol'])
    for key in ['protocol_id', 'method_id', 'basis_id', 'comparison_definition']:
        if not isinstance(parameters[key], str) or not parameters[key].strip():
            raise ValueError('Explicit protocol/method/basis/comparison definition required.')
    expected = parameters['expected_states']
    if not isinstance(expected, dict) or not 1 <= len(expected) <= 16:
        raise ValueError('Declare expected state IDs for each size label.')
    expected_pairs = set()
    for size, ids in expected.items():
        if not isinstance(size, str) or not size or not isinstance(ids, list) or not ids or len(ids) != len(set(ids)) or any(not isinstance(id_, str) or not id_ for id_ in ids):
            raise ValueError('Invalid expected state set.')
        expected_pairs.update((size, id_) for id_ in ids)
    states = data['states']
    if not isinstance(states, list) or not 1 <= len(states) <= 128:
        raise ValueError('Require 1–128 actual state records.')
    observed, groups = set(), {}
    for state in states:
        keys(state, ['size', 'id', 'energy_hartree', 'weight', 'eligible', 'source_id', 'state_definition',
                     'protocol_id', 'method_id', 'basis_id'])
        if any(state[k] != parameters[k] for k in ['protocol_id', 'method_id', 'basis_id']):
            raise ValueError('Incompatible scientific protocol or method/basis.')
        if type(state['eligible']) is not bool or any(not isinstance(state[k], str) or not state[k].strip() for k in ['size', 'id', 'source_id', 'state_definition']):
            raise ValueError('Explicit state definition, source and Boolean eligibility required.')
        pair = (state['size'], state['id'])
        if pair in observed:
            raise ValueError('Repeated state/size identity.')
        observed.add(pair)
        if any(type(state[k]) not in {int, float} or not np.isfinite(state[k]) for k in ['energy_hartree', 'weight']) or state['weight'] < 0:
            raise ValueError('Finite energies and nonnegative explicit weights required.')
        groups.setdefault(state['size'], []).append(state)
    if observed != expected_pairs:
        raise ValueError('Actual state set is incomplete or has undeclared states; no partial weighted result.')
    checks, summaries = [], []
    for size, rows in groups.items():
        weight_sum = sum(row['weight'] for row in rows)
        checks.append(check(size + '_weights_sum_to_one', abs(weight_sum - 1), atol))
        checks.append({'name': size + '_declared_endpoint_eligibility', 'passed': all(row['eligible'] for row in rows),
                       'actual': {row['id']: row['eligible'] for row in rows}, 'threshold': 'All declared endpoints eligible; source review still required'})
        value = sum(row['weight'] * row['energy_hartree'] for row in rows)
        if not np.isfinite(value):
            raise ValueError('Weighted energy overflow.')
        summaries.append({'size': size, 'weight_sum': weight_sum, 'candidate_weighted_energy_hartree': value,
                          'qualified_by_declared_checks': abs(weight_sum - 1) <= atol and all(row['eligible'] for row in rows)})
    return scope_result('COMPLETE_DECLARED_STATE_SETS_AND_FIXED_WEIGHT_ARITHMETIC_ONLY', checks,
                        summaries=summaries, comparison_definition=parameters['comparison_definition'],
                        new_state_optimizations='NOT_EXECUTED',
                        limits=['Weights are explicitly provided, not inferred populations or Boltzmann factors; this is not a free energy.',
                                'No automatic comparison/subtraction of total energies across different compositions/sizes.',
                                'Eligibility/source labels are declarations, not a new endpoint qualification.',
                                'No new multistate optimizer, state continuity proof or completeness beyond the explicitly declared state set.'])
