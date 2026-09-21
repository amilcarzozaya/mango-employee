from pathlib import Path
import json,sqlite3,uuid,datetime
from .state import create_run,transition,get_run
from .observability import provenance,metric
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def base(ep): p=Path(ep); return p.parent if p.is_file() else p
def connect(ep):
 p=base(ep)/'state/teams.db';p.parent.mkdir(parents=True,exist_ok=True);c=sqlite3.connect(p);c.row_factory=sqlite3.Row
 c.executescript("""CREATE TABLE IF NOT EXISTS teams(id TEXT PRIMARY KEY,name TEXT,status TEXT,owner TEXT,purpose TEXT,created_at TEXT,updated_at TEXT); CREATE TABLE IF NOT EXISTS team_members(team_id TEXT,employee_id TEXT,role TEXT,authority TEXT,can_delegate INTEGER,memory_scopes TEXT,created_at TEXT,PRIMARY KEY(team_id,employee_id)); CREATE TABLE IF NOT EXISTS handoffs(id TEXT PRIMARY KEY,team_id TEXT,from_employee TEXT,to_employee TEXT,parent_run_id TEXT,child_run_id TEXT,skill_id TEXT,task TEXT,deliverable TEXT,acceptance_criteria TEXT,context_refs TEXT,memory_scopes TEXT,status TEXT,reason TEXT,created_at TEXT,accepted_at TEXT,completed_at TEXT,updated_at TEXT); CREATE TABLE IF NOT EXISTS handoff_events(id INTEGER PRIMARY KEY AUTOINCREMENT,handoff_id TEXT,event TEXT,actor TEXT,detail TEXT,created_at TEXT);""");c.commit();return c
def create_team(ep,name,owner,purpose='',team_id=None):
 tid=team_id or 'team_'+uuid.uuid4().hex[:12];t=now();c=connect(ep);c.execute('INSERT INTO teams VALUES(?,?,?,?,?,?,?)',(tid,name,'active',owner,purpose,t,t));c.commit();c.close();return tid
def add_member(ep,tid,eid,role,authority='member',can_delegate=False,memory_scopes=None):
 c=connect(ep)
 if not c.execute('SELECT 1 FROM teams WHERE id=?',(tid,)).fetchone(): c.close();raise ValueError('Team not found')
 c.execute('INSERT OR REPLACE INTO team_members VALUES(?,?,?,?,?,?,?)',(tid,eid,role,authority,int(can_delegate),json.dumps(memory_scopes or []),now()));c.commit();c.close()
def member(ep,tid,eid):
 c=connect(ep);r=c.execute('SELECT * FROM team_members WHERE team_id=? AND employee_id=?',(tid,eid)).fetchone();c.close();return dict(r) if r else None
def team_status(ep,tid):
 c=connect(ep);t=c.execute('SELECT * FROM teams WHERE id=?',(tid,)).fetchone();ms=[dict(x) for x in c.execute('SELECT * FROM team_members WHERE team_id=?',(tid,))];hs=[dict(x) for x in c.execute('SELECT * FROM handoffs WHERE team_id=? ORDER BY created_at DESC',(tid,))];c.close();return {'team':dict(t) if t else None,'members':ms,'handoffs':hs}
def _cycle(ep,tid,a,b):
 c=connect(ep);rows=c.execute("SELECT from_employee,to_employee FROM handoffs WHERE team_id=? AND status IN ('proposed','running')",(tid,)).fetchall();c.close();g={}
 for x,y in rows:g.setdefault(x,set()).add(y)
 g.setdefault(a,set()).add(b);stack=[b];seen=set()
 while stack:
  n=stack.pop()
  if n==a:return True
  if n not in seen:seen.add(n);stack.extend(g.get(n,()))
 return False
def delegate(ep,tid,src,dst,skill,task,deliverable,criteria,parent_run_id=None,context_refs=None,memory_scopes=None):
 sm,dm=member(ep,tid,src),member(ep,tid,dst)
 if not sm or not (sm['can_delegate'] or sm['authority'] in ('lead','manager','owner')):raise PermissionError('delegator_not_authorized')
 if not dm:raise PermissionError('recipient_not_team_member')
 if src==dst:raise ValueError('self_delegation_forbidden')
 if _cycle(ep,tid,src,dst):raise ValueError('circular_delegation_forbidden')
 if not set(memory_scopes or []).issubset(set(json.loads(dm['memory_scopes']))):raise PermissionError('memory_scope_escalation')
 hid='handoff_'+uuid.uuid4().hex[:12];t=now();c=connect(ep);c.execute('INSERT INTO handoffs VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(hid,tid,src,dst,parent_run_id,None,skill,task,deliverable,json.dumps(criteria or []),json.dumps(context_refs or []),json.dumps(memory_scopes or []),'proposed',None,t,None,None,t));c.execute('INSERT INTO handoff_events(handoff_id,event,actor,detail,created_at) VALUES(?,?,?,?,?)',(hid,'proposed',src,None,t));c.commit();c.close();return hid
def get_handoff(ep,hid):
 c=connect(ep);r=c.execute('SELECT * FROM handoffs WHERE id=?',(hid,)).fetchone();c.close();return dict(r) if r else None
def accept(ep,hid,actor):
 h=get_handoff(ep,hid)
 if actor!=h['to_employee']:raise PermissionError('only_recipient_can_accept')
 if h['status']!='proposed':raise ValueError('handoff_not_proposed')
 child=create_run(ep,h['to_employee'],h['skill_id'],h['task'],parent_run_id=h['parent_run_id']);transition(ep,child,'running');t=now();c=connect(ep);c.execute("UPDATE handoffs SET status='running',child_run_id=?,accepted_at=?,updated_at=? WHERE id=?",(child,t,t,hid));c.commit();c.close();provenance(ep,child,'handoff',hid,'received_from',detail={'from':h['from_employee'],'team_id':h['team_id']});metric(ep,child,'handoffs_received',1,'count');return child
def return_handoff(ep,hid,actor,reason):
 h=get_handoff(ep,hid)
 if actor!=h['to_employee']:raise PermissionError('only_recipient_can_return')
 c=connect(ep);c.execute("UPDATE handoffs SET status='returned',reason=?,updated_at=? WHERE id=?",(reason,now(),hid));c.commit();c.close()
def complete(ep,hid,actor,result):
 h=get_handoff(ep,hid)
 if actor!=h['to_employee']:raise PermissionError('only_recipient_can_complete')
 if h['status']!='running' or get_run(ep,h['child_run_id'])['status']!='completed':raise ValueError('child_run_must_be_completed')
 c=connect(ep);t=now();c.execute("UPDATE handoffs SET status='completed',completed_at=?,updated_at=? WHERE id=?",(t,t,hid));c.commit();c.close();return get_handoff(ep,hid)
def handoff_contract(ep,hid):
 h=get_handoff(ep,hid);return {'handoff_id':hid,'team_id':h['team_id'],'from':h['from_employee'],'to':h['to_employee'],'skill':h['skill_id'],'task':h['task'],'deliverable':h['deliverable'],'acceptance_criteria':json.loads(h['acceptance_criteria']),'context_refs':json.loads(h['context_refs']),'memory_scopes':json.loads(h['memory_scopes']),'authority_rule':'Delegation never expands authority.'}
