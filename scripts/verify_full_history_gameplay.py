import sys,json,random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from nba_roulette.data import load_records,load_goat_pools
from nba_roulette.web import BrowserGame
from nba_roulette.models import Lock
from nba_roulette.scoring import Category
rows=load_records();goats=load_goat_pools();rng=random.Random(20261014)
masks=[[],['season'],['team'],['player'],['season','team'],['season','player'],['team','player']]
normal=set();all_seen=set();scores=[];spins=0
for seed in range(100):
 b=BrowserGame(rows,seed=seed,goat_pools=goats)
 for category in Category:
  for i in range(1+rng.randrange(3)):
   before=b.game.turn.current if b.game.turn else None
   keeps=rng.choice(masks) if before and before.pool=='normal' else []
   candidates=b.game.roulette.valid_outcomes(before,tuple(Lock(k) for k in keeps)) if before and before.pool=='normal' else b.game.roulette.records
   state=b.spin(keeps);spins+=1;after=b.game.turn.current;all_seen.add(after.season)
   assert after.player_id not in b.game.drafted_player_ids
   if after.pool=='normal':
    normal.add(after.season);assert after in rows
   else:candidates=tuple(r for r in goats[after.pool] if r.player_id not in b.game.drafted_player_ids)
   assert state['animation_choices']==dict(season=sorted({r.season for r in candidates}),team=sorted({r.team for r in candidates if r.season==after.season}),player=sorted({r.player for r in candidates if r.season==after.season and r.team==after.team}))
  b.score(category.value)
 assert b.game.is_complete and len(b.game.drafted_player_ids)==14
 scores.append(b.game.total_score)
 if seed%10==9:print('complete games',seed+1,flush=True)
assert normal=={r.season for r in rows}
out=dict(passed=True,records=len(rows),seasons=len(normal),team_seasons=len({(r.season,r.team) for r in rows}),complete_games=100,spins_checked=spins,normal_seasons_seen=sorted(normal),all_seasons_seen=sorted(all_seen),jackpot_only=sorted(all_seen-normal),score_min=min(scores),score_max=max(scores),goat_pools={k:len(v) for k,v in goats.items()})
Path('analysis/full_history_1973_2026_smoke.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
