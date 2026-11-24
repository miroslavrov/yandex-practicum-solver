# Финальная сдача проекта на ревью (урок «Отправка проекта на ревью»)

Тип урока: `external_url_homework` (is_revisor_review_homework, saver=external_url, upload_type=url).

## Чек-лист ТЗ

1. Ветка спринта содержит актуальный код (у нас `sprint-12`).
2. `checklists/sprint-12.md` — финальный чек-лист (основная часть + доп. фича + самопроверка).
3. `README.md` — описание проекта Playlist Maker, версии Android Studio/Kotlin/SDK, шаги сборки и запуска.
4. Ветка `review` создана от базовой точки.
5. Открытый PR `sprint-12 → review` — **не мёрджить и не закрывать** до ответа ревьюера.
6. Коллаборатор `interactivetextbook` в Settings → Collaborators (может добавить только владелец репозитория).
7. Отправить ссылку на PR формой «Сдать работу».

## API отправки

```
POST https://practicum.yandex.ru/api/lessons/<lesson_id>/submit_url/
{"homework": "<PR url>", "homework_external_url": "<PR url>"}
```

`GET /api/lessons/<id>/review_history/` — история отправок.

## После ревью

- принять PR, мёрдж `review → main`;
- `git tag v11.0 && git push --tags`.

## Замечания этого прогона

- Пользователь просил репозиторий **публичным** (преподаватель без кредитов должен видеть код) — переопределяет совет урока про Private.
- Все коммиты и PR — только от имени владельца репозитория (без Devin/bot-авторства и Co-Authored-By).
- Урок «Обратная связь» (следующий) отдаёт 403, пока домашка не отправлена.
