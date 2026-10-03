from pathlib import Path
import re, json, hashlib

p=Path("dist/index.html")
s=p.read_text(encoding="utf-8")

# 0.26 localization pass: migrate static player-visible HTML text out of markup.
# Dynamic JS text is migrated module-by-module in source patches; this pass deliberately
# does not rewrite JavaScript literals.
messages={}
counter={}

def key_for(text):
    base="ui.static."+hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]
    return base

def repl(m):
    open_tag,text,close=m.group(1),m.group(2),m.group(3)
    clean=text.strip()
    if not clean or not re.search(r"[\u3400-\u9fff]",clean):
        return m.group(0)
    # Never touch script/style/template source.
    key=key_for(clean);messages[key]=clean
    lead=text[:len(text)-len(text.lstrip())];trail=text[len(text.rstrip()):]
    return f'{open_tag[:-1]} data-i18n="{key}">{lead}{clean}{trail}{close}'

# Only ordinary text-bearing tags; avoids corrupting scripts/styles.
pat=re.compile(r"(<(?:button|label|h[1-6]|p|small|strong|option|div|span)(?:\s[^>]*)?>)([^<>]+)(</(?:button|label|h[1-6]|p|small|strong|option|div|span)>)",re.I)
s=pat.sub(repl,s)

payload=json.dumps(messages,ensure_ascii=False,separators=(",",":"))
runtime=f"""<script>
(()=>{{
 const I=window.ETE_I18N;if(!I)return;
 Object.assign(I.messages['zh-CN']||=( {{}} ),{payload});
 I.apply=(root=document)=>{{
  for(const el of root.querySelectorAll('[data-i18n]')){{
   const key=el.dataset.i18n;
   if(el.children.length===0)el.textContent=I.t(key);
  }}
  for(const el of root.querySelectorAll('[data-i18n-placeholder]'))el.placeholder=I.t(el.dataset.i18nPlaceholder);
  document.documentElement.lang=I.locale;
 }};
 I.setLocale=locale=>{{I.locale=locale;I.apply();if(typeof window.render==='function')window.render()}};
 addEventListener('DOMContentLoaded',()=>I.apply());
}})();
</script>"""
s=s.replace("</body>",runtime+"\n</body>",1)
p.write_text(s,encoding="utf-8")
print(f"static_i18n_messages={len(messages)}")
