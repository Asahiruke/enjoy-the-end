from pathlib import Path
import re,json
p=Path("dist/index.html")
s=p.read_text(encoding="utf-8")
messages={}
# Item/container registries use stable IDs; only their display labels are localized.
for registry,prefix in (("ITEMS","item"),("CONTAINERS","container")):
    m=re.search(r"(?:const|let|var)\s+"+registry+r"\s*=\s*\{",s)
    if not m: continue
    start=m.start(); depth=0; end=None
    for i in range(m.end()-1,len(s)):
        if s[i]=="{": depth+=1
        elif s[i]=="}":
            depth-=1
            if depth==0: end=i+1; break
    assert end
    block=s[start:end]
    for field in ("name","label","desc","description"):
        pat=re.compile(r"("+field+r"\\s*:\\s*)['\x22]([^'\x22\n]*[\u3400-\u9fff][^'\x22\\n]*)['\x22]")
        n=0
        def repl(x):
            nonlocal_n=None
            value=x.group(2)
            key=prefix+"."+str(abs(hash((registry,field,value))))+"."+field
            # deterministic key independent of Python hash randomization
            import hashlib
            key=prefix+"."+hashlib.sha1((field+"|"+value).encode()).hexdigest()[:10]+"."+field
            messages[key]=value
            return x.group(1)+"window.ETE_I18N.t("+json.dumps(key)+")"
        block=pat.sub(repl,block)
    s=s[:start]+block+s[end:]
payload=json.dumps(messages,ensure_ascii=False,separators=(",",":"))
runtime="<script id=\"ete-026-items-i18n\">(()=>{const I=window.ETE_I18N;if(I)Object.assign(I.messages['zh-CN']||={},"+payload+");})();</script>"
s=s.replace("</body>",runtime+"\n</body>",1)
p.write_text(s,encoding="utf-8")
print("items_i18n_messages="+str(len(messages)))
