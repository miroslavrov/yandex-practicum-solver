import sys, os, json, asyncio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import websockets

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
                        return m["data"]["status"]
                    if m["type"] == "LOG":
                        logs.append(str(m.get("data"))[:200])
            try:
                return await asyncio.wait_for(recv(), timeout=120), logs
            except asyncio.TimeoutError:
                return "timeout", logs
    except Exception as e:
        return f"ws_err {e}", []

async def main():
    pending = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "answers", "pending_tasks.json")))
    sols = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "answers", "solutions.json")))
    jobs = [(it["task_id"], it["lesson"]) for it in pending if it["kind"] == "task" and it["task_id"] in sols]
    results = await asyncio.gather(*[check_ws(tid, sols[tid]) for tid, _ in jobs])
    for (tid, lesson), (st, logs) in zip(jobs, results):
        print("TASK", lesson[:40], "->", st, flush=True)
        if st != "ok":
            for l in logs[-3:]:
                print("   ", l[:200], flush=True)

asyncio.run(main())
