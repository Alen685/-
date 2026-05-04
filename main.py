import json
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import messagebox


# Загружаем избранное из файла
def load_favorites():
    try:
        with open("favorites.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


# Сохраняем избранное в файл
def save_favorites(data):
    with open("favorites.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


favorites = load_favorites()
current_user = None


# Поиск пользователя
def search():
    global current_user
    username = entry.get().strip()

    # Проверка на пустой ввод
    if not username:
        messagebox.showwarning("Ошибка", "Поле поиска не может быть пустым!")
        return

    # Запрос к GitHub API
    url = f"https://api.github.com/users/{username}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "App"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

            # Выводим результат
            result = (
                f"Логин: {data['login']}\n"
                f"Имя: {data.get('name', 'не указано')}\n"
                f"Репозиториев: {data['public_repos']}\n"
                f"Подписчиков: {data['followers']}\n"
                f"Ссылка: {data['html_url']}"
            )
            text.delete(1.0, tk.END)
            text.insert(1.0, result)

            current_user = data
            btn_fav.config(state="normal")

    except urllib.error.HTTPError as e:
        text.delete(1.0, tk.END)
        if e.code == 404:
            text.insert(1.0, f"Пользователь '{username}' не найден")
        else:
            text.insert(1.0, f"Ошибка: {e.code}")
        current_user = None
        btn_fav.config(state="disabled")

    except:
        text.delete(1.0, tk.END)
        text.insert(1.0, "Нет интернета или ошибка соединения")
        current_user = None
        btn_fav.config(state="disabled")


# Добавить в избранное
def add_favorite():
    if not current_user:
        return

    # Проверка, есть ли уже
    for user in favorites:
        if user["id"] == current_user["id"]:
            messagebox.showinfo("Инфо", "Уже в избранном!")
            return

    # Добавляем
    favorites.append({
        "id": current_user["id"],
        "login": current_user["login"],
        "url": current_user["html_url"]
    })
    save_favorites(favorites)
    update_list()
    messagebox.showinfo("Успех", f"{current_user['login']} добавлен!")


# Удалить из избранного
def remove_favorite():
    sel = listbox.curselection()
    if not sel:
        messagebox.showwarning("Ошибка", "Выберите пользователя!")
        return

    index = sel[0]
    removed = favorites.pop(index)
    save_favorites(favorites)
    update_list()
    messagebox.showinfo("Успех", f"{removed['login']} удалён!")


# Обновить список избранных
def update_list():
    listbox.delete(0, tk.END)
    for user in favorites:
        listbox.insert(tk.END, f"★ {user['login']}")


# --- ОКНО ---
root = tk.Tk()
root.title("GitHub User Finder - Балашова Алёна")
root.geometry("500x500")
root.resizable(False, False)

# Поле ввода
tk.Label(root, text="Введите имя пользователя:", font=("Arial", 11)).pack(pady=(15, 5))
entry = tk.Entry(root, width=40, font=("Arial", 11))
entry.pack()
entry.bind("<Return>", lambda e: search())

# Кнопка поиска
tk.Button(root, text="Поиск", command=search, bg="#0366d6", fg="white", width=15).pack(pady=8)

# Результат
text = tk.Text(root, height=8, width=45, font=("Arial", 10))
text.pack(pady=5)

# Кнопка "в избранное"
btn_fav = tk.Button(root, text="В избранное", command=add_favorite, bg="green", fg="white", width=15,
state="disabled")
btn_fav.pack(pady=5)

# Список избранных
tk.Label(root, text="Избранные:", font=("Arial", 11)).pack(pady=(10, 5))
listbox = tk.Listbox(root, width=40, height=6, font=("Arial", 10))
listbox.pack()

# Кнопка удаления
tk.Button(root, text="Удалить", command=remove_favorite, bg="red", fg="white", width=15).pack(pady=8)

# Загружаем избранное при старте
update_list()

root.mainloop()