# Справочник по тестированию API (ProjectSprint)

В этом документе собраны готовые `curl` команды для проверки всех эндпоинтов нашего бэкенда. 

### ⚠️ Важные замечания перед началом:
1. **Выбор терминала:** Команды написаны для Linux / Mac / Git Bash / PowerShell. Если вы используете старую командную строку Windows (`cmd`), могут возникнуть проблемы с одинарными кавычками. Рекомендуется использовать встроенный терминал в VS Code или PyCharm.
2. **Красивый вывод JSON:** Если ответ от сервера слипается в одну нечитаемую строку, добавьте в конец команды `| python -m json.tool`. Это отформатирует JSON с красивыми отступами.
   *Пример:* `curl -X GET http://127.0.0.1:8080/api/settings | python -m json.tool`
3. **Порт:** По умолчанию указан порт `8080`. Если ваш Docker настроен на другой порт (например, `5000`), замените его в командах.

---

## 1. Настройки пользователя

### Получить настройки (GET)
```bash
curl -X GET http://127.0.0.1:8080/api/settings | python -m json.tool
```

### Обновить аккаунт (PATCH)
*Обязательно передаем заголовок `Content-Type: application/json`.*
```bash
curl -X PATCH http://127.0.0.1:8080/api/settings/account \
     -H "Content-Type: application/json" \
     -d '{"email": "artur_super@mail.com", "phone": "88005553535", "password": "new_password123"}'
```

### Обновить уведомления (PATCH)
```bash
curl -X PATCH http://127.0.0.1:8080/api/settings/notifications \
     -H "Content-Type: application/json" \
     -d '{"messages": false, "news": true}'
```

### Загрузить фото / аватар (POST)
*Для отправки файлов используется флаг `-F`. Перед путем к файлу обязательно должна стоять `@`. Положите тестовую картинку (например, `test.jpg`) в папку, откуда запускаете терминал, или укажите полный путь.*
```bash
curl -X POST http://127.0.0.1:8080/api/settings/avatar \
     -F "avatar=@test.jpg"
```

---

## 2. Управление проектами

### Получить все проекты (GET)
```bash
curl -X GET http://127.0.0.1:8080/api/projects | python -m json.tool
```

### Создать проект (POST)
*Обратите внимание: массивы передаются в одинарных кавычках внутри двойных, а файлы через `@`.*
```bash
curl -X POST http://127.0.0.1:8080/api/projects \
     -F "name=Новый портал" \
     -F "goal=Сделать круто" \
     -F "start_date=2026-04-01" \
     -F "end_date=2026-05-01" \
     -F "team_lead_id=1" \
     -F 'participants=[1, 2]' \
     -F 'tasks=[{"title": "БД", "progress": 100}, {"title": "API", "progress": 50}]' \
     -F "files=@test.jpg"
```

### Отредактировать проект (PATCH)
*Пример: меняем статус на "Готов" (процент выполнения автоматически станет 100% при GET запросе) и меняем название.*
```bash
curl -X PATCH http://127.0.0.1:8080/api/projects/1 \
     -F "name=Супер Портал 2.0" \
     -F "status=Готов"
```

---

## 3. Статистика и аналитика

### Общая статистика (Артур)
```bash
curl -X GET http://127.0.0.1:8080/api/statistics/general | python -m json.tool
```

### Эффективность команды (Татьяна)
```bash
curl -X GET http://127.0.0.1:8080/api/statistics/team | python -m json.tool
```

### Графики и динамика (Ярослав)
```bash
curl -X GET http://127.0.0.1:8080/api/statistics/charts | python -m json.tool
```