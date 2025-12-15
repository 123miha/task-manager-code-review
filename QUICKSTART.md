# Быстрый старт - Code Review проект

## 🚀 5 минут до запуска

### 1️⃣ Создайте репозиторий на GitHub
```
github.com → New repository → task-manager-code-review
```

### 2️⃣ Клонируйте и добавьте файлы
```bash
git clone https://github.com/USERNAME/task-manager-code-review.git
cd task-manager-code-review

# Скопируйте все файлы проекта сюда

git add .
git commit -m "Initial commit"
git push origin main
```

### 3️⃣ Создайте ветку "до ревью"
```bash
git checkout -b feature/before-review

# Оставьте только код из before-review/

git add .
git commit -m "Код до ревью - с проблемами"
git push origin feature/before-review
```

### 4️⃣ Создайте ветку "после ревью"
```bash
git checkout main
git checkout -b feature/after-review

# Замените на код из after-review/

git add .
git commit -m "Код после ревью - исправлено"
git push origin feature/after-review
```

### 5️⃣ Создайте Pull Request
```
GitHub → Pull requests → New PR
base: main ← compare: feature/after-review
```

### 6️⃣ WinMerge
```
1. Скачать: winmerge.org
2. File → Open
3. Left: before-review/task_manager.py
4. Right: after-review/task_manager.py
5. Сделать скриншоты!
```

## 📋 Что сдавать

1. ✅ Ссылка на GitHub репозиторий
2. ✅ Ссылка на Pull Request
3. ✅ Файл `docs/code-review.md`
4. ✅ Скриншоты WinMerge
5. ✅ Презентация (по желанию)

## 🎯 Основные проблемы исправленные в коде

| Проблема | До | После |
|----------|-----|--------|
| SQL-инъекции | `f"...{var}..."` | `execute("...", (var,))` |
| Обработка ошибок | Нет | `try-except` блоки |
| Дубликация | 10+ раз `connect()` | Context manager |
| Именование | `c`, `r`, `t`, `d` | `cursor`, `results`, `title` |
| Архитектура | Функции | ООП класс |
| Документация | Нет | Docstrings + типы |

## 💡 Для высокой оценки (бонус)

- [ ] GitHub Actions (автотесты)
- [ ] Unit-тесты (pytest)
- [ ] Защита веток (Branch Protection)
- [ ] Code coverage отчет
- [ ] Дополнительные комментарии в PR

Готово! 🎓
