# SoftGuide Agent

AI-агент для подбора и презентации программного обеспечения, доступного внутри компании.

---

## 🚀 Описание

SoftGuide Agent — это интеллектуальный ассистент, который:

- общается с пользователем в свободной форме
- определяет, о каком ПО идет речь
- проверяет, доступна ли программа в контуре компании
- формирует **готовую HTML-презентацию** с описанием ПО

Если программа недоступна — агент корректно сообщает об этом.

---

## 🎯 Для кого

- офисные сотрудники
- новые сотрудники (онбординг)
- пользователи, не знающие доступный стек ПО

---

## ⚙️ Основные возможности

- 🧠 Определение намерения пользователя (чат / запрос ПО)
- 🔍 Резолв программ по алиасам (Word, Excel, Notion и т.д.)
- ✅ Проверка доступности ПО через whitelist (`allowed_software.yaml`)
- 🌐 Web-поиск информации (Tavily)
- 🧾 Генерация HTML-презентации
- 🤖 Интеграция с Telegram-ботом
- 🌍 HTTP API через FastAPI

---

## 🏗️ Архитектура

Стек проекта:

- **LangChain + LangGraph** — оркестрация агента
- **OpenAI API** — LLM
- **Tavily** — web search
- **FastAPI** — backend API
- **Aiogram** — Telegram-бот
- **Docker** — контейнеризация

Упрощённый pipeline:

```

User → Chatbot → Normalize Query → Resolve Software
→ (если найдено) → Web Search → HTML Generation
→ Response

```

---

## 📁 Структура проекта

```

. \
├── app \
│   ├── agent \
│   │   ├── nodes \
│   │   ├── state.py \
│   │   └── graph.py \
│   ├── api \
│   └── bot \
├── data \
│   └── allowed_software.yaml \
├── main.py \
└── docker \

````

---

## ▶️ Запуск

### 1. Клонирование

```bash
git clone <your_repo>
cd project
````

### 2. Установка зависимостей

```bash
uv sync -n
```

### 3. Настройка .env

```env
OPENAI_API_KEY=...
TAVILY_API_KEY=...
```

### 4. Запуск API

```bash
uvicorn main:app --reload
```

---

## 🤖 Telegram-бот

Запускается через Aiogram:

```bash
python bot.py
```

---

## 🧪 Пример запроса

```
Что такое Word?
```

👉 Ответ:

* если программа доступна → HTML-код презентации
* если нет → сообщение о недоступности

---

## ⚠️ Ограничения

* работает только с ПО из `allowed_software.yaml`
* нет сложной нормализации (MVP)
* не обрабатывает несколько программ в одном запросе

---

## 🔮 Планы развития

* улучшенная нормализация (LLM fallback)
* поддержка нескольких программ
* сохранение истории пользователя
* UI интерфейс
* интеграция с внутренними системами компании

---

## 📌 Статус проекта

🚧 **Prototype / Pet Project**

---

## 👨‍💻 Автор

eugene-os

---

## Пример:

```html
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <title>Microsoft Word — текстовый редактор</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="min-h-screen bg-slate-950 text-slate-100 antialiased">
  <div class="min-h-screen flex flex-col">
    <header class="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-20">
      <div class="max-w-5xl mx-auto px-4 py-4 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 class="text-2xl md:text-3xl font-semibold tracking-tight text-cyan-300 drop-shadow-[0_0_12px_rgba(34,211,238,0.7)]">
            Microsoft Word
          </h1>
          <p class="text-sm md:text-base text-slate-300">
            Текстовый редактор для создания, просмотра, редактирования и форматирования документов различной сложности.
          </p>
        </div>
      </div>
    </header>

    <main class="flex-1">
      <section class="max-w-5xl mx-auto px-4 py-8 md:py-12">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8">
          <!-- Обзор -->
          <article class="rounded-xl border border-cyan-500/40 bg-slate-900/60 shadow-lg shadow-cyan-500/20 p-5 md:p-6">
            <h2 class="text-xl font-semibold mb-3 text-cyan-300">Обзор</h2>
            <p class="text-sm text-slate-200 mb-3">
              Microsoft Word — текстовый процессор, предназначенный для создания, просмотра, редактирования и форматирования текстовых документов: статей, деловых бумаг и других материалов. Выпускается корпорацией Microsoft в составе пакета Microsoft Office и является одним из самых распространённых текстовых редакторов.
            </p>
            <ul class="list-disc list-inside space-y-1 text-sm text-slate-300">
              <li>Первая версия создана для IBM PC под DOS в 1983 году.</li>
              <li>Существуют версии для Windows, macOS, Apple Macintosh, SCO UNIX.</li>
              <li>Доступна веб-версия Word Online, которой можно пользоваться в браузере.</li>
            </ul>
          </article>

          <!-- Основные возможности -->
          <article class="rounded-xl border border-purple-500/40 bg-slate-900/60 shadow-lg shadow-purple-500/20 p-5 md:p-6">
            <h2 class="text-xl font-semibold mb-3 text-purple-300">Основные возможности</h2>
            <ul class="list-disc list-inside space-y-1.5 text-sm text-slate-200">
              <li>Набор и оформление текста с настройкой шрифтов, размеров и начертания.</li>
              <li>Изменение формата страниц и выравнивания текста.</li>
              <li>Создание списков, содержаний и нумерации.</li>
              <li>Вставка таблиц, рисунков, диаграмм, изображений и других объектов.</li>
              <li>Использование библиотеки стилей и готовых наборов форматов.</li>
              <li>Автоматический перенос текста на следующую строку или страницу.</li>
              <li>Автоматическое исправление ошибок и автотекст для часто используемых выражений.</li>
              <li>Создание сложных таблиц, сносок, списков источников и комментариев.</li>
              <li>Режим совместного редактирования документов.</li>
              <li>Сохранение документов в форматах различных версий Word, а также PDF и RTF.</li>
            </ul>
          </article>

          <!-- Для чего используется -->
          <article class="rounded-xl border border-cyan-500/40 bg-slate-900/60 shadow-lg shadow-cyan-500/20 p-5 md:p-6">
            <h2 class="text-xl font-semibold mb-3 text-cyan-300">Для чего используется</h2>
            <ul class="list-disc list-inside space-y-1.5 text-sm text-slate-200">
              <li>Создание и оформление статей и деловых документов.</li>
              <li>Подготовка документов разной сложности — от заявлений до многостраничных публикаций.</li>
              <li>Оформление поздравительных открыток, визиток, приглашений и писем с помощью встроенных графических средств.</li>
              <li>Подготовка документов для корпоративной работы с текстами в компаниях.</li>
              <li>Работа с документами на компьютере и через веб-интерфейс Word Online.</li>
            </ul>
          </article>

          <!-- Преимущества -->
          <article class="rounded-xl border border-purple-500/40 bg-slate-900/60 shadow-lg shadow-purple-500/20 p-5 md:p-6">
            <h2 class="text-xl font-semibold mb-3 text-purple-300">Преимущества</h2>
            <ul class="list-disc list-inside space-y-1.5 text-sm text-slate-200">
              <li>Широкое распространение и популярность среди текстовых редакторов.</li>
              <li>Богатый набор функций для создания как простых, так и комплексных документов.</li>
              <li>Унифицированный интерфейс с другими приложениями Microsoft Office.</li>
              <li>Поддержка двоичного формата документов, ставшего стандартом де-факто (.doc).</li>
              <li>Наличие фильтров импорта и экспорта форматов Word в большинстве текстовых процессоров.</li>
            </ul>
          </article>

          <!-- Ограничения -->
          <article class="rounded-xl border border-cyan-500/40 bg-slate-900/60 shadow-lg shadow-cyan-500/20 p-5 md:p-6">
            <h2 class="text-xl font-semibold mb-3 text-cyan-300">Ограничения</h2>
            <ul class="list-disc list-inside space-y-1.5 text-sm text-slate-200">
              <li>Форматы документов разных версий программы могут отличаться.</li>
              <li>Форматирование, корректное в новой версии, может отображаться иначе в старых версиях.</li>
              <li>При сохранении для старых версий возможна частичная потеря форматирования.</li>
              <li>Некоторые сценарии многопользовательского редактирования зависят от настроек локальной сети.</li>
            </ul>
          </article>

          <!-- Источники -->
          <article class="rounded-xl border border-purple-500/40 bg-slate-900/60 shadow-lg shadow-purple-500/20 p-5 md:p-6">
            <h2 class="text-xl font-semibold mb-3 text-purple-300">Источники</h2>
            <ul class="list-disc list-inside space-y-1.5 text-sm text-cyan-200">
              <li>
                <a href="https://ru.wikipedia.org/wiki/Microsoft_Word" class="underline decoration-cyan-400 hover:text-cyan-300 hover:decoration-cyan-300" aria-label="Открыть статью Microsoft Word в Википедии">
                  Microsoft Word — статья в Википедии
                </a>
              </li>
              <li>
                <a href="https://portal.tpu.ru/SHARED/m/MARTYNOVYAA/study_work/ktit/labs/%D0%A2%D0%B5%D0%BE%D1%80%D0%B8%D1%8F%20Word_0.pdf" class="underline decoration-cyan-400 hover:text-cyan-300 hover:decoration-cyan-300" aria-label="Открыть PDF о текстовом редакторе Microsoft Word">
                  Текстовые редакторы Microsoft Word — учебный материал (PDF)
                </a>
              </li>
              <li>
                <a href="https://startpack.ru/application/microsoft-word" class="underline decoration-cyan-400 hover:text-cyan-300 hover:decoration-cyan-300" aria-label="Открыть обзор сервиса Microsoft Word на Startpack">
                  Microsoft Word — обзор сервиса на Startpack
                </a>
              </li>
            </ul>
          </article>
        </div>
      </section>
    </main>

    <footer class="border-t border-slate-800 bg-slate-950/80">
      <div class="max-w-5xl mx-auto px-4 py-4">
        <p class="text-xs text-slate-500">
          Информация на странице основана на открытых источниках о Microsoft Word.
        </p>
      </div>
    </footer>
  </div>
</body>
</html>
```
