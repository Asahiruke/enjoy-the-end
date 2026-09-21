from pathlib import Path

p=Path('dist/index.html')
s=p.read_text(encoding='utf-8')
s=s.replace('Prototype 0.21','Prototype 0.22')

patch=r'''<script id="ete-022-actions-review">
(()=>{
 const A=window.ETE_ACTIONS;
 if(A){
   Object.assign(A.defs,{
     open_container:{minutes:0,tags:['observation']},
     inspect_item:{minutes:0,tags:['observation']},
     inventory_view:{minutes:0,tags:['observation']},
     weather_view:{minutes:0,tags:['observation']},
     character_view:{minutes:0,tags:['observation']},
     settings_view:{minutes:0,tags:[]},
     mirror:{minutes:0,tags:['observation']},
     cook_quick:{minutes:10,tags:['cooking']},
     cook_meal:{minutes:25,tags:['cooking']},
     clean_small:{minutes:5,tags:['household','hygiene']},
     organize_container:{minutes:10,tags:['household','manipulation']},
     repair_small:{minutes:15,tags:['crafting','fine_motor']},
     first_aid:{minutes:5,tags:['medical','fine_motor']},
     sleep:{minutes:480,tags:['rest']},
     work_shift:{minutes:540,tags:['movement']},
     outing_depart:{minutes:1,tags:['movement']}
   });
 }
 // Semantic registry for existing controls. UI-only controls are explicitly zero-time.
 window.ETE_ACTION_BINDINGS=[
   {re:/设置|库存|储备|天气|状态|详情|查看物品/,id:'settings_view',ui:true},
   {re:/照镜子/,id:'mirror',ui:true},
   {re:/打开.*(?:柜|冰箱|箱|容器)|查看.*(?:柜|冰箱|箱|容器)/,id:'open_container',ui:true},
   {re:/拿取|取出/,id:'take_item'},{re:/放入|收进|存放/,id:'store_item'},
   {re:/换衣|更衣/,id:'change_clothes'},{re:/整理床|铺床/,id:'make_bed'},
   {re:/喝水|饮用/,id:'drink'},{re:/零食|小吃/,id:'snack'},{re:/吃饭|用餐/,id:'meal'},
   {re:/洗手/,id:'wash_hands'},{re:/洗澡|淋浴/,id:'shower'},
   {re:/整理.*(?:柜|箱|容器)/,id:'organize_container'},{re:/打扫|清理/,id:'clean_small'},
   {re:/急救|包扎|处理伤口/,id:'first_aid'},{re:/修理|维修/,id:'repair_small'}
 ];
 window.ETE_ACTION_ID_FOR_BUTTON=b=>{
   if(!b)return null;
   if(b.dataset?.actionId)return b.dataset.actionId;
   const t=(b.textContent||'').trim();
   const x=window.ETE_ACTION_BINDINGS.find(x=>x.re.test(t));
   return x?.id||null;
 };
 // Do not double-charge actions already handled by 0.21; this hook only covers registered legacy controls.
 document.addEventListener('click',e=>{
   const b=e.target.closest('button');if(!b||b.dataset.eteTimed==='1')return;
   const id=window.ETE_ACTION_ID_FOR_BUTTON(b);if(!id)return;
   const def=A?.defs?.[id];if(!def||def.minutes===0)return;
   b.dataset.eteTimed='1';A.perform(id);
 },true);

 // Character review screen, inserted after Life Setup.
 const life=document.getElementById('lifeSetupScreen');
 if(life&&!document.getElementById('characterReviewScreen')){
   const review=document.createElement('section');review.id='characterReviewScreen';review.className='screen hidden';
   review.innerHTML='<div class="title-card"><h2>关于你</h2><div id="characterReviewText" class="card"></div><div class="small" style="margin-top:10px">如果有哪里不像你，现在还可以回去修改。</div><div class="actions"><button onclick="reviewBackAppearance()">修改外貌</button><button onclick="reviewBackTraits()">修改特征</button><button onclick="reviewBackLife()">修改生活设定</button><button onclick="confirmCharacterReview()">确认</button></div></div>';
   life.insertAdjacentElement('afterend',review);
 }
 // Extend showScreen without rewriting its original implementation.
 if(typeof window.showScreen==='function'&&!window.__eteReviewScreenHook){
   const old=window.showScreen;window.showScreen=function(id){
     old(id);
     const r=document.getElementById('characterReviewScreen');
     if(r)r.classList.toggle('hidden',id!=='characterReviewScreen');
   };window.__eteReviewScreenHook=true;
 }
 const draft=()=>window.pendingCharacter||window.G?.characterDraft||window.G?.character||{};
 const value=(...xs)=>xs.find(x=>x!==undefined&&x!==null&&x!=='');
 const field=(obj,names)=>{for(const n of names){if(obj&&obj[n]!=null)return obj[n]}return null};
 const lifeData=()=>window.pendingLifeSetup||window.G?.lifeSetup||window.lifeSetupDraft||{};
 window.ETE_CHARACTER_SUMMARY={
   appearance:c=>typeof window.appearanceText==='function'?window.appearanceText(c):'镜子里是你熟悉的样子。',
   identity:c=>{const v=value(field(c,['genderPresentation','presentation','look']),field(c,['gender']));return v?'你看起来更偏向'+v+'。':''},
   home:l=>{const v=value(field(l,['home','housing','residence','houseType']),field(draft(),['home']));return v?'你住在'+v+'。':''},
   work:l=>{const v=field(l,['job','work','occupation']);return v?'你的日常工作是'+v+'。':''},
   transport:l=>{const v=field(l,['vehicle','transport']);return v?'平时出行时，你主要依赖'+v+'。':''},
   companion:c=>{const p=c?.companion;return p?.name?'和你一起生活的还有'+p.name+'。':''},
   traits:c=>{const ids=c?.traits||[];if(!ids.length)return'';try{const names=ids.map(id=>window.TRAIT_DEFS?.find(t=>t.id===id)?.name).filter(Boolean);return names.length?'你身上有这些比较明显的特点：'+names.join('、')+'。':''}catch(_){return''}}
 };
 window.renderCharacterReview=()=>{
   const c=draft(),l=lifeData(),S=window.ETE_CHARACTER_SUMMARY;
   const parts=[S.appearance(c),S.identity(c),S.home(l),S.work(l),S.transport(l),S.companion(c),S.traits(c)].filter(Boolean);
   const e=document.getElementById('characterReviewText');if(e)e.innerHTML=parts.map(x=>'<p>'+x+'</p>').join('');
 };
 window.reviewBackAppearance=()=>showScreen('characterScreen');
 window.reviewBackTraits=()=>{showScreen('traitScreen');try{renderTraitBuilder()}catch(_){}};
 window.reviewBackLife=()=>showScreen('lifeSetupScreen');

 // Life Setup's Back must return to appearance, not traits.
 if(life){
   [...life.querySelectorAll('button')].filter(b=>/返回|上一步/.test(b.textContent||'')).forEach(b=>{
     b.onclick=()=>showScreen('characterScreen');
   });
 }
 // Intercept the Life Setup final/next button: review first, actual start only after confirmation.
 let originalLifeConfirm=null;
 if(life){
   const candidates=[...life.querySelectorAll('button')].filter(b=>/开始|确认|下一步|完成/.test(b.textContent||''));
   const next=candidates[candidates.length-1];
   if(next){
     originalLifeConfirm=next.onclick;
     next.onclick=e=>{e?.preventDefault?.();renderCharacterReview();showScreen('characterReviewScreen');return false};
   }
 }
 window.confirmCharacterReview=()=>{
   // Prefer the game's original life-setup confirmation path so its existing field collection stays authoritative.
   if(typeof originalLifeConfirm==='function')return originalLifeConfirm.call(life);
   if(typeof window.startGame==='function')return window.startGame();
   showScreen('gameScreen');
 };
})();
</script>'''
s=s.replace('</body>',patch+'\n</body>',1)
p.write_text(s,encoding='utf-8')
