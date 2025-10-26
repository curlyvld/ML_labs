
---

## 🚀 Быстрый старт

### Шаг 1: Установка зависимостей

```bash
pip install numpy
```

### Шаг 2: Запуск

```bash
python3 lab3.py
```
---

## 📊 Что происходит

### 1. Создание базы данных

При первом запуске создается файл `fire_suppression.db` с таблицей правил:

```sql
CREATE TABLE rules (
    id INTEGER PRIMARY KEY,
    smoke_level TEXT,      -- None, Low, High
    zone_type TEXT,        -- Safe, Warning, Danger
    action_name TEXT,      -- Название действия
    action_description TEXT,-- Описание действия
    priority INTEGER       -- Приоритет (1-10)
)
```

### 2. Загрузка правил

Система автоматически загружает 10 правил:

| Дым | Зона | Действие | Приоритет |
|-----|------|----------|-----------|
| None | Safe | Monitor | 1 |
| None | Warning | PreventiveCheck | 2 |
| None | Danger | InspectZone | 3 |
| Low | Safe | Alert | 2 |
| Low | Warning | AlertAndVentilate | 3 |
| Low | Danger | ActivateSprinklersLocal | 4 |
| High | Safe | EvacuateAndVentilate | 5 |
| High | Warning | FullEvacuation | 6 |
| High | Danger | EmergencyProtocol | 7 |
| High | Danger | MaximumResponse | 9 |
| High | Danger | FireEmergency | 10 |

### 3. Нечеткая логика

**Фаззификация дыма:**
- 0-10 ppm → "None" (дыма нет)
- 10-50 ppm → "Low" (небольшое задымление)
- 50+ ppm → "High" (сильное задымление)

**Фаззификация температуры:**
- До 40°C → "Normal"
- 40-70°C → "Elevated"
- 70+°C → "Critical"

**Фаззификация зоны:**
- 0-40% → "Safe"
- 40-70% → "Warning"
- 70-100% → "Danger"

### 4. Принятие решения

1. Текущие значения → фаззификация
2. Поиск правила в SQLite по условиям
3. Выбор действия с максимальным приоритетом
4. Выполнение действия
5. Обратная связь → изменение условий

---


### Просмотр базы данных

Можно использовать любой SQLite клиент:

```bash
# Установить SQLite CLI
brew install sqlite3  # macOS
sudo apt install sqlite3  # Linux

# Просмотр базы
sqlite3 fire_suppression.db

# Запросы
SELECT * FROM rules;
```

Или использовать онлайн инструменты:
- https://sqliteviewer.app/
- https://sqlitebrowser.org/

### Изменение правил

Правила хранятся в коде (строки 44-60 в `lab3.py`). Чтобы изменить правила:

```python
rules = [
    ("None", "Safe", "Monitor", "Система в режиме мониторинга", 1),
    # Добавьте новые правила здесь
]
```
---

## 🧪 Тестирование

### Запуск разных сценариев

Измените параметры в конце файла `lab3.py`:

```python
system.simulate(
    initial_smoke=30,      # Ваш уровень дыма
    initial_temp=50,       # Ваша температура
    initial_zone_risk=60,  # Ваш риск зоны
    steps=10               # Количество шагов
)
```


---

## ✅ Что реализовано

1. ✅ Онтология предметной области в SQLite
2. ✅ Правила управления с приоритетами
3. ✅ Нечеткая логика (фаззификация)
4. ✅ Машина логического вывода
5. ✅ Симулятор с обратной связью
6. ✅ Тестирование в различных сценариях

---
