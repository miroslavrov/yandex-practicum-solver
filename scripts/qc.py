import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from practicum_helpers import netscape_to_playwright
from playwright.sync_api import sync_playwright
API="https://practicum.yandex.ru/api"
p=json.load(open('pending_tasks.json'))
with sync_playwright() as pw:
    b=pw.chromium.launch(headless=True); ctx=b.new_context(); ctx.add_cookies(netscape_to_playwright()); pg=ctx.new_page()
    for it in p:
        if it['kind']!='quiz_coding': continue
        c=it.get('content') or {}
        panes=[{"id":x["id"],"name":x["name"],"content":x["content"],"language":x.get("language","kotlin")} for x in c.get('panes',[])]
        r=pg.request.post(f"{API}/theory_blocks/quiz_coding/check/",data={"block_id":it['block_id'],"lesson_id":it['lid'],"panes":panes},headers={"Content-Type":"application/json"})
        ok=None
        try: ok=r.json().get("user_answer",{}).get("test_result",{}).get("solved")
        except Exception: pass
        print("QC",it['lesson'][:38],r.status,"solved:",ok,flush=True)
        if ok is not True: print("   ",r.text()[:250],flush=True)
    # re-solve lessons
    for lid in sorted({i['lid'] for i in p}):
        r=pg.request.post(f"{API}/lessons/{lid}/solve/",data={})
        d=pg.request.get(f"{API}/lessons/{lid}/")
        try: solved=d.json().get('solved')
        except Exception: solved='?'
        print("LESSON",lid[:8],"solve:",r.status,"solved:",solved,flush=True)
    b.close()
