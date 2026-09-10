from pathlib import Path

p = Path("dist/index.html")
s = p.read_text(encoding="utf-8")

# Prototype label/title cleanup.
s = s.replace("Prototype 0.17", "Prototype 0.18")
s = s.replace("<title>末日室内生存 Prototype", "<title>Enjoy the End Prototype")
s = s.replace("<h1>末日室内生存</h1>", "<h1>&nbsp;</h1>", 1)

# Smaller initial creation-point pool.
s = s.replace('<span id="traitPoints">30</span>', '<span id="traitPoints">12</span>', 1)
s = s.replace('return 30 - statCost(con)-statCost(str)-statCost(agi)-traitCost;', 'return 12 - statCost(con)-statCost(str)-statCost(agi)-traitCost;', 1)

# More negative traits. Vision tiers are mutually exclusive through the runtime helper below.
extra_traits = '''  {id:"mild_myopia",name:"轻度近视",cost:-2,desc:"远处的细节有些模糊；没有合适的矫正用品时，远距离观察会受到轻微影响。",mods:{con:0,str:0,agi:0},tags:["myopia_mild"],exclusiveGroup:"vision"},
  {id:"medium_myopia",name:"中度近视",cost:-4,desc:"不进行视力矫正时，远处目标与文字会明显难以辨认。",mods:{con:0,str:0,agi:0},tags:["myopia_medium"],exclusiveGroup:"vision"},
  {id:"severe_myopia",name:"重度近视",cost:-7,desc:"你高度依赖眼镜或其他矫正用品；失去它们会显著影响远距离观察与部分行动。",mods:{con:0,str:0,agi:0},tags:["myopia_severe"],exclusiveGroup:"vision"},
  {id:"alcohol_dependence",name:"酒精成瘾",cost:-8,desc:"长期缺少酒精会逐渐带来明显的不适、压力与状态惩罚。",mods:{con:-1,str:0,agi:0},tags:["alcohol_dependence"]},
  {id:"nicotine_dependence",name:"尼古丁成瘾",cost:-6,desc:"长期缺少尼古丁会增加烦躁与压力，并可能影响专注。",mods:{con:0,str:0,agi:0},tags:["nicotine_dependence"]},
  {id:"caffeine_dependence",name:"咖啡因成瘾",cost:-3,desc:"你已经习惯稳定摄入咖啡因；突然中断会让精神状态变差一阵。",mods:{con:0,str:0,agi:0},tags:["caffeine_dependence"]},
'''
needle = '  {id:"favorite_companion",name:"最爱的伙伴"'
if needle in s and 'id:"severe_myopia"' not in s:
    s = s.replace(needle, extra_traits + needle, 1)

# Settings: font scale slider.
font_card = '''    <div class="card toggle">
      <div><b>字体大小</b><div class="small">调整游戏界面的整体文字大小。</div></div>
      <div style="min-width:220px"><input id="fontScaleSlider" type="range" min="80" max="140" step="5" value="100" oninput="setGameFontScale(this.value)"><div class="small" style="text-align:right"><span id="fontScaleValue">100%</span></div></div>
    </div>
'''
settings_actions = '    <div class="actions"><button onclick="saveGame()">保存游戏</button><button onclick="loadGame()">读取游戏</button><button onclick="returnToTitle()">返回标题</button></div>'
if 'id="fontScaleSlider"' not in s:
    s = s.replace(settings_actions, font_card + settings_actions, 1)

s = s.replace('settings:{showCapacityNumbers:false}', 'settings:{showCapacityNumbers:false,fontScale:100}', 1)

# Two compact trait cards per row on wider screens; single column on phones.
layout = r'''<style id="ete-018-layout">
:root{--game-font-scale:1}
body{font-size:calc(16px * var(--game-font-scale))}
.small{font-size:calc(12px * var(--game-font-scale))}
h1{font-size:calc(20px * var(--game-font-scale))}
h2{font-size:calc(15px * var(--game-font-scale))}
h3{font-size:calc(13px * var(--game-font-scale))}
#traitScreen #traitList{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:8px!important}
#traitScreen .trait-card{min-height:70px!important;padding:10px 12px!important;column-gap:8px!important;row-gap:2px!important}
#traitScreen .trait-card .small{line-height:1.35!important}
@media(max-width:700px){#traitScreen #traitList{grid-template-columns:1fr!important}}
</style>'''
s = s.replace('</head>', layout + '\n</head>', 1)

runtime = r'''<script id="ete-018-runtime">
function setGameFontScale(v){
  const n=Math.max(80,Math.min(140,Number(v)||100));
  document.documentElement.style.setProperty('--game-font-scale',String(n/100));
  const out=document.getElementById('fontScaleValue'); if(out) out.textContent=n+'%';
  const slider=document.getElementById('fontScaleSlider'); if(slider && Number(slider.value)!==n) slider.value=n;
  if(window.G){ G.settings ||= {}; G.settings.fontScale=n; }
  try{localStorage.setItem('ete_font_scale',String(n))}catch(e){}
}
(function(){
  try{setGameFontScale(Number(localStorage.getItem('ete_font_scale'))||100)}catch(e){setGameFontScale(100)}
  document.addEventListener('change',e=>{
    const input=e.target.closest('input[data-trait]'); if(!input||!input.checked)return;
    try{
      const def=TRAIT_DEFS.find(t=>t.id===input.value), group=def?.exclusiveGroup;
      if(!group)return;
      document.querySelectorAll('input[data-trait]:checked').forEach(other=>{
        if(other===input)return;
        const od=TRAIT_DEFS.find(t=>t.id===other.value);
        if(od?.exclusiveGroup===group) other.checked=false;
      });
      renderTraitBuilder();
    }catch(err){}
  });
  if(typeof openSettings==='function'){
    const _openSettings=openSettings;
    openSettings=function(){_openSettings();setGameFontScale(G?.settings?.fontScale||Number(localStorage.getItem('ete_font_scale'))||100)};
  }
  if(typeof startGame==='function'){
    const _startGame=startGame;
    startGame=function(){const out=_startGame.apply(this,arguments);setGameFontScale(G?.settings?.fontScale||100);return out};
  }
  if(typeof loadGame==='function'){
    const _loadGame=loadGame;
    loadGame=function(){const out=_loadGame.apply(this,arguments);setTimeout(()=>setGameFontScale(G?.settings?.fontScale||Number(localStorage.getItem('ete_font_scale'))||100),0);return out};
  }
})();
</script>'''
s = s.replace('</body>', runtime + '\n</body>', 1)

p.write_text(s, encoding="utf-8")
