"""Directed-cycle arithmetic with explicit operator and endpoint identities."""
from decimal import Decimal
from .decimal_arithmetic import bounded_decimal, exact_context


def analyze(parameters, data):
    if set(parameters) != {'operator_id', 'basis_id', 'geometry_id', 'electron_count', 'atol_hartree'} or set(data) != {'edges'}:
        raise ValueError('Declare the fixed Hamiltonian identity, electron count, tolerance and edges.')
    if not all(isinstance(parameters[k], str) and parameters[k].strip() for k in ['operator_id', 'basis_id', 'geometry_id']):
        raise ValueError('Nonempty operator/basis/geometry identities are required.')
    if type(parameters['electron_count']) is not int or not 1 <= parameters['electron_count'] <= 1000:
        raise ValueError('Declare a positive integer electron count.')
    atol = parameters['atol_hartree']
    if type(atol) not in {int, float} or not 0 <= atol <= 1e-3:
        raise ValueError('Declare finite absolute tolerance in Hartree; no implicit relative tolerance.')
    edges = data['edges']
    if not isinstance(edges, list) or not 2 <= len(edges) <= 100:
        raise ValueError('Provide 2–100 ordered directed edges forming a cycle.')
    sources = []
    literals = [atol]
    for edge in edges:
        if not isinstance(edge, dict) or 'delta_hartree' not in edge:
            raise ValueError('Each edge requires an explicit difference.')
        literals.append(edge['delta_hartree'])
    with exact_context(literals, max_terms=100) as arithmetic:
        total = Decimal(0)
        for index, edge in enumerate(edges):
            if set(edge) != {'from', 'to', 'delta_hartree', 'source_id', 'operator_id', 'basis_id', 'geometry_id', 'electron_count'}:
                raise ValueError('Every edge needs explicit endpoints, energy, source and comparison identity.')
            if not all(isinstance(edge[k], str) and edge[k].strip() for k in ['from', 'to', 'source_id']):
                raise ValueError('Edge endpoints and sources must be nonempty strings.')
            if edge['from'] == edge['to'] or edge['to'] != edges[(index + 1) % len(edges)]['from']:
                raise ValueError('Edges are not a continuous nontrivial directed cycle.')
            for field in ['operator_id', 'basis_id', 'geometry_id', 'electron_count']:
                if edge[field] != parameters[field]:
                    raise ValueError('Incompatible comparison identity: ' + field)
            delta = bounded_decimal(edge['delta_hartree'])
            if not delta.is_finite():
                raise ValueError('Finite edge differences are required.')
            total += delta
            sources.append(edge['source_id'])
        passed = abs(total) <= bounded_decimal(atol)
        return {'arithmetic': arithmetic, 'scope': 'SAME_DECLARED_HAMILTONIAN_DIRECTED_CYCLE_ARITHMETIC',
                'cycle_residual_hartree': str(total), 'orientation': 'delta = E(to) - E(from)',
                'distinct_source_ids': len(set(sources)), 'edge_count': len(edges),
                'checks': [{'name': 'cycle_closure_absolute', 'passed': passed,
                            'actual': str(abs(total)), 'threshold': atol}],
                'limits': ['No new electronic-structure calculation or physical path uniqueness claim.',
                           'Matching identity/source labels are necessary declarations, not authenticated evidence.',
                           'Differences obtained from one shared energy table telescope algebraically; closure is not independent validation.',
                           'Different operators, basis, geometry or electron counts require explicitly defined bridges outside this module.']}
