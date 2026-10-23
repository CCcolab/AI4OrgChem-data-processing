"""Explicit chemical-semantic regression; three local runs, no model calls.

From the Skill directory: python runtime/chemical_regression.py --output ../chemical-check
This check always runs; no fixture hash silently enables or disables assertions.
"""
from pathlib import Path
import argparse
import csv
import importlib.util
import json

PAGE = Path(__file__).resolve().parents[1]


def table(path):
    with path.open(encoding='utf-8', newline='') as stream:
        return {row['id']: row for row in csv.DictReader(stream)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.is_relative_to(PAGE):
        parser.error('回归结果必须位于Skill目录之外。')
    output.mkdir(parents=True, exist_ok=False)
    spec = importlib.util.spec_from_file_location('rdkit_skill', PAGE / 'runtime/organic-smiles-rdkit.py')
    api = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(api)
    base = dict(radius=2, fp_size=2048, include_chirality=True,
                query_smarts='[CX3](=O)[OX2H1]', reference_id='E01')
    runs = {}
    for name, changes in [('boundary', {}),
                          ('stereo-on', {'reference_id': 'EPOS', 'query_smarts': 'C[C@H](O)C(=O)O'}),
                          ('stereo-off', {'reference_id': 'EPOS', 'query_smarts': 'C[C@H](O)C(=O)O',
                                          'include_chirality': False})]:
        receipt = api.run_skill(skill_file=PAGE / 'SKILL.md',
                                input_csv=PAGE / 'runtime/examples/chemistry-boundaries.csv',
                                parameters={**base, **changes}, task='显式化学语义回归，不调用模型。',
                                output_dir=output / name, mode='tools', case_name='chemical-regression')
        assert receipt['model_calls'] == 0 and receipt['status'] == 'PASS_LOCAL_TOOLS'
        runs[name] = table(output / name / 'analysis.csv')
    rows = runs['boundary']
    expected = json.loads((PAGE / 'runtime/examples/chemical-expectations.json').read_text('utf-8'))
    checks = []
    assert set(rows) == set(expected), 'Boundary records missing or unexpected'
    for id_, rule in expected.items():
        row = rows[id_]
        for field, value in rule.get('equals', {}).items():
            assert row[field] == str(value), (id_, field, row.get(field), value)
        for field, value in rule.get('approx', {}).items():
            assert abs(float(row[field]) - value) < 1e-7, (id_, field)
        codes = json.loads(row.get('warning_codes') or '[]')
        assert set(rule.get('warnings', [])).issubset(codes), (id_, codes)
        checks.append({'check': id_, 'status': 'PASS', 'expected': rule})
    for a, b in [('EPOS', 'ENEG'), ('TRANS', 'CIS'), ('ACID', 'ANION')]:
        assert rows[a]['canonical_isomeric_smiles'] != rows[b]['canonical_isomeric_smiles']
        checks.append({'check': a + '_distinct_from_' + b, 'status': 'PASS'})
    assert rows['BADTAG']['canonical_isomeric_smiles'] == 'CC(C)O'
    assert rows['ISO']['formula'] == 'C2H6O' and rows['ISO']['isotope_formula'] == 'C[13C]H6O'
    assert '2H' in rows['DEUTERIUM']['isotope_formula']
    on = table(output / 'stereo-on/similarity.csv')
    off = table(output / 'stereo-off/similarity.csv')
    assert float(on['ENEG']['tanimoto']) < 1 and float(off['ENEG']['tanimoto']) == 1
    assert runs['stereo-on']['ENEG']['query_match_count'] == '0'
    assert runs['stereo-off']['ENEG']['query_match_count'] == '1'
    for id_ in rows:
        if rows[id_]['parse_status'] == 'VALID':
            assert runs['stereo-on'][id_]['canonical_isomeric_smiles'] == runs['stereo-off'][id_]['canonical_isomeric_smiles']
    checks += [{'check': name, 'status': 'PASS'} for name in [
        'invalid_tag_cleanup_reported', 'isotope_formula_and_mass', 'explicit_deuterium_formula',
        'chirality_switch_affects_query_and_fingerprint_not_canonical_identity']]
    summary = {'status': 'PASS_CHEMICAL_SEMANTICS_DEFINED_REGRESSION',
               'scope': 'Specified 29 authored boundary inputs, three parameter settings; not universal chemical validation',
               'model_calls': 0, 'checks': checks, 'parameters': base,
               'version': 'rdkit-small-organic-semantics-1'}
    (output / 'chemical-semantics-acceptance.json').write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(summary['status'], len(checks), 'checks; model_calls=0')


if __name__ == '__main__':
    main()
