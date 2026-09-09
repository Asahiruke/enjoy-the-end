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

# Prototype 0.15 companion sofa behavior patch.
npc_patch = r"""<script>
(() => {
 const L={idle:["在房间里慢慢踱步，尾巴偶尔轻轻摆动。","停在墙边闻了闻，像是在确认新的气味。","从桌脚旁绕过去，又钻进了视线边缘。","蹲下来舔了舔前爪，随后认真地洗起脸。","趴在地上观察了一会儿，耳朵随着声音转动。","走到门边看了看，又若无其事地折返回来。","跳上矮柜待了一阵，俯视着整个房间。","在沙发附近转了一圈，但没有马上靠近你。","蜷在房间一角休息，偶尔抬眼看看你。","突然小跑着穿过房间，随后又恢复了若无其事的步伐。"],sofa:["轻巧地跳上沙发，在离你一点距离的位置坐下。","跳到沙发另一端，踩了几下软垫后趴了下来。","在沙发扶手上停住，尾巴垂在边缘轻轻晃着。","绕着沙发观察了一圈，最后选了个位置蜷起来。"],approach:["从房间另一头慢悠悠地走过来，最后跳上了沙发。","听见你的动静后从门边跑来，一跃落到沙发软垫上。","从家具后探出头，确认是你后才小跑过来跳上沙发。","本来正在房间里闲逛，过了一会儿才来到沙发旁，轻巧地跳了上来。"],near:["就在房间里。它抬头看了你一眼，随后直接跳上了沙发。","原本趴在不远处，听见呼唤后起身伸了个懒腰，再跳到你身边。","就在沙发附近，它甩了甩尾巴，很快跳上了软垫。"]};
 const pick=a=>a[Math.floor(Math.random()*a.length)];
 const npc=()=>{try{const g=window.G||window.game||window.state||{};const p=g.character?.companion||g.characterDraft?.companion||g.companion;return p?.name||"猫"}catch(_){return"猫"}};
 let sitting=false,onLap=false,onSofa=false;
 const log=t=>{const e=document.querySelector("#log,.log,#recentLog,.recent-log,[data-role='log']");if(e){const d=document.createElement("div");d.textContent=t;e.appendChild(d);e.scrollTop=e.scrollHeight}};
 const clearLap=()=>{onLap=false;document.querySelectorAll("*").forEach(e=>{if(!e.children.length&&/坐在你腿上|趴在你腿上|睡在你腿上|腿边/.test(e.textContent||""))e.textContent=(e.textContent||"").replace(/[^。；]*(?:坐在你腿上|趴在你腿上|睡在你腿上|腿边)[^。；]*/g,"")})};
 document.addEventListener("click",e=>{const b=e.target.closest("button");if(!b)return;const t=(b.textContent||"").trim();
  if(/起身|站起来|离开沙发/.test(t)){sitting=false;onSofa=false;clearLap();log(npc()+"从你身边让开了。你起身后，它也重新决定自己要待在哪里。");setTimeout(clearLap,30)}
  if(/坐在沙发上/.test(t)&&!/继续|保持/.test(t)){sitting=true;onLap=false;if(Math.random()<.28){onSofa=true;setTimeout(()=>log(npc()+pick(L.sofa)),40)}else{onSofa=false;setTimeout(()=>log(npc()+"没有立刻过来。"+pick(L.idle)),40)}}
  if(/继续坐|再坐|坐着|休息10分钟|待10分钟/.test(t)&&sitting){const r=Math.random();if(onSofa&&!onLap&&r<.18){onLap=true;log(npc()+"靠近了一些，踩过你的腿，最后在你腿上伏了下来。")}else if(!onSofa&&r<.30){onSofa=true;log(npc()+pick(L.approach))}else log(npc()+pick(L.idle))}
 },true);
 const refresh=()=>{const bs=[...document.querySelectorAll("button")],stand=bs.find(b=>/起身|站起来|离开沙发/.test(b.textContent||"")),old=document.getElementById("callShelterNpcBtn");if(!stand||!sitting){old?.remove();return}if(old){old.textContent="呼唤："+npc();return}const b=document.createElement("button");b.id="callShelterNpcBtn";b.textContent="呼唤："+npc();b.onclick=()=>{if(onSofa)log(npc()+"已经在沙发上了。它听见你叫它，只是抬头看了你一眼。");else{const near=Math.random()<.55;onSofa=true;log(npc()+pick(near?L.near:L.approach))}};stand.parentElement?.insertBefore(b,stand)};
 new MutationObserver(refresh).observe(document.body,{childList:true,subtree:true});setInterval(refresh,1200);
})();
</script>"""
s = s.replace("</body>", npc_patch + "\n</body>", 1)
