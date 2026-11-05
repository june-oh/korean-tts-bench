const el = id => document.getElementById(id);
async function read(path) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(path);
  return response.json();
}
function node(tag, text, cls) {
  const n = document.createElement(tag);
  if (text !== undefined) n.textContent = text;
  if (cls) n.className = cls;
  return n;
}
try {
  const [prompts, models] = await Promise.all([read("prompts.json"), read("models.json")]);
  await Promise.all(models.map(async m => { m.data = (await read("audio/" + m.id + "/measurements.json")).rows; }));
  let selected = prompts.find(p => p[0] === location.hash.slice(1)) || prompts[0];
  let blind = false, order = [...models];
  const buttons = new Map();
  for (const p of prompts) {
    const b = node("button");
    b.append(node("small",p[0]), document.createTextNode(p[1]));
    b.onclick = () => { selected = p; history.replaceState(null,"","#"+p[0]); shuffle(); render(); };
    buttons.set(p[0], b); el("list").append(b);
  }
  function shuffle() {
    order = [...models];
    if (blind) for (let i=order.length-1; i>0; i--) {
      const j = Math.floor(Math.random()*(i+1)); [order[i],order[j]]=[order[j],order[i]];
    }
  }
  el("blind").onclick = () => {
    blind = !blind;
    if (blind) shuffle(); // keep the order on reveal
    render();
  };
  function render() {
    const [id, category, text, hint] = selected;
    for (const [key,b] of buttons) b.setAttribute("aria-current",String(key===id));
    el("category").textContent=category; el("count").textContent=id+" / "+prompts.length;
    el("phrase").textContent=text; el("hint").textContent="청취 포인트 · "+hint;
    el("blind").textContent=blind?"모델 공개하기":"블라인드로 듣기";
    el("blind").setAttribute("aria-pressed",String(blind));
    el("players").replaceChildren();
    for (const [i,m] of order.filter(m=>m.data.some(r=>r.id===id)).entries()) {
      const r=m.data.find(r=>r.id===id), card=node("div",undefined,"card");
      const letter=String.fromCharCode(65+i);
      card.append(node("strong", blind?"음성 "+letter:letter+" · "+m.name));
      if (!blind) card.append(node("p",m.voice+" ｜ "+m.device,"detail"));
      const a=node("audio"); a.controls=true; a.preload="none";
      a.src="audio/"+m.id+"/"+id+".wav"; a.setAttribute("aria-label",blind?"음성 "+letter:m.name);
      a.onplay=()=>document.querySelectorAll("audio").forEach(other=>{if(other!==a)other.pause();});
      card.append(a);
      if (!blind) card.append(node("p",(r.seconds.length?"생성 "+r.seconds[0].toFixed(2)+"초 · RTF "+(r.seconds[0]/r.duration).toFixed(2):"생성 시간 미측정")+" · 음성 "+r.duration.toFixed(2)+"초 · "+(r.rate/1000)+" kHz","stats"));
      el("players").append(card);
    }
  }
  render();
} catch (error) {
  el("phrase").textContent="측정 자료를 불러오지 못했습니다. 새로고침해 주세요."; console.error(error);
}
