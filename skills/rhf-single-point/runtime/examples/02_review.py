"""Case 2: review; compute needs the existing registered Runtime, not a model account."""
from pathlib import Path
import runpy
import sys
PAGE=Path(__file__).resolve().parents[2]
if __name__ == '__main__':
    sys.argv=[str(PAGE/'runtime/run_skill.py'),'--mode','review',*sys.argv[1:]]
    runpy.run_path(str(PAGE/'runtime/run_skill.py'),run_name='__main__')
