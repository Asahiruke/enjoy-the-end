from pathlib import Path
import re,json
p=Path("dist/index.html")
s=p.read_text(encoding="utf-8")
start=s.index("const TRAIT_DEFS = [")
end=s.index("];",start)+2
block=s[start:end]
messages={}
def migrate(m):
    field,value=m.group(1),m.group(2)
    # Each field belongs to the nearest trait ID in the original definition.
    prefix=block[:m.start()]
    ids=list(re.finditer(r'\bid:"([^"]+)"',prefix))
    if not ids:return m.group(0)
    ident=ids[-1].group(1)
    key=f"trait.{ident}.{field}"
    messages[key]=value
    return f'{field}Key:"{key}"'
block2=re.sub(r'\b(name|desc):"([^"]*)"',migrate,block)
assert len(messages)>20, len(messages)
trait_ids=set(re.findall(r'\bid:"([^"]+)"',block))
expected={f"trait.{ident}.{field}" for ident in trait_ids for field in ("name","desc")}
assert set(messages)==expected, f"Missing: {sorted(expected-set(messages))}; unexpected: {sorted(set(messages)-expected)}"
s=s[:start]+block2+s[end:]
payload=json.dumps(messages,ensure_ascii=False,separators=(",",":"))
# Attach compatibility accessors after the core runtime has created ETE_I18N.
runtime=f"""
<script id="ete-026-traits-i18n">
(()=>{{
 const I=window.ETE_I18N;if(!I)return;
 Object.assign(I.messages['zh-CN']||={{}},{payload});
 for(const trait of window.ETE_TRAIT_DEFS||[])for(const field of ['name','desc']){{
  const key=trait[field+'Key'];
  if(key)Object.defineProperty(trait,field,{{configurable:true,enumerable:false,get:()=>I.t(key)}});
 }}
}})();
</script>
"""
# TRAIT_DEFS is lexical in the original script; expose it without changing the save shape.
idx=s.index("];",s.index("const TRAIT_DEFS = ["))+2
s=s[:idx]+"\nwindow.ETE_TRAIT_DEFS=TRAIT_DEFS;"+s[idx:]

s=s.replace("</body>",runtime+"\n</body>",1)
p.write_text(s,encoding="utf-8")
assert 'get:()=>I.t(key)' in s, 'Trait display must resolve locale at read time'\nassert s.index("window.ETE_I18N=") < s.index('id="ete-026-traits-i18n"'), "Traits initialized before I18N"
assert "window.ETE_TRAIT_DEFS=TRAIT_DEFS;" in s, "Trait registry bridge missing"
assert "for(const trait of window.ETE_TRAIT_DEFS||[])" in s, "Trait runtime registry missing"
print("trait_i18n_fields="+str(len(messages)))
