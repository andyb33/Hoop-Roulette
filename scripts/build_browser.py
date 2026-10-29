"""Export the Python scoring truth and build the standalone responsive browser game."""
from pathlib import Path
import json,shutil,sys
from nba_roulette.data import load_records,load_goat_pools
from nba_roulette.web import BrowserGame,CATEGORY_LABELS,CATEGORY_META
from nba_roulette.scoring import Category,category_score,category_available
from nba_roulette.models import Lock
ROOT=Path(__file__).resolve().parents[1]
out=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'browser'/'dist'
out.mkdir(parents=True,exist_ok=True)
rows=load_records();goats=load_goat_pools();allrows=(*rows,*goats['award'],*goats['prehistoric'])
export=[]
for r in allrows:
 p=BrowserGame._player(r);p.update(entry_id=r.entry_id,game_player_id=r.game_player_id,scores={c.value:category_score(r,c) for c in Category},available={c.value:category_available(r,c) for c in Category});export.append(p)
meta=[dict(id=c.value,label=CATEGORY_LABELS[c],section=BrowserGame._section(c),**CATEGORY_META[c]) for c in Category]
data=dict(rows=export,categories=meta,normal_pool=dict(records=len(rows),seasons=len({r.season for r in rows}),first_season=min(r.season for r in rows),last_season=max(r.season for r in rows)))
(out/'pool.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
for name in ['index.html','styles.css','app.js','engine.js']:
 shutil.copy(ROOT/'browser'/name,out/name)
for name in ['brand-mark.svg','app-icon.png']:shutil.copy(ROOT/'web/static'/name,out/name)
# Fixtures exclude export scores: exact candidate sets from Python's original rule engine.
b=BrowserGame(rows,seed=42);fixtures=[]
for r in rows[::max(1,len(rows)//30)]:
 for keeps in [[],['season'],['team'],['player'],['season','team'],['season','player'],['team','player']]:
  fixtures.append(dict(entry_id=r.entry_id,keeps=keeps,expected=sorted(v.entry_id for v in b.game.roulette.valid_outcomes(r,[Lock(k) for k in keeps]))))
(ROOT/'browser'/'parity-fixtures.json').write_text(json.dumps(fixtures,separators=(',',':')))
print(f'Exported {len(rows)} normal + {len(allrows)-len(rows)} GOAT records to {out}')
