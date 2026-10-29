/* Browser game state. Scoring and display data are exported by the Python engine. */
(function(root){
class HoopEngine {
  constructor(data, random=Math.random) { this.data=data; this.random=random; this.reset(); }
  pick(rows) { if(!rows.length) throw Error('No eligible outcomes remain'); return rows[Math.floor(this.random()*rows.length)]; }
  reset() { this.id=(globalThis.crypto?.randomUUID?.() || `game-${Date.now()}-${Math.random()}`);this.card={};this.current=null;this.spins=0;this.drafted=new Set();this.events=[];this.started=new Date().toISOString();return this.state(); }
  pool() {return this.data.rows.filter(r=>r.pool==='normal'&&!this.drafted.has(r.player_id));}
  outcomes(current,keeps) {
    const fields={season:'season',team:'team',player:'player_id'};
    const matching=this.pool().filter(r=>keeps.every(k=>r[fields[k]]===current[fields[k]]));
    const strict=matching.filter(r=>Object.keys(fields).every(k=>keeps.includes(k)||r[fields[k]]!==current[fields[k]]));
    if(strict.length)return strict;
    const changed=matching.filter(r=>r.entry_id!==current.entry_id);return changed.length?changed:matching;
  }
  hierarchical(rows) {const season=this.pick([...new Set(rows.map(r=>r.season))]);const seasonRows=rows.filter(r=>r.season===season);const team=this.pick([...new Set(seasonRows.map(r=>r.team))]);return this.pick(seasonRows.filter(r=>r.team===team));}
  spin(keeps=[]) {
    if(Object.keys(this.card).length===14)throw Error('The game is complete');
    if(this.current&&this.spins>=3)throw Error('No rerolls remain');
    if(keeps.some(k=>!['season','team','player'].includes(k)))throw Error('Unknown Keep');
    keeps=[...new Set(keeps)];if(keeps.length===3)throw Error('Release at least one reel');
    if(!this.current)keeps=[];
    if(this.current?.pool!=='normal'&&keeps.length)throw Error('GOAT results cannot be kept');
    let next,choices;
    if(!keeps.length&&Math.floor(this.random()*1296)===0){const pool=this.pick(['award','prehistoric']);const rows=this.data.rows.filter(r=>r.pool===pool&&!this.drafted.has(r.player_id));if(rows.length){next=this.pick(rows);choices=rows;}}
    if(!next){
      const rows=this.pool();const current=this.current?.pool==='normal'?this.current:null;
      choices=current?this.outcomes(current,keeps):rows;
      if(current&&!keeps.length){
        // Preserve Python's rejection-sampling distribution over the original hierarchy.
        const allowed=new Set(choices.map(r=>r.entry_id));
        do{next=this.hierarchical(rows);}while(!allowed.has(next.entry_id));
      }else next=this.hierarchical(choices);
    }
    this.current=next;this.spins++;this.events.push({event:'spin',turn:Object.keys(this.card).length+1,spin:this.spins,keeps,result:this.identity(next)});
    return {...this.state(),animation_choices:{season:[...new Set(choices.map(r=>r.season))].sort(),team:[...new Set(choices.filter(r=>r.season===next.season).map(r=>r.team))].sort(),player:[...new Set(choices.filter(r=>r.season===next.season&&r.team===next.team).map(r=>r.name))].sort()}};
  }
  identity(r){return {season:r.season,team:r.team,player_id:r.player_id,player:r.name,pool:r.pool,game_player_id:r.game_player_id,entry_id:r.entry_id};}
  score(id){if(!this.current)throw Error('Spin before scoring');if(this.card[id])throw Error('Category already used');if(!this.data.categories.some(c=>c.id===id))throw Error('Unknown category');const r=this.current;this.card[id]={score:r.scores[id],record:r};this.events.push({event:'score',turn:Object.keys(this.card).length,category:id,score:r.scores[id],spins_used:this.spins,result:this.identity(r)});this.drafted.add(r.player_id);this.current=null;this.spins=0;return this.state();}
  state(){const n=Object.keys(this.card).length;const upperIds=['points','rebounds','assists','steals','blocks'];const upper=upperIds.reduce((s,k)=>s+(this.card[k]?.score||0),0);const bonus=upperIds.every(k=>this.card[k])&&upper>=120?35:0;const categories=this.data.categories.map(c=>({...c,used:!!this.card[c.id],score:this.card[c.id]?.score??null,preview:this.current&&!this.card[c.id]?this.current.scores[c.id]:null,selection:this.card[c.id]?{player:this.card[c.id].record.name,season:this.card[c.id].record.season,team:this.card[c.id].record.team}:null,unavailable:!!this.current&&!this.current.available[c.id]}));let preview=[];
    if(this.current?.pool==='normal'&&this.spins<3)preview=this.outcomes(this.current,['team','player']).sort((a,b)=>a.season.localeCompare(b.season)).map(r=>({season:r.season,same_season:r.season===this.current.season,categories:categories.filter(c=>!c.used).map(c=>({id:c.id,label:c.label,section:c.section,score:r.scores[c.id],available:r.available[c.id]}))}));
    return {game_id:this.id,turn:Math.min(14,n+1),turns_total:14,complete:n===14,total_score:Object.values(this.card).reduce((s,c)=>s+c.score,bonus),upper_total:upper,upper_target:120,bonus,playtest:null,dev_jackpots:false,goat_enabled:true,normal_pool:this.data.normal_pool,keeps_allowed:this.current?.pool==='normal',spins_used:this.spins,spins_total:3,rerolls_left:this.current?3-this.spins:0,player:this.current,categories,reroll_preview:preview};}
  snapshot(){return {id:this.id,card:Object.fromEntries(Object.entries(this.card).map(([k,v])=>[k,v.record.entry_id])),current:this.current?.entry_id||null,spins:this.spins,events:this.events,started:this.started};}
  restore(saved){const byId=new Map(this.data.rows.map(r=>[r.entry_id,r]));const card={};for(const [k,id] of Object.entries(saved.card||{})){if(!this.data.categories.some(c=>c.id===k)||!byId.has(id))throw Error('Invalid saved game');card[k]={record:byId.get(id),score:byId.get(id).scores[k]};}if(saved.current&&!byId.has(saved.current))throw Error('Invalid saved player');if(!Number.isInteger(saved.spins)||saved.spins<0||saved.spins>3)throw Error('Invalid spin count');this.card=card;this.current=byId.get(saved.current)||null;this.spins=saved.spins;this.id=saved.id;this.events=Array.isArray(saved.events)?saved.events:[];this.started=saved.started;this.drafted=new Set(Object.values(card).map(v=>v.record.player_id));if(this.current&&this.drafted.has(this.current.player_id))throw Error('Drafted player in current result');return this.state();}
  log(){return {game_id:this.id,started_at:this.started,completed_at:new Date().toISOString(),final_score:this.state().total_score,version:'web-0.16.0',events:this.events};}
}
if(typeof module!=='undefined')module.exports=HoopEngine;else root.HoopEngine=HoopEngine;
})(globalThis);
