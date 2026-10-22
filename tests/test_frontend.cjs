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
  document:{body:node('body'),querySelector:node,querySelectorAll:()=>[],createElement:()=>({append(){}})},
  localStorage:{getItem:k=>storage.get(k),setItem:(k,v)=>storage.set(k,v)},
  window:{matchMedia:()=>({matches:false}),setInterval:()=>1,clearInterval(){},setTimeout:f=>f(),clearTimeout(){}},
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
    // Skip at each reel boundary, including repeated clicks and jackpot reveals.
    const originalTimers = {...window};
    for (const pool of ['normal','award']) for (let target=0;target<3;target++) {
      const timers = new Map();
      const intervals = new Set();
      let timerId=0;
      window.setTimeout=f=>{timers.set(++timerId,f);return timerId};
      window.clearTimeout=id=>timers.delete(id);
      window.setInterval=()=>{intervals.add(++timerId);return timerId};
      window.clearInterval=id=>intervals.delete(id);
      state.animation={skipped:false,finish:null};
      const animation = animateReels({spins_used:1,player:{pool,season:'1980-81',team:'BOS',name:'Larry Bird'}});
      for (let reel=0;reel<target;reel++) {
        const finish=state.animation.finish;
        if (!finish) throw Error('Missing active reel');
        finish();
        await Promise.resolve();
      }
      skipAnimation();skipAnimation();
      await animation;
      if (document.querySelector('#season-value').textContent!=='1980-81' ||
          document.querySelector('#team-value').textContent!=='BOS' ||
          document.querySelector('#player-value').textContent!=='Larry Bird') throw Error('Skip lost result');
      if(intervals.size || state.animation.finish)throw Error('Skip left active reel');
      // Any remaining landing timers must not overwrite the revealed result.
      for(const callback of timers.values())callback();
      if(document.querySelector('#player-value').textContent!=='Larry Bird')throw Error('Late timer overwrote result');
    }
    Object.assign(window, originalTimers);
    state.animation=null;
    skipAnimation(); // Safe outside a spin.
    setInstantSpins(true);
    if(!readInstantSpins() || !document.querySelector('#instant-spins').checked)throw Error('Preference not saved');
    const priorTimeout=window.setTimeout;
    window.setTimeout=()=>{throw Error('Instant spin scheduled animation')};
    await animateReels({spins_used:1,player:{pool:'award',season:'1980-81',team:'BOS',name:'Larry Bird'}});
    window.setTimeout=priorTimeout;
    setInstantSpins(false);
    if(readInstantSpins())throw Error('Preference not cleared');
    const active={...completed,game_id:'active',complete:false,spins_used:1,rerolls_left:2,keeps_allowed:true};
    render({...active,upper_total:119});
    if(document.querySelector('#bonus-remaining').textContent!=='1 point to bonus')throw Error('Bonus singular');
    render({...active,upper_total:120});
    if(document.querySelector('#bonus-remaining').textContent!=='Upper bonus earned!')throw Error('Bonus earned');
    render(active);
    state.keeps.add('season');state.keeps.add('team');
    render(active);
    if(document.querySelector('#clear-keeps').disabled)throw Error('Clear disabled with keeps');
    clearKeeps();
    if(state.keeps.size || !document.querySelector('#clear-keeps').disabled)throw Error('Keeps not cleared');
    state.keeps.add('season');setBusy(true);clearKeeps();
    if(!state.keeps.size)throw Error('Cleared during busy state');
    setBusy(false);state.keeps.clear();
    let requests=0;
    const originalRequest=request;
    request=async()=>{requests++;return {...active,spins_used:0,categories:[]}};
    requestNewGame();
    if(requests || !document.querySelector('#restart-confirm').open)throw Error('Restart skipped warning');
    document.querySelector('#restart-confirm').close();
    if(state.game.game_id!=='active')throw Error('Cancel changed game');
    await newGame();
    if(requests!==1 || document.querySelector('#restart-confirm').open)throw Error('Confirmed restart failed');
    state.game={...active,spins_used:0,categories:[{used:true}]};
    requestNewGame();
    if(requests!==1 || !document.querySelector('#restart-confirm').open)throw Error('Scored turn bypassed warning');
    document.querySelector('#restart-confirm').close();
    state.game={...active,spins_used:0};
    await requestNewGame();
    if(requests!==2)throw Error('Pristine game warned');
    state.game=completed;
    await requestNewGame();
    if(requests!==3)throw Error('Completed game warned');
    request=originalRequest;
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
    setInstantSpins(true);
    if(!instantSpins)throw Error('Preference failed without storage');
    localStorage.getItem=()=>{throw Error('Unavailable storage')};
    if(readInstantSpins())throw Error('Blocked storage default');
    saveCompletedScore({...g,game_id:'blocked'});
  })()`,context);
  assert.ok(storage.has('hoopreel.scores.v1'));
  console.log('Frontend animation and score-history checks passed');
})().catch(e=>{console.error(e);process.exitCode=1});
