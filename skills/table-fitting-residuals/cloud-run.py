"""Execute once in a private environment; credential remains in process memory."""
from pathlib import Path
import json,os,sys
from skill_agent import run_skill
root=Path(__file__).resolve().parent
if len(sys.argv)!=4:raise SystemExit('Usage: cloud-run.py parameter-file new-output-directory execution-location')
params=json.loads(Path(sys.argv[1]).read_text('utf-8'))
key=os.environ.get('DEEPSEEK_API_KEY','')
if not key:raise SystemExit('Credential missing; no Agent call performed')
try:receipt=run_skill(root,params,Path(sys.argv[2]),key,sys.argv[3])
except Exception as e:
    message=str(e)
    hints={'401':'凭据无效或已撤销，请在原配置位置更新。','402':'请检查DeepSeek账户额度。','429':'请求频率受限，请稍后手动重试。'}
    hint=next((v for k,v in hints.items() if 'HTTP '+k in message),'检查网络、提供者状态或failure.json中的安全失败类型；不自动重试。')
    raise SystemExit('调用失败：'+type(e).__name__+'；'+hint) from None
print(json.dumps(receipt,ensure_ascii=False))
