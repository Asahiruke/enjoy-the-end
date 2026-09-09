from pathlib import Path

p = Path("dist/index.html")
s = p.read_text(encoding="utf-8")
s = s.replace("Prototype 0.14", "Prototype 0.16")

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
 const refresh=()=>{const bs=[...document.querySelectorAll("button")],stand=bs.find(b=>/起身|站起来|离开沙发/.test(b.textContent||"")),old=document.getElementById("callShelterNpcBtn");if(!stand||!sitting){old?.remove();return}if(old){const label="呼唤："+npc();if(old.textContent!==label)old.textContent=label;return}const b=document.createElement("button");b.id="callShelterNpcBtn";b.textContent="呼唤："+npc();b.onclick=()=>{if(onSofa)log(npc()+"已经在沙发上了。它听见你叫它，只是抬头看了你一眼。");else{const near=Math.random()<.55;onSofa=true;log(npc()+pick(near?L.near:L.approach))}};stand.parentElement?.insertBefore(b,stand)};
 new MutationObserver(refresh).observe(document.body,{childList:true,subtree:true});setInterval(refresh,1200);
})();
</script>"""
s = s.replace("</body>", npc_patch + "\n</body>", 1)


# Prototype 0.16 — generic hourly NPC autonomy.
autonomy_patch = r"""<script>
(() => {
  const SYS = window.ETE_NPC_AUTONOMY = window.ETE_NPC_AUTONOMY || {};
  const state = () => window.G || window.game || window.state || null;
  const clamp = (v,a,b)=>Math.max(a,Math.min(b,v));
  const pickWeighted = entries => {
    const list=entries.filter(x=>x && x.weight>0), total=list.reduce((n,x)=>n+x.weight,0);
    if(!total) return null;
    let r=Math.random()*total;
    for(const x of list){ r-=x.weight; if(r<=0)return x; }
    return list[list.length-1];
  };

  // Furniture/scene interaction registry.
  // First gate: NPC type (person / animal); second gate: subtype/species; then personality modifies weights.
  SYS.sceneRules = {
    sofa: {
      person: {
        human: [
          {id:"sit",weight:28,text:"坐在沙发上休息。"},
          {id:"read",weight:13,text:"坐在沙发上安静地看着手边的东西。",personality:["quiet","studious"]},
          {id:"watch_room",weight:10,text:"靠在沙发上观察着房间里的动静。",personality:["cautious","quiet"]}
        ]
      },
      animal: {
        cat: [
          {id:"curl",weight:30,text:"蜷在沙发的一角休息。",personality:["sleepy","calm"]},
          {id:"knead",weight:14,text:"在沙发软垫上踩了几下。"},
          {id:"armrest",weight:12,text:"蹲在沙发扶手上，尾巴垂在边缘。",personality:["curious"]},
          {id:"play",weight:10,text:"在沙发上扑弄着看不见的东西。",personality:["energetic","playful"]}
        ],
        dog: [
          {id:"rest",weight:28,text:"趴在沙发旁边休息。"},
          {id:"watch",weight:14,text:"守在沙发附近观察房间。",personality:["alert"]}
        ]
      }
    },
    cabinet_top: {
      person: { human: [] },
      animal: {
        cat: [
          {id:"perch",weight:28,text:"跳上柜子，在高处俯视着房间。",personality:["curious","confident"]},
          {id:"nap",weight:18,text:"趴在柜子顶上打盹。",personality:["sleepy"]},
          {id:"inspect",weight:14,text:"在柜子上研究着摆放的东西。",personality:["curious"]}
        ]
      }
    },
    window: {
      person: {
        human: [
          {id:"look_out",weight:20,text:"站在窗边看着外面的情况。",personality:["cautious","observant"]},
          {id:"idle",weight:8,text:"在窗边发了一会儿呆。",personality:["quiet"]}
        ]
      },
      animal: {
        cat: [
          {id:"watch",weight:30,text:"坐在窗边盯着外面的动静。",personality:["curious","alert"]},
          {id:"sun",weight:12,text:"在窗边找了个舒服的位置趴下。",personality:["sleepy","calm"]}
        ],
        bird: [
          {id:"perch",weight:24,text:"停在靠近窗边的位置观察外面。"}
        ]
      }
    },
    bed: {
      person: {
        human: [
          {id:"sleep",weight:25,text:"躺在床上休息。",personality:["tired","quiet"]},
          {id:"sit",weight:10,text:"坐在床边整理自己的东西。",personality:["orderly"]}
        ]
      },
      animal: {
        cat: [
          {id:"sleep",weight:34,text:"在床上团成一团睡觉。",personality:["sleepy","affectionate"]},
          {id:"blanket",weight:12,text:"在被子附近踩来踩去，最后找了个位置趴下。"}
        ]
      }
    },
    floor_open: {
      person: {
        human: [
          {id:"pace",weight:10,text:"在房间里来回走动。",personality:["restless"]},
          {id:"idle",weight:18,text:"在房间里安静地待着。",personality:["quiet","calm"]}
        ]
      },
      animal: {
        cat: [
          {id:"walk",weight:24,text:"在房间里慢慢踱步。"},
          {id:"groom",weight:22,text:"停下来舔爪子，认真地洗起脸。"},
          {id:"zoom",weight:7,text:"突然小跑着穿过房间。",personality:["energetic","playful"]},
          {id:"observe",weight:15,text:"趴在地上观察着房间里的动静。",personality:["curious","cautious"]}
        ],
        dog: [
          {id:"walk",weight:20,text:"在房间里走了一圈。"},
          {id:"rest",weight:20,text:"找了个地方趴下休息。"}
        ],
        bird: [
          {id:"hop",weight:18,text:"在附近轻快地移动着。"}
        ]
      }
    }
  };

  SYS.personalityDomains = {
    person:["sociable","quiet","orderly","restless","cautious","observant","studious","calm"],
    animal:["social","independent","curious","timid","confident","energetic","sleepy","playful","affectionate","alert","calm"]
  };

  SYS.rollAnimalPersonality = species => {
    const pool=[...SYS.personalityDomains.animal], count=2+Math.floor(Math.random()*2), out=[];
    while(pool.length && out.length<count) out.push(pool.splice(Math.floor(Math.random()*pool.length),1)[0]);
    return out;
  };

  SYS.ensureProfile = npc => {
    if(!npc) return npc;
    npc.npcType ||= (["cat","dog","bird"].includes(npc.type) ? "animal" : "person");
    if(npc.npcType==="animal"){
      npc.species ||= npc.type || "animal";
      npc.animalPersonality ||= npc.personalityTags || SYS.rollAnimalPersonality(npc.species);
    }else{
      npc.personSubtype ||= "human";
      // Fixed human NPCs can define this explicitly in NPC_DEFS/runtime data.
      npc.humanPersonality ||= npc.personalityTags || ["calm"];
    }
    npc.autonomy ||= {currentAction:npc.currentAction||"待着",actionUntilHour:null,targetScene:null,lastHour:null};
    return npc;
  };

  const personality = npc => npc.npcType==="animal" ? (npc.animalPersonality||[]) : (npc.humanPersonality||[]);
  const hourSerial = g => {
    if(!g) return 0;
    return Math.floor(Date.UTC(g.year||2026,(g.month||1)-1,g.day||1,g.hour||0)/3600000);
  };
  const playerRoom = g => g?.currentRoom || g?.playerRoom || "living";
  const rooms = g => g?.rooms || [];

  const roomById = (g,id) => rooms(g).find(r=>r.id===id) || {id,name:id,desc:""};
  const roomScenes = (g,id) => {
    const room=roomById(g,id), blob=((room.name||"")+" "+(room.desc||"")+" "+JSON.stringify(room)).toLowerCase();
    const out=["floor_open"];
    if(/沙发|sofa|couch/.test(blob) || ["living","living_room"].includes(id)) out.push("sofa");
    if(/柜|cabinet|shelf|架/.test(blob)) out.push("cabinet_top");
    if(/窗|window/.test(blob)) out.push("window");
    if(/床|bed/.test(blob) || /bedroom/.test(id)) out.push("bed");
    return [...new Set(out)];
  };
  const eligibleSceneActions = (g,npc,roomId) => {
    const type=npc.npcType, subtype=type==="animal"?(npc.species||npc.type):(npc.personSubtype||"human");
    const tags=personality(npc);
    const out=[];
    for(const scene of roomScenes(g,roomId)){
      const rules=SYS.sceneRules[scene]?.[type]?.[subtype] || [];
      for(const r of rules){
        let w=r.weight||1;
        if(r.personality?.some(t=>tags.includes(t))) w*=1.8;
        out.push({scene,rule:r,weight:w});
      }
    }
    return out;
  };

  const chooseOtherRoom = (g,npc) => {
    const ids=rooms(g).map(r=>r.id).filter(Boolean).filter(id=>id!==npc.room);
    return ids.length ? ids[Math.floor(Math.random()*ids.length)] : npc.room;
  };

  SYS.tickNPC = (npc,serial) => {
    const g=state(); if(!g||!npc) return;
    SYS.ensureProfile(npc);
    const a=npc.autonomy, tags=personality(npc);
    if(a.actionUntilHour!=null && serial<a.actionUntilHour && Math.random()<0.82){
      a.lastHour=serial; return;
    }

    let keep=55, local=20, move=15, approach=7, special=3;
    if(tags.includes("sleepy")) keep+=8;
    if(tags.includes("energetic")||tags.includes("restless")){keep-=10;local+=6;move+=4}
    if(tags.includes("social")||tags.includes("sociable")||tags.includes("affectionate")) approach+=6;
    if(tags.includes("independent")||tags.includes("timid")) approach-=3;
    const mode=pickWeighted([
      {id:"keep",weight:keep},{id:"local",weight:local},{id:"move",weight:move},
      {id:"approach",weight:Math.max(1,approach)},{id:"special",weight:special}
    ])?.id || "keep";

    if(mode==="keep"){ a.lastHour=serial; return; }
    if(mode==="move"){
      npc.room=chooseOtherRoom(g,npc);
      npc.currentAction=npc.npcType==="animal"?"在房间里闲逛":"去了别的房间";
      a.currentAction=npc.currentAction;a.targetScene=null;a.actionUntilHour=serial+1;a.lastHour=serial;return;
    }
    if(mode==="approach"){
      npc.room=playerRoom(g);
      npc.currentAction=npc.npcType==="animal"?"来到你所在的房间附近":"来到你所在的房间";
      a.currentAction=npc.currentAction;a.targetScene="player";a.actionUntilHour=serial+1;a.lastHour=serial;return;
    }
    if(mode==="special" && npc.npcType==="animal" && (npc.species||npc.type)==="cat"){
      const lines=["忽然在房间里疯跑了一阵。","钻到家具下面待了一会儿。","对墙角某个你没注意到的东西研究了很久。","突然停住，竖起耳朵听着远处的声音。"];
      npc.currentAction=lines[Math.floor(Math.random()*lines.length)];
      a.currentAction=npc.currentAction;a.targetScene="special";a.actionUntilHour=serial+1;a.lastHour=serial;return;
    }
    const opts=eligibleSceneActions(g,npc,npc.room||playerRoom(g));
    const chosen=pickWeighted(opts);
    if(chosen){
      npc.currentAction=chosen.rule.text;
      a.currentAction=npc.currentAction;a.targetScene=chosen.scene;
      const sleepish=/睡|打盹|休息|蜷/.test(chosen.rule.text);
      a.actionUntilHour=serial+(sleepish?2:1);
    }
    a.lastHour=serial;
  };

  SYS.hourlyTick = serial => {
    const g=state(); if(!g) return;
    const list=Object.values(g.npcs||{});
    const companion=g.character?.companion;
    if(companion && !list.some(n=>n.id===companion.id)){
      g.npcs ||= {};
      g.npcs[companion.id]={...companion,room:companion.room||playerRoom(g),currentAction:companion.currentAction||"在房间里待着"};
      list.push(g.npcs[companion.id]);
    }
    for(const npc of list) SYS.tickNPC(npc,serial);
    if(typeof window.render==="function") try{window.render()}catch(_){}
  };

  SYS.processHourCrossing = (before,after) => {
    if(after<=before) return;
    // Cap very long skips; still preserves normal sleep/work crossings without runaway work.
    const start=Math.max(before+1,after-48);
    for(let h=start;h<=after;h++) SYS.hourlyTick(h);
  };

  // Wrap the game's time advancement once. Immediate player/NPC reactions still remain event-driven;
  // this only governs autonomous decisions on crossed whole hours.
  const installAdvanceHook = () => {
    if(SYS.advanceHooked || typeof window.advance!=="function") return;
    const original=window.advance;
    window.advance=function(){
      const g=state(), before=hourSerial(g);
      const out=original.apply(this,arguments);
      const after=hourSerial(state());
      SYS.processHourCrossing(before,after);
      return out;
    };
    SYS.advanceHooked=true;
  };

  // Profiles for user-created companion animals are independent from human personality.
  const seedExisting = () => {
    const g=state(); if(!g) return;
    for(const n of Object.values(g.npcs||{})) SYS.ensureProfile(n);
    const p=g.character?.companion;
    if(p && !p.animalPersonality) p.animalPersonality=SYS.rollAnimalPersonality(p.type||"cat");
  };

  addEventListener("DOMContentLoaded",()=>{installAdvanceHook();seedExisting()});
  setTimeout(()=>{installAdvanceHook();seedExisting()},500);
  setInterval(()=>{installAdvanceHook();seedExisting()},5000);
})();
</script>"""
s = s.replace("</body>", autonomy_patch + "\n</body>", 1)

# Final write must occur after every injected runtime patch.
p.write_text(s, encoding="utf-8")
