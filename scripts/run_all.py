import sys, os, json, time, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from practicum_helpers import netscape_to_playwright
from playwright.sync_api import sync_playwright

API = "https://practicum.yandex.ru/api"

def main():
    inv = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "answers", "inventory.json")))
    pending = []
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(locale="ru-RU")
        ctx.add_cookies(netscape_to_playwright())
        pg = ctx.new_page()
        def get(path):
            for _ in range(3):
                r = pg.request.get(f"{API}{path}")
                if r.status == 200:
                    try: return r.json()
                    except Exception: return None
                time.sleep(1)
            return None
        def post(path, body=None):
            for _ in range(3):
                try:
                    r = pg.request.post(f"{API}{path}", data=body or {}, headers={"Content-Type": "application/json"})
                    if r.status in (200, 201): return r.status
                except Exception:
                    pass
                time.sleep(1)
            return None
        def walk(n):
            yield n
            for c in n.get("nested") or []:
                yield from walk(c)
        n = 0
        for m in inv:
            for t in m["topics"]:
                for l in t["lessons"]:
                    if l.get("solved"):
                        continue
                    lid = l["id"]
                    try:
                        d = get(f"/lessons/{lid}/")
                        if not d or "theory" not in d:
                            print("SKIP", l["name"][:45], flush=True)
                            continue
                        if d.get("solved"):
                            l["solved"] = True
                            print("ALREADY", l["name"][:45], flush=True)
                            continue
                        post(f"/lessons/{lid}/checkin/")
                        for blk in walk(d["theory"]):
                            tp = blk["type"]
                            try:
                                if tp == "ActionButton":
                                    cid = blk["content"]["id"]
                                    post(f"/lessons/{lid}/quizzes/", {"user_answer": True, "markup": {"id": f"expander-{cid}", "type": "actionButton"}})
                                elif tp == "QuizSelect":
                                    c = blk["content"]
                                    sel = [o["id"] for o in c.get("options", []) if o.get("correct")]
                                    post(f"/lessons/{lid}/quizzes/", {"user_answer": sel, "markup": c})
                                elif tp == "QuizCoding":
                                    pending.append({"lesson": l["name"], "lid": lid, "kind": "quiz_coding",
                                                    "block_id": blk["id"], "content": blk["content"]})
                            except Exception as e:
                                print("  blk err", tp, str(e)[:80], flush=True)
                        post(f"/lessons/{lid}/solve/")
                        for tsk in d.get("tasks") or []:
                            pending.append({"lesson": l["name"], "lid": lid, "kind": "task", "task_id": tsk["id"]})
                        d2 = get(f"/lessons/{lid}/")
                        ok = d2 and d2.get("solved")
                        if ok:
                            l["solved"] = True
                            n += 1
                            print("SOLVED", l["name"][:45], flush=True)
                        else:
                            print("OPEN", l["name"][:45], "| tasks:", len(d.get("tasks") or []), flush=True)
                    except Exception:
                        print("FAIL", l["name"][:45], traceback.format_exc()[-200:], flush=True)
        json.dump(inv, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "answers", "inventory.json"), "w"), ensure_ascii=False, indent=1)
        json.dump(pending, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "answers", "pending_tasks.json"), "w"), ensure_ascii=False, indent=1)
        print(f"TOTAL solved this run: {n}, pending items: {len(pending)}", flush=True)
        b.close()

main()
