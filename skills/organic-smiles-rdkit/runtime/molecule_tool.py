"""Bounded educational RDKit tool. Copied to the new Skill page as molecule_tool.py."""

from pathlib import Path
import csv
import hashlib
import importlib.metadata
import io
import json
import math
import platform
import re

MAX_INPUT_BYTES = 128_000
MAX_RECORDS = 50
MAX_SMILES_LENGTH = 512
MAX_ATOMS = 128
MAX_MATCHES = 1_000
INPUT_FIELDS = ["id", "label", "smiles", "source_id", "role"]


def _query(text):
    from rdkit import Chem, rdBase

    options = Chem.SmartsParserParams()
    options.parseName = False
    options.allowCXSMILES = False
    with rdBase.BlockLogs():
        query = Chem.MolFromSmarts(text, options)
    if query is None or query.GetNumAtoms() > 32:
        raise ValueError("无效SMARTS、名称/扩展后缀或查询超过32原子；未执行分析。")
    return query


def _inputs(root, expected_sha):
    path = root / "molecules.csv"
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError("CSV超过128000字节上限。")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_sha:
        raise ValueError("样本哈希不匹配。")
    try:
        reader = csv.DictReader(
            io.StringIO(raw.decode("utf-8"), newline=""), strict=True
        )
        if reader.fieldnames != INPUT_FIELDS:
            raise ValueError("样本列与模板不一致。")
        rows = list(reader)
    except (UnicodeError, csv.Error) as exc:
        raise ValueError("CSV编码或引号格式错误；必须使用UTF-8。") from exc
    if not 1 <= len(rows) <= MAX_RECORDS:
        raise ValueError("本页限定1至50条记录。")
    for row in rows:
        if set(row) != set(INPUT_FIELDS) or any(
            not isinstance(v, str) for v in row.values()
        ):
            raise ValueError("CSV数据行存在缺列或多余列。")
        if any(len(v) > 1024 or any(ord(c) < 32 for c in v) for v in row.values()):
            raise ValueError("CSV字段过长或包含控制字符。")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", row["id"]):
            raise ValueError(
                "ID须为1至64位字母、数字、点、下划线或连字符，以字母或数字开头。"
            )
        if any(v.lstrip().startswith(("=", "+", "-", "@")) for v in row.values()):
            raise ValueError("CSV字段包含电子表格公式前缀；本页只接受字面文本。")
        if len(row["smiles"]) > MAX_SMILES_LENGTH:
            raise ValueError("SMILES超过512字符上限。")
    if len({row["id"] for row in rows}) != len(rows):
        raise ValueError("ID重复。")
    return rows


def validate_parameters(params):
    """Check the public schema without importing RDKit in the Python程序 host."""
    if not isinstance(params, dict) or set(params) != {
        "radius",
        "fp_size",
        "include_chirality",
        "query_smarts",
        "reference_id",
    }:
        raise ValueError("参数字段必须与parameters.json一致。")
    if type(params["radius"]) is not int or not 1 <= params["radius"] <= 4:
        raise ValueError("radius必须为1至4整数。")
    if type(params["fp_size"]) is not int or params["fp_size"] not in (
        1024,
        2048,
        4096,
    ):
        raise ValueError("fp_size限1024/2048/4096。")
    if type(params["include_chirality"]) is not bool:
        raise ValueError("include_chirality必须为布尔值。")
    if not isinstance(params["reference_id"], str) or not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", params["reference_id"]
    ):
        raise ValueError("reference_id必须是有效输入ID。")
    if (
        not isinstance(params["query_smarts"], str)
        or not 1 <= len(params["query_smarts"]) <= 120
        or any(c.isspace() for c in params["query_smarts"])
    ):
        raise ValueError("SMARTS必须为1至120字符，不接受名称或空白后缀。")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(p, value):
    Path(p).write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def validate(params):
    validate_parameters(params)
    _query(params["query_smarts"])


def _molecule(raw):
    from chemistry import parse

    mol, error, _ = parse(raw, MAX_ATOMS)
    return mol, error


def preflight(root, params):
    """Reject malformed input or an unusable reference before any paid request."""
    validate(params)
    root = Path(root)
    provenance = json.loads((root / "data-provenance.json").read_text("utf-8"))
    inputs = _inputs(root, provenance["sha256"])
    reference = next(
        (row for row in inputs if row["id"] == params["reference_id"]), None
    )
    if reference is None or _molecule(reference["smiles"])[1]:
        raise ValueError("reference_id不对应有效记录；未发送模型请求。")


def analyze(root, params, output):
    """Analyze verified input and write a new output directory after checks pass."""
    from rdkit import Chem, DataStructs, rdBase
    from rdkit.Chem import (
        Crippen,
        Descriptors,
        Draw,
        rdMolDescriptors,
        rdFingerprintGenerator,
    )
    from rdkit.Chem.Scaffolds import MurckoScaffold
    from chemistry import DESCRIPTOR_CONVENTIONS, ERROR_TEXT, interpret, parse

    validate(params)
    root, output = Path(root), Path(output)
    if output.exists():
        raise FileExistsError("输出目录已存在；请使用新目录，不能覆盖。")
    provenance = json.loads((root / "data-provenance.json").read_text("utf-8"))
    inputs = _inputs(root, provenance["sha256"])
    query = _query(params["query_smarts"])
    generator = rdFingerprintGenerator.GetMorganGenerator(
        radius=params["radius"],
        fpSize=params["fp_size"],
        includeChirality=params["include_chirality"],
    )
    results = []
    mols = {}
    fps = {}
    first = {}
    duplicates = []
    for index, record in enumerate(inputs):
        row = {"record_index": index, **record, "parse_status": "REJECTED", "error": ""}
        mol, error, stereo = parse(record["smiles"], MAX_ATOMS)
        if error:
            row["error"] = error
            row["error_hint"] = ERROR_TEXT[error]
            row["parse_details"] = json.dumps(stereo)
            row["descriptor_applicability"] = "NOT_CALCULATED"
            results.append(row)
            continue
        canonical = Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True)
        with rdBase.BlockLogs():
            again = Chem.MolFromSmiles(canonical)
        if again is None or Chem.MolToSmiles(again, isomericSmiles=True) != canonical:
            raise ArithmeticError("SMILES往返不一致。")
        matches = mol.GetSubstructMatches(
            query,
            uniquify=True,
            useChirality=params["include_chirality"],
            maxMatches=MAX_MATCHES + 1,
        )
        if len(matches) > MAX_MATCHES:
            raise ValueError("SMARTS匹配超过1000项；拒绝把截断数作为完整匹配数。")
        scaffold = Chem.MolToSmiles(
            MurckoScaffold.GetScaffoldForMol(mol), isomericSmiles=True
        )
        fp = generator.GetFingerprint(mol)
        row.update(
            parse_status="VALID",
            canonical_isomeric_smiles=canonical,
            formula=rdMolDescriptors.CalcMolFormula(mol),
            isotope_formula=rdMolDescriptors.CalcMolFormula(
                mol, separateIsotopes=True, abbreviateHIsotopes=False
            ),
            formal_charge=Chem.GetFormalCharge(mol),
            components=len(Chem.GetMolFrags(mol)),
            mol_wt_g_mol=Descriptors.MolWt(mol),
            mol_logp_model=Crippen.MolLogP(mol),
            hbd=rdMolDescriptors.CalcNumHBD(mol),
            hba=rdMolDescriptors.CalcNumHBA(mol),
            tpsa_A2=rdMolDescriptors.CalcTPSA(mol, includeSandP=False),
            tpsa_with_S_P_A2=rdMolDescriptors.CalcTPSA(mol, includeSandP=True),
            query_match_count=len(matches),
            query_atom_indices=json.dumps(matches),
            scaffold=scaffold,
            scaffold_status="NONEMPTY" if scaffold else "EMPTY_ACYCLIC",
            chiral_centers=json.dumps(
                Chem.FindMolChiralCenters(mol, includeUnassigned=True)
            ),
            fingerprint_on_bits=fp.GetNumOnBits(),
        )
        row.update(interpret(mol, stereo))
        if canonical in first:
            duplicates.append(
                {
                    "id": record["id"],
                    "first_id": first[canonical],
                    "rule": "RDKit canonical isomeric SMILES; no standardization",
                }
            )
        else:
            first[canonical] = record["id"]
        results.append(row)
        mols[record["id"]] = mol
        fps[record["id"]] = fp
    if params["reference_id"] not in fps:
        raise ValueError("reference_id不对应有效记录；拒绝分析。")
    similarities = []
    for id_, fp in fps.items():
        ref = fps[params["reference_id"]]
        score = DataStructs.TanimotoSimilarity(ref, fp)
        a, b = set(ref.GetOnBits()), set(fp.GetOnBits())
        union = a | b
        oracle = len(a & b) / len(union) if union else 1.0
        if abs(score - oracle) > 1e-15:
            raise ArithmeticError("Tanimoto独立位集合核算失败。")
        similarities.append(
            {
                "reference_id": params["reference_id"],
                "id": id_,
                "tanimoto": score,
                "set_oracle": oracle,
            }
        )
    checks = {
        "record_alignment": len(results) == len(inputs)
        and [r["id"] for r in results] == [r["id"] for r in inputs],
        "all_valid_roundtrip": all(
            r["canonical_isomeric_smiles"]
            == Chem.MolToSmiles(mols[r["id"]], isomericSmiles=True)
            for r in results
            if r["parse_status"] == "VALID"
        ),
        "finite_descriptors": all(
            math.isfinite(r[k])
            for r in results
            if r["parse_status"] == "VALID"
            for k in ["mol_wt_g_mol", "mol_logp_model", "tpsa_A2", "tpsa_with_S_P_A2"]
        ),
        "tanimoto_set_oracle": True,
        "self_similarity_one": next(
            r["tanimoto"] for r in similarities if r["id"] == params["reference_id"]
        )
        == 1.0,
        "inputs_unchanged": sha(root / "molecules.csv") == provenance["sha256"],
    }
    if not all(checks.values()):
        raise ArithmeticError(
            "科学程序检查失败：" + ",".join(k for k, v in checks.items() if not v)
        )
    output.mkdir(parents=True)
    dump(output / "parameters.json", params)
    dump(output / "descriptor-conventions.json", DESCRIPTOR_CONVENTIONS)
    for name in ["molecules.csv", "data-provenance.json", "sources.json", "SKILL.md"]:
        (output / name).write_bytes((root / name).read_bytes())
    fields = list(dict.fromkeys(k for row in results for k in row))
    for filename, rows, columns in [
        ("analysis.csv", results, fields),
        ("errors.csv", [r for r in results if r["parse_status"] != "VALID"], fields),
        ("warnings.csv", [r for r in results if json.loads(r.get("warning_codes", "[]"))], fields),
        ("duplicates.csv", duplicates, ["id", "first_id", "rule"]),
        (
            "similarity.csv",
            similarities,
            ["reference_id", "id", "tanimoto", "set_oracle"],
        ),
    ]:
        with (output / filename).open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=columns)
            w.writeheader()
            w.writerows(rows)
    (output / "molecules.png").write_bytes(
        Draw.MolsToGridImage(
            list(mols.values()),
            molsPerRow=4,
            subImgSize=(260, 180),
            legends=list(mols),
            returnPNG=True,
        )
    )
    # Atom numbers use the same zero-based parsed-graph indices as query_atom_indices.
    from rdkit.Chem.Draw import rdMolDraw2D
    from rdkit.Chem import rdDepictor

    ids = list(mols)
    drawer = rdMolDraw2D.MolDraw2DCairo(960, ((len(ids) + 3) // 4) * 240, 240, 240)
    drawer.drawOptions().addAtomIndices = True
    pictured = [Chem.Mol(mols[id_]) for id_ in ids]
    for mol in pictured:
        rdDepictor.Compute2DCoords(mol)
    highlights = [sorted({atom for match in mol.GetSubstructMatches(
        query, useChirality=params['include_chirality'], maxMatches=MAX_MATCHES + 1
    ) for atom in match}) for mol in pictured]
    drawer.DrawMolecules(pictured, legends=ids, highlightAtoms=highlights)
    drawer.FinishDrawing()
    (output / 'query-highlight.png').write_bytes(drawer.GetDrawingText())
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 4), layout="constrained")
    ax.bar([r["id"] for r in similarities], [r["tanimoto"] for r in similarities])
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Record ID")
    ax.set_ylabel("Morgan bit Tanimoto to " + params["reference_id"])
    ax.set_title(f"Morgan bit | radius={params['radius']} | fpSize={params['fp_size']} | "
                 f"chirality={params['include_chirality']} | reference={params['reference_id']}")
    fig.savefig(output / "similarity.png", dpi=130)
    plt.close(fig)
    summary = {
        "status": "PASS_BOUNDED_RDKIT_ANALYSIS",
        "records": len(inputs),
        "valid": len(mols),
        "rejected": len(inputs) - len(mols),
        "duplicates": duplicates,
        "checks": checks,
        "parameters": params,
        "preprocessing": "Original input retained; no desalting, neutralization or tautomer normalization; default RDKit valence/organometallic and stereo cleanup is diagnosed separately",
        "engineering_check_scope": "Six invariants only; chemical semantic regression is a separate explicit command, never hash-gated",
        "chemical_semantics_version": DESCRIPTOR_CONVENTIONS['version'],
        "descriptor_conventions": DESCRIPTOR_CONVENTIONS,
        "warning_records": sum(bool(json.loads(r.get('warning_codes', '[]'))) for r in results),
        "applicability_counts": {scope: sum(r.get('descriptor_applicability') == scope for r in results)
                                 for scope in sorted({r['descriptor_applicability'] for r in results})},
        "fingerprint_type": "fixed-length Morgan bit vector",
        "descriptor_units": {
            "mol_wt_g_mol": "g/mol",
            "mol_logp_model": "dimensionless model estimate, not logD",
            "tpsa_A2": "angstrom^2",
        },
        "environment": {
            "python": platform.python_version(),
            "rdkit": rdBase.rdkitVersion,
            "numpy": importlib.metadata.version("numpy"),
            "matplotlib": importlib.metadata.version("matplotlib"),
        },
        "limitations": [
            "Input provenance is recorded separately; structure strings alone do not authenticate experimental data",
            "SMARTS matches depend on the stated query, not a universal functional-group counter",
            "Fingerprint equality is not proof of molecular identity or biological equivalence",
            "Descriptors are computed estimates, not measured properties",
            "Parse validity is not descriptor applicability; flags are conservative review prompts, not a validated applicability domain",
            "Unspecified stereo is not absence of chirality or evidence of a racemate; non-tetrahedral stereo requires review",
            "No additional structure editing, desalting, neutralization, tautomer normalization, PubChem query, activity or reaction prediction",
        ],
        "new_rhf": "NOT_ACCEPTED",
    }
    dump(output / "numerical-result.json", summary)
    return summary
