from pathlib import Path

p = Path("dist/index.html")
s = p.read_text(encoding="utf-8")

old = 'function showScreen(id){["titleScreen","characterScreen","lifeSetupScreen","gameScreen"].forEach(x=>document.getElementById(x).classList.toggle("hidden",x!==id))}'
new = 'function showScreen(id){["titleScreen","characterScreen","traitScreen","companionScreen","lifeSetupScreen","gameScreen"].forEach(x=>{const el=document.getElementById(x);if(el)el.classList.toggle("hidden",x!==id)})}'
if old not in s:
    raise SystemExit("showScreen target not found")
s = s.replace(old, new, 1)

old = 'function finishCharacter(){pendingCharacter=collectCharacter();document.getElementById("setupCharacterSummary").textContent=appearanceText(pendingCharacter);showScreen("lifeSetupScreen")}'
new = 'function finishCharacter(){pendingCharacter=collectCharacter();showScreen("traitScreen");renderTraitBuilder()}'
if old not in s:
    raise SystemExit("finishCharacter target not found")
s = s.replace(old, new, 1)

s = s.replace(' G.characterDraft ||= collectCharacter();\n G.characterDraft.stats=stats;\n G.characterDraft.traits=ids;\n G.characterDraft.tags=[...(G.characterDraft.tags||[])];',
''' pendingCharacter ||= collectCharacter();
 pendingCharacter.stats=stats;
 pendingCharacter.traits=ids;
 pendingCharacter.tags=[...(pendingCharacter.tags||[])];''', 1)
s = s.replace('   G.characterDraft.tags.push(...(t.tags||[]));', '   pendingCharacter.tags.push(...(t.tags||[]));', 1)
s = s.replace('   G.character=G.characterDraft;showScreen("selectScreen");',
'   document.getElementById("setupCharacterSummary").textContent=appearanceText(pendingCharacter);showScreen("lifeSetupScreen");', 1)
s = s.replace(' G.characterDraft.companion=pet;\n G.character=G.characterDraft;\n showScreen("selectScreen");',
''' pendingCharacter ||= collectCharacter();
 pendingCharacter.companion=pet;
 document.getElementById("setupCharacterSummary").textContent=appearanceText(pendingCharacter);
 showScreen("lifeSetupScreen");''', 1)

p.write_text(s, encoding="utf-8")
