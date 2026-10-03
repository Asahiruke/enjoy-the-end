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
s=s[:start]+block2+s[end:]
payload=json.dumps(messages,ensure_ascii=False,separators=(",",":"))
# Compatibility getters keep existing UI renderers working without persisting localized names.
bridge=f"""
<script id="ete-026-traits-i18n">
(()=>{{
 const I=window.ETE_I18N;
 if(!I)return;
 Object.assign(I.messages['zh-CN']||={{}},{payload});
 for(const trait of TRAIT_DEFS){{
  for(const field of ['name','desc']){{
   const key=trait[field+'Key'];
   if(key)Object.defineProperty(trait,field,{{configurable:true,enumerable:false,get:()=>I.t(key)}});
  }}
 }}
}})();
</script>
"""
# Insert into same lexical script as TRAIT_DEFS rather than separate script.
inline=f"""
;(()=>{{
 const I=window.ETE_I18N;if(!I)return;
 Object.assign(I.messages['zh-CN']||={{}},{payload});
 for(const trait of TRAIT_DEFS)for(const field of ['name','desc']){{
  const key=trait[field+'Key'];
  if(key)Object.defineProperty(trait,field,{{configurable:true,enumerable:false,get:()=>I.t(key)}});
 }}
}})();
"""
idx=s.index("];",s.index("const TRAIT_DEFS = ["))+2
s=s[:idx]+inline+s[idx:]
p.write_text(s,encoding="utf-8")
print("trait_i18n_fields="+str(len(messages)))
