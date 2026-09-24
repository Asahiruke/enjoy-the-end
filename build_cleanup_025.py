from pathlib import Path
import re

p=Path("dist/index.html")
s=p.read_text(encoding="utf-8")
s=s.replace("Prototype 0.24","Prototype 0.25-dev")
s=s.replace('function advance(min){','function advanceClockPrimitive(min){',1)
s=s.replace('let selectedJob="office",selectedHome="normalApartment",pendingCharacter=null,G=null,uid=1;',
            'let selectedJob="office",selectedHome="normalApartment",G=null,uid=1;')
s=s.replace('{id:"good_endurance",name:"耐力良好",cost:5,', '{id:"good_endurance",name:"耐力良好",cost:5,exclusiveGroup:"endurance",')
s=s.replace('{id:"poor_endurance",name:"耐力不足",cost:-5,', '{id:"poor_endurance",name:"耐力不足",cost:-5,exclusiveGroup:"endurance",')

# Remove obsolete runtime generations before the browser ever sees them.
for script_id in [
    "ete-020-sofa-actions","ete-021-action-system","ete-022-actions-review",
    "ete-023-action-journal","ete-024-action-core"
]:
    s=re.sub(r'<script id="'+re.escape(script_id)+r'">.*?</script>\s*','',s,flags=re.S)

# Remove the two pre-ID legacy NPC scripts injected by build_patch.py.
s=re.sub(r'<script>\s*\(\(\) => \{\s*const L=\{idle:.*?</script>\s*','',s,flags=re.S)
s=re.sub(r'<script>\s*\(\(\) => \{\s*const SYS = window\.ETE_NPC_AUTONOMY.*?</script>\s*','',s,flags=re.S)


# Migrate the remaining world-action controls to explicit IDs.
# UI/navigation controls deliberately keep their existing onclick handlers and consume no game time.
repls = {
'''<button onclick="sleep()">睡觉 8h</button>''':'''<button data-action-id="sleep">睡觉 8h</button>''',
'''<button onclick="log('你把被子和枕头重新整理好。');advance(10);render()">整理床铺 10m</button>''':'''<button data-action-id="make_bed">整理床铺 3m</button>''',
'''<button onclick="shower()">洗澡 20m</button>''':'''<button data-action-id="shower">洗澡 15m</button>''',
'''<button onclick="groom('basic')">整理外貌 10m</button>''':'''<button data-action-id="groom_simple">整理外貌 2m</button>''',
'''<button onclick="groom('hair')">修剪头发 30m</button>''':'''<button data-action-id="groom_hair">修剪头发 30m</button>''',
'''<button onclick="cook('breakfast')">简单早餐 30m</button>''':'''<button data-action-id="cook_breakfast">简单早餐 30m</button>''',
'''<button onclick="cook('instant')">方便面 15m</button>''':'''<button data-action-id="cook_instant">方便面 15m</button>''',
'''<button onclick="advance(60);G.raw.boredom=Math.max(0,G.raw.boredom-10);log('你在书桌前读了一会儿书。');render()">读书 1h</button>''':'''<button data-action-id="read_book">读书 1h</button>''',
'''<button onclick="advance(30);log('你在沙发上发了一会儿呆。');render()">休息 30m</button>''':'''<button data-action-id="rest_medium">休息 30m</button>''',
'''<button onclick="log('你随便看了一会节目。');advance(60);G.raw.boredom=Math.max(0,G.raw.boredom-10);render()">看节目 1h</button>''':'''<button data-action-id="watch_tv">看节目 1h</button>''',
'''<button onclick="staySeated()">保持坐着 10m</button>''':'''<button data-action-id="rest_short">休息 10m</button>''',
'''<button onclick="standUpFromSofa()">起身</button>''':'''<button data-action-id="stand_up">起身</button>''',
'''<button onclick="sitOnSofa()">坐在沙发上</button>''':'''<button data-action-id="sit_down">坐在沙发上</button>''',
'''<button onclick="petCat('head')">摸摸额头</button>''':'''<button data-action-id="pet_animal" data-pet-style="head">摸摸额头</button>''',
'''<button onclick="petCat('chin')">挠下巴</button>''':'''<button data-action-id="pet_animal" data-pet-style="chin">挠下巴</button>''',
'''<button onclick="petCat('back')">顺毛</button>''':'''<button data-action-id="pet_animal" data-pet-style="back">顺毛</button>''',
'''<button onclick="petCat('paws')">碰碰爪子</button>''':'''<button data-action-id="pet_animal" data-pet-style="paws">碰碰爪子</button>'''
}
for old,new in repls.items():
    s=s.replace(old,new)

# Dynamic room movement is a physical action; room selection itself is no longer an inline state mutation.
s=s.replace(
'''<button class="${G.currentRoom===r.id?"active":""}" onclick="G.currentRoom='${r.id}';closeStation();render()">${r.name}</button>''',
'''<button class="${G.currentRoom===r.id?"active":""}" data-action-id="room_move" data-room-id="${r.id}">${r.name}</button>'''
)

# Work and walk become parameterized Action Definitions; no inline advance/log remains.
s=s.replace(
'''<button ${G.world.workRequired?"":"disabled"} onclick="advance(${JOBS[G.job].workMinutes});G.money+=${JOBS[G.job].pay};log('你照常去上班了。');render()">出发上班 ${JOBS[G.job].workMinutes/60}h</button>''',
'''<button ${G.world.workRequired?"":"disabled"} data-action-id="work_shift" data-action-minutes="${JOBS[G.job].workMinutes}">出发上班 ${JOBS[G.job].workMinutes/60}h</button>'''
)
s=s.replace(
'''<button onclick="advance(60);log('你在附近走了一圈。');render()">在附近走一圈 1h</button>''',
'''<button data-action-id="outing_walk">在附近走一圈 1h</button>'''
)

# Clothing is physical; the item is passed as action context instead of calling wear() directly.
s=s.replace(
'''<button onclick="wear('${s.item}')">穿上</button>''',
'''<button data-action-id="change_clothes" data-item-id="${s.item}">穿上</button>'''
)

# Purchases retain item/price as context. Travel/purchase time is owned by the action.
s=s.replace(
'''<button onclick="buy('${id}',${p})">购买 ×1</button>''',
'''<button data-action-id="shop_purchase" data-item-id="${id}" data-price="${p}">购买 ×1</button>'''
)

# Old world-action functions are reduced to compatibility effect functions with no time or action logs.
s=re.sub(r'function groom\\(type\\)\\{.*?\\n', 'function groom(type){return type==="basic"?actionGroomSimple():actionGroomHair()}\\n', s)
s=re.sub(r'function shower\\(\\)\\{.*?\\n', 'function shower(){return actionShower()}\\n', s)
s=re.sub(r'function sleep\\(\\)\\{.*?\\n', 'function sleep(){return actionSleep()}\\n', s)
s=re.sub(r'function buy\\(id,p\\)\\{.*?\\n', 'function buy(id,p){return actionPurchase(id,p)}\\n', s)


# Delete obsolete business-action implementations after their controls have been migrated.
# Patterns intentionally avoid backslash-heavy regex so this patch remains readable.
for name in ["staySeated","sitOnSofa","standUpFromSofa","cook"]:
    s=re.sub(r'function '+name+r'[(][^)]*[)][{].*?^}', '', s, flags=re.S|re.M)
s=re.sub(r'^function (?:groom|shower|sleep|buy)[^\n]*\n', '', s, flags=re.M)


# Character creation legacy writers are removed; the 0.25 core owns the draft lifecycle.
# Remove multiline legacy writers first.
for name in ["saveTraitsAndContinue","saveCompanionAndContinue"]:
    s=re.sub(r'^function '+name+r'[(][^)]*[)][{].*?^}', '', s, flags=re.S|re.M)
# One-line writers must be removed line-wise; a multiline regex would consume the next function body.
s=re.sub(r'^function (?:beginNewGame|finishCharacter)[^\n]*\n', '', s, flags=re.M)
# Repair old cleanup output if rebuilding from a previously patched intermediate.
s=s.replace('function showScreen(id){["titleScreen","characterScreen","traitScreen","companionScreen","lifeSetupScreen","gameScreen"].forEach(x=>{const el=document.getElementById(x);if(el)el.classList.toggle("hidden",x!==id)})}\n}\nfunction appearanceText',
            'function showScreen(id){["titleScreen","characterScreen","traitScreen","companionScreen","lifeSetupScreen","gameScreen"].forEach(x=>{const el=document.getElementById(x);if(el)el.classList.toggle("hidden",x!==id)})}\nfunction appearanceText')

# startGame no longer reads pendingCharacter. It consumes the finalized CharacterDraft passed by the core.
s=s.replace('function startGame(){', 'function createGameFromDraft(){', 1)
s=s.replace('character:pendingCharacter||collectCharacter(),job:selectedJob,home:selectedHome,',
            'character:window.ETE_CHARACTER_DRAFT.finalize(),job:selectedJob,home:selectedHome,')


s=re.sub(r'^function petCat[(][^)]*[)][{].*?^}', '', s, flags=re.S|re.M)

runtime=r'''<script id="ete-025-core">
(()=>{
'use strict';

/* ---------- Character draft: one authoritative creation object ---------- */
const CharacterDraft=window.ETE_CHARACTER_DRAFT={
  data:null,
  create(seed={}){ this.data={tags:[],personalityTags:[],skills:{},clothingTags:[],...seed}; return this.data; },
  ensure(){ return this.data||this.create(); },
  patch(part={}){ Object.assign(this.ensure(),part); return this.data; },
  setAppearance(part){ const d=this.ensure(); d.appearance={...(d.appearance||{}),...(part||{})}; return d; },
  setTraits(ids,stats){
    const defs=window.TRAIT_DEFS||TRAIT_DEFS||[], seen=new Map(), clean=[];
    for(const id of ids||[]){const t=defs.find(x=>x.id===id);if(!t)continue;const g=t.exclusiveGroup;if(g&&seen.has(g))continue;if(g)seen.set(g,id);clean.push(id)}
    const tags=[];for(const id of clean){const t=defs.find(x=>x.id===id);tags.push(...(t?.tags||[]))}
    return this.patch({traits:clean,stats,tags:[...new Set(tags)]});
  },
  setCompanion(pet){return this.patch({companion:pet})},
  setLife({job,home}){return this.patch({job,home})},
  validate(){
    const d=this.ensure(), errors=[];if(!d.name)errors.push('name');if(!d.appearance)errors.push('appearance');
    const groups=new Set();for(const id of d.traits||[]){const t=TRAIT_DEFS.find(x=>x.id===id);if(t?.exclusiveGroup){if(groups.has(t.exclusiveGroup))errors.push('trait:'+t.exclusiveGroup);groups.add(t.exclusiveGroup)}}
    return {ok:errors.length===0,errors};
  },
  finalize(){const v=this.validate();if(!v.ok)throw new Error('Invalid CharacterDraft: '+v.errors.join(','));return JSON.parse(JSON.stringify(this.data))}
};

/* Character creation writes one authoritative draft. */
window.collectCharacter=function(){return{
 name:(document.getElementById('charName').value||'主角').trim(),
 appearance:{
  gender:document.getElementById('char_gender').value,hairLength:document.getElementById('char_hairLength').value,
  hairColor:document.getElementById('char_hairColor').value,eyeColor:document.getElementById('char_eyeColor').value,
  eyeShape:document.getElementById('char_eyeShape').value,skinTone:document.getElementById('char_skinTone').value,
  height:document.getElementById('char_height').value,weight:document.getElementById('char_weight').value
 },
 tags:[],personalityTags:[],skills:{},clothingTags:[]
}};

window.beginNewGame=function(){CharacterDraft.create();updateCharacterPreview();showScreen('characterScreen')};
window.finishCharacter=function(){
 const fresh=collectCharacter();CharacterDraft.patch(fresh);showScreen('traitScreen');renderTraitBuilder()
};
window.saveTraitsAndContinue=function(){
 if(traitBudget()<0)return;
 CharacterDraft.setTraits(getSelectedTraits(),finalStats());
 const d=CharacterDraft.ensure();
 if(d.traits.includes('favorite_companion')){showScreen('companionScreen');renderPetPreview()}
 else{document.getElementById('setupCharacterSummary').textContent=appearanceText(d);showScreen('lifeSetupScreen')}
};
function collectCompanionDraft(){
 return {
  id:'favorite_cat',type:'cat',name:(document.getElementById('petName').value||'小灰').trim(),
  appearance:{
   hairLength:document.getElementById('petHairLength').value,baseColor:document.getElementById('petBaseColor').value,
   pattern:document.getElementById('petPattern').value,white:document.getElementById('petWhite').value,
   facePattern:document.getElementById('petFacePattern').value,eyeColor:document.getElementById('petEyeColor').value,
   build:document.getElementById('petBuild').value,tail:document.getElementById('petTail').value,
   ears:document.getElementById('petEars').value,noseColor:document.getElementById('petNoseColor').value,
   padColor:document.getElementById('petPadColor').value
  },
  relation:100,resident:true,location:'player_home',room:'living',currentAction:'打盹',
  mood:'calm',sleeping:false,nearPlayer:false,onLap:false
 };
}
window.saveCompanionAndContinue=function(){
 CharacterDraft.setCompanion(collectCompanionDraft());
 document.getElementById('setupCharacterSummary').textContent=appearanceText(CharacterDraft.ensure());
 showScreen('lifeSetupScreen')
};
const _chooseJob=window.chooseJob,_chooseHome=window.chooseHome;
window.chooseJob=function(k){_chooseJob(k);CharacterDraft.setLife({job:k,home:selectedHome})};
window.chooseHome=function(k){_chooseHome(k);CharacterDraft.setLife({job:selectedJob,home:k})};
window.startGame=function(){
 CharacterDraft.setLife({job:selectedJob,home:selectedHome});
 CharacterDraft.finalize();
 return createGameFromDraft()
};

/* ---------- Event bus + canonical time engine ---------- */
const Events=window.ETE_EVENTS={
 hooks:new Map(),
 on(name,fn){const a=this.hooks.get(name)||[];a.push(fn);this.hooks.set(name,a);return()=>this.hooks.set(name,(this.hooks.get(name)||[]).filter(x=>x!==fn))},
 emit(name,payload){for(const fn of this.hooks.get(name)||[]){try{fn(payload)}catch(e){console.error(e)}}}
};
const clockHourSerial=g=>Math.floor(Date.UTC(g?.year||2026,(g?.month||1)-1,g?.day||1,g?.hour||0)/3600000);
const Time=window.ETE_TIME={
 advance(minutes,cause=null){
  const n=Math.max(0,Math.round(Number(minutes)||0));if(!n)return;
  const before=clockHourSerial(window.G);advanceClockPrimitive(n);const after=clockHourSerial(window.G);
  Events.emit('time:advanced',{minutes:n,cause,beforeHour:before,afterHour:after});
  for(let h=Math.max(before+1,after-48);h<=after;h++)Events.emit('hour:crossed',{serial:h,cause});
 }
};

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
instant('pet_animal',2,['social','manipulation'],ctx=>{
 const cat=typeof getFavoriteCat==='function'?getFavoriteCat():null,n=cat?(NPC_DEFS[cat.id]?.name||cat.id):'猫';
 return {head:`你伸手摸了摸${n}的额头和耳后。它微微眯起了眼睛。`,chin:`你挠了挠${n}的下巴。它抬起头，似乎很满意。`,back:`你顺着${n}的背轻轻摸了几下。尾巴尖缓慢地晃着。`,paws:`你试着碰了碰${n}的前爪。它先缩了一下，随后又把爪子放了回来。`}[ctx.petStyle]||`你摸了摸${n}。`
}); instant('call_npc',0,['social']);
instant('drink',1,['drinking']); instant('snack',3,['eating']); instant('wash_hands',1,['hygiene']);
span('meal',15,['eating'],'你开始吃饭。','你吃完了。');
span('shower',15,['hygiene'],'你开始洗澡。','你洗完澡，擦干了身体。');
span('rest_short',10,['rest'],'你坐下来休息一会儿。','你结束了短暂的休息。');
span('rest_medium',30,['rest'],'你开始休息。','你休息了一阵。');
span('cook_quick',10,['cooking'],'你开始准备一些简单的食物。','简单的食物准备好了。');
span('cook_breakfast',30,['cooking'],'你开始准备早餐。','简单的早餐做好了。');
span('cook_instant',15,['cooking'],'你开始煮方便面。','方便面煮好了。');
span('groom_hair',30,['self_care','fine_motor'],'你开始简单修剪头发。','你结束了修剪。');
span('read_book',60,['observation','rest'],'你坐下来开始读书。','你合上了书。');
span('watch_tv',60,['observation','rest'],'你打开电视看了一会节目。','你关掉了节目。');
span('shop_purchase',45,['movement','lifting'],'你开始采购需要的东西。','你结束了这次采购。');
span('cook_meal',25,['cooking'],'你开始做饭。','饭做好了。');
span('clean_small',5,['household','hygiene'],'你开始收拾这里。','你收拾完了。');
span('organize_container',10,['household','manipulation'],'你开始整理这里的东西。','你结束了整理。');
span('repair_small',15,['crafting','fine_motor'],'你开始处理需要维修的东西。','你暂时结束了维修。',{interruptible:true});
span('first_aid',5,['medical','fine_motor'],'你开始处理伤处。','你完成了简单处理。');
span('sleep',480,['rest'],'你准备睡一觉。','你醒了过来。',{interruptible:true});
span('work_shift',540,['movement'],'你出门去上班了。','你结束了今天的工作。',{interruptible:true});
span('outing_walk',60,['movement'],'你出门走一走。','你结束了这次外出，回到了住处。',{interruptible:true});
['open_container','inspect_item','inventory_view','weather_view','character_view','settings_view','mirror'].forEach(ui);

Action.on=(name,fn)=>{const a=Action.hooks.get(name)||[];a.push(fn);Action.hooks.set(name,a)};
Action.emit=(name,payload)=>{for(const fn of Action.hooks.get(name)||[]){try{fn(payload)}catch(e){console.error(e)}}};
Action.addModifier=fn=>{if(typeof fn==='function')Action.modifiers.push(fn)};
Action.handlers={};
Action.handle=(id,fn)=>Action.handlers[id]=fn;
Action.inventoryCount=id=>(G?.stacks||[]).filter(x=>x.itemId===id).reduce((n,x)=>n+(Number(x.qty)||0),0);
Action.consumeItem=(id,n=1)=>{
 let left=n;for(const st of G.stacks||[]){if(st.itemId!==id||left<=0)continue;const take=Math.min(left,st.qty);st.qty-=take;left-=take}
 G.stacks=(G.stacks||[]).filter(st=>st.qty>0);return left===0
};
Action.validate=(a,ctx)=>{
 if(a.id==='shower'&&!G?.world?.water)return '没有水。';
 if(a.id==='cook_breakfast'&&!(Action.inventoryCount('bread')>0&&Action.inventoryCount('eggs')>0))return '缺少吐司或鸡蛋。';
 if(a.id==='cook_instant'&&!(Action.inventoryCount('instant')>0))return '家里没有方便面。';
 if(a.id==='shop_purchase'&&G.money<Number(ctx.price||0))return '钱不够。';
 if(a.id==='pet_animal'){const cat=typeof getFavoriteCat==='function'?getFavoriteCat():null;if(!cat||cat.room!==G.currentRoom||!(cat.nearPlayer||cat.onLap))return '猫现在不在你伸手就能够到的位置。';}
 return null;
};
Action.resolve=(id,ctx={})=>{
 const base=Action.defs[id];if(!base)throw new Error('Unknown action '+id);
 let a={...base,tags:[...base.tags],baseMinutes:base.minutes,minutes:ctx.minutes??base.minutes,ctx};
 for(const fn of Action.modifiers)a=fn(a,ctx)||a;
 a.minutes=Math.max(0,Math.round(a.minutes));return a;
};
const log=(text,a,phase)=>{
 if(!text)return;
 const f=window.log||window.addLog||window.logEvent||window.pushLog;
 if(typeof f==='function'){f(text);return}
 const e=document.querySelector('#log,.log,#recentLog,.recent-log,[data-role="log"]');if(!e)return;
 const d=document.createElement('div');d.dataset.action=a.id;d.dataset.phase=phase;d.textContent=text;e.appendChild(d);e.scrollTop=e.scrollHeight;
};
const msg=(a,k,ctx)=>{const v=ctx[k+'Text']??a[k];return typeof v==='function'?v(ctx,a):v};
Action.perform=(id,ctx={})=>{
 const a=Action.resolve(id,ctx),p={action:a,ctx};
 const blocked=Action.validate(a,ctx);if(blocked){log(blocked,a,'blocked');if(typeof render==='function')render();return null}
 Action.emit('before',p);
 if(a.log==='span'){log(msg(a,'start',ctx),a,'start');Action.emit('start',p)}
 if(a.minutes)Time.advance(a.minutes,{type:'action',id:a.id,context:ctx});
 if(a.log==='instant')log(msg(a,'complete',ctx),a,'complete');
 if(a.log==='span'){log(msg(a,'end',ctx),a,'end');Action.emit('end',p)}
 const handler=Action.handlers[id];if(handler)handler(ctx,a);
 Action.emit('after',p);if(typeof render==='function')render();return a;
};
window.performAction=Action.perform;

/* ---------- NPC autonomy: subscribes to world events; never owns the clock ---------- */
const NPC=window.ETE_NPC_AUTONOMY={};
NPC.ensureProfile=n=>{
 if(!n)return n;n.npcType||=(['cat','dog','bird'].includes(n.type)?'animal':'person');
 if(!n.autonomy)n.autonomy={currentAction:n.currentAction||'待着',actionUntilHour:null,lastHour:null};return n;
};
NPC.seed=()=>{const g=G;if(!g)return;for(const n of (Array.isArray(g.npcs)?g.npcs:Object.values(g.npcs||{})))NPC.ensureProfile(n?.state||n)};
NPC.hourlyTick=serial=>{
 const g=G;if(!g)return;NPC.seed();
 for(const entry of (Array.isArray(g.npcs)?g.npcs:Object.values(g.npcs||{}))){const n=NPC.ensureProfile(entry?.state||entry);if(!n)continue;const a=n.autonomy;if(a.lastHour===serial)continue;a.lastHour=serial}
};
Events.on('hour:crossed',({serial})=>NPC.hourlyTick(serial));
Events.on('game:init',()=>NPC.seed());
Events.on('save:loaded',()=>NPC.seed());
document.addEventListener('DOMContentLoaded',()=>NPC.seed());

/* ---------- World effects: no time advancement and no action-owned log calls ---------- */
Action.handle('room_move',({roomId})=>{if(!roomId)return;G.currentRoom=roomId;closeStation?.()});
Action.handle('sit_down',()=>{if(!roomHasSofa?.())return;G.playerPose={type:'sitting',target:'sofa',since:{year:G.year,month:G.month,day:G.day,hour:G.hour,minute:G.minute}};if(typeof maybeCatJoin==='function')maybeCatJoin(false)});
Action.handle('stand_up',()=>{const cat=typeof getFavoriteCat==='function'?getFavoriteCat():null;if(cat?.onLap){cat.onLap=false;cat.nearPlayer=true;cat.sleeping=false;cat.currentAction='被你起身惊醒，留在沙发边'}G.playerPose=null});
Action.handle('room_move_stairs',({roomId})=>{if(!roomId)return;G.currentRoom=roomId;closeStation?.()});
Action.handle('work_shift',()=>{G.money+=JOBS[G.job].pay});
Action.handle('outing_walk',()=>{});
Action.handle('pet_animal',()=>{const cat=getFavoriteCat();if(cat)cat.relation=Math.min(100,(cat.relation||0)+1)});
Action.handle('make_bed',()=>{});
Action.handle('groom_simple',()=>{G.raw.stress=Math.max(0,G.raw.stress-2)});
Action.handle('groom_hair',()=>{});
Action.handle('shower',()=>{G.raw.dirt=0;G.raw.odor=0});
Action.handle('sleep',()=>{G.raw.sleepDebt=Math.max(0,G.raw.sleepDebt-75)});
Action.handle('read_book',()=>{G.raw.boredom=Math.max(0,G.raw.boredom-10)});
Action.handle('watch_tv',()=>{G.raw.boredom=Math.max(0,G.raw.boredom-10)});
Action.handle('cook_breakfast',()=>{Action.consumeItem('bread');Action.consumeItem('eggs');G.raw.stomach=Math.max(0,G.raw.stomach-38)});
Action.handle('cook_instant',()=>{Action.consumeItem('instant');G.raw.stomach=Math.max(0,G.raw.stomach-28)});
Action.handle('change_clothes',({itemId})=>{if(itemId&&typeof wear==='function')wear(itemId)});
Action.handle('shop_purchase',({itemId,price})=>{
 G.money-=price;const target=itemId==='bread'||itemId==='eggs'||itemId==='milk'?'fridge1':itemId==='instant'||itemId==='canned'?'cupboard1':itemId==='medicine'||itemId==='masks'?'cabinet1':null;
 const rm=target?contById(target).room:'living';G.stacks.push(stack(itemId,1,rm,target,ITEMS[itemId].cat==='food'?120:9999,'刚购买'))
});

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
 Action.perform(id,{
   control:b,label:(b.textContent||'').trim(),
   minutes:b.dataset.actionMinutes?Number(b.dataset.actionMinutes):undefined,
   roomId:b.dataset.roomId||undefined,itemId:b.dataset.itemId||undefined,
   price:b.dataset.price?Number(b.dataset.price):undefined,petStyle:b.dataset.petStyle||undefined
 });
};
document.addEventListener('click',actionClick,true);

/* ---------- Trait exclusivity: definitions are the only source of truth ---------- */
document.addEventListener('change',e=>{
 const input=e.target.closest('input[data-trait]');if(!input?.checked)return;
 const defs=window.TRAIT_DEFS||TRAIT_DEFS||[];
 const d=defs.find(x=>x.id===input.value),group=d?.exclusiveGroup;if(!group)return;
 document.querySelectorAll('input[data-trait]:checked').forEach(o=>{
  if(o===input)return;const od=defs.find(x=>x.id===o.value);
  if(od?.exclusiveGroup===group)o.checked=false;
 });
});
})();
</script>'''
s=s.replace("</body>",runtime+"\n</body>",1)
p.write_text(s,encoding="utf-8")
