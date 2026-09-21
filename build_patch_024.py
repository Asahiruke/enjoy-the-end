from pathlib import Path
p=Path('dist/index.html')
s=p.read_text(encoding='utf-8').replace('Prototype 0.23','Prototype 0.24')
patch=r'''<script id="ete-024-action-core">
(()=>{
 const previous=window.ETE_ACTIONS||{};
 const Action=window.ETE_ACTIONS={
   version:'0.24',
   tags:previous.tags||{},
   defs:{},
   modifiers:[],
   hooks:{before:[],after:[],start:[],end:[],interrupt:[]},
   active:null
 };
 const D=Action.defs;
 const def=(id,o)=>D[id]=Object.freeze({id,minutes:0,tags:[],log:'none',interruptible:false,...o});
 // log: none = UI/silent, instant = one completion entry, span = start + end.
 def('room_move',{minutes:1,tags:['movement'],log:'instant',complete:'你去了另一个房间。'});
 def('room_move_stairs',{minutes:2,tags:['movement','stairs'],log:'instant',complete:'你去了另一层。'});
 def('sit_down',{minutes:1,tags:['posture'],log:'instant',complete:'你坐了下来。'});
 def('stand_up',{minutes:1,tags:['posture'],log:'instant',complete:'你站起身。'});
 def('take_item',{minutes:1,tags:['manipulation'],log:'instant'});
 def('store_item',{minutes:1,tags:['manipulation'],log:'instant'});
 def('change_clothes',{minutes:3,tags:['self_care','manipulation'],log:'instant',complete:'你换好了衣服。'});
 def('groom_simple',{minutes:2,tags:['self_care','fine_motor'],log:'instant'});
 def('make_bed',{minutes:3,tags:['household'],log:'instant'});
 def('pet_animal',{minutes:2,tags:['social','manipulation'],log:'instant'});
 def('call_npc',{minutes:0,tags:['social'],log:'instant'});
 def('drink',{minutes:1,tags:['drinking'],log:'instant'});
 def('snack',{minutes:3,tags:['eating'],log:'instant'});
 def('meal',{minutes:15,tags:['eating'],log:'span',start:'你开始吃饭。',end:'你吃完了。'});
 def('wash_hands',{minutes:1,tags:['hygiene'],log:'instant'});
 def('shower',{minutes:15,tags:['hygiene'],log:'span',start:'你开始洗澡。',end:'你洗完澡，擦干了身体。'});
 def('rest_short',{minutes:10,tags:['rest'],log:'span',start:'你坐下来休息一会儿。',end:'你结束了短暂的休息。'});
 def('rest_medium',{minutes:30,tags:['rest'],log:'span',start:'你开始休息。',end:'你休息了一阵。'});
 def('cook_quick',{minutes:10,tags:['cooking'],log:'span',start:'你开始准备一些简单的食物。',end:'简单的食物准备好了。'});
 def('cook_meal',{minutes:25,tags:['cooking'],log:'span',start:'你开始做饭。',end:'饭做好了。'});
 def('clean_small',{minutes:5,tags:['household','hygiene'],log:'span',start:'你开始收拾这里。',end:'你收拾完了。'});
 def('organize_container',{minutes:10,tags:['household','manipulation'],log:'span',start:'你开始整理这里的东西。',end:'你结束了整理。'});
 def('repair_small',{minutes:15,tags:['crafting','fine_motor'],log:'span',interruptible:true,start:'你开始处理需要维修的东西。',end:'你暂时结束了维修。'});
 def('first_aid',{minutes:5,tags:['medical','fine_motor'],log:'span',start:'你开始处理伤处。',end:'你完成了简单处理。'});
 def('sleep',{minutes:480,tags:['rest'],log:'span',interruptible:true,start:'你准备睡一觉。',end:'你醒了过来。'});
 def('work_shift',{minutes:540,tags:['movement'],log:'span',interruptible:true,start:'你出门去上班了。',end:'你结束了今天的工作。'});
 def('outing_walk',{minutes:30,tags:['movement'],log:'span',interruptible:true,start:'你出门走一走。',end:'你结束了这次外出，回到了住处。'});
 // Information/UI actions are explicit zero-time definitions.
 for(const id of ['open_container','inspect_item','inventory_view','weather_view','character_view','settings_view','mirror'])
   def(id,{minutes:0,tags:id==='settings_view'?[]:['observation'],log:'none',ui:true});

 const logger=(msg,a,phase)=>{
   if(!msg)return;
   const f=window.addLog||window.logEvent||window.pushLog;
   if(typeof f==='function'){try{f(msg);return}catch(_){}}
   const e=document.querySelector('#log,.log,#recentLog,.recent-log,[data-role="log"]');if(!e)return;
   const row=document.createElement('div');row.dataset.action=a.id;row.dataset.phase=phase;row.textContent=msg;e.appendChild(row);e.scrollTop=e.scrollHeight;
 };
 const message=(a,key,ctx)=>{const v=ctx[key+'Text']??a[key];return typeof v==='function'?v(ctx,a):v};
 Action.on=(phase,fn)=>{if(Action.hooks[phase]&&typeof fn==='function')Action.hooks[phase].push(fn);return()=>{Action.hooks[phase]=Action.hooks[phase].filter(x=>x!==fn)}};
 const emit=(phase,payload)=>{for(const fn of Action.hooks[phase]||[]){try{fn(payload)}catch(_){}};try{window.dispatchEvent(new CustomEvent('ete:action-'+phase,{detail:payload}))}catch(_){}};
 Action.addModifier=fn=>{if(typeof fn==='function')Action.modifiers.push(fn)};
 Action.resolve=(id,ctx={})=>{
   const base=D[id];if(!base)throw new Error('Unknown action: '+id);
   let a={...base,tags:[...base.tags],baseMinutes:base.minutes,minutes:ctx.minutes??base.minutes,ctx};
   for(const fn of Action.modifiers){try{a=fn(a,ctx)||a}catch(_){}}
   a.minutes=Math.max(0,Math.round(a.minutes));return a;
 };
 Action.perform=(id,ctx={})=>{
   const a=Action.resolve(id,ctx),payload={action:a,ctx};
   emit('before',payload);
   if(a.log==='span'){logger(message(a,'start',ctx),a,'start');emit('start',payload)}
   if(a.minutes>0&&typeof window.advance==='function')window.advance(a.minutes);
   if(a.log==='instant')logger(message(a,'complete',ctx),a,'complete');
   if(a.log==='span'){logger(message(a,'end',ctx),a,'end');emit('end',payload)}
   emit('after',payload);return a;
 };
 Action.performLong=Action.perform;
 window.performAction=Action.perform;window.performLongAction=Action.perform;

 // One compatibility map while old markup is migrated. It only assigns action IDs; execution is centralized above.
 const rules=[
   [/上班|去工作|工作\s*\d*\s*(?:小时|h)?/i,'work_shift'],[/出门走|出去走|散步|走一圈/,'outing_walk'],
   [/坐在沙发上/,'sit_down'],[/起身|站起来|离开沙发/,'stand_up'],
   [/楼上|楼下|上楼|下楼/,'room_move_stairs'],[/前往|进入|去往|移动到|回到/,'room_move'],
   [/呼唤[:：]?/,'call_npc'],[/摸摸|抚摸/,'pet_animal'],[/换衣|更衣/,'change_clothes'],
   [/拿取|取出/,'take_item'],[/放入|收进|存放/,'store_item'],[/喝水|饮用/,'drink'],
   [/零食|小吃/,'snack'],[/吃饭|用餐/,'meal'],[/洗手/,'wash_hands'],[/洗澡|淋浴/,'shower'],
   [/整理.*(?:柜|箱|容器)/,'organize_container'],[/打扫|清理/,'clean_small'],
   [/急救|包扎|处理伤口/,'first_aid'],[/修理|维修/,'repair_small'],[/照镜子/,'mirror'],
   [/设置/,'settings_view'],[/天气/,'weather_view'],[/库存|储备/,'inventory_view'],[/状态/,'character_view'],
   [/打开.*(?:柜|冰箱|箱|容器)|查看.*(?:柜|冰箱|箱|容器)/,'open_container']
 ];
 Action.idForControl=b=>b?.dataset?.actionId||rules.find(([re])=>re.test((b?.textContent||'').trim()))?.[1]||null;
 const mark=()=>{
   document.querySelectorAll('button').forEach(b=>{if(!b.dataset.actionId){const id=Action.idForControl(b);if(id)b.dataset.actionId=id}})
 };
 mark();
 document.addEventListener('click',e=>{
   const b=e.target.closest('button');if(!b)return;
   const id=b.dataset.actionId||Action.idForControl(b);if(!id||!D[id])return;
   // UI definitions deliberately do nothing to time/log. Existing UI handler continues normally.
   if(D[id].ui)return;
   // Dynamic sofa buttons have their own world effect; timing/logging is centralized here.
   Action.perform(id,{control:b,label:(b.textContent||'').trim()});
 },true);
 // Re-mark controls after normal renders, without polling.
 window.addEventListener('ete:action-after',()=>queueMicrotask(mark));
 window.addEventListener('DOMContentLoaded',mark);
})();
</script>'''
s=s.replace('</body>',patch+'\n</body>',1)
p.write_text(s,encoding='utf-8')
