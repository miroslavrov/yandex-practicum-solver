# Банк ответов — WS-задачи курса (jrunner)

`solutions.json` — task_id → `files[]` с финальными ПРИНЯТЫМИ сервером решениями (проверены на этом прогоне). Ниже — что за задача и на чём спотыкается препроцессор. Сабмит: `{"type":"CHECK","data":{"files":[...]}}` на `wss://practicum.yandex.ru/ws-proxy/jrunner/task/<task_id>/` с куками и `Origin: https://practicum.yandex.ru`.

| task_id | Урок | Задача | Грабли препроцессора |
|---|---|---|---|
| f9c74e04-4227-4c50-b94a-9651ac79c966 | Цикл while | Степени двойки ≤ max | без граблей |
| 4d7f0258-47b3-4bb4-abef-298117b7c01b | Массивы | Максимум температур | без граблей |
| f171a4b6-456d-4e66-b2a3-bc793758ef56 | Коллекции | Корзина товаров, цены Random | обязателен **вложенный `for`** и добавление через **`.add()`** (не `+=`) |
| c81b3ca2-bffe-47f9-956e-f970ff7f26ef | Коллекции. Функции | Таблица умножения 1..9 | script-mode: **только top-level код, `fun main` ЗАПРЕЩЁН**; итерация через **`forEach`** |
| 2d28153b-404b-40da-89fe-961fe6bf87a6 | Enum | `enum class Week` | без граблей |
| 379cd50d-e03f-4b11-925e-068a4f8b2be1 | Наследование | Vocalist/Guitarist/Drummer : RockMusician | без граблей |
| 17d9b34b-120d-469c-bba3-3f4eac8dd5f4 | Sealed/интерфейсы | sealed NetworkError + ErrorHandler + `Network.onNetworkError` | точные имена классов/методов из ТЗ |
| fc33067c-2fb9-4230-ab04-1303906820d3 | Singleton/Object | PiggyBank + Money с приватным ctor | companion-константы с ТОЧНЫМИ именами: `coins_10`, `coins_50`, `coins_100`, `bill_50`, `bill_100`, `bill_500`, `bill_1000` |
| 6b027798-1c46-41a7-9a69-e767654d012f | Анонимные классы | DiceRoller: object : Callback | без граблей |
| b67ed566-8b43-4c50-8041-3c94a3b04157 | Функции высшего порядка | CatDownloaderV2 | сигнатура `downloadCats(count, onNext, onComplete, onError)` — все 4 параметра |
| 446e05b4-2b15-4e62-aaf5-a754ab7e240e | Мульти-декларации | operator +,−,×,÷ в Point | компонентные функции для деструктуризации |
| a3fdcf6d-3ca1-4e7b-b925-09c4d14e206e | Анонимные классы | DiceRollerV2: fun interfaces + лямбды | `fun interface`, колбэки лямбдами |
| 628aa2aa-9121-43f8-8afa-d75364e75145 | Функции высшего порядка | downloadCat | нужны `onStart` + `allowErrors` параметры и `onError` с аргументами |
| 36ba7d78-c65c-4cd3-88e8-b1d9e9074679 | Анонимные классы | QueryHandler | функциональные параметры по ТЗ |
| a6204ec4-2bda-48b0-9b4e-eb2c9f280603 | Анонимные классы | Кофемашина | ингредиенты стартуют **0** (не максимум); `equals(ignoreCase = true)` и enum.name = команде; `scanner.hasNextLine()` вместо голого nextLine; кавычки — triple-quoted |
| 05fa05a4-3923-41c2-ad31-a66564da8ef8 | Функции высшего порядка | Студенты по городам | обязательны `mapValues()` + `map()` (+filter) |
| 3e455486-53ff-4bab-afb2-d0de9630ee41 | Коллекции. Функции | HoneyBear | деструктуризация в лямбде и в `val` |

## Общие правила, чтобы принимало с первого раза

- Открывать задачи по одной: следующая отдаёт 403, пока не решена предыдущая в этом уроке.
- WS-чеки — последовательно; залп >5 соединений душится таймаутами (~120 с).
- Реальный вердикт — в `RESULT.status`; тексты ошибок с подсказками — в `LOG`-фреймах, читать дословно.
- Если pane пришёл без `fun main` — не добавлять его: тренажёр ждёт top-level скрипт.
- JSON собирать через `json.dumps` — ручное экранирование кавычек съедает код.
- Задачи «открываются» позже (403 на GET /api/tasks/<id>/) — решать после разблокировки, не переделывать.

## quiz_coding (теоретические блоки с кодом)

`quiz_coding_solutions.json` — 12 проверенных ответов: block_id → {lesson_id, panes}. Сабмит: `POST /api/theory_blocks/quiz_coding/check/` `{block_id, lesson_id, panes}`.
- Демо-блоки (`use_tests:false`) принимаются стартовым кодом — в файле он уже сохранён как принятый.
- Блоки с правкой кода: enum AuthorizationType (тип параметра enum, не String), sealed interface State вместо data class, `inner class ViewHolder`, downloadCat с `onError`, downloadCat с `onSuccess: (Cat) -> Unit` + `onError: (String) -> Unit`, деструктуризация в HoneyBear и в лямбде `CanEat { (name, size, color) -> }`.
- Если сервер ругается на `pane.id` — перед сабмитом перечитать `GET /api/lessons/<lid>/`, взять `content.panes` блока и подставить свежие `id`/`name`, контент — из этого файла.
