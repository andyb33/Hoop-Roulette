// DOM-independent checks for animation sequencing and browser-local score history.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const nodes = new Map();
function node(key) {
  if (!nodes.has(key)) nodes.set(key, {textContent: '', disabled: false, children: [],
    classList: {add(){},remove(){},toggle(){}}, style:{setProperty(){}}, dataset:{},
    addEventListener(){}, append(...v){this.children.push(...v)}, replaceChildren(...v){this.children=v},
    showModal(){this.open=true;this.openCount=(this.openCount||0)+1}, close(){this.open=false}, querySelector(){return node(key+'child')},
    setAttribute(){}, closest(){return node(key+'slot')}});
  return nodes.get(key);
}
const storage = new Map();
const context = vm.createContext({console, Date, Math, Number, Set, JSON, Promise,
  document:{querySelector:node,querySelectorAll:()=>[],createElement:()=>({append(){}})},
  localStorage:{getItem:k=>storage.get(k),setItem:(k,v)=>storage.set(k,v)},
  window:{matchMedia:()=>({matches:false}),setInterval:()=>1,clearInterval(){},setTimeout:f=>f()},
  fetch:()=>new Promise(()=>{})});
vm.runInContext(fs.readFileSync('web/static/app.js','utf8'),context);
(async()=>{
  await vm.runInContext(`(async()=>{
    const completed={game_id:'dismiss-check',complete:true,total_score:200,upper_total:100,upper_target:120,bonus:0,categories:[],player:null,keeps_allowed:false,spins_used:0,spins_total:3,rerolls_left:0,turn:14,turns_total:14};
    render(completed);
    document.querySelector('#finished').close();
    render(completed);
    if(document.querySelector('#finished').open || document.querySelector('#finished').openCount!==1)throw Error('Dismissed results reopened');
    scores={recent:[],best:0};
    const calls=[];
    cycleReel = async (...args) => calls.push(args);
    await animateReels({spins_used:1,player:{pool:'normal',season:'1980-81',team:'BOS',name:'Larry Bird'},animation_choices:{season:['1980-81','2025-26'],team:['BOS'],player:['Larry Bird']}});
    if (calls.map(c=>c[0]).join()!=='season,team,player') throw Error('Reel order');
    if (calls.reduce((n,c)=>n+c[2],0)!==1100) throw Error('Unbounded duration');
    if (calls[2][4] || calls[2][3][0]!=='Larry Bird') throw Error('Wrong player choices');
    const g={game_id:'one',total_score:286,upper_total:120,bonus:35,categories:[],dev_jackpots:false};
    saveCompletedScore(g);saveCompletedScore(g);
    if(scores.recent.length!==1)throw Error('Duplicate completion');
    saveCompletedScore({...g,game_id:'two',total_score:300});
    if(scores.best!==300)throw Error('Personal best');
    saveCompletedScore({...g,game_id:'preview',dev_jackpots:true});
    if(scores.recent.length!==2)throw Error('Preview saved');
    for(let i=0;i<55;i++)saveCompletedScore({...g,game_id:'game'+i,total_score:100});
    if(scores.recent.length!==50 || scores.best!==300)throw Error('Retention/best');
    localStorage.setItem=()=>{throw Error('Unavailable storage')};
    saveCompletedScore({...g,game_id:'blocked'});
  })()`,context);
  assert.ok(storage.has('hoopreel.scores.v1'));
  console.log('Frontend animation and score-history checks passed');
})().catch(e=>{console.error(e);process.exitCode=1});
