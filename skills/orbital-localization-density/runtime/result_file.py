"""Complete adapter for user-produced normalized result JSON in any existing environment.

No solver is launched. Export results from your existing program using the
analysis.py schema, then point this adapter at that file. File provenance must
identify actual software, method, units, geometry and convergence evidence.
"""
from pathlib import Path
import hashlib
import json


def read_result_file(request, output_dir):
    if set(request['parameters']) != {'result_file'} or request['data']:
        raise ValueError('File adapter expects parameters.result_file and empty data.')
    if not isinstance(request['parameters']['result_file'], str) or not request['parameters']['result_file'].strip():
        raise ValueError('result_file must be a nonempty path string.')
    source = Path(request['parameters']['result_file'])
    if not source.is_absolute() or source.is_symlink() or not source.is_file() or source.stat().st_size > 2_000_000:
        raise ValueError('Provide an absolute regular result JSON file <=2 MB.')
    with source.open('rb') as stream:
        raw = stream.read(2_000_001)
    if len(raw) > 2_000_000:
        raise ValueError('Result file grew beyond 2 MB.')
    (output_dir / 'source-result.original.json').write_bytes(raw)
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result

    normalized = json.loads(raw.decode('utf-8-sig'), object_pairs_hook=unique,
                            parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Nonfinite JSON: ' + value)))
    return {'review_request': normalized,
            'execution': {'kind': 'USER_SUPPLIED_RESULT_FILE_REVIEW', 'new_quantum_calls': 0,
                          'model_calls': 0, 'network_calls': 0,
                          'source_file_sha256': hashlib.sha256(raw).hexdigest(),
                          'source_authentication': 'USER_DECLARED_NOT_INDEPENDENTLY_AUTHENTICATED'}}
