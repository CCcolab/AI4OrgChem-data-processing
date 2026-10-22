"""Bounded educational RDKit tool. Copied to the new Skill page as molecule_tool.py."""
from pathlib import Path
import csv, hashlib, importlib.metadata, json, math, platform

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def dump(p, value): Path(p).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def validate(params):
    from rdkit import Chem
    if not isinstance(params,dict) or set(params)!={'radius','fp_size','include_chirality','query_smarts','reference_id'}: raise ValueError('参数字段必须与parameters.json一致。')
    if type(params['radius']) is not int or not 1<=params['radius']<=4: raise ValueError('radius必须为1至4整数。')
    if type(params['fp_size']) is not int or params['fp_size'] not in [1024,2048,4096]: raise ValueError('fp_size限1024/2048/4096。')
    if type(params['include_chirality']) is not bool: raise ValueError('include_chirality必须为布尔值。')
    if not isinstance(params['reference_id'],str) or not params['reference_id']: raise ValueError('reference_id缺失。')
    if not isinstance(params['query_smarts'],str) or not 1<=len(params['query_smarts'])<=120: raise ValueError('SMARTS不能为空或过长。')
    if Chem.MolFromSmarts(params['query_smarts']) is None: raise ValueError('无效SMARTS；未执行分析。')

def analyze(root, params, output):
    from rdkit import Chem, DataStructs, rdBase
    from rdkit.Chem import Crippen, Descriptors, Draw, rdMolDescriptors, rdFingerprintGenerator
    from rdkit.Chem.Scaffolds import MurckoScaffold
    validate(params)
    root,output=Path(root),Path(output)
    if output.exists(): raise FileExistsError('输出目录已存在；请使用新目录，不能覆盖。')
    provenance=json.loads((root/'data-provenance.json').read_text('utf-8'))
    if sha(root/'molecules.csv')!=provenance['sha256']: raise ValueError('样本哈希不匹配。')
    with (root/'molecules.csv').open(encoding='utf-8',newline='') as f:
        reader=csv.DictReader(f)
        if reader.fieldnames!=['id','label','smiles','source_id','role']: raise ValueError('样本列与模板不一致。')
        inputs=list(reader)
    if not 1<=len(inputs)<=50: raise ValueError('本页限定1至50条记录。')
    if len({r['id'] for r in inputs})!=len(inputs) or any(not r['id'] for r in inputs): raise ValueError('ID缺失或重复。')
    query=Chem.MolFromSmarts(params['query_smarts'])
    generator=rdFingerprintGenerator.GetMorganGenerator(radius=params['radius'],fpSize=params['fp_size'],includeChirality=params['include_chirality'])
    results=[];mols={};fps={};first={};duplicates=[]
    for index,record in enumerate(inputs):
        row={'record_index':index,**record,'parse_status':'REJECTED','error':''}
        raw=record['smiles']
        if not raw.strip(): row['error']='EMPTY_SMILES';results.append(row);continue
        with rdBase.BlockLogs(): mol=Chem.MolFromSmiles(raw)
        if mol is None: row['error']='PARSE_OR_SANITIZE_FAILED';results.append(row);continue
        canonical=Chem.MolToSmiles(mol,canonical=True,isomericSmiles=True)
        with rdBase.BlockLogs(): again=Chem.MolFromSmiles(canonical)
        if again is None or Chem.MolToSmiles(again,isomericSmiles=True)!=canonical: raise ArithmeticError('SMILES往返不一致。')
        matches=mol.GetSubstructMatches(query,uniquify=True,useChirality=params['include_chirality'])
        scaffold=Chem.MolToSmiles(MurckoScaffold.GetScaffoldForMol(mol),isomericSmiles=True)
        fp=generator.GetFingerprint(mol)
        row.update(parse_status='VALID',canonical_isomeric_smiles=canonical,
            formula=rdMolDescriptors.CalcMolFormula(mol),formal_charge=Chem.GetFormalCharge(mol),
            components=len(Chem.GetMolFrags(mol)),mol_wt_g_mol=Descriptors.MolWt(mol),
            mol_logp_model=Crippen.MolLogP(mol),hbd=rdMolDescriptors.CalcNumHBD(mol),
            hba=rdMolDescriptors.CalcNumHBA(mol),tpsa_A2=rdMolDescriptors.CalcTPSA(mol),
            query_match_count=len(matches),query_atom_indices=json.dumps(matches),
            scaffold=scaffold,scaffold_status='NONEMPTY' if scaffold else 'EMPTY_ACYCLIC',
            chiral_centers=json.dumps(Chem.FindMolChiralCenters(mol,includeUnassigned=True)),
            fingerprint_on_bits=fp.GetNumOnBits())
        if canonical in first: duplicates.append({'id':record['id'],'first_id':first[canonical],'rule':'RDKit canonical isomeric SMILES; no standardization'})
        else:first[canonical]=record['id']
        results.append(row);mols[record['id']]=mol;fps[record['id']]=fp
    if params['reference_id'] not in fps: raise ValueError('reference_id不对应有效记录；拒绝分析。')
    similarities=[]
    for id_,fp in fps.items():
        ref=fps[params['reference_id']]
        score=DataStructs.TanimotoSimilarity(ref,fp)
        a,b=set(ref.GetOnBits()),set(fp.GetOnBits())
        union=a|b
        oracle=len(a&b)/len(union) if union else 1.0
        if abs(score-oracle)>1e-15: raise ArithmeticError('Tanimoto独立位集合核算失败。')
        similarities.append({'reference_id':params['reference_id'],'id':id_,'tanimoto':score,'set_oracle':oracle})
    checks={'record_alignment':len(results)==len(inputs) and [r['id'] for r in results]==[r['id'] for r in inputs],
        'all_valid_roundtrip':all(r['canonical_isomeric_smiles']==Chem.MolToSmiles(mols[r['id']],isomericSmiles=True) for r in results if r['parse_status']=='VALID'),
        'finite_descriptors':all(math.isfinite(r[k]) for r in results if r['parse_status']=='VALID' for k in ['mol_wt_g_mol','mol_logp_model','tpsa_A2']),
        'tanimoto_set_oracle':True,'self_similarity_one':next(r['tanimoto'] for r in similarities if r['id']==params['reference_id'])==1.0,
        'inputs_unchanged':sha(root/'molecules.csv')==provenance['sha256']}
    # These independent chemical regression expectations apply only to the bundled teaching fixture.
    fixture={r['id']:r for r in results}
    expected_ids=[f'{n:03}' for n in range(1,15)]
    if list(fixture)==expected_ids:
        checks.update(ethanol_equivalent=fixture['001']['canonical_isomeric_smiles']==fixture['002']['canonical_isomeric_smiles'],
          acid_and_acetate_distinct=fixture['003']['canonical_isomeric_smiles']!=fixture['004']['canonical_isomeric_smiles'] and fixture['003']['formal_charge']==0 and fixture['004']['formal_charge']==-1,
          enantiomers_preserved=fixture['009']['canonical_isomeric_smiles']!=fixture['010']['canonical_isomeric_smiles'],
          invalid_and_empty_retained=fixture['011']['parse_status']==fixture['012']['parse_status']=='REJECTED',
          disconnected_salt_retained=fixture['013']['components']==2,
          isotope_preserved='13C' in fixture['014']['canonical_isomeric_smiles'],
          benzene_formula=fixture['005']['formula']=='C6H6',aspirin_formula=fixture['008']['formula']=='C9H8O4')
        if params['query_smarts']=='[CX3](=O)[OX2H1]': checks['carboxylic_acid_query']=all(fixture[i]['query_match_count']==n for i,n in [('003',1),('004',0),('007',1),('008',1)])
        # Element-count formula is independent of descriptor name lookup; average atomic weights from RDKit table.
        pt=Chem.GetPeriodicTable();mass=2*pt.GetAtomicWeight(6)+6*pt.GetAtomicWeight(1)+pt.GetAtomicWeight(8)
        checks['ethanol_formula_and_mass']=fixture['001']['formula']=='C2H6O' and abs(fixture['001']['mol_wt_g_mol']-mass)<1e-8
    if not all(checks.values()): raise ArithmeticError('科学程序检查失败：'+','.join(k for k,v in checks.items() if not v))
    output.mkdir(parents=True)
    dump(output/'parameters.json',params)
    for name in ['molecules.csv','data-provenance.json','sources.json','SKILL.md']:(output/name).write_bytes((root/name).read_bytes())
    fields=list(dict.fromkeys(k for row in results for k in row))
    for filename,rows,columns in [('analysis.csv',results,fields),('errors.csv',[r for r in results if r['parse_status']!='VALID'],fields),('duplicates.csv',duplicates,['id','first_id','rule']),('similarity.csv',similarities,['reference_id','id','tanimoto','set_oracle'])]:
        with (output/filename).open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows(rows)
    (output/'molecules.png').write_bytes(Draw.MolsToGridImage(list(mols.values()),molsPerRow=4,subImgSize=(260,180),legends=list(mols),returnPNG=True))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(9,4),layout='constrained')
    ax.bar([r['id'] for r in similarities],[r['tanimoto'] for r in similarities]);ax.set_ylim(0,1.05);ax.set_xlabel('Record ID');ax.set_ylabel('Morgan bit Tanimoto to '+params['reference_id'])
    fig.savefig(output/'similarity.png',dpi=130);plt.close(fig)
    summary={'status':'PASS_BOUNDED_RDKIT_ANALYSIS','records':len(inputs),'valid':len(mols),'rejected':len(inputs)-len(mols),'duplicates':duplicates,
        'checks':checks,'parameters':params,'preprocessing':'No desalting, neutralization, tautomer normalization or stereochemistry removal',
        'fingerprint_type':'fixed-length Morgan bit vector','descriptor_units':{'mol_wt_g_mol':'g/mol','mol_logp_model':'dimensionless model estimate, not logD','tpsa_A2':'angstrom^2'},
        'environment':{'python':platform.python_version(),'rdkit':rdBase.rdkitVersion,'numpy':importlib.metadata.version('numpy'),'matplotlib':importlib.metadata.version('matplotlib')},
        'limitations':['Teaching structures, not an experimental dataset','SMARTS matches depend on the stated query, not a universal functional-group counter','Fingerprint equality is not proof of molecular identity or biological equivalence','Descriptors are computed estimates, not measured properties','No structure edits, standardization, PubChem query, activity or reaction prediction in this page'], 'new_rhf':'NOT_ACCEPTED'}
    dump(output/'numerical-result.json',summary)
    return summary
