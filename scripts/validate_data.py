import json, sys
from pathlib import Path

p = Path("data/sample.jsonl")
if not p.exists():
    print("ERROR: data/sample.jsonl not found"); sys.exit(2)

errors = []
count = 0
for i, line in enumerate(p.read_text(encoding="utf8").splitlines(), start=1):
    if not line.strip():
        continue
    try:
        obj = json.loads(line)
    except Exception as e:
        errors.append(f"line {i}: invalid json ({e})")
        continue
    count += 1
    if "id" not in obj or "prompt" not in obj or "response" not in obj:
        errors.append(f"line {i}: missing required fields (id,prompt,response)")
    if not isinstance(obj.get("prompt",""), str) or not isinstance(obj.get("response",""), str):
        errors.append(f"line {i}: prompt/response must be strings")

if errors:
    print("VALIDATION FAILED")
    for e in errors[:20]:
        print(e)
    sys.exit(1)
else:
    print(f"VALIDATION OK: {count} examples")
    sys.exit(0)
