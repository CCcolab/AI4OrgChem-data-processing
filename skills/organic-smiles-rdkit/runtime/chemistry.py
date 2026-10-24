"""Chemical interpretation flags, independent of parse success and net charge."""
import json

SEMANTICS_VERSION = 'rdkit-small-organic-semantics-2'
ORGANIC_ELEMENTS = {1, 5, 6, 7, 8, 9, 14, 15, 16, 17, 35, 53}
METALS = ({3, 4, 11, 12, 13, 19, 20, 37, 38, 49, 50, 55, 56, 81, 82, 83, 87, 88}
          | set(range(21, 31)) | set(range(39, 49)) | set(range(57, 81))
          | set(range(89, 113)) | {113, 114, 115, 116})
WARNING_TEXT = {
    'PARSER_CLEANUP_CHANGED_GRAPH': 'RDKit解析清理调整了形式电荷或键表达；见cleanup_changes，原始输入仍保留。这不是额外的脱盐或中和。',
    'ATOM_MAPPING_PRESENT': '含原子映射标签；规范字符串及重复映射保留这些标签，不是忽略映射标签的化学身份比较。',
    'STEREO_MARKER_CLEANED': '输入立体标记被RDKit清理；应核对原始结构，不能宣称该标记有效保留。',
    'DIRECTIONAL_STEREO_REVIEW': '部分斜线方向标记未对应已指定的有效双键立体信息，请核对输入。',
    'NON_TETRAHEDRAL_STEREO_REVIEW': '非四面体立体编码超出本页已验证范围，需专业复核。',
    'STEREO_ANALYSIS_REVIEW': '立体语义检查未能完成，不能据此认定无立体信息。',
    'UNSPECIFIED_STEREO': '检测到潜在立体单元但构型未指定；这不等于无手性或外消旋混合物。',
    'MULTICOMPONENT': '多组分输入按整个图计算；结果不是该混合物或盐的实测物性。',
    'CHARGED_ATOMS': '存在带电原子（即使净电荷为0）；描述符对应输入的电荷/质子化状态。',
    'RADICAL': '存在自由基电子；普通闭壳层有机分子描述符的解释需复核。',
    'METAL': '含金属，超出本页普通有机分子描述符解释范围。',
    'NO_CARBON': '不含碳，超出本页有机分子解释范围。',
    'ELEMENT_SCOPE_REVIEW': '含本页名义有机元素集合之外的元素，描述符适用性待审。',
    'TPSA_S_P_CONVENTION': '含硫/磷；主TPSA明确不计S/P贡献，另列计入S/P的对照值。',
}
ERROR_TEXT = {
    'EMPTY_SMILES': '结构为空；请填写SMILES，原记录仍保留。',
    'SYNTAX_ERROR': 'SMILES语法解析失败；检查括号、闭环数字、原子符号及键写法。',
    'VALENCE_ERROR': '价态/属性清理失败；检查键级、显式氢、形式电荷和允许价态。',
    'AROMATICITY_ERROR': '芳香性或Kekule清理失败；检查芳香原子是否成环及芳香键写法。',
    'SANITIZATION_OTHER': '其他分子清理失败；需结合固定RDKit版本专业复核。',
    'ATOM_LIMIT_OR_DUMMY_ATOM': '超过128原子或含虚拟原子；不在本版输入范围。',
}
DESCRIPTOR_CONVENTIONS = {
    'version': SEMANTICS_VERSION,
    'mol_wt_g_mol': {'api': 'Descriptors.MolWt', 'unit': 'g/mol',
                    'definition': 'Average atomic weights for unlabeled atoms; specified isotope masses where labeled; not ExactMolWt.'},
    'formula': {'api': 'CalcMolFormula', 'separateIsotopes': False},
    'isotope_formula': {'api': 'CalcMolFormula', 'separateIsotopes': True, 'abbreviateHIsotopes': False},
    'mol_logp_model': {'api': 'Crippen.MolLogP', 'model': 'Wildman-Crippen atom contributions',
                       'unit': 'dimensionless', 'not': 'measured partition coefficient or pH-dependent logD'},
    'hbd': {'api': 'rdMolDescriptors.CalcNumHBD', 'unit': 'count', 'definition': 'Pinned RDKit H-bond donor definitions (Lipinski.cpp); not CalcNumLipinskiHBD.'},
    'hba': {'api': 'rdMolDescriptors.CalcNumHBA', 'unit': 'count', 'definition': 'Pinned RDKit H-bond acceptor definitions (Lipinski.cpp); not CalcNumLipinskiHBA.'},
    'tpsa_A2': {'api': 'rdMolDescriptors.CalcTPSA', 'unit': 'angstrom^2', 'includeSandP': False},
    'tpsa_with_S_P_A2': {'api': 'rdMolDescriptors.CalcTPSA', 'unit': 'angstrom^2', 'includeSandP': True},
    'protonation': 'All descriptors refer to the supplied graph; no pH prediction, neutralization or desalting.',
    'parser_cleanup': 'Default RDKit sanitization includes valence/organometallic cleanup. Charge and bond changes from those cleanup stages are reported; aromaticity perception and H removal are also part of parsing.',
    'duplicate_policy': 'Exact canonical isomeric SMILES equality in the pinned RDKit version, retaining atom maps; not universal or map-insensitive chemical identity.',
    'scope_policy': 'Per-record interpretation flags are conservative prompts, not a validated applicability-domain classifier.',
    'nominal_organic_atomic_numbers': sorted(ORGANIC_ELEMENTS),
    'metal_atomic_numbers_for_warning': sorted(METALS),
    'stereo_policy': 'Keep original input; report valid parsed stereo and detected cleanup/unspecified/unsupported information. Not complete stereochemical identity certification.',
    'index_policy': 'Query and potential-stereo indices: zero-based parsed molecule after default H removal. Input-marker indices: pre-cleanup graph with explicit H retained.',
}


def parse(raw, max_atoms=128):
    """Separate syntax and sanitization diagnostics; retain raw stereo tags."""
    from rdkit import Chem, rdBase

    if not raw.strip():
        return None, 'EMPTY_SMILES', {}
    options = Chem.SmilesParserParams()
    options.parseName = False
    options.allowCXSMILES = False
    options.sanitize = False
    options.removeHs = False
    with rdBase.BlockLogs():
        probe = Chem.MolFromSmiles(raw, options)
        if probe is None:
            return None, 'SYNTAX_ERROR', {}
        if probe.GetNumAtoms() > max_atoms or any(a.GetAtomicNum() == 0 for a in probe.GetAtoms()):
            return None, 'ATOM_LIMIT_OR_DUMMY_ATOM', {}
        tagged = {a.GetIdx(): a.GetChiralTag() for a in probe.GetAtoms()
                  if a.GetChiralTag() != Chem.ChiralType.CHI_UNSPECIFIED}
        directions = [b.GetIdx() for b in probe.GetBonds()
                      if b.GetBondDir() in (Chem.BondDir.ENDUPRIGHT, Chem.BondDir.ENDDOWNRIGHT)]
        # Isolate cleanup from aromaticity perception and H removal. Indices here
        # refer to the original explicit-H graph, not the final drawing.
        cleanup = Chem.Mol(probe)
        Chem.Cleanup(cleanup)
        Chem.CleanupOrganometallics(cleanup)
        changes = {
            'atoms': [{'index': a.GetIdx(), 'formal_charge_before': a.GetFormalCharge(),
                       'formal_charge_after': cleanup.GetAtomWithIdx(a.GetIdx()).GetFormalCharge()}
                      for a in probe.GetAtoms()
                      if a.GetFormalCharge() != cleanup.GetAtomWithIdx(a.GetIdx()).GetFormalCharge()],
            'bonds': [{'index': b.GetIdx(), 'type_before': str(b.GetBondType()),
                       'type_after': str(cleanup.GetBondWithIdx(b.GetIdx()).GetBondType())}
                      for b in probe.GetBonds()
                      if b.GetBondType() != cleanup.GetBondWithIdx(b.GetIdx()).GetBondType()],
        }
        flag = Chem.SanitizeMol(probe, catchErrors=True)
        if flag:
            if flag & Chem.SanitizeFlags.SANITIZE_PROPERTIES:
                error = 'VALENCE_ERROR'
            elif flag & (Chem.SanitizeFlags.SANITIZE_KEKULIZE | Chem.SanitizeFlags.SANITIZE_SETAROMATICITY):
                error = 'AROMATICITY_ERROR'
            else:
                error = 'SANITIZATION_OTHER'
            return None, error, {'sanitize_flag': str(flag)}
        Chem.AssignStereochemistry(probe, cleanIt=True, force=True)
        cleaned = [i for i in tagged if probe.GetAtomWithIdx(i).GetChiralTag() == Chem.ChiralType.CHI_UNSPECIFIED]
        unsupported = [i for i, tag in tagged.items() if tag not in (
            Chem.ChiralType.CHI_TETRAHEDRAL_CW, Chem.ChiralType.CHI_TETRAHEDRAL_CCW)]
        assigned_bonds = {b.GetIdx() for b in probe.GetBonds()
                          if b.GetStereo() not in (Chem.BondStereo.STEREONONE, Chem.BondStereo.STEREOANY)}
        unused_directions = []
        for idx in directions:
            bond = probe.GetBondWithIdx(idx)
            neighbors = {b.GetIdx() for atom in (bond.GetBeginAtom(), bond.GetEndAtom())
                         for b in atom.GetBonds() if b.GetBondType() == Chem.BondType.DOUBLE}
            if not neighbors.intersection(assigned_bonds):
                unused_directions.append(idx)
        options.sanitize = True
        options.removeHs = True
        mol = Chem.MolFromSmiles(raw, options)
    if mol is None:
        return None, 'SANITIZATION_OTHER', {}
    return mol, '', {'input_tagged_atom_indices': sorted(tagged), 'cleaned_atom_indices': cleaned,
                     'non_tetrahedral_atom_indices': unsupported, 'unused_direction_bond_indices': unused_directions,
                     'cleanup_changes': changes}


def interpret(mol, stereo):
    """Parse status is unchanged; warnings govern interpretation separately."""
    from rdkit import Chem

    codes = []
    if any(stereo['cleanup_changes'].values()):
        codes.append('PARSER_CLEANUP_CHANGED_GRAPH')
    if any(a.GetAtomMapNum() for a in mol.GetAtoms()):
        codes.append('ATOM_MAPPING_PRESENT')
    if stereo['cleaned_atom_indices']:
        codes.append('STEREO_MARKER_CLEANED')
    if stereo['unused_direction_bond_indices']:
        codes.append('DIRECTIONAL_STEREO_REVIEW')
    if stereo['non_tetrahedral_atom_indices']:
        codes.append('NON_TETRAHEDRAL_STEREO_REVIEW')
    try:
        potential = [{'type': str(s.type), 'index': s.centeredOn, 'specified': str(s.specified),
                      'descriptor': str(s.descriptor)} for s in Chem.FindPotentialStereo(mol)]
    except (RuntimeError, ValueError):
        potential = []
        codes.append('STEREO_ANALYSIS_REVIEW')
    if any(s['specified'] == 'Unspecified' for s in potential):
        codes.append('UNSPECIFIED_STEREO')
    atoms = list(mol.GetAtoms())
    components = len(Chem.GetMolFrags(mol))
    charged = sum(a.GetFormalCharge() != 0 for a in atoms)
    radicals = sum(a.GetNumRadicalElectrons() for a in atoms)
    metals = sorted({a.GetSymbol() for a in atoms if a.GetAtomicNum() in METALS})
    outside = sorted({a.GetSymbol() for a in atoms if a.GetAtomicNum() not in ORGANIC_ELEMENTS})
    for condition, code in [(components > 1, 'MULTICOMPONENT'), (charged, 'CHARGED_ATOMS'),
                             (radicals, 'RADICAL'), (metals, 'METAL'),
                             (not any(a.GetAtomicNum() == 6 for a in atoms), 'NO_CARBON'),
                             (outside, 'ELEMENT_SCOPE_REVIEW'),
                             (any(a.GetAtomicNum() in (15, 16) for a in atoms), 'TPSA_S_P_CONVENTION')]:
        if condition:
            codes.append(code)
    if any(code in codes for code in ('METAL', 'NO_CARBON', 'ELEMENT_SCOPE_REVIEW')):
        applicability = 'OUTSIDE_NOMINAL_ORGANIC_SCOPE'
    elif any(code in codes for code in ('MULTICOMPONENT', 'CHARGED_ATOMS', 'RADICAL')):
        applicability = 'DESCRIPTOR_INTERPRETATION_REVIEW_REQUIRED'
    else:
        applicability = 'NOMINAL_SMALL_ORGANIC_MODEL_NOT_EXPERIMENTAL'
    stereo_codes = [c for c in codes if 'STEREO' in c]
    status = ('REVIEW_REQUIRED' if any(c != 'UNSPECIFIED_STEREO' for c in stereo_codes)
              else 'UNSPECIFIED_POTENTIAL_STEREO' if stereo_codes
              else 'SPECIFIED' if potential else 'NO_POTENTIAL_STEREO_DETECTED')
    return {'charged_atom_count': charged, 'radical_electrons': radicals,
            'metal_elements': json.dumps(metals), 'descriptor_applicability': applicability,
            'stereo_status': status, 'stereo_details': json.dumps({**stereo, 'potential': potential}),
            'warning_codes': json.dumps(codes),
            'warning_messages': ' '.join(WARNING_TEXT[c] for c in codes)}
