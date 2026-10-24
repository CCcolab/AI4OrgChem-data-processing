"""Read-only routing and existing Runtime host-identity review; never launches it."""
from pathlib import Path
import hashlib
import json
import re

ROUTES={
 'fixed_water_rhf':{'service':'molecular-service','task':'single-point','scientific_execution':'NOT_EXECUTED','limit':'Only the registered fixed-water ordinary RHF protocol, not arbitrary user conditional calculations.'},
 'saved_ao_review':{'service':'LOCAL_POSTPROCESSING_NO_RUNTIME','task':'supplied-arrays-review','scientific_execution':'NO_NEW_SCF','limit':'Use actual arrays, overlap metric, AO ordering, occupation and source; never substitute old outputs for a new calculation.'},
 'conditional_user_compute':None,
}

def exact(value,required):
    if not isinstance(value,dict) or set(value)!=set(required):raise ValueError('Require exactly: '+','.join(required))

def analyze(parameters,data):
    exact(parameters,['mode','intent']);mode=parameters['mode'];intent=parameters['intent']
    if mode not in {'route','inspect'} or intent not in ROUTES:raise ValueError('Unsupported explicit mode/intent.')
    if ROUTES[intent] is None:raise ValueError('Arbitrary user conditional compute is not admitted. No automatic registration/installation or fallback to saved results.')
    route=dict(ROUTES[intent]);checks=[];identity=None
    if mode=='route':exact(data,['user_goal'])
    else:
        exact(data,['user_goal','runtime_root','installation_record','expected_record_sha256'])
        if intent!='fixed_water_rhf':raise ValueError('Installation inspection is only for fixed ordinary water route.')
        root=Path(data['runtime_root']).resolve();record_path=Path(data['installation_record'])
        digest=data['expected_record_sha256']
        if not isinstance(digest,str) or not re.fullmatch('[0-9a-f]{64}',digest):raise ValueError('Explicit SHA-256 is required, not copied from an unchecked local file by this tool.')
        if record_path.is_symlink() or not record_path.is_file() or record_path.stat().st_size>128000:raise ValueError('Provide a bounded existing regular installation record.')
        raw=record_path.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('Installation record identity mismatch; stop, do not re-register.')
        record=json.loads(raw)
        if (record.get('schema')!='ai4orgchem-runtime-installation-v1' or record.get('service')!='molecular-service'
            or record.get('tasks')!=['single-point'] or record.get('modes')!=['live'] or record.get('backend')!='docker'
            or not re.fullmatch('sha256:[0-9a-f]{64}',record.get('image_id',''))):raise ValueError('Registration does not match supported Docker single-point service.')
        host=record.get('host_files')
        if not isinstance(host,dict) or not 1<=len(host)<=64 or 'scripts/run-installed-runtime.py' not in host:raise ValueError('Expected bounded registered host file catalog.')
        for name,sha in host.items():
            path=root/name
            if not isinstance(name,str) or not re.fullmatch('[0-9a-f]{64}',sha) or path.is_symlink() or not path.resolve().is_relative_to(root) or not path.is_file() or path.stat().st_size>5000000 or hashlib.sha256(path.read_bytes()).hexdigest()!=sha:
                raise ValueError('Registered host file differs: '+str(name))
        identity={'record_sha256':digest,'service':record['service'],'image_id':record['image_id'],
            'host_files_verified':len(host),'scientific_acceptance_from_record':record.get('scientific_acceptance','UNKNOWN'),
            'engine_status':'NOT_PROBED','container_image_presence':'NOT_PROBED','profile_scientific_gates':'NOT_EXECUTED'}
        checks.append({'name':'existing_record_and_registered_host_bytes_match','passed':True,'actual':True,'threshold':True})
    if not isinstance(data['user_goal'],str) or not data['user_goal'].strip():raise ValueError('Explicit user goal required.')
    return {'scope':'READ_ONLY_RUNTIME_ROUTING_AND_OPTIONAL_HOST_IDENTITY_NOT_COMPUTE_OR_BACKEND_ACCEPTANCE',
        'route':route,'installation_identity':identity,'checks':checks,'launched_processes':0,'registry_writes':0,
        'preflight_next':['Verify actual installed service, image, dependency lock and profile through its own registered launcher.',
                         'Keep queue, scientific execution and cleanup windows separate; do not silently change occupation/operator/protocol.',
                         'Run only after explicit execution scope and budget are set; inspect actual final receipt and numerical gates.'],
        'limits':['A matching record/host catalog does not prove an engine is running, image is present or science has passed.',
                  'This helper does not invoke Docker, install packages, register services, build images, change settings or launch scientific work.',
                  'Unsupported tasks stop explicitly; saved data never masquerade as new backend computation.']}
