import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from practicum_helpers import netscape_to_playwright
from playwright.sync_api import sync_playwright
API="https://practicum.yandex.ru/api"
p=json.load(open('pending_tasks.json'))
d=json.load(open('task_details.json'))
FIX={
"1fe30ece-58fa-4bed-aac0-965d0d30a409":"""enum class AuthorizationType {
    LOGIN,
    PHONE_NUMBER,
    EMAIL
}

// Метод для обработки того или иного способа авторизации
fun handleAuthorization(type: AuthorizationType) {
    when (type) {
        AuthorizationType.LOGIN -> println("login")
        AuthorizationType.PHONE_NUMBER -> println("phone")
        AuthorizationType.EMAIL -> println("email")
    }
}

fun main()  {
	// Этот метод можно использовать с константами, как и задумано
    handleAuthorization(AuthorizationType.EMAIL)
    handleAuthorization(AuthorizationType.LOGIN)
}
""",
"39677ddf-f1e1-4c64-82c4-8d3999a3d4f2":"""class RecyclerViewAdapter {

    val dataList = listOf("Анна", "Василий")
    inner class ViewHolder() {
        fun resendAllData(): List<String> {
       		return dataList
   		}
    }
}
""",
"aec7ac2b-3a99-447c-98be-fece60ff81f8":"""class Cat(val name: String)

fun downloadCat(
    onSuccess: (Cat) -> Unit,
    onError: () -> Unit
) {
    // загружает фотографии котиков из интернета
}

fun main(){}
""",
"11d46a6e-e0d5-4012-b695-a082ffa378f4":"""class Cat(val name: String)

fun downloadCat(
    onSuccess: (Cat) -> Unit,
    onError: (String) -> Unit
) {
    // загружает фотографии котиков из интернета
}
""",
"617370ae-f8f0-4ffd-b4d4-991aa51663c8":"""data class HoneyBear(
    val name: String,
    val size: Int,
    val color: String,
)

fun interface CanEat {
    fun eat(honeyBear: HoneyBear)
}

fun main() {
    val (name, size, color) = HoneyBear("Задира", 5, "Чёрный")
    val canEatLambda = CanEat { (name, size, color) ->
        println("Медоед $name имеет размер $size и цвет $color")
    }

    println("Медоед $name имеет размер $size и цвет $color")
    canEatLambda.eat(HoneyBear("Злюка", 12, "Рыжий"))
}
""",
}
with sync_playwright() as pw:
    b=pw.chromium.launch(headless=True); ctx=b.new_context(); ctx.add_cookies(netscape_to_playwright()); pg=ctx.new_page()
    for it in p:
        if it['kind']!='quiz_coding' or (it.get('content') or {}).get('id') not in FIX: continue
        c=it.get('content') or {}
        panes=[{"id":x["id"],"name":x["name"],"content":FIX[c.get('id')],"language":x.get("language","kotlin")} for x in c.get('panes',[])]
        for att in range(3):
            try:
                r=pg.request.post(f"{API}/theory_blocks/quiz_coding/check/",data={"block_id":it['block_id'],"lesson_id":it['lid'],"panes":panes},headers={"Content-Type":"application/json"},timeout=120000)
            except Exception as e:
                print("  post err",str(e)[:80],flush=True); continue
            ok=None
            try: ok=r.json().get("user_answer",{}).get("test_result",{}).get("solved")
            except Exception: pass
            print("QC",it['block_id'][:8],r.status,"solved:",ok,flush=True)
            if ok is True: break
            txt=r.text()
            print("   ",txt[-400:],flush=True)
    b.close()
