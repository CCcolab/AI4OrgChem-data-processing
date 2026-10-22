"""Credential selection only; never print, persist or interpolate credentials."""

from pathlib import Path
import re
import sys

KEY_NAME = "DEEPSEEK_API_KEY"


class CredentialConfigError(RuntimeError):
    pass


def read_local_key(env_file):
    path = Path(env_file)
    try:
        if path.stat().st_size > 1_000_000:
            raise CredentialConfigError("本地.env超过1MB；请使用只含本任务配置的文件。")
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeError):
        raise CredentialConfigError(
            "未找到或无法读取本地.env。请设置ENV_FILE为已有配置文件路径；不要将密钥写进代码。"
        ) from None
    values = []
    for line in lines:
        match = re.match(r"^\s*(?:export\s+)?DEEPSEEK_API_KEY\s*=\s*(.*?)\s*$", line)
        if match:
            values.append(match.group(1))
    if len(values) != 1:
        raise CredentialConfigError(
            "本地.env必须且只能包含一项DEEPSEEK_API_KEY配置；请检查缺失或重复变量。"
        )
    value = values[0]
    if value.startswith(('"', "'")):
        quote = value[0]
        closing = value.find(quote, 1)
        if closing < 0 or (
            value[closing + 1 :].strip()
            and not value[closing + 1 :].lstrip().startswith("#")
        ):
            raise CredentialConfigError(
                "DEEPSEEK_API_KEY的引号或行尾格式错误，请检查.env。"
            )
        value = value[1:closing]
    else:
        value = re.split(r"\s+#", value, maxsplit=1)[0].strip()
    return validate_value(value, "本地.env")


def validate_value(value, source):
    if not isinstance(value, str) or not value.strip():
        raise CredentialConfigError(
            source + "中的DEEPSEEK_API_KEY为空；未执行模型调用。"
        )
    if len(value) > 1024 or any(not 33 <= ord(c) <= 126 for c in value):
        raise CredentialConfigError(
            source
            + "中的配置过长或包含空白/控制/非ASCII字符；仅填写密钥值，不要包含变量名。"
        )
    return value


def read_colab_key(getter=None):
    if getter is None:
        try:
            from google.colab import userdata

            getter = userdata.get
        except ImportError:
            raise CredentialConfigError(
                "当前不在Colab；请使用本地.env读取方式。"
            ) from None
    try:
        value = getter(KEY_NAME)
    except Exception as exc:
        name = type(exc).__name__
        if name == "SecretNotFoundError":
            message = "Colab中未找到Secret：DEEPSEEK_API_KEY。点击左侧钥匙→添加新密钥，名称填变量名，值填密钥；不要修改代码。"
        elif name == "NotebookAccessError":
            message = "此Notebook未获准读取DEEPSEEK_API_KEY。请在左侧Secret开启本Notebook访问权限。"
        else:
            message = "Colab Secret读取失败。请确认已登录正确账号、保存同名Secret并允许此Notebook访问，再重试凭据单元。"
        raise CredentialConfigError(message) from None
    return validate_value(value, "Colab Secret")


def load_credential(env_file, mode=None):
    selected = mode or ("colab" if "google.colab" in sys.modules else "local")
    if selected == "colab":
        return read_colab_key()
    if selected == "local":
        return read_local_key(env_file)
    raise CredentialConfigError("凭据来源必须为local或colab。")
