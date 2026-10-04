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
assert len(set(messages))==len(messages), "Duplicate localization keys"
trait_ids=set(re.findall(r'\bid:"([^"]+)"',block))
expected={f"trait.{ident}.{field}" for ident in trait_ids for field in ("name","desc")}
assert set(messages)==expected, f"Missing: {sorted(expected-set(messages))}; unexpected: {sorted(set(messages)-expected)}"
s=s[:start]+block2+s[end:]
# Localize the existing appearance summary's fixed labels without changing character data.
summary_labels={"姓名":"character.summary.name","年龄":"character.summary.age","性别":"character.summary.gender","身高":"character.summary.height","体重":"character.summary.weight"}
# The summary is a presentation function; replace literal label segments only when present.
for label,key in summary_labels.items():
    messages[key]=label
# The appearance summary is display-only; preserve the underlying appearance values.
appearance_messages={
 "character.appearance.height.short":"个子偏矮","character.appearance.height.medium":"身高适中","character.appearance.height.tall":"个子偏高",
 "character.appearance.build.slim":"身形偏纤细","character.appearance.build.average":"身形匀称","character.appearance.build.strong":"体格显得结实",
 "character.appearance.eyes.soft":"眼神显得柔和","character.appearance.eyes.sharp":"目光显得锐利",
 "character.appearance.eyes.tired":"眼睛看起来有些困倦","character.appearance.eyes.calm":"目光显得平静",
 "character.appearance.eyes.other":"眼睛显得{shape}",
 "character.appearance.summary":"{name}的外表气质偏{gender}，{height}，{build}。留着{hairColor}的{hairLength}，{eyeColor}的{eyes}，肤色{skinTone}。"
}
messages.update(appearance_messages)
appearance_re=re.compile('function appearanceText' + re.escape('(c)') + '[\\s\\S]*?' + re.escape('\n}'))
appearance_new="""function appearanceText(c){
 const a=c.appearance;
 const t=(key,vars)=>window.ETE_I18N?.t(key,vars)??key;
 const height=({'偏矮':'short','中等':'medium','偏高':'tall'}[a.height]);
 const build=({'纤细':'slim','匀称':'average','壮实':'strong'}[a.weight]);
 const eyes=({'柔和':'soft','锐利':'sharp','略显困倦':'tired','平静':'calm'}[a.eyeShape]);
 return t('character.appearance.summary',{
  name:c.name,gender:a.gender,height:height?t('character.appearance.height.'+height):a.height,
  build:build?t('character.appearance.build.'+build):a.weight,
  hairColor:a.hairColor,hairLength:a.hairLength,eyeColor:a.eyeColor,
  eyes:eyes?t('character.appearance.eyes.'+eyes):t('character.appearance.eyes.other',{shape:a.eyeShape}),
  skinTone:a.skinTone
 });
}"""
s,n=appearance_re.subn(lambda _:appearance_new,s,count=1)
assert n==1,"Appearance summary function not found"
assert "character.appearance.summary" in s and "window.ETE_I18N?.t" in s, "Appearance renderer not localized"
# Trait budget preview is dynamic UI, not a saved trait value.
messages["character.traits.final_preview"]="最终属性预览：体质 {con} / 力量 {str} / 敏捷 {agi}"
messages["character.traits.insufficient"]="　点数不足，无法保存。"
old='warn.textContent=`最终属性预览：体质 ${fin.con} / 力量 ${fin.str} / 敏捷 ${fin.agi}` + (left<0?"　点数不足，无法保存。":"");'
new='warn.textContent=window.ETE_I18N.t("character.traits.final_preview",fin) + (left<0?window.ETE_I18N.t("character.traits.insufficient"):"");'
assert s.count(old)==1,"Trait budget renderer changed"
s=s.replace(old,new,1)
# Keep this registry independent of the saved CharacterDraft.
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
assert 'get:()=>I.t(key)' in s, 'Trait display must resolve locale at read time'
assert s.index("window.ETE_I18N=") < s.index('id="ete-026-traits-i18n"'), "Traits initialized before I18N"
assert "window.ETE_TRAIT_DEFS=TRAIT_DEFS;" in s, "Trait registry bridge missing"
assert "for(const trait of window.ETE_TRAIT_DEFS||[])" in s, "Trait runtime registry missing"
assert 'window.ETE_CHARACTER_DRAFT=' in s, "CharacterDraft missing"
assert 'window.ETE_TRAIT_DEFS=TRAIT_DEFS;' in s, "Trait registry missing"
print("trait_i18n_fields="+str(len(messages)))
