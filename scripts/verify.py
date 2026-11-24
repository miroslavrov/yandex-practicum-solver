import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from practicum_helpers import netscape_to_playwright
from playwright.sync_api import sync_playwright
API="https://practicum.yandex.ru/api"
inv=json.load(open('inventory.json'))
with sync_playwright() as pw:
    b=pw.chromium.launch(headless=True); ctx=b.new_context(); ctx.add_cookies(netscape_to_playwright()); pg=ctx.new_page()
    r=pg.request.get(f"{API}/subscriptions/" + os.environ.get("PRACTICUM_SUBSCRIPTION", "<subscription_id>") + "/finished_lessons_count/")
    print("finished:",r.text(),flush=True)
    unsolved=[]
    for m in inv:
        for t in m['topics']:
            for l in t['lessons']:
                try:
                    d=pg.request.get(f"{API}/lessons/{l['id']}/").json()
                    sv=d.get('solved')
                    if sv: l['solved']=True
                    else:
                        l['solved']=False
                        unsolved.append((l['id'],l['name'],len(d.get('tasks') or [])))
                except Exception as e:
                    unsolved.append((l['id'],l['name'],'ERR '+str(e)[:50]))
        print("module done",flush=True)
    json.dump(inv,open('inventory.json','w'),ensure_ascii=False,indent=1)
    print("UNSOLVED:",len(unsolved),flush=True)
    for u in unsolved: print(" ",u,flush=True)
    b.close()
