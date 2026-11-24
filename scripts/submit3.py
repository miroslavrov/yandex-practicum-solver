import sys, os, json, asyncio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import websockets
COOKIE = "; ".join(l.split("\t")[5] + "=" + l.split("\t")[6].strip() for l in open(os.environ.get("PRACTICUM_COOKIES", "practicum_cookies.txt")) if l.strip() and not l.startswith("#"))
async def check(tid, files):
    url = f"wss://practicum.yandex.ru/ws-proxy/jrunner/task/{tid}/"
    async with websockets.connect(url, additional_headers={"Cookie": COOKIE, "Origin": "https://practicum.yandex.ru"}, open_timeout=20) as ws:
        await ws.send(json.dumps({"type":"CHECK","data":{"files":files}}))
        logs=[]
        async for raw in ws:
            m=json.loads(raw)
            if m["type"]=="RESULT": return m["data"]["status"], logs
            if m["type"]=="LOG": logs.append(str(m.get("data"))[:250])
async def main():
    sols=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "answers", "solutions.json")))
    tid="3e455486-53ff-4bab-afb2-d0de9630ee41"
    for att in range(4):
        try:
            st,logs=await asyncio.wait_for(check(tid,sols[tid]),timeout=180)
        except Exception as e:
            st=f"err {e}";logs=[]
        print(tid[:8],st,flush=True)
        if st=="ok": break
        for l in logs[-4:]: print("  ",l[:250])
        await asyncio.sleep(3)
asyncio.run(main())
