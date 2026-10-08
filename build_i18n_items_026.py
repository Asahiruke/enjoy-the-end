from pathlib import Path
import re, json
p=Path("dist/index.html")
s=p.read_text(encoding="utf-8")
messages={}
# The original registry is a plain object. Keep canonical IDs and stored data unchanged.
m=re.search(r"const ITEMS\s*=\s*\{",s)
assert m, "ITEMS registry missing"
start=m.end()
end=s.index("};",start)
block=s[start:end]
entries=re.findall(r"([a-zA-Z][\w]*)\s*:\s*\{name:\s*[\"']([^\"']+)[\"']",block)
assert len(entries)>=10, "Item registry layout changed"
for ident,name in entries:
    messages["item."+ident+".name"]=name
# Container definitions are in the home setup, not a CONTAINERS registry.
containers=re.findall(r"\{id:\s*[\"']([^'\"\n]+)[\"']\s*,name:\s*[\"']([^'\"\n]+)[\"']\s*,room:",s)
assert len(containers)>=5, "Container definitions missing"
for ident,name in containers:
    messages["container."+ident+".name"]=name
# Preserve the original name fields for save compatibility. UI reads resolve localized
# display names through getters, with the original label as fallback.
pairs=json.dumps(messages,ensure_ascii=False,separators=(",",":"))
runtime="""<script id="ete-026-items-i18n">(()=>{
const I=window.ETE_I18N;
if(!I)return;
Object.assign(I.messages['zh-CN']||={},PAYLOAD);
const localize=(o,key)=>{
 if(!o)return;
 const original=o.name;
 Object.defineProperty(o,'name',{configurable:true,enumerable:true,
 get(){const value=I.t(key);return value===key?original:value},
 set(v){Object.defineProperty(this,'name',{value:v,writable:true,configurable:true,enumerable:true})}});
};
for(const [id,obj] of Object.entries(ITEMS))localize(obj,'item.'+id+'.name');
const originalContainer=window.ETE_CONTAINER_NAME||null;
window.ETE_CONTAINER_NAME=(obj)=>{
 const key='container.'+obj.id+'.name';
 const value=I.t(key);
 return value===key?obj.name:value;
};
})();</script>""".replace("PAYLOAD",pairs)
# Container labels are used via contById(...).name and local container objects.
# Do not mutate persisted container names here; follow-up UI render migration will
# use ETE_CONTAINER_NAME in the relevant rendering sites.
s=s.replace("</body>",runtime+"\n</body>",1)
p.write_text(s,encoding="utf-8")
print("items_i18n_messages="+str(len(messages))+" item_names="+str(len(entries))+" containers="+str(len(containers)))
