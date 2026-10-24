"""table-fitting-residuals: local Python entry; use --help for parameters."""

from pathlib import Path
import sys

if __name__ == "__main__":
    runtime = Path(__file__).resolve().parent
    if not (runtime / "python_runner.py").is_file():
        raise SystemExit("请下载并解压完整Python代码包，保持本文件与runtime目录同级。")
    sys.path.insert(0, str(runtime))
    from python_runner import main

    raise SystemExit(main("table", __file__))
