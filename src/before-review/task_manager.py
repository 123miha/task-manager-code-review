import sqlite3
from datetime import datetime

# Плохое именование, отсутствие класса
def create_db():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    # SQL-инъекция потенциально возможна
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY, t TEXT, d TEXT, s TEXT, dt TEXT)''')
    conn.commit()
    conn.close()

# Дублирование кода подключения к БД
def add_task(title, desc, status):
    # Нет валидации входных данных
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    # SQL-инъекция!
    query = f"INSERT INTO tasks (t, d, s, dt) VALUES ('{title}', '{desc}', '{status}', '{datetime.now()}')"
    c.execute(query)
    conn.commit()
    conn.close()
    return True

# Плохое именование функции
def get_all():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute("SELECT * FROM tasks")
    r = c.fetchall()  # Плохое имя переменной
    conn.close()
    return r

# Нет обработки ошибок
def update_task(id, title, desc, status):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    # SQL-инъекция!
    query = f"UPDATE tasks SET t='{title}', d='{desc}', s='{status}' WHERE id={id}"
    c.execute(query)
    conn.commit()
    conn.close()

def delete_task(id):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    # SQL-инъекция!
    c.execute(f"DELETE FROM tasks WHERE id={id}")
    conn.commit()
    conn.close()

# Функция с слишком большой ответственностью
def search_and_filter(term, status_filter, sort_by):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    
    # Сложная логика без разделения
    if term and status_filter:
        query = f"SELECT * FROM tasks WHERE t LIKE '%{term}%' AND s='{status_filter}'"
    elif term:
        query = f"SELECT * FROM tasks WHERE t LIKE '%{term}%'"
    elif status_filter:
        query = f"SELECT * FROM tasks WHERE s='{status_filter}'"
    else:
        query = "SELECT * FROM tasks"
    
    if sort_by == 'date':
        query += " ORDER BY dt DESC"
    elif sort_by == 'title':
        query += " ORDER BY t"
    
    c.execute(query)
    r = c.fetchall()
    conn.close()
    return r

# Нет проверки на существование задачи
def get_task_by_id(id):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute(f"SELECT * FROM tasks WHERE id={id}")
    r = c.fetchone()
    conn.close()
    return r

# Magic numbers
def get_priority_tasks():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE s='high' OR s='urgent'")
    r = c.fetchall()
    conn.close()
    return r

if __name__ == "__main__":
    create_db()
    add_task("Test task", "Description", "pending")
    print(get_all())
