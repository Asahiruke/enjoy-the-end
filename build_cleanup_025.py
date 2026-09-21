from pathlib import Path
import re

p=Path("dist/index.html")
s=p.read_text(encoding="utf-8")
s=s.replace("Prototype 0.24","Prototype 0.25-dev")

# Remove obsolete runtime generations before the browser ever sees them.
for script_id in [
    "ete-020-sofa-actions","ete-021-action-system","ete-022-actions-review",
    "ete-023-action-journal","ete-024-action-core"
]:
    s=re.sub(r'<script id="'+re.escape(script_id)+r'">.*?</script>\s*','',s,flags=re.S)

# Remove the two pre-ID legacy NPC scripts injected by build_patch.py.
s=re.sub(r'<script>\s*\(\(\) => \{\s*const L=\{idle:.*?</script>\s*','',s,flags=re.S)
s=re.sub(r'<script>\s*\(\(\) => \{\s*const SYS = window\.ETE_NPC_AUTONOMY.*?</script>\s*','',s,flags=re.S)

runtime=r'''<script id="ete-025-core">
(()=>{
'use strict';

/* ---------- Character draft: one authoritative creation object ---------- */
const CharacterDraft=window.ETE_CHARACTER_DRAFT={
  get value(){
    if(!window.pendingCharacter) window.pendingCharacter={};
    return window.pendingCharacter;
  },
  reset(v={}){ window.pendingCharacter=v; return window.pendingCharacter; },
  patch(part){ Object.assign(this.value,part||{}); return this.value; },
  finalize(){ return structuredClone?structuredClone(this.value):JSON.parse(JSON.stringify(this.value)); }
};
Object.defineProperty(window,'characterDraft',{configurable:true,get:()=>CharacterDraft.value,set:v=>CharacterDraft.reset(v||{})});

/* ---------- Action registry ---------- */
const Action=window.ETE_ACTIONS={
 version:'0.25-dev',defs:{},tags:{},modifiers:[],hooks:new Map(),active:null
};
const tag=(id,body=[],exertion=0)=>Action.tags[id]={id,body,exertion};
tag('movement',['legs','balance'],1);tag('stairs',['legs','balance'],2);tag('posture',['legs','core'],.5);
tag('manipulation',['hands','arms'],.5);tag('fine_motor',['hands','vision'],.5);tag('lifting',['arms','back','legs'],2);
tag('self_care',['hands','arms'],.5);tag('household',['hands','arms','back'],1);tag('cooking',['hands','arms','vision'],1);
tag('hygiene',['hands','arms'],.75);tag('medical',['hands','vision'],.5);tag('crafting',['hands','arms','vision'],1);
tag('eating',['hands','mouth'],.25);tag('drinking',['hands','mouth'],.2);tag('social',['voice','hearing'],.1);
tag('observation',['vision','hearing'],.1);tag('rest',[],-1);

const define=(id,o={})=>Action.defs[id]=Object.freeze({
 id,minutes:0,tags:[],log:'none',interruptible:false,requirements:[],effects:[],...o
});
const instant=(id,minutes,tags,complete)=>define(id,{minutes,tags,log:'instant',complete});
const span=(id,minutes,tags,start,end,extra={})=>define(id,{minutes,tags,log:'span',start,end,...extra});
const ui=id=>define(id,{ui:true,minutes:0,log:'none',tags:['observation']});

instant('room_move',1,['movement'],'你去了另一个房间。');
instant('room_move_stairs',2,['movement','stairs'],'你去了另一层。');
instant('sit_down',1,['posture'],'你坐了下来。'); instant('stand_up',1,['posture'],'你站起身。');
instant('take_item',1,['manipulation']); instant('store_item',1,['manipulation']);
instant('change_clothes',3,['self_care','manipulation'],'你换好了衣服。');
instant('groom_simple',2,['self_care','fine_motor']); instant('make_bed',3,['household']);
instant('pet_animal',2,['social','manipulation']); instant('call_npc',0,['social']);
instant('drink',1,['drinking']); instant('snack',3,['eating']); instant('wash_hands',1,['hygiene']);
span('meal',15,['eating'],'你开始吃饭。','你吃完了。');
span('shower',15,['hygiene'],'你开始洗澡。','你洗完澡，擦干了身体。');
span('rest_short',10,['rest'],'你坐下来休息一会儿。','你结束了短暂的休息。');
span('rest_medium',30,['rest'],'你开始休息。','你休息了一阵。');
span('cook_quick',10,['cooking'],'你开始准备一些简单的食物。','简单的食物准备好了。');
span('cook_meal',25,['cooking'],'你开始做饭。','饭做好了。');
span('clean_small',5,['household','hygiene'],'你开始收拾这里。','你收拾完了。');
span('organize_container',10,['household','manipulation'],'你开始整理这里的东西。','你结束了整理。');
span('repair_small',15,['crafting','fine_motor'],'你开始处理需要维修的东西。','你暂时结束了维修。',{interruptible:true});
span('first_aid',5,['medical','fine_motor'],'你开始处理伤处。','你完成了简单处理。');
span('sleep',480,['rest'],'你准备睡一觉。','你醒了过来。',{interruptible:true});
span('work_shift',540,['movement'],'你出门去上班了。','你结束了今天的工作。',{interruptible:true});
span('outing_walk',30,['movement'],'你出门走一走。','你结束了这次外出，回到了住处。',{interruptible:true});
['open_container','inspect_item','inventory_view','weather_view','character_view','settings_view','mirror'].forEach(ui);

Action.on=(name,fn)=>{const a=Action.hooks.get(name)||[];a.push(fn);Action.hooks.set(name,a)};
Action.emit=(name,payload)=>{for(const fn of Action.hooks.get(name)||[]){try{fn(payload)}catch(e){console.error(e)}}};
Action.addModifier=fn=>{if(typeof fn==='function')Action.modifiers.push(fn)};
Action.resolve=(id,ctx={})=>{
 const base=Action.defs[id];if(!base)throw new Error('Unknown action '+id);
 let a={...base,tags:[...base.tags],baseMinutes:base.minutes,minutes:ctx.minutes??base.minutes,ctx};
 for(const fn of Action.modifiers)a=fn(a,ctx)||a;
 a.minutes=Math.max(0,Math.round(a.minutes));return a;
};
const log=(text,a,phase)=>{
 if(!text)return;
 const f=window.addLog||window.logEvent||window.pushLog;
 if(typeof f==='function'){f(text);return}
 const e=document.querySelector('#log,.log,#recentLog,.recent-log,[data-role="log"]');if(!e)return;
 const d=document.createElement('div');d.dataset.action=a.id;d.dataset.phase=phase;d.textContent=text;e.appendChild(d);e.scrollTop=e.scrollHeight;
};
const msg=(a,k,ctx)=>{const v=ctx[k+'Text']??a[k];return typeof v==='function'?v(ctx,a):v};
Action.perform=(id,ctx={})=>{
 const a=Action.resolve(id,ctx),p={action:a,ctx};
 Action.emit('before',p);
 if(a.log==='span'){log(msg(a,'start',ctx),a,'start');Action.emit('start',p)}
 if(a.minutes&&typeof window.advance==='function')window.advance(a.minutes); // the ONLY action-owned advance call
 if(a.log==='instant')log(msg(a,'complete',ctx),a,'complete');
 if(a.log==='span'){log(msg(a,'end',ctx),a,'end');Action.emit('end',p)}
 Action.emit('after',p);return a;
};
window.performAction=Action.perform;

/* ---------- NPC autonomy: event-driven only, no polling ---------- */
const NPC=window.ETE_NPC_AUTONOMY={};
const hourSerial=g=>Math.floor(Date.UTC(g?.year||2026,(g?.month||1)-1,g?.day||1,g?.hour||0)/3600000);
NPC.ensureProfile=n=>{
 if(!n)return n;n.npcType||=(['cat','dog','bird'].includes(n.type)?'animal':'person');
 n.autonomy||={currentAction:n.currentAction||'待着',actionUntilHour:null,lastHour:null};return n;
};
NPC.seed=()=>{const g=window.G;if(!g)return;Object.values(g.npcs||{}).forEach(NPC.ensureProfile);if(g.character?.companion)NPC.ensureProfile(g.character.companion)};
NPC.hourlyTick=serial=>{
 const g=window.G;if(!g)return;NPC.seed();
 for(const n of Object.values(g.npcs||{})){const a=n.autonomy;if(a.lastHour===serial)continue;a.lastHour=serial}
};
NPC.processCrossing=(before,after)=>{for(let h=Math.max(before+1,after-48);h<=after;h++)NPC.hourlyTick(h)};
NPC.installClock=()=>{
 if(NPC.clockInstalled||typeof window.advance!=='function')return;
 const raw=window.advance;window.advance=function(){const before=hourSerial(window.G),out=raw.apply(this,arguments),after=hourSerial(window.G);NPC.processCrossing(before,after);return out};
 NPC.clockInstalled=true;
};
document.addEventListener('DOMContentLoaded',()=>{NPC.installClock();NPC.seed()});
window.addEventListener('ete:game-init',()=>{NPC.installClock();NPC.seed()});
window.addEventListener('ete:save-loaded',()=>{NPC.installClock();NPC.seed()});

/* ---------- Sofa: one state, reacts to completed actions ---------- */
const Sofa=window.ETE_SOFA_STATE={sitting:false,room:null,catNear:false,catLap:false};
const room=()=>window.G?.currentRoom||window.G?.room||null;
const stand=()=>{Sofa.sitting=false;Sofa.room=null;Sofa.catNear=false;Sofa.catLap=false};
Action.on('after',({action})=>{
 if(action.id==='sit_down'){Sofa.sitting=true;Sofa.room=room()}
 if(action.id==='stand_up'||action.tags.includes('movement'))stand();
});

/* ---------- ID-driven controls ---------- */
const actionClick=e=>{
 const b=e.target.closest('[data-action-id]');if(!b)return;
 const id=b.dataset.actionId;if(!Action.defs[id])return;
 if(Action.defs[id].ui)return; // UI's own handler runs; no time/log.
 Action.perform(id,{control:b,label:(b.textContent||'').trim()});
};
document.addEventListener('click',actionClick,true);

/* ---------- Trait exclusivity: data, not special cases ---------- */
window.ETE_TRAIT_GROUP_FIX={good_endurance:'endurance',poor_endurance:'endurance'};
document.addEventListener('change',e=>{
 const input=e.target.closest('input[data-trait]');if(!input?.checked)return;
 const defs=window.TRAIT_DEFS||[];
 const d=defs.find(x=>x.id===input.value);const group=d?.exclusiveGroup||window.ETE_TRAIT_GROUP_FIX[d?.id];
 if(!group)return;
 document.querySelectorAll('input[data-trait]:checked').forEach(o=>{
  if(o===input)return;const od=defs.find(x=>x.id===o.value);
  if((od?.exclusiveGroup||window.ETE_TRAIT_GROUP_FIX[od?.id])===group)o.checked=false;
 });
});
})();
</script>'''
s=s.replace("</body>",runtime+"\n</body>",1)
p.write_text(s,encoding="utf-8")
