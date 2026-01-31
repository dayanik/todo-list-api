# todo-list-api
g# URL Shortening Service 🧩
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
restfull todo list api with authentication, authorization. [roadmap.sh](https://roadmap.sh/projects/todo-list-api)
---
## 🎯 Возможности

- CRUD постов

---
## 🛠 Установка и запуск

1. Клонируй репозиторий и перейди в директорию проекта
```bash
git clone https://github.com/dayanik/url-shortening-service.git
cd url-shortening-service
```
2. В этом проекте используется sqlite3 асинхронная версия

3. Запусти Docker контейнеры через compose:
```bash
docker-compose up -d --build
````
---
## 🔄 Примеры API

| Метод  | Путь               | Описание               |
| ------ | ------------------ | ---------------------- |
| POST   | `/posts`           | Создать статью.        |
| GET    | `/posts/{post_id}` | Получение статьи по id |
| PUT    | `/posts/{post_id}` | Изменить статью        |
| GET    | `/posts`           | получить все статьи    |
| DELETE | `/posts/{post_id}` | Удалить статью по id   |

**Пример ответа:**

```json
[
  {
    "post_id": 1,
    "title": "My new Blog Post",
    "content": "This is the content of my new blog post.",
    "category": "Technology",
    "tags": [
      "Tech",
      "Programming"
    ],
    "created_at": "2026-01-30T21:05:36",
    "updated_at": "2026-01-30T21:05:36"
  }
]
```

---

## ✅ Проверка и тесты

*(если ты добавишь тесты — укажи здесь как их запускать: jest, mocha и т.д.)*

```bash
test
```

---
## 📈 Стек технологий

* FastAPI
* SQLite3
* ORM SqlAlchemy
* Docker

---
## 📄 Лицензия

Этот проект лицензирован под [MIT License](LICENSE).

---
## ✍🏼 Контакты / Благодарности

Если хочешь связаться или внести вклад — открывай issue или pull request.
Большое спасибо за интерес к проекту!