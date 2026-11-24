import sys, os, json, asyncio, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import websockets
from practicum_helpers import netscape_to_playwright
from playwright.sync_api import sync_playwright

API = "https://practicum.yandex.ru/api"
COOKIE = "; ".join(
    l.split("\t")[5] + "=" + l.split("\t")[6].strip()
    for l in open(os.environ.get("PRACTICUM_COOKIES", "practicum_cookies.txt")) if l.strip() and not l.startswith("#")
)

async def check_ws(tid, files):
    url = f"wss://practicum.yandex.ru/ws-proxy/jrunner/task/{tid}/"
    try:
        async with websockets.connect(url, additional_headers={"Cookie": COOKIE, "Origin": "https://practicum.yandex.ru"}, open_timeout=20) as ws:
            await ws.send(json.dumps({"type": "CHECK", "data": {"files": files}}))
            logs = []
            async def recv():
                async for raw in ws:
                    m = json.loads(raw)
                    if m["type"] == "RESULT":
                        return m["data"]["status"], logs
                    if m["type"] == "LOG":
                        logs.append(str(m.get("data"))[:300])
            try:
                return await asyncio.wait_for(recv(), timeout=90)
            except asyncio.TimeoutError:
                return "timeout", logs
    except Exception as e:
        return f"ws_err {e}", []

async def run_tasks(pg):
    pending = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "answers", "pending_tasks.json")))
    sols = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "answers", "solutions.json")))
    done = {}
    for it in pending:
        if it["kind"] != "task":
            continue
        tid = it["task_id"]
        files = sols.get(tid)
        if not files:
            print("NOSOL", it["lesson"], tid, flush=True)
            continue
        st, logs = await check_ws(tid, files)
        print("TASK", it["lesson"][:40], "->", st, flush=True)
        if st != "ok":
            for l in logs[-4:]:
                print("   ", l[:250], flush=True)
        done[tid] = st
    return done

def run_quiz_coding(pg):
    pending = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "answers", "pending_tasks.json")))
    for it in pending:
        if it["kind"] != "quiz_coding":
            continue
        c = it.get("content") or {}
        panes = [{"id": p["id"], "name": p["name"], "content": p["content"], "language": p.get("language", "kotlin")} for p in c.get("panes", [])]
        body = {"block_id": it["block_id"], "lesson_id": it["lid"], "panes": panes}
        r = pg.request.post(f"{API}/theory_blocks/quiz_coding/check/", data=body, headers={"Content-Type": "application/json"})
        ok = None
        try:
            d = r.json()
            ok = d.get("user_answer", {}).get("test_result", {}).get("solved")
        except Exception:
            pass
        print("QC", it["lesson"][:40], r.status, "solved:", ok, flush=True)
        if ok is not True:
            print("    body:", r.text()[:300], flush=True)

def main():
    pending = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "answers", "pending_tasks.json")))
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(); ctx.add_cookies(netscape_to_playwright())
        pg = ctx.new_page()
        asyncio.run(run_tasks(pg))
        run_quiz_coding(pg)
        # re-verify lessons
        lids = sorted({it["lid"] for it in pending})
        for lid in lids:
            time.sleep(0.3)
            r = pg.request.post(f"{API}/lessons/{lid}/solve/", data={})
            d = pg.request.get(f"{API}/lessons/{lid}/")
            try:
                solved = d.json().get("solved")
            except Exception:
                solved = "?"
            print("LESSON", lid[:8], "solve:", r.status, "solved:", solved, flush=True)
        b.close()

main()
