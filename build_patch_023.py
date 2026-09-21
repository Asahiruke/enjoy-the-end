from pathlib import Path

p=Path('dist/index.html')
s=p.read_text(encoding='utf-8')
s=s.replace('Prototype 0.22','Prototype 0.23')

patch=r'''<script id="ete-023-action-journal">
(()=>{
 const A=window.ETE_ACTIONS;if(!A)return;
 const clock=()=>{
   const g=window.G||{};
   const y=g.year||2026,m=String(g.month||1).padStart(2,'0'),d=String(g.day||1).padStart(2,'0');
   const h=String(g.hour||0).padStart(2,'0'),mi=String(g.minute||0).padStart(2,'0');
   return {stamp:y+'-'+m+'-'+d+' '+h+':'+mi,time:h+':'+mi};
 };
 const write=(msg,phase,a)=>{
   // Prefer the game's own logger so timestamps/ordering remain consistent.
   const f=window.addLog||window.logEvent||window.pushLog;
   if(typeof f==='function'){try{return f(msg)}catch(_){}}
   const e=document.querySelector('#log,.log,#recentLog,.recent-log,[data-role="log"]');if(!e)return;
   const d=document.createElement('div');d.dataset.phase=phase;d.dataset.action=a?.id||'';d.textContent='['+clock().time+'] '+msg;e.appendChild(d);e.scrollTop=e.scrollHeight;
 };
 A.journal={
   work_shift:{start:'你出门去上班了。',end:'你结束了今天的工作。'},
   outing_walk:{start:'你出门走一走。',end:'你结束了这次外出，回到了住处。'},
   outing_depart:{start:'你离开了住处。',end:'你回到了住处。'},
   sleep:{start:'你准备睡一觉。',end:'你醒了过来。'},
   shower:{start:'你开始洗澡。',end:'你洗完澡，擦干了身体。'},
   cook_quick:{start:'你开始准备一些简单的食物。',end:'简单的食物准备好了。'},
   cook_meal:{start:'你开始做饭。',end:'饭做好了。'},
   organize_container:{start:'你开始整理这里的东西。',end:'你结束了整理。'},
   repair_small:{start:'你开始处理需要维修的东西。',end:'你暂时结束了维修。'},
   clean_small:{start:'你开始收拾这里。',end:'你收拾完了。'}
 };
 A.defs.outing_walk ||= {minutes:30,tags:['movement']};
 A.longActionIds=new Set(['work_shift','outing_walk','sleep','shower','cook_quick','cook_meal','organize_container','repair_small','clean_small']);
 A.describe=(id,phase,ctx={})=>{
   const j=A.journal[id]||{};
   const v=ctx[phase+'Text']||j[phase];
   return typeof v==='function'?v(ctx):v;
 };
 // Canonical long-action runner: START is written before time advances; END after all crossed ticks resolve.
 A.performLong=(id,ctx={})=>{
   const a=A.resolve(id,ctx);
   const start=A.describe(id,'start',ctx);if(start)write(start,'start',a);
   if(a.minutes>0&&typeof window.advance==='function')window.advance(a.minutes);
   try{window.dispatchEvent(new CustomEvent('ete:action-complete',{detail:a}))}catch(_){}
   const end=A.describe(id,'end',ctx);if(end)write(end,'end',a);
   return a;
 };
 window.performLongAction=A.performLong;
 // Route registered long actions through the paired journal automatically.
 const basePerform=A.perform;
 A.perform=(id,ctx={})=>A.longActionIds.has(id)?A.performLong(id,ctx):basePerform(id,ctx);
 window.performAction=A.perform;

 // Existing legacy controls: identify the two currently important long actions explicitly.
 window.ETE_ACTION_BINDINGS=window.ETE_ACTION_BINDINGS||[];
 window.ETE_ACTION_BINDINGS.unshift(
   {re:/上班|去工作|工作\s*\d*\s*(?:小时|h)?/i,id:'work_shift'},
   {re:/出门走|出去走|散步|走一圈/,id:'outing_walk'}
 );
})();
</script>'''
s=s.replace('</body>',patch+'\n</body>',1)
p.write_text(s,encoding='utf-8')
