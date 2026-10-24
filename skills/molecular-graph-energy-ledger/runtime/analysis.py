"""Graph queries and explicitly sourced, same-state Hartree arithmetic are separate."""
from decimal import Decimal
from .decimal_arithmetic import bounded_decimal, exact_context
import importlib.util
import json
from pathlib import Path


def keys(value, expected):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError('Expected fields: ' + ','.join(expected))


def analyze(parameters, data):
    if parameters.get('mode') == 'graph':
        return graph(parameters, data)
    if parameters.get('mode') == 'ledger':
        return ledger(parameters, data)
    raise ValueError('Choose explicit mode graph or ledger; neither implies the other.')


def graph(parameters, data):
    from rdkit import Chem, rdBase
    keys(parameters, ['mode', 'query_smarts', 'include_chirality'])
    keys(data, ['molecules'])
    query_text = parameters['query_smarts']
    if not isinstance(query_text, str) or not 1 <= len(query_text) <= 120 or type(parameters['include_chirality']) is not bool:
        raise ValueError('Declare bounded SMARTS and Boolean chirality.')
    opts = Chem.SmartsParserParams()
    opts.parseName = False
    opts.allowCXSMILES = False
    with rdBase.BlockLogs():
        query = Chem.MolFromSmarts(query_text, opts)
    if query is None or query.GetNumAtoms() > 32:
        raise ValueError('Invalid SMARTS or more than 32 query atoms.')
    records = data['molecules']
    if not isinstance(records, list) or not 1 <= len(records) <= 50:
        raise ValueError('Require 1–50 molecular records.')
    spec = importlib.util.spec_from_file_location('_graph_chemistry', Path(__file__).with_name('chemistry.py'))
    chemistry = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(chemistry)
    seen, rows = set(), []
    for record in records:
        keys(record, ['id', 'smiles'])
        id_, raw = record['id'], record['smiles']
        if not isinstance(id_, str) or not id_ or id_ in seen or not isinstance(raw, str) or len(raw) > 512:
            raise ValueError('Unique nonempty string IDs and SMILES <=512 characters are required.')
        seen.add(id_)
        mol, error, stereo = chemistry.parse(raw)
        if mol is None:
            rows.append({'id': id_, 'raw_smiles': raw, 'parse_status': 'REJECTED', 'error': error})
            continue
        matches = mol.GetSubstructMatches(query, useChirality=parameters['include_chirality'],
                                         uniquify=True, maxMatches=1001)
        if len(matches) > 1000:
            raise ValueError('Enumeration exceeds 1000; refusing a truncated count.')
        rows.append({'id': id_, 'raw_smiles': raw, 'parse_status': 'VALID',
                     'canonical_isomeric_smiles': Chem.MolToSmiles(mol, isomericSmiles=True),
                     'matches': [list(match) for match in matches], 'match_count': len(matches),
                     'semantic_warnings': json.loads(chemistry.interpret(mol, stereo)['warning_codes'])})
    return {'scope': 'BOUNDED_SMARTS_GRAPH_MATCHING_NOT_ENERGY_OR_IDENTITY_CERTIFICATION',
            'environment': {'rdkit': rdBase.rdkitVersion}, 'records': rows, 'checks': [],
            'parameters': parameters, 'atom_index_convention': 'ZERO_BASED_PARSED_GRAPH_QUERY_ATOM_ORDER',
            'limits': ['Default RDKit cleanup is reported; no extra desalting or neutralization.',
                       'SMARTS matches are query-defined, not universal functional-group classification.',
                       'No energy is derived from molecular graphs.']}


def ledger(parameters, data):
    keys(parameters, ['mode', 'protocol_id', 'atol_hartree'])
    keys(data, ['terms', 'reference_hartree', 'reference_source', 'quantity_definition'])
    tolerance = parameters['atol_hartree']
    if type(tolerance) not in {int, float} or not 0 <= tolerance <= 1e-3:
        raise ValueError('Declare finite atol_hartree in [0,1e-3].')
    if not isinstance(parameters['protocol_id'], str) or not parameters['protocol_id'].strip():
        raise ValueError('Protocol identity is required.')
    if not all(isinstance(data[key], str) and data[key].strip()
               for key in ['reference_source', 'quantity_definition']):
        raise ValueError('Separate reference source and quantity definition are required.')
    terms = data['terms']
    if not isinstance(terms, list) or not 1 <= len(terms) <= 100:
        raise ValueError('Require 1–100 explicit terms.')
    signatures, ids = set(), set()
    literals = [tolerance, data['reference_hartree']]
    for term in terms:
        if not isinstance(term, dict) or not {'coefficient', 'value_hartree'} <= term.keys():
            raise ValueError('Each ledger term requires a coefficient and value.')
        literals.extend([term['coefficient'], term['value_hartree']])
    with exact_context(literals, max_terms=100) as arithmetic:
        total = Decimal(0)
        for term in terms:
            keys(term, ['id', 'coefficient', 'value_hartree', 'source', 'method', 'basis',
                        'geometry_id', 'state_id', 'operator_id'])
            if not all(isinstance(term[key], str) and term[key].strip() for key in
                       ['id', 'source', 'method', 'basis', 'geometry_id', 'state_id', 'operator_id']):
                raise ValueError('Every term needs explicit scientific identity and source.')
            if term['id'] in ids:
                raise ValueError('Repeated term ID.')
            ids.add(term['id'])
            signatures.add(tuple(term[key] for key in ['method', 'basis', 'geometry_id', 'state_id', 'operator_id']))
            values = [bounded_decimal(term[key]) for key in ['coefficient', 'value_hartree']]
            if not all(value.is_finite() for value in values):
                raise ValueError('Finite coefficients and energies are required.')
            total += values[0] * values[1]
        if len(signatures) != 1:
            raise ValueError('This same-state composition does not admit mixed scientific identities.')
        reference = bounded_decimal(data['reference_hartree'])
        if not reference.is_finite():
            raise ValueError('Reference must be finite.')
        residual = total - reference
        passed = abs(residual) <= bounded_decimal(tolerance)
        return {'arithmetic': arithmetic, 'scope': 'DECLARED_SAME_STATE_HARTREE_ARITHMETIC_ONLY', 'assembled_hartree': str(total),
                'reference_hartree': str(reference), 'residual_hartree': str(residual),
                'quantity_definition': data['quantity_definition'], 'terms': terms,
                'checks': [{'name': 'declared_composition_closure', 'passed': passed,
                            'actual': str(abs(residual)), 'threshold': tolerance}],
                'limits': ['Source names and identity fields are declarations, not source authentication.',
                           'Arithmetic closure does not validate a physical energy decomposition.',
                           'No mixed-unit conversion or graph-derived quantum energy.']}
