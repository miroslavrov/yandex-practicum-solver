import sys, os, json, asyncio, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from practicum_helpers import netscape_to_playwright
from playwright.sync_api import sync_playwright
import websockets

COOKIES = {}
for line in open(os.environ.get("PRACTICUM_COOKIES", "practicum_cookies.txt")):
    if line.startswith("#") or not line.strip():
        continue
    parts = line.strip().split("\t")
    if len(parts) >= 7 and ".yandex.ru" in parts[0]:
        COOKIES[parts[5]] = parts[6]
COOKIE_HDR = "; ".join(f"{k}={v}" for k, v in COOKIES.items())

API = "https://practicum.yandex.ru/api"

def check_task_ws(tid, files, timeout=180):
    """Send CHECK over jrunner ws, return (status, last_log)."""
    async def run():
        url = f"wss://practicum.yandex.ru/ws-proxy/jrunner/task/{tid}/"
        logs = []
        async with websockets.connect(url, additional_headers={"Cookie": COOKIE_HDR, "Origin": "https://practicum.yandex.ru"}) as ws:
            await ws.send(json.dumps({"type": "CHECK", "data": {"files": files}}))
            try:
                async for raw in ws:
                    m = json.loads(raw)
                    t = m.get("type")
                    if t == "LOG":
                        logs.append(m["data"]["message"])
                    elif t == "RESULT":
                        return m["data"]["status"], "\n".join(logs)
            except websockets.exceptions.ConnectionClosed:
                pass
        return "closed", "\n".join(logs)
    return asyncio.run(asyncio.wait_for(run(), timeout))


class Session:
    def __init__(self):
        self.pw = sync_playwright().start()
        self.b = self.pw.chromium.launch(headless=True)
        self.ctx = self.b.new_context(locale="ru-RU")
        self.ctx.add_cookies(netscape_to_playwright())
        self.pg = self.ctx.new_page()

    def get(self, path):
        r = self.pg.request.get(f"{API}{path}")
        try:
            return r.status, r.json()
        except Exception:
            return r.status, r.text()

    def post(self, path, body=None):
        kw = {"headers": {"Content-Type": "application/json"}}
        if body is not None:
            kw["data"] = body
        else:
            kw["data"] = "{}"
        r = self.pg.request.post(f"{API}{path}", **kw)
        return r.status, r.text()

    def close(self):
        self.b.close()
        self.pw.stop()


def lesson_blocks(d):
    out = []
    def walk(n):
        out.append(n)
        for c in n.get("nested") or []:
            walk(c)
    walk(d["theory"])
    return out


def handle_lesson_meta(pg_req, lid, d):
    """Do checkin + expander clicks + quiz selects. Returns list of unsolved tasks."""
    post = lambda path, body=None: pg_req(path, body)
    post(f"/lessons/{lid}/checkin/")
    for n in lesson_blocks(d):
        t = n["type"]
        if t == "ActionButton":
            cid = n["content"]["id"]
            post(f"/lessons/{lid}/quizzes/", {"user_answer": True, "markup": {"id": f"expander-{cid}", "type": "actionButton"}})
        elif t == "QuizSelect":
            c = n["content"]
            sel = [o["id"] for o in c["options"] if o.get("correct")]
            post(f"/lessons/{lid}/quizzes/", {"user_answer": sel, "markup": c})
    return d.get("tasks") or []


if __name__ == "__main__":
    inv = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "answers", "inventory.json")))
    s = Session()
    def req(path, body=None):
        return s.post(path, body)
    tasks_all = []
    n_done = n_skip = 0
    for m in inv:
        for t in m["topics"]:
            for l in t["lessons"]:
                if l.get("solved"):
                    continue
                lid = l["id"]
                st, d = s.get(f"/lessons/{lid}/")
                if st != 200 or not isinstance(d, dict) or "theory" not in d:
                    print("SKIP", lid, l["name"][:40], st)
                    n_skip += 1
                    continue
                tasks = handle_lesson_meta(req, lid, d)
                s.post(f"/lessons/{lid}/solve/")
                st, d2 = s.get(f"/lessons/{lid}/")
                solved = d2.get("solved")
                if solved:
                    n_done += 1
                    print("SOLVED-INSTANT", l["name"][:50])
                else:
                    print("NEEDS-TASKS", l["name"][:50], "| tasks:", len(tasks))
                    for tk in tasks:
                        tasks_all.append({"lesson": l["name"], "lid": lid, "task_id": tk["id"]})
    json.dump(tasks_all, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "answers", "pending_tasks.json"), "w"), indent=1)
    print(f"done instant: {n_done}, skipped: {n_skip}, tasks pending: {len(tasks_all)}")
    s.close()
