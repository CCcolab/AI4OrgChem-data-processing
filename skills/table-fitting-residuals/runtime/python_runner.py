"""Local Python execution, optional bounded agent, and self-contained reports."""

from pathlib import Path
import argparse
import base64
import hashlib
import html
import importlib
import importlib.metadata
import json
import os
import platform
import re
import subprocess
import sys
import uuid
import zipfile


def digest(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, value):
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def strict_json(path):
    if path.stat().st_size > 128_000:
        raise ValueError("参数文件超过128000字节。")

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("参数存在重复字段。")
            result[key] = value
        return result

    return json.loads(
        path.read_text("utf-8-sig"),
        object_pairs_hook=pairs,
        parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError("参数必须为有限JSON数值。")
        ),
    )


def verify_resources(page):
    root = page / "runtime"
    rows = strict_json(root / "resource-manifest.json")
    if not isinstance(rows, list) or not rows:
        raise ValueError("资源清单无效。")
    if any(
        not isinstance(row, dict)
        or set(row) != {"file", "sha256"}
        or not isinstance(row["file"], str)
        or not isinstance(row["sha256"], str)
        or re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) is None
        for row in rows
    ):
        raise ValueError("资源清单字段或哈希无效。")
    names = [row["file"] for row in rows]
    actual = {
        p.name
        for p in root.iterdir()
        if p.is_file() and p.name != "resource-manifest.json"
    }
    if len(names) != len(set(names)) or set(names) != actual:
        raise ValueError("资源清单缺失、多余或重复。")
    for row in rows:
        name = row["file"]
        if Path(name).name != name or "/" in name or "\\" in name:
            raise ValueError("资源路径不合法。")
        path = root / name
        if path.is_symlink() or digest(path.read_bytes()) != row["sha256"]:
            raise ValueError("资源SHA-256不一致：" + name)
    if (page / "SKILL.md").read_bytes() != (root / "SKILL.md").read_bytes():
        raise ValueError("顶层SKILL.md与运行资源不一致。")
    return root


def check_environment(root):
    required = {}
    for line in (root / "requirements.txt").read_text("utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            name, version = line.split("==")
            required[name] = version
    actual = {}
    for name, expected in required.items():
        try:
            actual[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            raise RuntimeError(
                "缺少依赖；请先运行 python -m pip install -r requirements.txt。"
            ) from None
        # RDKit metadata normalizes a zero-padded release component.
        if tuple(int(x) for x in actual[name].split(".")) != tuple(
            int(x) for x in expected.split(".")
        ):
            raise RuntimeError(
                "依赖版本不符：" + name + "；请在独立虚拟环境安装requirements.txt。"
            )
    return {"python": platform.python_version(), "packages": actual}


def run_agent(kind, root, parameters, output, env_file):
    credentials = importlib.import_module("credential_config")
    key = credentials.read_local_key(env_file)
    worker = (
        "import json,os,sys;from pathlib import Path;"
        "sys.path.insert(0,sys.argv[1]);import skill_agent;"
        "getattr(skill_agent,sys.argv[2])(Path(sys.argv[1]),json.loads(sys.argv[3]),"
        "Path(sys.argv[4]),os.environ['DEEPSEEK_API_KEY'],'LOCAL')"
    )
    environment = dict(os.environ)
    environment["DEEPSEEK_API_KEY"] = key
    environment["MPLBACKEND"] = "Agg"
    process = None
    try:
        process = subprocess.Popen(
            [
                sys.executable,
                "-B",
                "-c",
                worker,
                str(root),
                "run" if kind == "rdkit" else "run_skill",
                json.dumps(parameters, allow_nan=False),
                str(output),
            ],
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            stdout, stderr = process.communicate(
                timeout=290 if kind == "table" else 230
            )
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                process.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate(timeout=5)
            raise RuntimeError("可选AI任务超时，已终止；没有自动重试。") from None
        if process.returncode:
            raise RuntimeError(
                "可选AI调用失败；请检查本地配置、提供者额度或结果目录的安全失败记录。"
            )
    finally:
        environment.pop("DEEPSEEK_API_KEY", None)
        key = None
    return json.loads((output / "run-receipt.json").read_text("utf-8"))


def finish(root, parameters, output, receipt, environment):
    for name in [
        "SKILL.md",
        "sources.json",
        "data-provenance.json",
        "task-template.txt",
        "molecules.csv",
        "caffeine-calibration.csv",
    ]:
        if not (root / name).is_file():
            continue
        target = output / name
        if not target.exists():
            target.write_bytes((root / name).read_bytes())
    dump(output / "parameters.json", parameters)
    dump(
        output / "python-execution.json",
        {
            "mode": (
                "agent"
                if receipt["status"] == "PASS_REAL_MODEL_AND_TOOL_CALL"
                else "numerical"
            ),
            "execution_location": "LOCAL",
            "environment": environment,
            "skill_sha256": digest((root / "SKILL.md").read_bytes()),
            "new_rhf": "NOT_ACCEPTED",
        },
    )
    model_file = output / "agent-explanation.md"
    parts = [
        "<!doctype html><html lang='zh-CN'><meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width,initial-scale=1'>",
        "<title>Skill计算结果</title><style>body{font:16px/1.7 sans-serif;max-width:1050px;margin:30px auto;padding:0 20px}pre{white-space:pre-wrap;overflow-wrap:anywhere}img{max-width:100%}a{margin-right:20px}</style>",
        "<h1>Skill计算结果</h1><h2>程序回执</h2><pre>"
        + html.escape(json.dumps(receipt, ensure_ascii=False, indent=2))
        + "</pre>",
        "<h2>实际参数</h2><pre>"
        + html.escape(json.dumps(parameters, ensure_ascii=False, indent=2))
        + "</pre>",
    ]
    for name in ["molecules.png", "similarity.png", "calibration-and-residuals.png"]:
        if (output / name).is_file():
            parts.append(
                "<h2>"
                + name
                + "</h2><img alt='"
                + name
                + "' src='data:image/png;base64,"
                + base64.b64encode((output / name).read_bytes()).decode()
                + "'>"
            )
    if model_file.is_file():
        parts.append(
            "<h2>可选模型解释</h2><p>模型文字不决定文件状态，也不是独立专家认证。</p><pre>"
            + html.escape(model_file.read_text("utf-8"))
            + "</pre>"
        )
    else:
        parts.append("<p>本次为本地数值计算，没有调用模型，也没有生成模型解释。</p>")
    parts.append(
        "<h2>保存结果</h2><a href='results.zip' download>结果ZIP</a><a href='SHA256SUMS.txt'>SHA-256文件清单</a></html>"
    )
    (output / "report.html").write_text("".join(parts), encoding="utf-8")
    files = sorted(p for p in output.iterdir() if p.is_file())
    if any(p.is_symlink() for p in files):
        raise ValueError("结果目录包含符号链接。")
    manifest = "".join(digest(p.read_bytes()) + "  " + p.name + "\n" for p in files)
    (output / "SHA256SUMS.txt").write_text(manifest, encoding="utf-8")
    with zipfile.ZipFile(output / "results.zip", "x", zipfile.ZIP_DEFLATED) as archive:
        for path in files + [output / "SHA256SUMS.txt"]:
            archive.write(path, path.name)
    (output / "results.zip.sha256").write_text(
        digest((output / "results.zip").read_bytes()) + "  results.zip\n",
        encoding="utf-8",
    )
    verify_output(output)


def verify_output(output):
    if output.is_symlink():
        raise ValueError("结果目录不能为符号链接。")
    rows = (output / "SHA256SUMS.txt").read_text("utf-8").splitlines()
    if not rows or len(rows) > 100:
        raise ValueError("结果清单为空或超过100项。")
    expected = {}
    for row in rows:
        value, name = row.split("  ", 1)
        if (
            Path(name).name != name
            or "/" in name
            or "\\" in name
            or ":" in name
            or name in expected
            or re.fullmatch(r"[0-9a-f]{64}", value) is None
        ):
            raise ValueError("结果清单路径无效或重复。")
        path = output / name
        if path.is_symlink() or digest(path.read_bytes()) != value:
            raise ValueError("结果文件哈希不一致：" + name)
        expected[name] = value
    raw = (output / "results.zip").read_bytes()
    if len(raw) > 25_000_000:
        raise ValueError("结果ZIP超过大小上限。")
    if digest(raw) != (output / "results.zip.sha256").read_text("utf-8").split()[0]:
        raise ValueError("结果ZIP哈希不一致。")
    with zipfile.ZipFile(output / "results.zip") as archive:
        names = archive.namelist()
        if (
            len(names) > 100
            or sum(info.file_size for info in archive.infolist()) > 25_000_000
        ):
            raise ValueError("结果ZIP超过文件数或解压大小上限。")
        if (
            len(names) != len(set(names))
            or set(names) != set(expected) | {"SHA256SUMS.txt"}
            or archive.testzip() is not None
        ):
            raise ValueError("结果ZIP清单或CRC不一致。")
        for name, value in expected.items():
            if digest(archive.read(name)) != value:
                raise ValueError("ZIP内文件哈希不一致：" + name)
        if archive.read("SHA256SUMS.txt") != (output / "SHA256SUMS.txt").read_bytes():
            raise ValueError("ZIP内清单不一致。")


def main(kind, entry):
    page = Path(entry).resolve().parent
    parser = argparse.ArgumentParser(
        description="本地Python计算；默认不联网、不读取密钥。"
    )
    parser.add_argument("--params", type=Path, help="参数JSON；省略时使用内置模板")
    parser.add_argument("--output", type=Path, help="全新结果目录；已有目录拒绝覆盖")
    parser.add_argument(
        "--agent", action="store_true", help="显式使用DeepSeek及自己的额度"
    )
    parser.add_argument(
        "--env-file", type=Path, help="仅--agent使用，读取本地DEEPSEEK_API_KEY"
    )
    parser.add_argument("--verify", type=Path, help="只核对已有结果和ZIP，不运行计算")
    args = parser.parse_args()
    if args.env_file and not args.agent:
        parser.error("--env-file只在显式--agent模式中使用。")
    if args.agent and not args.env_file:
        parser.error("--agent必须显式指定--env-file；不要在命令中填写密钥值。")
    if args.verify and (args.params or args.output or args.agent):
        parser.error("--verify不能与计算参数同时使用。")
    try:
        if args.verify:
            verify_output(args.verify.absolute())
            print("PASS：已有结果、ZIP与SHA-256一致；未运行计算。")
            return 0
        root = verify_resources(page)
        environment = check_environment(root)
        params = strict_json(
            args.params.resolve() if args.params else root / "parameters.json"
        )
        core = importlib.import_module(
            "molecule_tool" if kind == "rdkit" else "skill_agent"
        )
        if kind == "rdkit":
            core.preflight(root, params)
        else:
            core.check_params(params)
        raw_output = args.output or Path.cwd() / (
            "skill-results-" + uuid.uuid4().hex[:12]
        )
        if raw_output.is_symlink():
            raise ValueError("结果目录不能为符号链接。")
        output = raw_output.resolve()
        if output.exists() or output.is_symlink():
            raise FileExistsError("结果目录已存在；请指定新目录，原结果不会覆盖。")
        if output.is_relative_to(page) and output != page:
            raise ValueError("结果目录请放在解压后的Skill源码目录之外。")
        if args.agent:
            receipt = run_agent(kind, root, params, output, args.env_file.resolve())
        else:
            if kind == "rdkit":
                core.analyze(root, params, output)
            else:
                output.mkdir(parents=True, exist_ok=False)
                core.numeric_calibration(root, params, output)
            receipt = {
                "status": "PASS_LOCAL_NUMERICAL",
                "skill": page.name,
                "parameters": params,
                "execution_location": "LOCAL",
                "model_calls": 0,
                "agent_called": False,
                "skill_sha256": digest((root / "SKILL.md").read_bytes()),
                "new_rhf": "NOT_ACCEPTED",
            }
            dump(output / "run-receipt.json", receipt)
        finish(root, params, output, receipt, environment)
        print(receipt["status"])
        print("结果报告：", output / "report.html")
        print("结果ZIP：", output / "results.zip")
        print("ZIP SHA-256：", digest((output / "results.zip").read_bytes()))
        return 0
    except (
        OSError,
        ValueError,
        RuntimeError,
        ArithmeticError,
        ImportError,
        zipfile.BadZipFile,
    ) as error:
        print("执行失败：" + str(error), file=sys.stderr)
        return 2
