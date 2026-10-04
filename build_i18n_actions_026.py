from pathlib import Path
import re,json
p=Path("dist/index.html")
s=p.read_text(encoding="utf-8")
start=s.index("/* ---------- Action registry ---------- */")
end=s.index("/* ---------- NPC autonomy:",start)
block=s[start:end]
messages={}
# Only migrate literal action lifecycle messages in the authoritative registry.
pattern=re.compile(r"(instant|span)\('([^']+)',[^;\n]*?\);")
# Match single-quoted Chinese literals in action declarations, retaining callback expressions.
for kind,ident in re.findall(r"(instant|span)\('([^']+)'",block):
    line=re.search(r"(?m)^.*?"+kind+r"\('"+re.escape(ident)+r"'.*$",block)
    if not line: continue
    original=line.group(0)
    values=re.findall(r"'([^'\n]*[\u3400-\u9fff][^'\n]*)'",original)
    for index,value in enumerate(values):
        key=f"action.{ident}."+("complete" if kind=="instant" else ("start" if index==0 else "end"))
        messages[key]=value
        original=original.replace("'"+value+"'","'"+key+"'",1)
    block=block[:line.start()]+original+block[line.end():]
assert len(messages)>=35, len(messages)
# Localize action validation failures in the same authoritative action layer.
validation={
 "没有水。":"action.error.no_water","缺少吐司或鸡蛋。":"action.error.breakfast_missing",
 "家里没有方便面。":"action.error.no_instant_noodles","钱不够。":"action.error.not_enough_money",
 "猫现在不在你伸手就能够到的位置。":"action.error.pet_out_of_reach"
}
for value,key in validation.items():
    assert block.count("'"+value+"'")==1, "Validation source changed: "+value
    messages[key]=value
    block=block.replace("'"+value+"'","window.ETE_I18N.t('"+key+"')",1)
# Localize the dynamic pet interaction log without changing NPC identity/state.
pet_templates={
 "head":"你伸手摸了摸{name}的额头和耳后。它微微眯起了眼睛。",
 "chin":"你挠了挠{name}的下巴。它抬起头，似乎很满意。",
 "back":"你顺着{name}的背轻轻摸了几下。尾巴尖缓慢地晃着。",
 "paws":"你试着碰了碰{name}的前爪。它先缩了一下，随后又把爪子放了回来。",
 "default":"你摸了摸{name}。"
}
for style,value in pet_templates.items():
    key="action.pet_animal."+style
    messages[key]=value
    old=("\`"+value.replace("{name}","\${n}")+"\`")
    if old in block:
        block=block.replace(old,"window.ETE_I18N.t('"+key+"',{name:n})",1)
# Message resolution happens at log emission, not when the registry is constructed.
old="return typeof v==='function'?v(ctx,a):v"
assert block.count(old)==1
block=block.replace(old,"return typeof v==='function'?v(ctx,a):(typeof v==='string'&&v.startsWith('action.')?window.ETE_I18N.t(v):v)")
s=s[:start]+block+s[end:]
payload=json.dumps(messages,ensure_ascii=False,separators=(",",":"))
runtime="<script id=\"ete-026-actions-i18n\">(()=>{const I=window.ETE_I18N;if(I)Object.assign(I.messages['zh-CN']||={},"+payload+");})();</script>"
s=s.replace("</body>",runtime+"\n</body>",1)
p.write_text(s,encoding="utf-8")
print("action_i18n_messages="+str(len(messages)))
