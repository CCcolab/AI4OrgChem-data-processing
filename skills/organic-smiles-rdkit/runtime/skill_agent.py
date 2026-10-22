"""Actual bounded DeepSeek call; exact source Skill plus explicit execution authorization."""

from pathlib import Path
import json
import time
import urllib.request
import urllib.error
import zipfile
from molecule_tool import analyze, validate, preflight, dump, sha
from result_presentation import tool_file_evidence, verify_download, model_denies_files

MODEL = "deepseek-flash"
ENDPOINT = "https://api.deepseek.com/chat/completions"
MAX_RESPONSE_BYTES = 1_000_000


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError("模型服务发生重定向；已停止，不向其他地址转发凭据。")


def _redact(value, key):
    if isinstance(value, str):
        return value.replace(key, "[REDACTED]")
    if isinstance(value, list):
        return [_redact(item, key) for item in value]
    if isinstance(value, dict):
        return {_redact(name, key): _redact(item, key) for name, item in value.items()}
    return value


def strict_json(text):
    def pairs(items):
        out = {}
        for k, v in items:
            if k in out:
                raise ValueError("重复JSON字段。")
            out[k] = v
        return out

    return json.loads(
        text,
        object_pairs_hook=pairs,
        parse_constant=lambda v: (_ for _ in ()).throw(ValueError("非有限JSON数值。")),
    )


def _request_context(root, params):
    for item in strict_json((root / "resource-manifest.json").read_text("utf-8")):
        if (
            Path(item["file"]).name != item["file"]
            or sha(root / item["file"]) != item["sha256"]
        ):
            raise ValueError("资源身份不匹配。")
    preflight(root, params)
    skill = (root / "SKILL.md").read_text("utf-8")
    skill_hash = sha(root / "SKILL.md")
    tools = [
        {
            "type": "function",
            "function": {
                "name": "analyze_organic_molecules",
                "description": "Run bounded RDKit parsing, descriptors, SMARTS, Morgan similarities and checks on the provided teaching structures; no arbitrary code, edits or network lookup.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "radius": {"type": "integer", "minimum": 1, "maximum": 4},
                        "fp_size": {"type": "integer", "enum": [1024, 2048, 4096]},
                        "include_chirality": {"type": "boolean"},
                        "query_smarts": {"type": "string"},
                        "reference_id": {"type": "string"},
                    },
                    "required": list(params),
                    "additionalProperties": False,
                },
            },
        }
    ]
    messages = [
        {
            "role": "system",
            "content": skill
            + "\n\n适配器说明：Skill默认交付代码。本次用户明确授权在Colab验收执行，覆盖默认不执行步骤，只能调用analyze_organic_molecules白名单工具，不生成或运行任意代码。必须严格采用用户参数。工具返回真实结果后用中文约200字解释结构、无效记录、身份和相似度局限；不编造数据，不预测活性或反应。文件状态只依据program_files中程序核对的实际文件；数值文件已写入，ZIP由程序在本段模型回复后封装。不要声称本次未执行或未生成文件，不要虚构下载地址；下载统一提示使用Notebook课末程序下载单元。模型不决定文件是否可下载。",
        },
        {
            "role": "user",
            "content": (root / "task-template.txt").read_text("utf-8")
            + "\n参数："
            + json.dumps(params, ensure_ascii=False)
            + "\n样本：\n"
            + (root / "molecules.csv").read_text("utf-8"),
        },
    ]
    return skill_hash, tools, messages


def run(root, params, output, key, location):
    root, output = Path(root), Path(output)
    if output.exists():
        raise FileExistsError("必须使用新输出目录。")
    rounds = []
    events = []
    result = None
    start = time.monotonic()
    try:
        skill_hash, tools, messages = _request_context(root, params)
        for i in range(3):
            payload = {
                "model": MODEL,
                "messages": messages,
                "tools": tools,
                "tool_choice": "auto",
                "temperature": 0,
                "max_tokens": 1200,
                "thinking": {"type": "disabled"},
                "stream": False,
            }
            req = urllib.request.Request(
                ENDPOINT,
                data=json.dumps(payload, ensure_ascii=False).encode(),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + key,
                },
            )
            try:
                opener = urllib.request.build_opener(NoRedirect())
                with opener.open(req, timeout=60) as resp:
                    body = resp.read(MAX_RESPONSE_BYTES + 1)
                if len(body) > MAX_RESPONSE_BYTES:
                    raise RuntimeError("模型响应超过1MB上限。")
                raw = body.decode("utf-8")
            except urllib.error.HTTPError as exc:
                raise RuntimeError(
                    "DeepSeek HTTP "
                    + str(exc.code)
                    + "；请检查凭据权限、额度或服务状态；不自动重试。"
                ) from None
            except RuntimeError:
                raise
            except Exception as exc:
                raise RuntimeError(
                    "模型网络失败：" + type(exc).__name__ + "；不自动重试。"
                ) from None
            response = _redact(strict_json(raw), key)
            choice = response["choices"][0]
            msg = choice["message"]
            clean = {
                "role": "assistant",
                "content": msg.get("content"),
                "tool_calls": msg.get("tool_calls", []),
            }
            rounds.append(
                {
                    "round": i + 1,
                    "model": response.get("model"),
                    "usage": response.get("usage"),
                    "finish_reason": choice["finish_reason"],
                    "message": clean,
                }
            )
            messages.append(clean)
            if not clean["tool_calls"]:
                if (
                    result is None
                    or not msg.get("content")
                    or choice["finish_reason"] != "stop"
                ):
                    raise RuntimeError("未完成真实工具调用或解释；不能验收。")
                (output / "agent-explanation.md").write_text(
                    msg["content"], encoding="utf-8"
                )
                break
            for tc in clean["tool_calls"]:
                if result is not None:
                    raise ValueError("重复工具调用被阻止。")
                if tc["function"]["name"] != "analyze_organic_molecules":
                    raise ValueError("不支持的工具。")
                args = strict_json(tc["function"]["arguments"])
                validate(args)
                if args != params:
                    raise ValueError("模型改变用户参数，拒绝执行。")
                result = analyze(root, args, output)
                events.append(
                    {
                        "name": tc["function"]["name"],
                        "arguments": args,
                        "numerical_sha256": sha(output / "numerical-result.json"),
                        "status": "PASS",
                    }
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": json.dumps(
                            {
                                "analysis": result,
                                "program_files": tool_file_evidence(output),
                            },
                            ensure_ascii=False,
                        ),
                    }
                )
        else:
            raise RuntimeError("超出3轮API预算。")
        dump(
            output / "agent-trace.json",
            {"rounds": rounds, "tool_events": events, "credentials_persisted": False},
        )
        receipt = {
            "status": "PASS_REAL_MODEL_AND_TOOL_CALL",
            "skill": "organic-smiles-rdkit",
            "skill_sha256": skill_hash,
            "execution_location": location,
            "parameters": params,
            "provider": "DeepSeek",
            "model": rounds[-1]["model"],
            "api_rounds": len(rounds),
            "tool_calls": len(events),
            "program_files_provided_to_model": True,
            "model_file_status_claim": (
                "CONTRADICTED"
                if model_denies_files(msg["content"])
                else "NOT_FLAGGED_NOT_CERTIFIED"
            ),
            "numerical_checks": "PASS",
            "model_interpretation": "GENERATED_NOT_EXPERT_CERTIFIED",
            "elapsed_s": round(time.monotonic() - start, 3),
            "budget": {"api_rounds": 3, "per_request_s": 60, "auto_retry": False},
            "new_rhf": "NOT_ACCEPTED",
        }
        dump(output / "run-receipt.json", receipt)
        for name in [
            "molecule_tool.py",
            "skill_agent.py",
            "credential_config.py",
            "result_presentation.py",
            "requirements-colab.txt",
            "task-template.txt",
            "resource-manifest.json",
        ]:
            (output / name).write_bytes((root / name).read_bytes())
        manifest = [
            {"file": p.name, "sha256": sha(p)}
            for p in sorted(output.iterdir())
            if p.is_file()
        ]
        dump(output / "export-manifest.json", manifest)
        with zipfile.ZipFile(
            output / "organic-smiles-rdkit-results.zip", "x", zipfile.ZIP_DEFLATED
        ) as z:
            for p in sorted(output.iterdir()):
                if p.is_file() and p.suffix != ".zip":
                    z.write(p, p.name)
        verify_download(output)
        return receipt
    except Exception as exc:
        output.mkdir(exist_ok=True)
        dump(
            output / "failure.json",
            {
                "status": "FAILED",
                "type": type(exc).__name__,
                "message": str(exc).replace(key, "[REDACTED]"),
            },
        )
        dump(output / "agent-trace.json", {"rounds": rounds, "tool_events": events})
        raise
