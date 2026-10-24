"""Read SKILL.md and resolve explicit identifiers, retaining all bounded candidates.

Local SMILES validation uses RDKit. Remote lookups require --allow-network.
No model service, key, structure upload, automatic fallback or code execution.
"""
from pathlib import Path
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import importlib.metadata
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile

PAGE = Path(__file__).resolve().parents[1]
PUBCHEM = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/'
CIR = 'https://cactus.nci.nih.gov/chemical/structure/'
FIELDS = ['id', 'query_type', 'query', 'service', 'status', 'candidate', 'cid',
          'returned_smiles', 'rdkit_isomeric_smiles', 'inchikey', 'formula',
          'warning', 'error']


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def cas_checksum(value):
    if not re.fullmatch(r'[1-9]\d{1,6}-\d{2}-\d', value):
        return False
    digits = value.replace('-', '')
    return sum(int(v) * n for n, v in enumerate(reversed(digits[:-1]), 1)) % 10 == int(digits[-1])


def read_source(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 32000:
        raise ValueError('Provide a regular UTF-8 CSV no larger than 32000 bytes.')
    return path.read_bytes()


def read_input(path, raw=None):
    raw = read_source(path) if raw is None else raw
    try:
        records = list(csv.reader(io.StringIO(raw.decode('utf-8-sig'), newline=''), strict=True))
    except csv.Error as error:
        raise ValueError('Invalid CSV quoting: ' + str(error)) from None
    header = records[0] if records else []
    if len(header) != 3 or len(set(header)) != 3 or set(header) != {'id', 'query_type', 'query'}:
        raise ValueError('Require exactly three unique CSV headers: id,query_type,query.')
    if any(len(row) != len(header) for row in records[1:]):
        raise ValueError('Every CSV record must contain exactly three fields; blank/ragged records are rejected.')
    rows = [dict(zip(header, row)) for row in records[1:]]
    if not 1 <= len(rows) <= 10:
        raise ValueError('Require 1–10 records.')
    seen = set()
    for row in rows:
        if set(row) != {'id', 'query_type', 'query'} or None in row.values():
            raise ValueError('Require exactly id,query_type,query columns and complete rows.')
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,63}', row['id']) or row['id'] in seen:
            raise ValueError('IDs must be unique safe strings.')
        seen.add(row['id'])
        if row['query_type'] not in {'local_smiles', 'name', 'cas', 'cid', 'inchikey'}:
            raise ValueError('Unknown explicit query_type.')
        query = row['query']
        if not query or query != query.strip() or len(query) > 256 or any(ord(c) < 32 for c in query):
            raise ValueError('Query must be 1–256 characters without controls or surrounding spaces.')
    return raw, rows


class Client:
    def __init__(self, output):
        self.output = output
        self.events = []
        self.last_request = 0.0
        self.cache = {}

    def get(self, url):
        if url in self.cache:
            return self.cache[url]
        for attempt in range(2):
            time.sleep(max(0, 0.4 - (time.monotonic() - self.last_request)))
            self.last_request = time.monotonic()
            request = urllib.request.Request(url, headers={'User-Agent': 'AI4OrgChem-Identifier-Teaching/1.0',
                                                           'Accept': 'application/json,text/plain'})
            status = None
            body = b''
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    if urllib.parse.urlparse(response.url).hostname != urllib.parse.urlparse(url).hostname:
                        raise ValueError('Unexpected cross-host redirect.')
                    status = response.status
                    body = response.read(2_000_001)
                if len(body) > 2_000_000:
                    raise ValueError('Response exceeds 2 MB.')
                value = body.decode('utf-8')
            except urllib.error.HTTPError as error:
                status = error.code
                body = error.read(32000)
                value = None
            except (urllib.error.URLError, TimeoutError, OSError) as error:
                self.events.append({'url': url, 'status': status, 'error_type': type(error).__name__,
                                    'time_utc': datetime.now(timezone.utc).isoformat()})
                raise RuntimeError('NETWORK_ERROR_' + type(error).__name__) from None
            index = len(self.events) + 1
            response_file = f'responses/{index:03}.txt'
            (self.output / response_file).write_bytes(body)
            self.events.append({'url': url, 'status': status, 'response_file': response_file,
                                'sha256': sha(body), 'time_utc': datetime.now(timezone.utc).isoformat()})
            if status == 200:
                self.cache[url] = value
                return value
            if status in {429, 503} and attempt == 0:
                time.sleep(1)
                continue
            raise RuntimeError('HTTP_' + str(status))
        raise RuntimeError('NETWORK_RETRY_EXHAUSTED')


def canonical(raw):
    from rdkit import Chem, rdBase

    options = Chem.SmilesParserParams()
    options.parseName = False
    options.allowCXSMILES = False
    with rdBase.BlockLogs():
        mol = Chem.MolFromSmiles(raw, options)
    if mol is None or mol.GetNumAtoms() > 128 or any(a.GetAtomicNum() == 0 for a in mol.GetAtoms()):
        raise ValueError('SMILES_PARSE_OR_SCOPE_ERROR')
    return Chem.MolToSmiles(mol, isomericSmiles=True)


def pubchem(row, client):
    query_type, query = row['query_type'], row['query']
    namespace = 'name' if query_type == 'cas' else query_type
    if query_type == 'cid':
        cids = [int(query)]
    else:
        url = PUBCHEM + namespace + '/' + urllib.parse.quote(query, safe='') + '/cids/JSON'
        response = json.loads(client.get(url))
        cids = response.get('IdentifierList', {}).get('CID')
        if not isinstance(cids, list) or not cids:
            raise ValueError('MALFORMED_OR_EMPTY_CID_LIST')
    if len(cids) > 10 or any(type(cid) is not int or cid < 1 for cid in cids) or len(set(cids)) != len(cids):
        raise ValueError('CID_LIST_EXCEEDS_SCOPE_OR_INVALID')
    properties = 'MolecularFormula,SMILES,ConnectivitySMILES,InChIKey'
    response = json.loads(client.get(PUBCHEM + 'cid/' + ','.join(map(str, cids)) + '/property/' + properties + '/JSON'))
    values = response.get('PropertyTable', {}).get('Properties')
    if (not isinstance(values, list) or not all(isinstance(v, dict) for v in values)
            or {v.get('CID') for v in values} != set(cids) or len(values) != len(cids)):
        raise ValueError('CID_PROPERTY_ALIGNMENT_ERROR')
    results = []
    for value in values:
        returned = value.get('SMILES')
        if not isinstance(returned, str) or not returned:
            raise ValueError('MISSING_ISOMERIC_SMILES_NO_CONNECTIVITY_FALLBACK')
        results.append({'candidate': len(results) + 1, 'cid': value['CID'],
                        'returned_smiles': returned, 'rdkit_isomeric_smiles': canonical(returned),
                        'inchikey': value.get('InChIKey', ''), 'formula': value.get('MolecularFormula', ''),
                        'status': 'AMBIGUOUS_CANDIDATES' if len(cids) > 1 else 'CANDIDATE_REQUIRES_REVIEW',
                        'warning': 'Database standardization and identifier resolution do not certify the supplied chemical identity.'})
    return results


def cir(row, client):
    if row['query_type'] not in {'name', 'cas', 'inchikey'}:
        raise ValueError('CIR_SUPPORTS_NAME_CAS_INCHIKEY_IN_THIS_MODULE')
    returned = client.get(CIR + urllib.parse.quote(row['query'], safe='') + '/smiles').strip()
    if '\n' in returned or len(returned) > 512:
        raise ValueError('UNEXPECTED_CIR_RESPONSE')
    return [{'candidate': 1, 'returned_smiles': returned, 'rdkit_isomeric_smiles': canonical(returned),
             'status': 'SERVICE_SELECTED_STRUCTURE_REQUIRES_REVIEW',
             'warning': 'CIR may choose one interpretation and omit named stereochemistry; this is not exhaustive candidate enumeration.'}]


def validate_query(row):
    kind, query = row['query_type'], row['query']
    if kind == 'cas' and not cas_checksum(query):
        raise ValueError('INVALID_CAS_SYNTAX_OR_CHECKSUM')
    if kind == 'cid' and not re.fullmatch(r'[1-9]\d{0,9}', query):
        raise ValueError('INVALID_CID')
    if kind == 'inchikey' and not re.fullmatch(r'[A-Z]{14}-[A-Z]{10}-[A-Z]', query):
        raise ValueError('INVALID_INCHIKEY_SYNTAX')


def save_input_failure(raw, output_dir, error):
    output = Path(output_dir).resolve()
    if output.is_relative_to(PAGE) or output.exists():
        raise ValueError('Use a NEW result directory outside the Skill source.')
    output.mkdir(parents=True)
    (output / 'input.csv').write_bytes(raw)
    (output / 'SKILL.used.md').write_bytes((PAGE / 'SKILL.md').read_bytes())
    dump(output / 'failure.json', {'status': 'FAILED_INPUT_RETAINED', 'type': type(error).__name__,
                                 'message': str(error), 'model_calls': 0, 'http_requests': 0})
    files = sorted(path for path in output.iterdir() if path.is_file())
    (output / 'SHA256SUMS.txt').write_text(''.join(sha(path.read_bytes()) + '  ' + path.name + '\n'
                                                for path in files), encoding='utf-8')
    with zipfile.ZipFile(output / 'results.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files + [output / 'SHA256SUMS.txt']:
            archive.write(path, path.name)


def run_skill(*, input_csv, output_dir, service='pubchem', allow_network=False):
    if service not in {'pubchem', 'cir', 'both'} or type(allow_network) is not bool:
        raise ValueError('Invalid service or network option.')
    raw = read_source(Path(input_csv))
    try:
        _, rows = read_input(Path(input_csv), raw=raw)
    except (ValueError, UnicodeError) as error:
        save_input_failure(raw, output_dir, error)
        raise
    if any(row['query_type'] != 'local_smiles' for row in rows) and not allow_network:
        raise ValueError('Remote identifiers require explicit --allow-network; nothing was sent.')
    output = Path(output_dir).resolve()
    if output.is_relative_to(PAGE) or output.exists():
        raise ValueError('Use a NEW result directory outside the Skill source.')
    skill = (PAGE / 'SKILL.md').read_bytes()
    skill.decode('utf-8')
    output.mkdir(parents=True)
    (output / 'responses').mkdir()
    (output / 'input.csv').write_bytes(raw)
    (output / 'SKILL.used.md').write_bytes(skill)
    client, results = Client(output), []
    for row in rows:
        services = ['local'] if row['query_type'] == 'local_smiles' else ['pubchem', 'cir'] if service == 'both' else [service]
        for provider in services:
            try:
                validate_query(row)
                if provider == 'local':
                    values = [{'candidate': 1, 'returned_smiles': row['query'],
                               'rdkit_isomeric_smiles': canonical(row['query']), 'status': 'LOCAL_GRAPH_PARSED',
                               'warning': 'Parsed graph only; no name, registry, stereochemical or experimental identity certification.'}]
                else:
                    values = (pubchem if provider == 'pubchem' else cir)(row, client)
                results.extend({**row, 'service': provider, **value} for value in values)
            except (ValueError, RuntimeError, KeyError, TypeError, UnicodeError) as error:
                results.append({**row, 'service': provider, 'status': 'FAILED_RETAINED', 'error': str(error)[:500]})
    with (output / 'candidates.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(results)
    dump(output / 'requests.json', client.events)
    failed = sum(row['status'] == 'FAILED_RETAINED' for row in results)
    receipt = {'status': 'COMPLETE_WITH_RETAINED_FAILURES' if failed else 'COMPLETE_CANDIDATES_NOT_CERTIFIED',
               'skill_use': 'READ_AND_SNAPSHOTTED_NO_MODEL_INTERPRETATION', 'model_calls': 0,
               'skill_sha256': sha(skill), 'input_sha256': sha(raw), 'records': len(rows),
               'candidate_rows': len(results), 'failed_service_rows': failed,
               'http_requests': len(client.events), 'service': service, 'allow_network': allow_network,
               'environment': {'python': sys.version.split()[0], 'rdkit': importlib.metadata.version('rdkit')},
               'scope': 'Bounded identifier candidates; no identity certification, no reverse InChIKey decoding.'}
    dump(output / 'run-receipt.json', receipt)
    files = sorted(path for path in output.rglob('*') if path.is_file())
    (output / 'SHA256SUMS.txt').write_text(''.join(sha(path.read_bytes()) + '  ' + path.relative_to(output).as_posix() + '\n'
                                                for path in files), encoding='utf-8')
    with zipfile.ZipFile(output / 'results.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files + [output / 'SHA256SUMS.txt']:
            archive.write(path, path.relative_to(output).as_posix())
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=PAGE / 'runtime/examples/01-local.csv')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--service', choices=['pubchem', 'cir', 'both'], default='pubchem')
    parser.add_argument('--allow-network', action='store_true')
    args = parser.parse_args()
    try:
        receipt = run_skill(input_csv=args.input, output_dir=args.output, service=args.service, allow_network=args.allow_network)
        print(json.dumps(receipt, ensure_ascii=False))
        return 0 if receipt['failed_service_rows'] == 0 else 1
    except (ValueError, OSError, UnicodeError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
