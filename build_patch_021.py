from pathlib import Path

p=Path('dist/index.html')
s=p.read_text(encoding='utf-8')
s=s.replace('Prototype 0.20','Prototype 0.21')

patch=r'''<script id="ete-021-action-system">
(()=>{
  // Semantic action tags. Duration is data; injuries/status effects modify tags rather than button names.
  const A=window.ETE_ACTIONS=window.ETE_ACTIONS||{};
  A.tags={
    movement:{label:'移动',body:['legs','balance'],exertion:1},
    stairs:{label:'上下楼',body:['legs','balance'],exertion:2},
    posture:{label:'姿势变化',body:['legs','core'],exertion:.5},
    manipulation:{label:'拿取/操作',body:['hands','arms'],exertion:.5},
    fine_motor:{label:'精细操作',body:['hands','vision'],exertion:.5},
    self_care:{label:'个人护理',body:['hands','arms'],exertion:.5},
    eating:{label:'进食',body:['hands','mouth'],exertion:.25},
    drinking:{label:'饮水',body:['hands','mouth'],exertion:.2},
    social:{label:'社交',body:['voice','hearing'],exertion:.1},
    observation:{label:'观察',body:['vision','hearing'],exertion:.1},
    rest:{label:'休息',body:[],exertion:-1},
    household:{label:'家务',body:['hands','arms','back'],exertion:1},
    cooking:{label:'料理',body:['hands','arms','vision'],exertion:1},
    hygiene:{label:'清洁',body:['hands','arms'],exertion:.75},
    medical:{label:'医疗',body:['hands','vision'],exertion:.5},
    crafting:{label:'制作/维修',body:['hands','arms','vision'],exertion:1},
    lifting:{label:'搬运',body:['arms','back','legs'],exertion:2}
  };
  A.defs={
    room_move:{minutes:1,tags:['movement']},
    room_move_stairs:{minutes:2,tags:['movement','stairs']},
    sit_down:{minutes:1,tags:['posture']},
    stand_up:{minutes:1,tags:['posture']},
    take_item:{minutes:1,tags:['manipulation']},
    store_item:{minutes:1,tags:['manipulation']},
    change_clothes:{minutes:3,tags:['self_care','manipulation']},
    groom_simple:{minutes:2,tags:['self_care','fine_motor']},
    make_bed:{minutes:3,tags:['household']},
    pet_animal:{minutes:2,tags:['social','manipulation']},
    call_npc:{minutes:0,tags:['social']},
    inspect:{minutes:0,tags:['observation']},
    observe:{minutes:5,tags:['observation']},
    drink:{minutes:1,tags:['drinking']},
    snack:{minutes:3,tags:['eating']},
    meal:{minutes:15,tags:['eating']},
    wash_hands:{minutes:1,tags:['hygiene']},
    shower:{minutes:15,tags:['hygiene']},
    rest_short:{minutes:10,tags:['rest']},
    rest_medium:{minutes:30,tags:['rest']}
  };
  A.modifiers=[];
  A.addModifier=fn=>{if(typeof fn==='function')A.modifiers.push(fn)};
  A.resolve=(id,ctx={})=>{
    const base=A.defs[id]||{minutes:Number(ctx.minutes)||0,tags:ctx.tags||[]};
    let out={id,minutes:base.minutes,tags:[...base.tags],...ctx};
    // Future injuries, pain, encumbrance, traits and weather register modifiers here.
    for(const fn of A.modifiers){try{out=fn(out)||out}catch(_){}}
    out.minutes=Math.max(0,Math.round(out.minutes));
    return out;
  };
  A.perform=(id,ctx={})=>{
    const a=A.resolve(id,ctx);
    if(a.minutes>0&&typeof window.advance==='function')window.advance(a.minutes);
    try{window.dispatchEvent(new CustomEvent('ete:action-complete',{detail:a}))}catch(_){}
    return a;
  };
  window.performAction=A.perform;

  const sofa=()=>window.ETE_SOFA_STATE;
  const standImplicit=()=>{
    const S=sofa(); if(!S?.sitting)return;
    S.sitting=false;S.room=null;S.catNear=false;S.catLap=false;
    document.getElementById('eteSofaRest')?.remove();
    document.getElementById('etePetCat')?.remove();
  };
  const text=b=>(b?.textContent||'').trim();

  // Attach semantic time to existing small world actions without charging UI-only inspection/navigation.
  document.addEventListener('click',e=>{
    const b=e.target.closest('button');if(!b||b.dataset.eteTimed==='1')return;
    const t=text(b);
    if(/坐在沙发上/.test(t)&&!/休息|继续|保持/.test(t)){b.dataset.eteTimed='1';A.perform('sit_down');return}
    if(/起身|站起来|离开沙发/.test(t)){b.dataset.eteTimed='1';A.perform('stand_up');return}
    const move=/前往|进入|去往|移动到|回到/.test(t)||b.dataset?.room||b.dataset?.targetRoom;
    if(move){
      const stair=/楼上|楼下|上楼|下楼/.test(t)||b.dataset?.stairs==='true';
      standImplicit();
      b.dataset.eteTimed='1';A.perform(stair?'room_move_stairs':'room_move');return;
    }
    if(/呼唤[:：]?/.test(t)){b.dataset.eteTimed='1';A.perform('call_npc');return}
  },true);

  // Replace sofa action timing with semantic actions.
  window.addEventListener('ete:action-complete',e=>{
    const S=sofa();if(!S?.sitting)return;
    // Existing 0.20 reaction logic remains action-driven; this event is the canonical hook for later NPC reactions.
  });
})();
</script>'''
s=s.replace('</body>',patch+'\n</body>',1)
p.write_text(s,encoding='utf-8')
