import sys, os, json, asyncio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import websockets
COOKIE = "; ".join(l.split("\t")[5] + "=" + l.split("\t")[6].strip() for l in open(os.environ.get("PRACTICUM_COOKIES", "practicum_cookies.txt")) if l.strip() and not l.startswith("#"))
async def main():
    sols=json.load(open("solutions.json"))
    tid="a6204ec4-2bda-48b0-9b4e-eb2c9f280603"
    url=f"wss://practicum.yandex.ru/ws-proxy/jrunner/task/{tid}/"
    async with websockets.connect(url, additional_headers={"Cookie":COOKIE,"Origin":"https://practicum.yandex.ru"}) as ws:
        await ws.send(json.dumps({"type":"CHECK","data":{"files":sols[tid]}}))
        async for raw in ws:
            m=json.loads(raw)
            if m["type"]=="LOG":
                print(m.get("data",{}).get("message","")[:200].rstrip())
            if m["type"]=="RESULT":
                print("RESULT", m["data"]["status"]); break
asyncio.run(main())
