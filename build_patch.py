from pathlib import Path
import re, gzip, base64, textwrap
p=Path('dist/index.html')
s=p.read_text(encoding='utf-8')
s=s.replace('Prototype 0.11','Prototype 0.12')
s=s.replace('const SAVE_KEY="apocalypse_text_game_save_v011";','const SAVE_KEY="apocalypse_text_game_save_v012";')
# character form
s=s.replace('<div class="field"><label>性别</label><select id="char_gender" onchange="updateCharacterPreview()"><option>女性</option><option>男性</option><option>其他 / 不指定</option></select></div>',
'''<div class="field"><label>外表气质</label><select id="char_gender" onchange="updateCharacterPreview()"><option>男性化</option><option selected>中性</option><option>女性化</option></select></div>''')
s=s.replace('<div class="field"><label>体重 / 体型</label><select id="char_weight" onchange="updateCharacterPreview()"><option>偏轻</option><option selected>中等</option><option>偏重</option></select></div>',
'''<div class="field"><label>体格</label><select id="char_weight" onchange="updateCharacterPreview()"><option>纤细</option><option selected>匀称</option><option>壮实</option></select></div>''')
s=s.replace('''    <h3>镜中预览</h3><div id="characterPreview" class="card"></div>
    <div class="card small">性格 / 技能 / 服装：继续预留数据结构。</div>''', '''    <h3>镜中预览</h3><div id="characterPreview" class="card"></div>
    <details class="card"><summary>身体特征（预留）</summary>
      <div class="small" style="margin:8px 0">这些数据不会进入普通的镜中外貌描述，仅为后续身体、服装及特殊事件判定预留。</div>
      <div class="form-grid">
        <div class="field"><label>胸部轮廓</label><select id="char_chest"><option value="unset">不设置</option><option value="flat">平坦</option><option value="slight">轻微</option><option value="medium">中等</option><option value="full">明显</option></select></div>
        <div class="field"><label>男性身体特征</label><select id="char_maleTraits"><option value="none">无</option><option value="present">有</option></select></div>
        <div class="field"><label>女性身体特征</label><select id="char_femaleTraits"><option value="none">无</option><option value="present">有</option></select></div>
      </div>
    </details>
    <div class="card small">性格 / 技能 / 服装：继续预留数据结构。</div>''')
# collectCharacter + appearanceText
old='''function collectCharacter(){return{
 name:(document.getElementById("charName").value||"主角").trim(),
 appearance:{
  gender:document.getElementById("char_gender").value,hairLength:document.getElementById("char_hairLength").value,
  hairColor:document.getElementById("char_hairColor").value,eyeColor:document.getElementById("char_eyeColor").value,
  eyeShape:document.getElementById("char_eyeShape").value,skinTone:document.getElementById("char_skinTone").value,
  height:document.getElementById("char_height").value,weight:document.getElementById("char_weight").value
 },
 tags:[],personalityTags:[],skills:{},clothingTags:[]
}}
function appearanceText(c){const a=c.appearance;return `${c.name}看起来${a.height}，体型${a.weight}。${a.hairColor}的${a.hairLength}，${a.eyeColor}的眼睛显得${a.eyeShape}，肤色${a.skinTone}。`}'''
new='''function collectCharacter(){return{
 name:(document.getElementById("charName").value||"主角").trim(),
 appearance:{
  gender:document.getElementById("char_gender").value,hairLength:document.getElementById("char_hairLength").value,
  hairColor:document.getElementById("char_hairColor").value,eyeColor:document.getElementById("char_eyeColor").value,
  eyeShape:document.getElementById("char_eyeShape").value,skinTone:document.getElementById("char_skinTone").value,
  height:document.getElementById("char_height").value,weight:document.getElementById("char_weight").value
 },
 body:{
  chest:document.getElementById("char_chest")?.value||"unset",
  maleTraits:document.getElementById("char_maleTraits")?.value||"none",
  femaleTraits:document.getElementById("char_femaleTraits")?.value||"none"
 },
 tags:[],personalityTags:[],skills:{},clothingTags:[]
}}
function appearanceText(c){
 const a=c.appearance;
 const height={"偏矮":"个子偏矮","中等":"身高适中","偏高":"个子偏高"}[a.height]||a.height;
 const build={"纤细":"身形偏纤细","匀称":"身形匀称","壮实":"体格显得结实"}[a.weight]||a.weight;
 const eyes={"柔和":"眼神显得柔和","锐利":"目光显得锐利","略显困倦":"眼睛看起来有些困倦","平静":"目光显得平静"}[a.eyeShape]||`眼睛显得${a.eyeShape}`;
 return `${c.name}的外表气质偏${a.gender}，${height}，${build}。留着${a.hairColor}的${a.hairLength}－${a.eyeColor}的${eyes}，肤色${a.skinTone}。`;
}'''
if old not in s: print('WARN collect old not found')
s=s.replace(old,new)
# CSS for mobile views
s=s.replace('@media(max-width:800px){#app{padding:10px}.grid,.form-grid{grid-template-columns:1fr}.reserve-toolbar select{width:100%}.title-wrap{min-height:70vh}}', '''
.mobile-view-menu{display:none}.mobile-close{display:none}
@media(max-width:800px){
 #app{padding:10px}.grid,.form-grid{grid-template-columns:1fr}.reserve-toolbar select{width:100%}.title-wrap{min-height:70vh}
 #gameScreen .grid{display:flex;flex-direction:column}
 #gameScreen main,#gameScreen aside{display:contents}
 #roomCorePanel{order:1} #statusPanel{order:2} #mobileViewMenu{order:3} #logPanel{order:4}
 #roomToolsPanel,#actionMainPanel,#reservePanel,#containersPanel,#weatherPanel,#entitiesPanel,#carryPanel,#worldPanel{display:none;order:5}
 .mobile-view-menu{display:block}
 .mobile-view-menu .actions{display:grid;grid-template-columns:1fr 1fr}
 .mobile-secondary.mobile-open{display:block!important;position:fixed;inset:0;z-index:80;overflow:auto;margin:0;padding:16px 12px 90px;background:var(--bg)}
 .mobile-secondary.mobile-open .mobile-close{display:block;position:sticky;top:0;margin-left:auto;z-index:82}
 body.mobile-view-open{overflow:hidden}
}''')
# Replace game screen markup block whole section before settings modal
start=s.index('<section id="gameScreen" class="hidden">')
end=s.index('\n<div id="settingsModal"', start)
new_game='''<section id="gameScreen" class="hidden">
  <div class="topbar"><div class="topbar-inner"><div id="topCharacterName" class="small">角色</div><button onclick="openSettings()">设置</button></div></div>
  <div class="grid">
    <main>
      <section class="panel" id="roomCorePanel">
        <div class="row small"><span id="dateLine"></span><span id="moneyLine"></span></div>
        <div id="houseNav" class="house-nav"></div>
        <h1 id="roomTitle"></h1><div id="roomDesc" class="desc"></div><div id="roomAtmosphere" class="small" style="margin-top:8px"></div><div id="roomMeta" class="room-meta"></div>
      </section>

      <section class="panel mobile-secondary" id="roomToolsPanel"><button class="mobile-close" onclick="closeMobileView()">关闭</button>
        <h2>房间互动</h2>
        <h3>观察</h3><div class="actions"><button onclick="observe('window')">看窗外</button><button onclick="observe('phone')">看手机 / 网络</button><button onclick="observe('neighbor')">听邻居动静</button><button onclick="observe('room')">环顾房间</button></div>
        <h3>设施 / 工作台</h3><div id="stationList"></div><div id="stationPanel"></div>
      </section>

      <section class="panel mobile-secondary" id="actionMainPanel"><button class="mobile-close" onclick="closeMobileView()">关闭</button><h2>行动</h2><div class="actions"><button onclick="openActionMenu('outside')">出门 / 行动</button><button onclick="openActionMenu('renovation')">住宅改造</button></div><div id="actionPanel"></div></section>
      <section class="panel" id="logPanel"><h2>近期记录</h2><div id="log"></div></section>
    </main>

    <aside>
      <section class="panel" id="statusPanel"><h2>身体与心理状态</h2><div id="statuses"></div></section>
      <section class="panel mobile-view-menu" id="mobileViewMenu"><h2>其他视图</h2><div class="actions"><button onclick="openMobileView('roomToolsPanel')">房间互动</button><button onclick="openMobileView('actionMainPanel')">行动</button><button onclick="openMobileView('reservePanel')">家中储备</button><button onclick="openMobileView('containersPanel')">容器</button><button onclick="openMobileView('weatherPanel')">天气 / 预报</button><button onclick="openMobileView('carryPanel')">外出装备</button><button onclick="openMobileView('worldPanel')">世界状况</button></div></section>
      <section class="panel mobile-secondary" id="reservePanel"><button class="mobile-close" onclick="closeMobileView()">关闭</button><h2>家中储备</h2><div class="reserve-toolbar"><select id="catFilter" onchange="renderReserve()"><option value="all">全部种类</option><option value="food">食物</option><option value="water">饮水</option><option value="medical">医疗</option><option value="tool">工具</option><option value="clothing">服装</option><option value="entertainment">娱乐</option></select><select id="roomFilter" onchange="refreshContainerFilter();renderReserve()"><option value="all">全部房间</option></select><select id="containerFilter" onchange="renderReserve()"><option value="all">全部容器</option></select></div><div id="reserve"></div></section>
      <section class="panel mobile-secondary" id="containersPanel"><button class="mobile-close" onclick="closeMobileView()">关闭</button><h2>容器</h2><div id="containersView"></div></section>
      <section class="panel mobile-secondary" id="weatherPanel"><button class="mobile-close" onclick="closeMobileView()">关闭</button><h2>天气 / 预报</h2><div id="weatherNow" class="small"></div><div id="forecastView" class="forecast-row" style="margin-top:8px"></div></section>
      <section class="panel mobile-secondary" id="entitiesPanel"><button class="mobile-close" onclick="closeMobileView()">关闭</button><h2>当前房间的其他存在</h2><div id="roomEntities" class="small"></div></section>
      <section class="panel mobile-secondary" id="carryPanel"><button class="mobile-close" onclick="closeMobileView()">关闭</button><h2>外出装备</h2><div id="carryView"></div></section>
      <section class="panel mobile-secondary" id="worldPanel"><button class="mobile-close" onclick="closeMobileView()">关闭</button><h2>世界状况</h2><div id="worldState" class="small"></div></section>
    </aside>
  </div>
</section>
'''
s=s[:start]+new_gam+s[end:]
# add mobile view functions before settings funcs

anchor='function toggleCapacityNumbers(v)'
idx=s.index(anchor)
mobile_funcs='''function openMobileView(id){
 if(innerWidth>800)return;
 closeMobileView();
 const el=document.getElementById(id);if(!el)return;
 el.classList.add("mobile-open");document.body.classList.add("mobile-view-open");
}
function closeMobileView(){document.querySelectorAll(".mobile-secondary.mobile-open").forEach(x=>x.classList.remove("mobile-open"));document.body.classList.remove("mobile-view-open")}
'''
s=s[:idx]+mobile_funcs+s[idx:]
# render room atmosphere by patching current weather/entity rendering
needle=''' const cw=currentWeather();
 document.getElementById("weatherNow").innerHTML=`${cw.name} · ${cw.low}～${cw.high}℃<br>${cw.description}<br>路况：${({normal:"正常",wet:"湿滑",flooded:"积水",snowy:"积雪"})[cw.roadCondition]||cw.roadCondition} · 风险：${({low:"低",medium:"中",high:"高",extreme:"极端"})[cw.exposureRisk]||cw.exposureRisk}`;'''
replacement=''' const cw=currentWeather();
 document.getElementById("weatherNow").innerHTML=`${cw.name} · ${cw.low}～${cw.high}℃<br>${cw.description}<br>路况：${({normal:"正常",wet:"湿滑",flooded:"积水",snowy:"积雪"})[cw.roadCondition]||cw.roadCondition} · 风险：${({low:"低",medium:"中",high:"高",extreme:"极端"})[cw.exposureRisk]||cw.exposureRisk}`;'''
s=s.replace(needle,replacement)
# append atmosphere after entity resolution block
needle2=''' const ents=getEntitiesInPlayerRoom();
 document.getElementById("roomEntities").innerHTML=ents.length?ents.map(e=>`<div class="entity-line">${NPC_DEFS[e.id]?.name||e.id} · ${e.currentAction||"正在这里停留"}</div>`).join(""):"这里目前没有其他人或动物。";'''
rep2=''' const ents=getEntitiesInPlayerRoom();
 document.getElementById("roomEntities").innerHTML=ents.length?ents.map(e=>`<div class="entity-line">${NPC_DEFS[e.id]?.name||e.id} · ${e.currentAction||"正在这里停留"}</div>`).join(""):"这里目前没有其他人或动物。";
 const atmosphere=[];
 atmosphere.push(`窗外是${cw.name}，气温约在 ${cw.low}～${cw.high}℃ 之间。${cw.description}`);
 if(ents.length)atmosphere.push(ents.map(e=>`${NPC_DEFS[e.id]?.name||e.id}${e.currentAction?`正在${e.currentAction}`:"正在这里停留"}。`).join(" "));
 document.getElementById("roomAtmosphere").textContent=atmosphere.join(" ");'''
if needle2 not in s: print('WARN ents block not found')
s=s.replace(needle2,rep2)

p.write_text(s, encoding='utf-8')
print('patched', len(s))
