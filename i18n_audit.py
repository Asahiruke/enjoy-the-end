from pathlib import Path
import re, html
p=Path("dist/index.html")
s=p.read_text(encoding="utf-8")
# Inventory only: migration uses this to find user-facing CJK still outside the registry.
# Strip the central zh-CN message table so already-migrated text is not counted.
scan=re.sub(r"messages:\{'zh-CN':\{.*?\}\},t\(key,vars=\{\}\)", "messages:{'zh-CN':{}},t(key,vars={})", s, count=1, flags=re.S)
rows=[]
# HTML text nodes.
for m in re.finditer(r">([^<>]*[\u3400-\u9fff][^<>]*)<",scan):
    v=html.unescape(re.sub(r"\s+"," ",m.group(1)).strip())
    if v and not v.startswith(("/*","//")): rows.append(("html",v))
# Quoted JS/HTML strings. This intentionally over-reports; goal is a migration backlog, not a parser.
for m in re.finditer(r"""(['"`])((?:(?!\1).)*?[\u3400-\u9fff].*?)\1""",scan):
    v=re.sub(r"\s+"," ",m.group(2)).strip()
    if v and len(v)<240: rows.append(("string",v))
seen=set(); out=[]
for kind,v in rows:
    k=(kind,v)
    if k not in seen:
        seen.add(k); out.append(k)
print(f"I18N_REMAINING_UNIQUE={len(out)}")
for kind,v in out[:400]: print(f"{kind}\t{v}")
