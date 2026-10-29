const assert=require('node:assert/strict');const fs=require('node:fs');const Engine=require('./engine.js');
const data=JSON.parse(fs.readFileSync(process.argv[2]||'browser/dist/pool.json'));const fixtures=JSON.parse(fs.readFileSync('browser/parity-fixtures.json'));
const e=new Engine(data);const byId=new Map(data.rows.map(r=>[r.entry_id,r]));
for(const f of fixtures)assert.deepEqual(e.outcomes(byId.get(f.entry_id),f.keeps).map(r=>r.entry_id).sort(),f.expected);
let seed=718;const rng=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};
let seen=new Set(),bonus=0;
for(let game=0;game<100;game++){
 const e=new Engine(data,rng);const picks=new Set();
 for(let turn=0;turn<14;turn++){
  let state=e.spin();
  for(let spin=0;spin<2;spin++){
   const keeps=[[],['season'],['team'],['player'],['season','team'],['team','player'],['season','player']][Math.floor(rng()*7)];const legal=e.current.pool==='normal'?keeps:[];const prev=e.current;const valid=prev.pool==='normal'?e.outcomes(prev,legal):null;
   state=e.spin(legal);if(state.player.pool==='normal'&&valid)assert(valid.some(r=>r.entry_id===state.player.entry_id));seen.add(state.player.season);
  }
  assert(!picks.has(state.player.player_id));picks.add(state.player.player_id);const category=state.categories.find(c=>!c.used);const expected=e.current.scores[category.id];state=e.score(category.id);assert.equal(state.categories.find(c=>c.id===category.id).score,expected);
  const restored=new Engine(data,rng);restored.restore(JSON.parse(JSON.stringify(e.snapshot())));assert.equal(restored.state().total_score,state.total_score);
 }
 const result=e.state();assert(result.complete);assert.equal(picks.size,14);assert.equal(result.total_score,result.categories.reduce((s,c)=>s+c.score,result.bonus));if(result.bonus)bonus++;
 assert.throws(()=>e.spin(),/complete/);
}
// GOAT activation and identity exclusion, without exposing a force-pool control in the UI.
let draws=[0,0,0];const goat=new Engine(data,()=>draws.length?draws.shift():.5);assert.equal(goat.spin().player.pool,'award');assert.throws(()=>goat.spin(['team']),/cannot be kept/);const id=goat.current.player_id;goat.score('major_award');assert(!goat.pool().some(r=>r.player_id===id));
console.log(`Passed ${fixtures.length} exact Python legal-outcome fixtures, 100 complete games, save restore, GOAT and draft checks (${seen.size} seasons).`);
