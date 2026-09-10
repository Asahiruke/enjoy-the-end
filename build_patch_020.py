from pathlib import Path

p=Path('dist/index.html')
s=p.read_text(encoding='utf-8')
s=s.replace('Prototype 0.19','Prototype 0.20')

patch=r'''<script id="ete-020-sofa-actions">
(()=>{
  // Sofa posture is persistent state. NPC checks happen only after player actions,
  // never on a real-time timer. Changing rooms implicitly stands the player up.
  const S=window.ETE_SOFA_STATE=window.ETE_SOFA_STATE||{sitting:false,room:null,catNear:false,catLap:false};
  const txt=e=>(e?.textContent||'').trim();
  const catName=()=>{try{const g=window.G||{};return g.character?.companion?.name||g.characterDraft?.companion?.name||'猫'}catch(_){return'猫'}};
  const addLog=t=>{const e=document.querySelector('#log,.log,#recentLog,.recent-log,[data-role="log"]');if(!e)return;const d=document.createElement('div');d.textContent=t;e.appendChild(d);e.scrollTop=e.scrollHeight};
  const currentRoom=()=>{try{return (window.G||{}).currentRoom||(window.G||{}).room||null}catch(_){return null}};
  const stand=()=>{S.sitting=false;S.room=null;S.catNear=false;S.catLap=false};
  const companionHere=()=>{try{const g=window.G||{};const c=g.character?.companion||g.characterDraft?.companion||g.companion;if(!c)return false;const r=currentRoom();return !c.room||!r||c.room===r||c.location===r}catch(_){return false}};
  const rollAfterAction=()=>{
    if(!S.sitting)return;
    if(S.room&&currentRoom()&&S.room!==currentRoom()){stand();return}
    if(!companionHere()){S.catNear=false;S.catLap=false;return}
    const r=Math.random();
    if(!S.catNear&&r<.28){S.catNear=true;addLog(catName()+'走到沙发附近，在你触手可及的地方停了下来。')}
    else if(S.catNear&&!S.catLap&&r<.10){S.catLap=true;addLog(catName()+'踩上沙发，慢慢挪到你的腿上伏了下来。')}
    else if(S.catNear&&r<.16){S.catNear=false;S.catLap=false;addLog(catName()+'忽然对别处有了兴趣，从沙发边走开了。')}
  };
  const ensureButtons=()=>{
    const buttons=[...document.querySelectorAll('button')];
    const leave=buttons.find(b=>/起身|站起来|离开沙发/.test(txt(b)));
    if(!S.sitting||!leave)return;
    let rest=document.getElementById('eteSofaRest');
    if(!rest){rest=document.createElement('button');rest.id='eteSofaRest';rest.textContent='休息';rest.onclick=()=>{if(typeof window.advance==='function')window.advance(30);addLog('你继续靠在沙发上休息了一会儿。');rollAfterAction();setTimeout(ensureButtons,0)};leave.parentElement?.insertBefore(rest,leave)}
    const old=[...document.querySelectorAll('button')].filter(b=>/保持坐|继续坐|再坐/.test(txt(b)));old.forEach(b=>{if(b.id!=='eteSofaRest')b.style.display='none'});
    let pet=document.getElementById('etePetCat');
    if(S.catNear){if(!pet){pet=document.createElement('button');pet.id='etePetCat';pet.textContent='摸摸：'+catName();pet.onclick=()=>{addLog('你伸手摸了摸'+catName()+'。');rollAfterAction();setTimeout(ensureButtons,0)};leave.parentElement?.insertBefore(pet,leave)}else pet.textContent='摸摸：'+catName()}
    else pet?.remove();
  };
  document.addEventListener('click',e=>{
    const b=e.target.closest('button');if(!b)return;const t=txt(b);
    if(/坐在沙发上/.test(t)&&!/保持|继续|休息/.test(t)){S.sitting=true;S.room=currentRoom();S.catNear=false;S.catLap=false;setTimeout(()=>{rollAfterAction();ensureButtons()},0);return}
    if(/起身|站起来|离开沙发/.test(t)){stand();document.getElementById('eteSofaRest')?.remove();document.getElementById('etePetCat')?.remove();return}
    // Any explicit room movement implicitly cancels sitting before the move resolves.
    if(S.sitting&&(/前往|进入|去往|移动到|回到/.test(t)||b.dataset?.room||b.dataset?.targetRoom)){stand();document.getElementById('eteSofaRest')?.remove();document.getElementById('etePetCat')?.remove();return}
    // Every other player action is one opportunity for nearby-NPC state to change.
    if(S.sitting&&b.id!=='eteSofaRest'&&b.id!=='etePetCat')setTimeout(()=>{rollAfterAction();ensureButtons()},0);
  },true);
  // No setInterval / polling: render refreshes are requested only by actions above.
})();
</script>'''
s=s.replace('</body>',patch+'\n</body>',1)
p.write_text(s,encoding='utf-8')
