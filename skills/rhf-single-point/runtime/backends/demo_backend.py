"""Complete bridge demonstration using supplied numbers, NOT a quantum engine.

An actual adapter has the same signature and calls the user's installed library
or reads their existing result files. Never silently substitute this demo for it.
"""
from copy import deepcopy


def run_backend(request, output_dir):
    (output_dir / 'backend-call-count.txt').write_text('1', encoding='utf-8')
    reviewed = deepcopy(request)
    reviewed['provenance'] = {
        'kind': 'SYNTHETIC_ENGINEERING_DEMO',
        'description': 'Bridge invocation replaying supplied numbers; NO SCF, localization or optimization.'}
    return {'review_request': reviewed,
            'execution': {'kind': 'SYNTHETIC_ENGINEERING_DEMO', 'software': 'Python standard library',
                          'quantum_calls': 0, 'model_calls': 0, 'network_calls': 0,
                          'resources': 'Tiny in-process copy; no CPU/memory/wall-clock hard limits'}}
