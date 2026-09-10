from pathlib import Path

p = Path("dist/index.html")
s = p.read_text(encoding="utf-8")

# Prototype label/title cleanup.
s = s.replace("Prototype 0.17", "Prototype 0.19")
s = s.replace("Prototype 0.18", "Prototype 0.19")
s = s.replace("<title>末日室内生存 Prototype", "<title>Enjoy the End Prototype")
s = s.replace("<h1>末日室内生存</h1>", "<h1>&nbsp;</h1>", 1)

# Smaller initial creation-point pool.
s = s.replace('<span id="traitPoints">30</span>', '<span id="traitPoints">12</span>', 1)
s = s.replace('return 30 - statCost(con)-statCost(str)-statCost(agi)-traitCost;', 'return 12 - statCost(con)-statCost(str)-statCost(agi)-traitCost;', 1)

# Expanded trait pool. Positive traits use positive cost; negative traits refund points with negative cost.
extra_traits = '''  {id:"mild_myopia",name:"轻度近视",cost:-2,desc:"远处的细节有些模糊；没有合适的矫正用品时，远距离观察会受到轻微影响。",mods:{con:0,str:0,agi:0},tags:["myopia_mild"],exclusiveGroup:"vision"},
  {id:"medium_myopia",name:"中度近视",cost:-4,desc:"不进行视力矫正时，远处目标与文字会明显难以辨认。",mods:{con:0,str:0,agi:0},tags:["myopia_medium"],exclusiveGroup:"vision"},
  {id:"severe_myopia",name:"重度近视",cost:-7,desc:"你高度依赖眼镜或其他矫正用品；失去它们会显著影响远距离观察与部分行动。",mods:{con:0,str:0,agi:0},tags:["myopia_severe"],exclusiveGroup:"vision"},
  {id:"alcohol_dependence",name:"酒精成瘾",cost:-8,desc:"长期缺少酒精会逐渐带来明显的不适、压力与状态惩罚。",mods:{con:-1,str:0,agi:0},tags:["alcohol_dependence"]},
  {id:"nicotine_dependence",name:"尼古丁成瘾",cost:-6,desc:"长期缺少尼古丁会增加烦躁与压力，并可能影响专注。",mods:{con:0,str:0,agi:0},tags:["nicotine_dependence"]},
  {id:"caffeine_dependence",name:"咖啡因成瘾",cost:-3,desc:"你已经习惯稳定摄入咖啡因；突然中断会让精神状态变差一阵。",mods:{con:0,str:0,agi:0},tags:["caffeine_dependence"]},
  {id:"good_endurance",name:"耐力良好",cost:5,desc:"长时间活动时，你比一般人更不容易积累疲劳。",mods:{con:3,str:0,agi:0},tags:["good_endurance"]},
  {id:"first_aid_knowledge",name:"急救知识",cost:5,desc:"你掌握常见伤势的基础处理知识，也更懂得如何利用有限的医疗用品。",mods:{con:0,str:0,agi:0},tags:["first_aid_knowledge"]},
  {id:"observant",name:"观察敏锐",cost:5,desc:"你更容易注意到环境里的异常、痕迹与容易被忽略的细节。",mods:{con:0,str:0,agi:1},tags:["observant"]},
  {id:"good_direction",name:"方向感良好",cost:3,desc:"在陌生区域行动时，你更容易记住路线与空间关系。",mods:{con:0,str:0,agi:0},tags:["good_direction"],exclusiveGroup:"direction"},
  {id:"good_sleeper",name:"睡眠质量好",cost:3,desc:"只要环境允许，你通常能获得更稳定的睡眠与恢复。",mods:{con:1,str:0,agi:0},tags:["good_sleeper"],exclusiveGroup:"sleep_quality"},
  {id:"animal_affinity",name:"亲近动物",cost:3,desc:"你比较擅长判断动物的情绪与距离感，更容易建立稳定互动。",mods:{con:0,str:0,agi:0},tags:["animal_affinity"]},
  {id:"poor_endurance",name:"耐力不足",cost:-5,desc:"持续活动会更快让你感到疲惫，需要更频繁地休息。",mods:{con:-4,str:0,agi:0},tags:["poor_endurance"],exclusiveGroup:"endurance"},
  {id:"clumsy_hands",name:"手脚笨拙",cost:-4,desc:"精细操作和部分制作行为对你来说更费时间，也更容易出现小失误。",mods:{con:0,str:0,agi:-2},tags:["clumsy_hands"]},
  {id:"sensitive_stomach",name:"肠胃脆弱",cost:-4,desc:"不新鲜的食物与可疑饮水更容易让你身体不适。",mods:{con:-2,str:0,agi:0},tags:["sensitive_stomach"]},
  {id:"picky_eater",name:"挑食",cost:-3,desc:"某些食物很难让你满意；长期将就会额外影响心情。",mods:{con:0,str:0,agi:0},tags:["picky_eater"]},
  {id:"easily_stressed",name:"容易紧张",cost:-4,desc:"危险、未知与持续异常更容易让你的压力累积。",mods:{con:0,str:0,agi:0},tags:["easily_stressed"]},
  {id:"poor_direction",name:"方向感差",cost:-4,desc:"陌生地区的路线不容易留在你的脑中，探索更容易耗费额外时间。",mods:{con:0,str:0,agi:0},tags:["poor_direction"],exclusiveGroup:"direction"},
  {id:"fear_dark",name:"怕黑",cost:-3,desc:"缺乏可靠照明时，黑暗会明显增加你的压力。",mods:{con:0,str:0,agi:0},tags:["fear_dark"]},
  {id:"sleepy",name:"嗜睡",cost:-4,desc:"你需要更长的睡眠，也更容易在缺觉后迅速积累疲劳。",mods:{con:-1,str:0,agi:0},tags:["sleepy"],exclusiveGroup:"sleep_quality"},
  {id:"social_dependence",name:"社交依赖",cost:-4,desc:"长期独处会比一般人更快消耗你的精神状态。",mods:{con:0,str:0,agi:0},tags:["social_dependence"],exclusiveGroup:"social_style"},
  {id:"loner",name:"独来独往",cost:-2,desc:"独处对你影响较小，但你与人物NPC建立亲密关系会更慢。",mods:{con:0,str:0,agi:0},tags:["loner"],exclusiveGroup:"social_style"},
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

# Title-screen settings button. It uses a lightweight pre-game panel because no save needs to exist yet.
title_settings = '''<div id="titleSettingsPanel" class="modal hidden"><div class="modalbox">
  <h2>设置</h2>
  <div class="card toggle"><div><b>字体大小</b><div class="small">这个设置会同时应用到新游戏与存档。</div></div>
  <div style="min-width:180px"><input id="titleFontScaleSlider" type="range" min="80" max="140" step="5" value="100" oninput="setGameFontScale(this.value)"><div class="small" style="text-align:right"><span id="titleFontScaleValue">100%</span></div></div></div>
  <div class="actions"><button onclick="closeTitleSettings()">关闭</button></div>
</div></div>'''
if 'id="titleSettingsPanel"' not in s:
    s = s.replace('</body>', title_settings + '\n</body>', 1)

# Put a settings button on the title screen next to the existing title actions when possible.
if 'onclick="openTitleSettings()"' not in s:
    marker = '<button onclick="newGame()">新游戏</button>'
    if marker in s:
        s = s.replace(marker, marker + '<button onclick="openTitleSettings()">设置</button>', 1)
    else:
        marker = '<button onclick="startNewGame()">新游戏</button>'
        if marker in s:
            s = s.replace(marker, marker + '<button onclick="openTitleSettings()">设置</button>', 1)

# Two compact trait cards per row on wider screens; single column on phones.
layout = r'''<style id="ete-019-layout">
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

runtime = r'''<script id="ete-019-runtime">
function setGameFontScale(v){
  const n=Math.max(80,Math.min(140,Number(v)||100));
  document.documentElement.style.setProperty('--game-font-scale',String(n/100));
  for(const id of ['fontScaleValue','titleFontScaleValue']){const out=document.getElementById(id);if(out)out.textContent=n+'%'}
  for(const id of ['fontScaleSlider','titleFontScaleSlider']){const slider=document.getElementById(id);if(slider&&Number(slider.value)!==n)slider.value=n}
  if(window.G){ G.settings ||= {}; G.settings.fontScale=n; }
  try{localStorage.setItem('ete_font_scale',String(n))}catch(e){}
}
function openTitleSettings(){const e=document.getElementById('titleSettingsPanel');if(e)e.classList.remove('hidden');setGameFontScale(Number(localStorage.getItem('ete_font_scale'))||100)}
function closeTitleSettings(){document.getElementById('titleSettingsPanel')?.classList.add('hidden')}

// Room-description vocabulary registry. These are deliberately data-driven so housing, weather,
// clutter, utilities, NPC presence and future renovation systems can compose descriptions instead of replacing them.
window.ETE_ROOM_DESCRIPTORS = {
  living:{base:['这里是家中最适合长时间停留的公共空间。'],tidy:['地面还算整洁，家具之间留有足够的通行空间。'],cluttered:['越来越多的东西占据了原本空着的位置，通道也显得窄了一些。'],dark:['失去照明后，家具的轮廓沉在昏暗里。'],cold:['室内的冷意正一点点渗进家具和地面。'],hot:['空气闷在房间里，连坐着不动也很难忽略热意。']},
  bedroom:{base:['这里比公共区域安静一些，床铺占据了视线里最明确的位置。'],tidy:['床铺整理得很平整，属于你的东西各自待在熟悉的位置。'],cluttered:['衣物和零碎物品开始侵占床边与过道。'],dark:['黑暗让卧室显得比白天更狭小。'],cold:['被褥摸起来也带着一点挥之不去的凉意。']},
  kitchen:{base:['料理台、水槽与储存食物的地方挤在同一个功能明确的空间里。'],stocked:['能吃的东西被分散收在冰箱、柜子和其他容器中。'],empty:['能直接拿来做饭的东西已经显得有些单薄。'],dirty:['料理留下的痕迹开始堆积，水槽和台面都需要整理。'],power_off:['没有电以后，冰箱里安静得让人有些在意。'],water_off:['水龙头没有回应，厨房一下少了最基本的便利。']},
  bathroom:{base:['这里主要用于清洁身体和处理日常卫生。'],clean:['潮气散去后，瓷砖和镜面显得还算干净。'],humid:['水汽停留在镜面和墙面上，空气带着明显的潮湿。'],water_off:['没有供水后，这个房间的大部分用途都变得奢侈起来。'],cold:['裸露的皮肤很快就能感觉到这里的冷。']},
  entrance:{base:['门把屋内与外面的世界隔开，鞋和准备外出的东西通常会留在这里。'],secured:['门上的额外加固让这里多了一层笨重但可靠的感觉。'],blocked:['为了防护堆在附近的东西压缩了原本的出入空间。'],outside_noise:['门外偶尔传来的声音会比屋里任何动静都更让人在意。']},
  corridor:{base:['这段空间主要负责连接各个房间。'],clear:['通道保持畅通，来回移动并不费事。'],cluttered:['临时堆放的东西正在一点点挤占过道。'],dark:['没有照明时，通向其他房间的方向只剩模糊轮廓。']},
  storage:{base:['这里的价值几乎完全取决于还能塞进多少东西，以及你是否记得它们放在哪里。'],ordered:['物资被分门别类收好，寻找东西并不困难。'],cluttered:['不同用途的物资混在一起，想找某件东西需要多翻一会儿。'],full:['能利用的空隙已经所剩无几。']}
};

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
