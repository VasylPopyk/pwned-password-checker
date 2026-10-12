# 🔐 SEC-Auditor — Pwned Password Checker

**🌐 Language / Мова:** [🇬🇧 English](#-english) · [🇺🇦 Українська](#-українська)

---

<a id="-english"></a>
# 🇬🇧 English

A command-line utility written in Python for **batch checking passwords or SHA-1 hashes** against known data breaches (via the [Have I Been Pwned](https://haveibeenpwned.com/Passwords) *Pwned Passwords* API) and for **analysing password complexity** against corporate security standards.

The project is built around two core ideas:

- **Privacy first** — the full password hash is **never** sent to the third-party API (k-anonymity).
- **Simple workflow** — an interactive console wizard (`compiler.py`) builds and runs the command for the main script (`script.py`).

## 📑 Table of Contents

- [Features](#features)
- [How k-anonymity works](#how-k-anonymity-works)
- [Project structure](#project-structure)
- [Requirements and installation](#requirements-and-installation)
- [Usage](#usage)
- [Input formats](#input-formats)
- [Report format (JSON)](#report-format-json)
- [Complexity policy](#complexity-policy)
- [Error handling](#error-handling)
- [Roadmap](#roadmap)
- [Security notes](#security-notes)
- [License](#license)

## Features

- Two operating modes:
  - `passwords` — hashing (SHA-1, SHA-256), complexity analysis and breach check;
  - `hashes` — breach check only for pre-computed SHA-1 hashes (the original password is unknown).
- Breach check through the HIBP Pwned Passwords API using **k-anonymity**.
- Password complexity analysis with recommendations on how to improve the password.
- Input from `.txt` (one item per line) and `.csv` (first column) files.
- Detailed JSON report (to a file or to the console).
- Optional export of generated SHA-1 hashes to a separate text file.
- Interactive colourful console wizard with input validation.

## How k-anonymity works

1. The utility computes the **SHA-1** hash of the password locally.
2. Only the **first 5 characters** of the hash (the *prefix*) are sent to the API: `GET https://api.pwnedpasswords.com/range/{prefix}`.
3. The API returns a list of hash *suffixes* (the remaining 35 characters) with the number of times each was seen in breaches.
4. The utility looks for its own suffix **locally** in that list.

```
password ──SHA-1──► 5BAA6 1E4C9B93F3F0682250B6CF8331B7EE68FD8
                    └─┬─┘ └──────────────┬───────────────────┘
                 sent to API       stays on your machine
```

The API never receives the full hash, so it cannot determine which password was checked.

## Project structure

```
password-checker/
├── compiler.py     # Interactive console wizard (launcher for script.py)
├── script.py       # Main utility: hashing, complexity analysis, HIBP check, report
├── passwords.txt   # Example input: list of passwords
├── hashes.txt      # Example input / output: list of SHA-1 hashes
├── audit.json      # Example output: JSON report
└── README.md
```

| File | Purpose |
|------|---------|
| `script.py` | Core logic. Parses CLI arguments (`argparse`), computes hashes (`hashlib`), queries the API (`requests`), generates the report. |
| `compiler.py` | Friendly interactive wrapper. Asks for the mode, input file and output names, shows the generated command and runs `script.py` via `subprocess`. |

## Requirements and installation

- Python **3.10+**
- Internet access (to reach `api.pwnedpasswords.com`)
- Library: [`requests`](https://pypi.org/project/requests/)

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

# 2. (Optional) create a virtual environment
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install requests
```

> `compiler.py` uses plain ANSI escape codes for colours — no extra libraries are required.

## Usage

### Option 1 — Interactive wizard (recommended for beginners)

```bash
python compiler.py
```

The wizard will:

1. Show the main menu (run wizard / list directory contents / exit).
2. Ask you to choose the mode: `passwords` (or `1`) / `hashes` (or `2`).
3. Ask for the input file path (and verify that it exists).
4. Ask for the JSON report name (press **Enter** to print the report to the console).
5. In `passwords` mode, optionally ask whether to save the generated SHA-1 hashes to a separate file.
6. Show the generated command, ask for confirmation, run it and print a short mini-report.

### Option 2 — Direct CLI call

```bash
python script.py -f <input_file> -m <mode> [-o <report.json>] [--hash-output <hashes.txt>]
```

| Argument | Required | Description |
|----------|:--------:|-------------|
| `-f`, `--file` | ✅ | Path to the input file (`.txt` or `.csv`). |
| `-m`, `--mode` | ✅ | Operation mode: `passwords` or `hashes`. |
| `-o`, `--output` | ❌ | Path to the output JSON report. If omitted, the report is printed to the console. |
| `--hash-output` | ❌ | File to save generated SHA-1 hashes (**`passwords` mode only**). |

### Examples

```bash
# Check plain-text passwords and save a JSON report
python script.py -f passwords.txt -m passwords -o audit.json

# Check passwords, save the report and export generated SHA-1 hashes
python script.py -f passwords.txt -m passwords -o audit.json --hash-output hashes.txt

# Check pre-computed SHA-1 hashes (breach check only)
python script.py -f hashes.txt -m hashes -o report.json

# Print the report to the console
python script.py -f passwords.txt -m passwords
```

## Input formats

**`passwords.txt`** (one password per line):

```
123456
qwerty
Tr0ub4dor&3
correct-horse-battery-staple
```

**`hashes.txt`** (one **SHA-1** hash per line, hex):

```
5BAA61E4C9B93F3F0682250B6CF8331B7EE68FD8
B1B3773A05C0ED0176787A4F1574FF0075F7521E
```

- For `.csv` files, only the **first column** of every row is used.
- Empty lines are skipped.
- In `hashes` mode, hashes must be **SHA-1** (the HIBP Pwned Passwords API works with SHA-1).

## Report format (JSON)

Example report for `passwords` mode (breach count is illustrative):

```json
{
    "mode": "passwords",
    "total_checked": 1,
    "results": [
        {
            "input_type": "password",
            "hashes": {
                "sha1": "5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8",
                "sha256": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
            },
            "complexity": {
                "length": 8,
                "complexity_level": "Low",
                "is_corporate_compliant": false,
                "feedback": [
                    "Extend the password length to at least 12 characters.",
                    "Add uppercase letters.",
                    "Add digits.",
                    "Add special characters."
                ]
            },
            "breach_status": {
                "compromised": true,
                "count": 9999999,
                "error": null
            }
        }
    ]
}
```

Example item for `hashes` mode:

```json
{
    "input_type": "hash",
    "hash_value": "5BAA61E4C9B93F3F0682250B6CF8331B7EE68FD8",
    "breach_status": {
        "compromised": true,
        "count": 9999999,
        "error": null
    }
}
```

**`breach_status` fields**

| Field | Meaning |
|-------|---------|
| `compromised` | `true` if the hash suffix was found in the API response. |
| `count` | How many times the password appeared in known breaches. |
| `error` | `null` on success, otherwise the API status or network error text. |

## Complexity policy

The score is calculated as follows:

| Criterion | Points |
|-----------|:------:|
| Length ≥ 12 | +2 |
| Length 8–11 | +1 |
| Uppercase letters | +1 |
| Lowercase letters | +1 |
| Digits | +1 |
| Special characters | +1 |

| Total score | Level |
|:-----------:|:-----:|
| 5–6 | High |
| 3–4 | Medium |
| 0–2 | Low |

A password is marked `is_corporate_compliant: true` when its score is **≥ 4**. The `feedback` array lists concrete recommendations for every missing criterion.

## Error handling

- File read errors (missing file, wrong encoding) → an error message and a clean exit with code `1`.
- Network problems and timeouts (10 s) → recorded in the `error` field of `breach_status` for the affected item; the rest of the list is still processed.
- Non-200 responses from the API → recorded as `API status <code>` in the `error` field.
- In the wizard (`compiler.py`), invalid menu choices and non-existent files are re-prompted; a failing `script.py` is reported without crashing the wizard.

## Roadmap

Planned improvements:

- [ ] Explicit item status: `Safe` / `Compromised` / `Policy Violation`.
- [ ] Timestamp of the check in the JSON report.
- [ ] Local blacklist of common / dictionary passwords and pattern detection (`123456`, `qwerty`, sequences).
- [ ] Short console statistics (checked / compromised / policy violations).
- [ ] Strict policy mode: ≥ 12 characters **and** upper + lower case **and** digits **and** special characters.
- [ ] Validation of SHA-1 format in `hashes` mode.
- [ ] Linting with `flake8` / `pylint` and unit tests.

## Security notes

- Only the 5-character SHA-1 prefix leaves your machine.
- The report in `passwords` mode contains **SHA-1 and SHA-256 hashes** of the checked passwords — store and share it carefully.
- Do not commit real password lists or reports to a public repository. Consider adding them to `.gitignore`:

```gitignore
passwords.txt
hashes.txt
audit.json
report.json
```

<a id="-українська"></a>
# 🇺🇦 Українська

Консольна утиліта на Python для **пакетної перевірки паролів або SHA-1 хешів** на компрометацію (витік у відомих базах даних) через API [Have I Been Pwned](https://haveibeenpwned.com/Passwords) (*Pwned Passwords*) та для **аналізу складності паролів** відповідно до корпоративних стандартів інформаційної безпеки.

В основі проєкту дві ідеї:

- **Приватність насамперед** — повний хеш пароля **ніколи** не надсилається стороннім сервісам (k-anonymity).
- **Простий робочий процес** — інтерактивний консольний майстер (`compiler.py`) формує та запускає команду для головного скрипта (`script.py`).

## 📑 Зміст

- [Можливості](#можливості)
- [Як працює k-anonymity](#як-працює-k-anonymity)
- [Структура проєкту](#структура-проєкту)
- [Вимоги та встановлення](#вимоги-та-встановлення)
- [Використання](#використання)
- [Формати вхідних даних](#формати-вхідних-даних)
- [Формат звіту (JSON)](#формат-звіту-json)
- [Політика складності](#політика-складності)
- [Обробка помилок](#обробка-помилок)
- [Плани розвитку](#плани-розвитку)
- [Нотатки з безпеки](#нотатки-з-безпеки)
- [Ліцензія](#ліцензія)

## Можливості

- Два режими роботи:
  - `passwords` — хешування (SHA-1, SHA-256), аналіз складності та перевірка на витоки;
  - `hashes` — лише перевірка на компрометацію для готових SHA-1 хешів (оригінальний пароль невідомий).
- Перевірка на витоки через HIBP Pwned Passwords API з використанням **k-anonymity**.
- Аналіз складності пароля з рекомендаціями щодо його покращення.
- Читання `.txt` (один елемент на рядок) та `.csv` (перший стовпець) файлів.
- Детальний JSON-звіт (у файл або в консоль).
- Додатковий експорт згенерованих SHA-1 хешів в окремий текстовий файл.
- Інтерактивний кольоровий консольний майстер із валідацією введення.

## Як працює k-anonymity

1. Утиліта локально обчислює **SHA-1** хеш пароля.
2. До API надсилаються лише **перші 5 символів** хешу (*префікс*): `GET https://api.pwnedpasswords.com/range/{prefix}`.
3. API повертає список *суфіксів* хешів (решта 35 символів) разом із кількістю збігів у витоках.
4. Утиліта шукає власний суфікс у цьому списку **локально**.

```
password ──SHA-1──► 5BAA6 1E4C9B93F3F0682250B6CF8331B7EE68FD8
                    └─┬─┘ └──────────────┬───────────────────┘
               надсилається в API    залишається на вашому ПК
```

API ніколи не отримує повний хеш, тому не може визначити, який саме пароль перевірявся.

## Структура проєкту

```
password-checker/
├── compiler.py     # Інтерактивний консольний майстер (запускає script.py)
├── script.py       # Головна утиліта: хешування, аналіз складності, HIBP, звіт
├── passwords.txt   # Приклад вхідних даних: список паролів
├── hashes.txt      # Приклад вхідних / вихідних даних: список SHA-1 хешів
├── audit.json      # Приклад результату: JSON-звіт
└── README.md
```

| Файл | Призначення |
|------|-------------|
| `script.py` | Основна логіка. Обробка аргументів CLI (`argparse`), обчислення хешів (`hashlib`), запити до API (`requests`), формування звіту. |
| `compiler.py` | Зручна інтерактивна оболонка. Запитує режим, вхідний файл і назви вихідних файлів, показує згенеровану команду та запускає `script.py` через `subprocess`. |

## Вимоги та встановлення

- Python **3.10+**
- Доступ до інтернету (для звернення до `api.pwnedpasswords.com`)
- Бібліотека: [`requests`](https://pypi.org/project/requests/)

```bash
# 1. Клонуйте репозиторій
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

# 2. (Опційно) створіть віртуальне середовище
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 3. Встановіть залежності
pip install requests
```

> `compiler.py` використовує прості ANSI-коди для кольорів — додаткові бібліотеки не потрібні.

## Використання

### Варіант 1 — Інтерактивний майстер (рекомендовано для початківців)

```bash
python compiler.py
```

Майстер виконає такі кроки:

1. Покаже головне меню (запустити майстер / переглянути вміст директорії / вийти).
2. Запропонує обрати режим: `passwords` (або `1`) / `hashes` (або `2`).
3. Запитає шлях до вхідного файлу (і перевірить, що він існує).
4. Запитає назву JSON-звіту (натисніть **Enter**, щоб вивести звіт у консоль).
5. У режимі `passwords` запропонує зберегти згенеровані SHA-1 хеші в окремий файл.
6. Покаже згенеровану команду, запитає підтвердження, запустить її та виведе короткий міні-звіт.

### Варіант 2 — Прямий виклик через CLI

```bash
python script.py -f <вхідний_файл> -m <режим> [-o <report.json>] [--hash-output <hashes.txt>]
```

| Аргумент | Обов'язковий | Опис |
|----------|:------------:|------|
| `-f`, `--file` | ✅ | Шлях до вхідного файлу (`.txt` або `.csv`). |
| `-m`, `--mode` | ✅ | Режим роботи: `passwords` або `hashes`. |
| `-o`, `--output` | ❌ | Шлях до вихідного JSON-звіту. Якщо не вказано — звіт виводиться в консоль. |
| `--hash-output` | ❌ | Файл для збереження згенерованих SHA-1 хешів (**лише режим `passwords`**). |

### Приклади

```bash
# Перевірка відкритих паролів із збереженням JSON-звіту
python script.py -f passwords.txt -m passwords -o audit.json

# Перевірка паролів, збереження звіту та експорт SHA-1 хешів
python script.py -f passwords.txt -m passwords -o audit.json --hash-output hashes.txt

# Перевірка готових SHA-1 хешів (лише на витоки)
python script.py -f hashes.txt -m hashes -o report.json

# Вивести звіт у консоль
python script.py -f passwords.txt -m passwords
```

## Формати вхідних даних

**`passwords.txt`** (один пароль на рядок):

```
123456
qwerty
Tr0ub4dor&3
correct-horse-battery-staple
```

**`hashes.txt`** (один **SHA-1** хеш на рядок, hex):

```
5BAA61E4C9B93F3F0682250B6CF8331B7EE68FD8
B1B3773A05C0ED0176787A4F1574FF0075F7521E
```

- Для `.csv` файлів використовується лише **перший стовпець** кожного рядка.
- Порожні рядки пропускаються.
- У режимі `hashes` хеші мають бути **SHA-1** (HIBP Pwned Passwords API працює саме з SHA-1).

## Формат звіту (JSON)

Приклад звіту для режиму `passwords` (кількість витоків умовна):

```json
{
    "mode": "passwords",
    "total_checked": 1,
    "results": [
        {
            "input_type": "password",
            "hashes": {
                "sha1": "5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8",
                "sha256": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
            },
            "complexity": {
                "length": 8,
                "complexity_level": "Low",
                "is_corporate_compliant": false,
                "feedback": [
                    "Extend the password length to at least 12 characters.",
                    "Add uppercase letters.",
                    "Add digits.",
                    "Add special characters."
                ]
            },
            "breach_status": {
                "compromised": true,
                "count": 9999999,
                "error": null
            }
        }
    ]
}
```

Приклад елемента для режиму `hashes`:

```json
{
    "input_type": "hash",
    "hash_value": "5BAA61E4C9B93F3F0682250B6CF8331B7EE68FD8",
    "breach_status": {
        "compromised": true,
        "count": 9999999,
        "error": null
    }
}
```

**Поля `breach_status`**

| Поле | Значення |
|------|----------|
| `compromised` | `true`, якщо суфікс хешу знайдено у відповіді API. |
| `count` | Скільки разів пароль траплявся у відомих витоках. |
| `error` | `null` у разі успіху, інакше — статус API або текст мережевої помилки. |

## Політика складності

Оцінка розраховується так:

| Критерій | Бали |
|----------|:----:|
| Довжина ≥ 12 | +2 |
| Довжина 8–11 | +1 |
| Великі літери | +1 |
| Малі літери | +1 |
| Цифри | +1 |
| Спеціальні символи | +1 |

| Сума балів | Рівень |
|:----------:|:------:|
| 5–6 | High |
| 3–4 | Medium |
| 0–2 | Low |

Пароль отримує `is_corporate_compliant: true`, якщо оцінка **≥ 4**. Масив `feedback` містить конкретні рекомендації щодо кожного відсутнього критерію.

## Обробка помилок

- Помилки читання файлу (файл не знайдено, неправильне кодування) → повідомлення про помилку та коректне завершення з кодом `1`.
- Мережеві проблеми та тайм-аути (10 с) → записуються в поле `error` у `breach_status` для відповідного елемента; решта списку продовжує оброблятися.
- Відповіді API зі статусом не 200 → записуються як `API status <code>` у полі `error`.
- У майстрі (`compiler.py`) некоректний вибір у меню та неіснуючі файли запитуються повторно; помилка `script.py` виводиться без аварійного завершення майстра.

## Плани розвитку

Заплановані покращення:

- [ ] Явний статус елемента: `Safe` / `Compromised` / `Policy Violation`.
- [ ] Час перевірки у JSON-звіті.
- [ ] Локальний чорний список поширених / словникових паролів та пошук патернів (`123456`, `qwerty`, послідовності).
- [ ] Коротка статистика в консолі (перевірено / скомпрометовано / порушення політики).
- [ ] Сувора політика: ≥ 12 символів **і** великі та малі літери **і** цифри **і** спецсимволи.
- [ ] Валідація формату SHA-1 у режимі `hashes`.
- [ ] Лінтинг через `flake8` / `pylint` та юніт-тести.

## Нотатки з безпеки

- З вашого комп'ютера виходить лише 5-символьний префікс SHA-1 хешу.
- Звіт у режимі `passwords` містить **SHA-1 та SHA-256 хеші** перевірених паролів — зберігайте та передавайте його обережно.
- Не публікуйте реальні списки паролів чи звіти у відкритому репозиторії. Рекомендується додати їх до `.gitignore`:

```gitignore
passwords.txt
hashes.txt
audit.json
report.json
```
