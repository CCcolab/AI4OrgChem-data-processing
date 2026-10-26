"""Complete adapter for user-produced normalized result JSON in any existing environment.

No solver is launched. Export results from your existing program using the
analysis.py schema, then point this adapter at that file. File provenance must
identify actual software, method, units, geometry and convergence evidence.
"""
from pathlib import Path
import hashlib
import json


def run_backend(request, output_dir):
    if set(request['parameters']) != {'backend_result_file'} or request['data']:
        raise ValueError('File adapter expects parameters.backend_result_file and empty data.')
    source = Path(request['parameters']['backend_result_file'])
    if not source.is_absolute() or source.is_symlink() or not source.is_file() or source.stat().st_size > 2_000_000:
        raise ValueError('Provide an absolute regular result JSON file <=2 MB.')
    raw = source.read_bytes()
    (output_dir / 'backend-result.original.json').write_bytes(raw)
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
