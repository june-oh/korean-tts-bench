const el=id=>document.getElementById(id);
const n=(tag,text,cls)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e};
async function read(path){const response=await fetch(path,{cache:"no-cache"});if(!response.ok)throw new Error(path);return response.json()}
const sections=[
 ["숫자와 한글 표기의 대조",["P13","P16","P01","P02","P03","P04","P09","P12"]],
 ["영문 혼용과 장문 안내",["P14","P15","P08"]],
 ["음운·자모와 운율",["P05","P06","P07","P10","P11"]]
];
const refs={arena:["KO-TTS Arena","#ref-arena"],corea:["CoreaSpeech","#ref-corea"],nikl:["표준 발음법","#ref-nikl"]};
const sources={P01:"corea",P02:"corea",P03:"arena corea",P04:"corea",P05:"nikl",P08:"arena corea",P09:"arena",P12:"corea",P13:"arena corea",P14:"arena",P15:"arena",P16:"corea"};
try{
 const [prompts,models]=await Promise.all([read("prompts.json"),read("models.json")]);
 await Promise.all(models.map(async m=>{const result=await read("audio/"+m.id+"/measurements.json");m.byId=new Map(result.rows.map(r=>[r.id,r]))}));
 const byId=new Map(prompts.map(p=>[p[0],p]));
 let blind=false,order=[...models];
 const group=el("group");
 for(const [title] of sections)group.add(new Option(title,title));
 for(const m of models){
  const p=n("p"),link=n("a",m.name);link.href=m.url;
  p.append(link,document.createTextNode(" · "+m.voice+" · "+m.device+" · "+m.license));el("models").append(p);
 }
 function render(){
  const box=el("tables");box.replaceChildren();
  for(const [title,ids] of sections){
   if(group.value&&group.value!==title)continue;
   const h=n("h3",title),wrapper=n("div",undefined,"scroll"),table=n("table");
   wrapper.tabIndex=0;wrapper.setAttribute("aria-label",title+" 비교표, 좁은 화면에서는 좌우로 스크롤");
   table.setAttribute("aria-label",title);const header=table.createTHead().insertRow();
   for(const label of ["원문 · 청취 포인트",...order.map((m,i)=>blind?"음성 "+String.fromCharCode(65+i):m.name)]){
    const th=n("th",label);th.scope="col";header.append(th);
   }
   header.firstChild.style.width="33%";const body=table.createTBody();
   for(const id of ids){
    const [,category,text,hint]=byId.get(id),row=body.insertRow(),th=n("th");row.id=id;th.scope="row";
    th.append(n("span",id+" · "+category,"code"),document.createTextNode(text),n("span",hint,"hint"));
    const ref=n("span",undefined,"hint");
    if(sources[id])for(const key of sources[id].split(" ")){const a=n("a",refs[key][0]);a.href=refs[key][1];ref.append(a," ")}
    else ref.textContent="자체 탐색 문항";
    th.append(ref);row.append(th);
    for(const [i,m] of order.entries()){
     const cell=row.insertCell(),r=m.byId.get(id);
     if(!r){cell.textContent=m.failures?.[id] || "미측정";continue}
     const a=n("audio");a.controls=true;a.preload=id==="P13"?"metadata":"none";
     const mp3="listen/"+m.id+"/"+id+".mp3", wav="audio/"+m.id+"/"+id+".wav";
     for(const [url,type] of [[mp3,"audio/mpeg"],[wav,"audio/wav"]]){
      const source=n("source");source.src=url;source.type=type;a.append(source);
     }
     a.setAttribute("aria-label",id+" "+(blind?"음성 "+String.fromCharCode(65+i):m.name));
     a.onplay=()=>document.querySelectorAll("audio").forEach(other=>{if(other!==a)other.pause()});
     cell.append(a);
     const links=n("div",undefined,"filelinks");
     for(const [url,label] of [[mp3,"MP3 직접 듣기"],[wav,"원본 WAV"]]){
      const link=n("a",label);link.href=url;link.target="_blank";link.rel="noopener";
      link.setAttribute("aria-label",a.getAttribute("aria-label")+" "+label);links.append(link);
     }
     cell.append(links);
     if(!blind){const value=r.seconds[0];cell.append(n("p",(value?("생성 "+value.toFixed(2)+"초 · RTF "+(value/r.duration).toFixed(2)):"생성 미측정")+" · 길이 "+r.duration.toFixed(2)+"초","meta"))}
    }
   }
   wrapper.append(table);box.append(h,wrapper);
  }
 }
 group.onchange=render;
 el("blind").onclick=()=>{
  blind=!blind;
  if(blind){order=[...models];for(let i=order.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[order[i],order[j]]=[order[j],order[i]]}}
  el("blind").textContent=blind?"모델 이름 공개":"모델 가리기";el("blind").setAttribute("aria-pressed",String(blind));render();
 };
 render();
 if(/^#P\d\d$/.test(location.hash))el(location.hash.slice(1))?.scrollIntoView();
}catch(e){el("tables").textContent="샘플을 불러오지 못했습니다. 페이지를 새로고침해 주세요.";console.error(e)}
