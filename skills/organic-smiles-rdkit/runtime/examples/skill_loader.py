"""Load run_skill() from the hyphenated public Python filename."""
from pathlib import Path
import importlib.util

SKILL_DIR = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('organic_smiles_rdkit', SKILL_DIR / 'runtime/organic-smiles-rdkit.py')
skill_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(skill_module)
run_skill = skill_module.run_skill
