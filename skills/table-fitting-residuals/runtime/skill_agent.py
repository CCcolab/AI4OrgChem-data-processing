"""Bounded DeepSeek tool-calling executor for one verified Skill demonstration.

No OpenAI SDK/API. The model receives the exact Skill and public sample only.
The sole tool computes calibration; model-generated code is never executed.
"""

from pathlib import Path
from decimal import Decimal, localcontext
import csv, hashlib, importlib.metadata, io, json, math, os, platform, re, time, urllib.request, urllib.error, zipfile

MODEL = "deepseek-flash"
ENDPOINT = "https://api.deepseek.com/chat/completions"
KEY_NAME = "DEEPSEEK_API_KEY"


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def dump(path, value):
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def strict_object(pairs):
    result = {}
    for k, v in pairs:
        if k in result:
            raise ValueError("Duplicate JSON key")
        result[k] = v
    return result


def load_json(text):
    return json.loads(
        text,
        object_pairs_hook=strict_object,
        parse_constant=lambda x: (_ for _ in ()).throw(ValueError("Nonfinite JSON")),
    )


from credential_config import read_local_key


def check_params(params):
    if not isinstance(params, dict) or set(params) != {
        "include_highest_standard",
        "unknown_peak_area",
        "fit_intercept",
    }:
        raise ValueError("Parameter fields differ from template")
    if type(params["include_highest_standard"]) is not bool:
        raise ValueError("include_highest_standard must be boolean")
    if params["fit_intercept"] is not True:
        raise ValueError(
            "This example requires a fitted intercept; origin forcing is unsupported"
        )
    a = params["unknown_peak_area"]
    if type(a) not in (float, int) or not math.isfinite(a) or a < 0:
        raise ValueError("unknown_peak_area must be finite and nonnegative")


def verified_resources(root):
    rows = load_json((root / "resource-manifest.json").read_text("utf-8"))
    for r in rows:
        name = r["file"]
        p = Path(name)
        if p.is_absolute() or ".." in p.parts or ":" in name:
            raise ValueError("Invalid resource name")
        if digest((root / name).read_bytes()) != r["sha256"]:
            raise ValueError("Resource hash mismatch: " + name)
    return rows


def numeric_calibration(root, params, output):
    check_params(params)
    import numpy as np
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    records = list(
        csv.DictReader((root / "caffeine-calibration.csv").open(encoding="utf-8"))
    )
    if len(records) != 4:
        raise ValueError("Four cited standards required")
    chosen = records if params["include_highest_standard"] else records[:-1]
    x = np.array([float(r["concentration_mg_L"]) for r in chosen])
    y = np.array([float(r["peak_area_au"]) for r in chosen])
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("Nonfinite observations")
    A = np.column_stack([np.ones(len(x)), x])
    coef, _, rank, _ = np.linalg.lstsq(A, y, rcond=None)
    if rank != 2 or len(x) <= 2:
        raise ValueError("Insufficient full-rank observations")
    fitted = A @ coef
    residual = y - fitted
    rss = float(residual @ residual)
    sst = float(np.sum((y - y.mean()) ** 2))
    intercept, slope = map(float, coef)
    if abs(slope) < 1e-12:
        raise ValueError("Calibration inverse is undefined")
    concentration = (params["unknown_peak_area"] - intercept) / slope
    with localcontext() as ctx:
        ctx.prec = 45
        dx = [Decimal(r["concentration_mg_L"]) for r in chosen]
        dy = [Decimal(r["peak_area_au"]) for r in chosen]
        n = Decimal(len(dx))
        b = (n * sum(a * b for a, b in zip(dx, dy)) - sum(dx) * sum(dy)) / (
            n * sum(a * a for a in dx) - sum(dx) ** 2
        )
        a = (sum(dy) - b * sum(dx)) / n
        exact_c = (Decimal(str(params["unknown_peak_area"])) - a) / b
    checks = {
        "intercept_abs_error": abs(intercept - float(a)),
        "slope_abs_error": abs(slope - float(b)),
        "concentration_abs_error": abs(concentration - float(exact_c)),
        "residual_sum_abs": abs(float(residual.sum())),
        "normal_equation_residual_scaled": float(
            np.linalg.norm(A.T @ residual)
            / (np.linalg.norm(A) * max(np.linalg.norm(y), 1.0))
        ),
    }
    if (
        checks["intercept_abs_error"] > 1e-7
        or checks["slope_abs_error"] > 1e-8
        or checks["concentration_abs_error"] > 1e-8
        or checks["residual_sum_abs"] > 1e-6
        or checks["normal_equation_residual_scaled"] > 1e-12
    ):
        raise ArithmeticError("Independent calibration check failed")
    result = {
        "execution_status": "SUCCEEDED",
        "numerical_checks": "PASS",
        "analysis_scope": "descriptive external-standard OLS calibration only",
        "n": len(x),
        "df_residual": len(x) - 2,
        "intercept": intercept,
        "intercept_unit": "peak area arbitrary units",
        "slope": slope,
        "slope_unit": "peak area arbitrary units / (mg/L)",
        "rss": rss,
        "rss_unit": "(peak area arbitrary units)^2",
        "r_squared": 1 - rss / sst,
        "residual_convention": "observed minus fitted",
        "unknown_peak_area": params["unknown_peak_area"],
        "sample_concentration_mg_L": concentration,
        "inside_calibration_range": bool(x.min() <= concentration <= x.max()),
        "used_ids": [r["id"] for r in chosen],
        "independent_decimal_oracle": {
            "intercept": str(a),
            "slope": str(b),
            "concentration_mg_L": str(exact_c),
        },
        "checks": checks,
        "limitations": [
            "4 source standards, or a declared 3-point sensitivity subset; no replicates",
            "No proof of linearity or homoscedasticity from a high R squared",
            "No uncertainty interval, detection limit, reaction mechanism or new HPLC experiment claimed",
        ],
        "new_rhf": "NOT_EXECUTED",
    }
    dump(output / "numerical-result.json", result)
    with (output / "fitted-and-residuals.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "id",
                "concentration_mg_L",
                "peak_area_au",
                "fitted_peak_area_au",
                "residual_au",
            ]
        )
        writer.writerows(zip(result["used_ids"], x, y, fitted, residual))
    fig, axes = plt.subplots(2, 1, figsize=(8, 7), layout="constrained")
    axes[0].scatter(x, y, label="Cited caffeine standards")
    grid = np.linspace(x.min(), x.max(), 100)
    axes[0].plot(grid, intercept + slope * grid, label="OLS with fitted intercept")
    axes[0].set_ylabel("Peak area (arbitrary units)")
    axes[0].legend()
    axes[1].axhline(0, color="gray")
    axes[1].scatter(x, residual)
    axes[1].set_xlabel("Caffeine concentration (mg/L)")
    axes[1].set_ylabel("Observed - fitted (arbitrary units)")
    fig.savefig(output / "calibration-and-residuals.png", dpi=140)
    plt.close(fig)
    return result


def completion(key, messages, tools, max_tokens=1400):
    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto",
        "thinking": {"type": "disabled"},
        "temperature": 0,
        "max_tokens": max_tokens,
        "stream": False,
    }
    raw = json.dumps(payload, ensure_ascii=False).encode()
    req = urllib.request.Request(
        ENDPOINT,
        data=raw,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        raise RuntimeError(
            "DeepSeek HTTP " + str(e.code) + "; no automatic retry"
        ) from None
    except Exception as e:
        raise RuntimeError(
            "DeepSeek transport failed: " + type(e).__name__ + "; no automatic retry"
        ) from None
    # Defensive: never persist an echoed credential even if the upstream returned one.
    body = body.replace(key, "[REDACTED]")
    return load_json(body)


def run_skill(root, params, output, key, execution_location):
    root = Path(root)
    output = Path(output)
    check_params(params)
    if output.exists():
        raise FileExistsError("New output directory required; existing files preserved")
    resources = verified_resources(root)
    output.mkdir(parents=True)
    start = time.monotonic()
    calls = []
    tool_events = []
    result = None
    dump(output / "parameters.json", params)
    dump(
        output / "environment.json",
        {
            "python": platform.python_version(),
            "platform": platform.system(),
            "location": execution_location,
            "packages": {
                x: importlib.metadata.version(x) for x in ["numpy", "matplotlib"]
            },
            "provider": "DeepSeek",
            "model_requested": MODEL,
            "endpoint": ENDPOINT,
            "budget": {
                "max_api_rounds": 4,
                "per_request_timeout_s": 60,
                "max_output_tokens_per_round": 1400,
                "auto_retry": False,
            },
            "credentials_persisted": False,
        },
    )
    skill = (root / "SKILL.md").read_text("utf-8")
    skill_hash = digest(skill.encode())
    task = (root / "task-template.txt").read_text("utf-8")
    tools = [
        {
            "type": "function",
            "function": {
                "name": "fit_caffeine_calibration",
                "description": "Fit the cited caffeine table using user-selected exact parameters. Returns program-computed coefficients, residuals, inverse calibration and independent checks. No arbitrary code or file paths.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "include_highest_standard": {"type": "boolean"},
                        "unknown_peak_area": {"type": "number"},
                        "fit_intercept": {"type": "boolean", "enum": [True]},
                    },
                    "required": [
                        "include_highest_standard",
                        "unknown_peak_area",
                        "fit_intercept",
                    ],
                    "additionalProperties": False,
                },
            },
        }
    ]
    context = {
        "parameters": params,
        "data": list(
            csv.DictReader((root / "caffeine-calibration.csv").open(encoding="utf-8"))
        ),
        "provenance": load_json((root / "data-provenance.json").read_text("utf-8")),
    }
    messages = [
        {
            "role": "system",
            "content": skill
            + "\n\n执行环境：你正在使用该Skill。只允许fit_caffeine_calibration工具，不可编造数值或执行其它代码。用户明确要求执行，必须按用户参数调用工具；不得悄悄删点、更改模型、强制过原点或替换样本。工具返回后用中文说明校准结果和局限，约300字，说明这是有机分析校准例，不是反应机理课。",
        },
        {
            "role": "user",
            "content": task + "\n" + json.dumps(context, ensure_ascii=False),
        },
    ]
    dump(
        output / "agent-input.json",
        {
            "skill_sha256": skill_hash,
            "task": task,
            "context": context,
            "tool_names": ["fit_caffeine_calibration"],
        },
    )
    try:
        for round_no in range(4):
            response = completion(key, messages, tools)
            msg = response["choices"][0]["message"]
            finish = response["choices"][0]["finish_reason"]
            calls.append(
                {
                    "round": round_no + 1,
                    "request_id": response.get("id"),
                    "model_returned": response.get("model"),
                    "finish_reason": finish,
                    "usage": response.get("usage"),
                    "message": {
                        "role": "assistant",
                        "content": msg.get("content"),
                        "tool_calls": msg.get("tool_calls", []),
                    },
                }
            )
            messages.append(
                {
                    "role": "assistant",
                    "content": msg.get("content"),
                    "tool_calls": msg.get("tool_calls", []),
                }
            )
            tool_calls = msg.get("tool_calls", [])
            if not tool_calls:
                if result is None:
                    raise RuntimeError(
                        "Model returned no actual tool call; not accepted as Skill execution"
                    )
                if finish != "stop" or not msg.get("content"):
                    raise RuntimeError("Incomplete model interpretation")
                (output / "agent-explanation.md").write_text(
                    msg["content"], encoding="utf-8"
                )
                break
            for tc in tool_calls:
                if result is not None:
                    raise RuntimeError(
                        "Duplicate scientific call blocked; no automatic repeat"
                    )
                if tc["function"]["name"] != "fit_caffeine_calibration":
                    raise ValueError("Unsupported tool")
                arguments = load_json(tc["function"]["arguments"])
                check_params(arguments)
                if arguments != params:
                    raise ValueError("Model changed user-confirmed parameters")
                result = numeric_calibration(root, arguments, output)
                tool_events.append(
                    {
                        "tool_call_id": tc["id"],
                        "name": tc["function"]["name"],
                        "arguments": arguments,
                        "result_sha256": digest(
                            (output / "numerical-result.json").read_bytes()
                        ),
                        "status": "PASS",
                    }
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": json.dumps(result, ensure_ascii=False),
                    }
                )
        else:
            raise RuntimeError("Agent round budget exhausted")
        dump(
            output / "agent-trace.json",
            {
                "provider": "DeepSeek",
                "skill_sha256": skill_hash,
                "rounds": calls,
                "actual_tool_calls": tool_events,
            },
        )
        receipt = {
            "status": "PASS_REAL_MODEL_AND_TOOL_CALL",
            "skill": "table-fitting-residuals",
            "skill_sha256": skill_hash,
            "execution_location": execution_location,
            "parameters": params,
            "provider": "DeepSeek",
            "model_requested": MODEL,
            "model_returned": calls[-1]["model_returned"],
            "api_rounds": len(calls),
            "tool_calls": len(tool_events),
            "numerical_checks": "PASS",
            "model_interpretation": "GENERATED_NOT_INDEPENDENTLY_CERTIFIED",
            "elapsed_seconds": round(time.monotonic() - start, 3),
            "credentials_saved": False,
            "new_rhf": "NOT_EXECUTED",
        }
        dump(output / "run-receipt.json", receipt)
        for resource in [
            "SKILL.md",
            "skill_agent.py",
            "credential_config.py",
            "python_runner.py",
            "requirements.txt",
            "resource-manifest.json",
            "caffeine-calibration.csv",
            "data-provenance.json",
            "sources.json",
            "task-template.txt",
        ]:
            (output / resource).write_bytes((root / resource).read_bytes())
        files = sorted(p for p in output.iterdir() if p.is_file())
        manifest = [{"file": p.name, "sha256": digest(p.read_bytes())} for p in files]
        dump(output / "export-manifest.json", manifest)
        archive = output / "skill-results.zip"
        with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as z:
            for p in sorted(output.iterdir()):
                if p.is_file() and p != archive:
                    z.write(p, p.name)
        return receipt
    except Exception as e:
        dump(
            output / "agent-trace.json",
            {"rounds": calls, "actual_tool_calls": tool_events},
        )
        dump(
            output / "failure.json",
            {
                "execution_status": "FAILED",
                "error_type": type(e).__name__,
                "message": str(e).replace(key, "[REDACTED]"),
                "new_rhf": "NOT_EXECUTED",
            },
        )
        raise
