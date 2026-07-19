import json
from tkinter import *
from tkinter import messagebox, simpledialog
from tkinter import ttk

tasks = []
dark_mode = False
buttons = []
current_filter = "All"  # 'All', 'Pending', 'Completed'

# ---------- CORE ----------

def add_task(title, priority):
    tasks.append({"title": title, "done": False, "priority": priority})
    save_tasks()

def delete_task(index):
    actual_task = get_filtered_tasks()[index]
    tasks.remove(actual_task)
    save_tasks()

def delete_all_tasks():
    tasks.clear()
    save_tasks()

def complete_task(index):
    actual_task = get_filtered_tasks()[index]
    actual_task["done"] = not actual_task["done"]
    save_tasks()

def edit_task(index):
    actual_task = get_filtered_tasks()[index]
    old_title = actual_task["title"]
    new_title = simpledialog.askstring(
        "Edit Task", "New title:", initialvalue=old_title, parent=window
    )
    if new_title is not None:
        new_title = new_title.strip()
        if new_title:
            actual_task["title"] = new_title
            save_tasks()

def save_tasks():
    try:
        with open("tasks.json", "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
    except Exception as e:
        messagebox.showerror("Error", f"Could not save tasks: {e}")

def load_tasks():
    global tasks
    try:
        with open("tasks.json", "r", encoding="utf-8") as f:
            tasks = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        tasks = []

# ---------- UI HELPER ----------

def get_filtered_tasks():
    search_query = search_entry.get().strip().lower()
    filtered = tasks

    if current_filter == "Pending":
        filtered = [t for t in filtered if not t["done"]]
    elif current_filter == "Completed":
        filtered = [t for t in filtered if t["done"]]

    if search_query:
        filtered = [t for t in filtered if search_query in t["title"].lower()]

    return filtered

# ---------- UI ----------

def update_counts_and_progress():
    total = len(tasks)
    done_count = sum(1 for t in tasks if t["done"])
    not_done_count = total - done_count

    count_label.config(
        text=f"Total: {total}   Done: {done_count}   Not done: {not_done_count}"
    )

    if total > 0:
        progress_percent = (done_count / total) * 100
        progress_bar["value"] = progress_percent
        progress_text.config(text=f"{int(progress_percent)}%")
    else:
        progress_bar["value"] = 0
        progress_text.config(text="0%")

def refresh_list():
    listbox.delete(0, END)
    displayed_tasks = get_filtered_tasks()

    for index, t in enumerate(displayed_tasks):
        status = "✔" if t["done"] else "✖"
        priority_tag = f"[{t.get('priority', 'Medium')}]"
        listbox.insert(END, f"  {status}  {priority_tag} {t['title']}")

        p = t.get("priority", "Medium")
        if dark_mode:
            if p == "High":
                listbox.itemconfigure(index, fg="#ff4d4d")
            elif p == "Medium":
                listbox.itemconfigure(index, fg="#ffa500")
            else:
                listbox.itemconfigure(index, fg="#00ff00")
        else:
            if p == "High":
                listbox.itemconfigure(index, fg="#b30000")
            elif p == "Medium":
                listbox.itemconfigure(index, fg="#b37400")
            else:
                listbox.itemconfigure(index, fg="#006600")

    update_counts_and_progress()

def set_filter(filter_type):
    global current_filter
    current_filter = filter_type
    refresh_list()

def on_search_change(*args):
    refresh_list()

def get_selected_index():
    selected = listbox.curselection()
    if not selected:
        messagebox.showwarning("Warning", "Select a task first!", parent=window)
        return None
    return selected[0]

def ask_priority():
    priority_window = Toplevel(window)
    priority_window.title("Select Priority")
    priority_window.geometry("250x150")
    priority_window.resizable(False, False)
    priority_window.grab_set()

    selected_priority = StringVar(value="Medium")

    Label(
        priority_window, text="Choose priority for this task:", font=("Arial", 10)
    ).pack(pady=10)

    Radiobutton(
        priority_window, text="High", variable=selected_priority, value="High"
    ).pack()
    Radiobutton(
        priority_window, text="Medium", variable=selected_priority, value="Medium"
    ).pack()
    Radiobutton(
        priority_window, text="Low", variable=selected_priority, value="Low"
    ).pack()

    def confirm():
        priority_window.destroy()

    Button(priority_window, text="OK", command=confirm, width=10).pack(pady=10)

    window.wait_window(priority_window)
    return selected_priority.get()

def add_from_ui(event=None):
    title = entry.get().strip()
    if not title:
        messagebox.showwarning("Warning", "Task is empty!", parent=window)
        return

    top_add_btn.config(state=DISABLED)
    add_btn.config(state=DISABLED)
    entry.unbind("<Return>")

    try:
        priority = ask_priority()
        add_task(title, priority)
        entry.delete(0, END)
        refresh_list()
    finally:
        top_add_btn.config(state=NORMAL)
        add_btn.config(state=NORMAL)
        entry.bind("<Return>", add_from_ui)
        entry.focus_set()

def delete_from_ui():
    index = get_selected_index()
    if index is not None:
        delete_task(index)
        refresh_list()

def delete_all_from_ui():
    if not tasks:
        messagebox.showinfo(
            "Delete All", "There are no tasks to delete.", parent=window
        )
        return

    answer = messagebox.askyesno(
        "Delete All",
        "Are you sure you want to delete all tasks?",
        parent=window,
    )
    if answer:
        delete_all_tasks()
        refresh_list()

def complete_from_ui(event=None):
    index = get_selected_index()
    if index is not None:
        complete_task(index)
        refresh_list()

def edit_from_ui():
    index = get_selected_index()
    if index is not None:
        edit_task(index)
        refresh_list()

def toggle_theme():
    global dark_mode

    if not dark_mode:
        window.configure(bg="#1e1e1e")
        top_frame.configure(bg="#1e1e1e")
        search_frame.configure(bg="#1e1e1e")
        filter_frame.configure(bg="#1e1e1e")
        progress_frame.configure(bg="#1e1e1e")
        middle_frame.configure(bg="#1e1e1e")
        bottom_frame.configure(bg="#1e1e1e")
        count_frame.configure(bg="#1e1e1e")

        entry.configure(bg="#2d2d2d", fg="white", insertbackground="white")
        search_entry.configure(bg="#2d2d2d", fg="white", insertbackground="white")
        listbox.configure(bg="#2d2d2d", selectbackground="#4a4a4a", selectforeground="white")
        
        count_label.configure(bg="#1e1e1e", fg="#00adb5")
        progress_title_label.configure(bg="#1e1e1e", fg="white")
        progress_text.configure(bg="#1e1e1e", fg="white")
        search_label.configure(bg="#1e1e1e", fg="white")

        for btn in buttons:
            btn.configure(
                bg="#3a3a3a",
                fg="white",
                activebackground="#555555",
                activeforeground="white",
            )

        theme_btn.configure(text="Light Theme")
        dark_mode = True
    else:
        window.configure(bg=default_bg)
        top_frame.configure(bg=default_bg)
        search_frame.configure(bg=default_bg)
        filter_frame.configure(bg=default_bg)
        progress_frame.configure(bg=default_bg)
        middle_frame.configure(bg=default_bg)
        bottom_frame.configure(bg=default_bg)
        count_frame.configure(bg=default_bg)

        entry.configure(bg="white", fg="black", insertbackground="black")
        search_entry.configure(bg="white", fg="black", insertbackground="black")
        listbox.configure(bg="white", selectbackground="lightgray", selectforeground="black")
        
        count_label.configure(bg=default_bg, fg="black")
        progress_title_label.configure(bg=default_bg, fg="black")
        progress_text.configure(bg=default_bg, fg="black")
        search_label.configure(bg=default_bg, fg="black")

        for btn in buttons:
            btn.configure(
                bg=default_bg,
                fg="black",
                activebackground="lightgray",
                activeforeground="black",
            )

        theme_btn.configure(text="Dark Theme")
        dark_mode = False

    refresh_list()

def on_close():
    save_tasks()
    window.destroy()

# ---------- GUI LAYOUT ----------

window = Tk()
default_bg = window.cget("bg")

window.title("Advanced Task Manager")
window.geometry("560x680")
window.resizable(False, False)
window.protocol("WM_DELETE_WINDOW", on_close)

top_frame = Frame(window)
top_frame.pack(pady=(10, 5), padx=10, fill=X)

entry = Entry(top_frame, font=("Arial", 12))
entry.pack(side=LEFT, padx=5, expand=True, fill=X)
entry.bind("<Return>", add_from_ui)

top_add_btn = Button(top_frame, text="Add", command=add_from_ui, width=10)
top_add_btn.pack(side=LEFT, padx=5)

search_frame = Frame(window)
search_frame.pack(pady=5, padx=10, fill=X)

search_label = Label(search_frame, text="🔍 Search:", font=("Arial", 10))
search_label.pack(side=LEFT, padx=5)

search_var = StringVar()
search_var.trace_add("write", on_search_change)
search_entry = Entry(search_frame, textvariable=search_var, font=("Arial", 11))
search_entry.pack(side=LEFT, padx=5, expand=True, fill=X)

filter_frame = Frame(window)
filter_frame.pack(pady=5, padx=10, fill=X)

all_btn = Button(filter_frame, text="All", command=lambda: set_filter("All"))
all_btn.pack(side=LEFT, padx=2, expand=True, fill=X)

pending_btn = Button(
    filter_frame, text="Pending", command=lambda: set_filter("Pending")
)
pending_btn.pack(side=LEFT, padx=2, expand=True, fill=X)

completed_btn = Button(
    filter_frame, text="Completed", command=lambda: set_filter("Completed")
)
completed_btn.pack(side=LEFT, padx=2, expand=True, fill=X)

progress_frame = Frame(window)
progress_frame.pack(fill=X, padx=15, pady=5)

progress_title_label = Label(
    progress_frame, text="Progress:", font=("Arial", 10, "bold")
)
progress_title_label.pack(side=LEFT, padx=(0, 5))

progress_bar = ttk.Progressbar(
    progress_frame, orient=HORIZONTAL, mode="determinate"
)
progress_bar.pack(side=LEFT, expand=True, fill=X, padx=5)

progress_text = Label(progress_frame, text="0%", font=("Arial", 10, "bold"))
progress_text.pack(side=LEFT, padx=(5, 0))

count_frame = Frame(window)
count_frame.pack(fill=X, padx=15, pady=(5, 0))

count_label = Label(count_frame, text="", font=("Arial", 10, "bold"))
count_label.pack(anchor="w")

middle_frame = Frame(window)
middle_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)

scrollbar = Scrollbar(middle_frame)
scrollbar.pack(side=RIGHT, fill=Y)

listbox = Listbox(
    middle_frame, font=("Arial", 12), yscrollcommand=scrollbar.set
)
listbox.pack(fill=BOTH, expand=True)
scrollbar.config(command=listbox.yview)

listbox.bind("<Double-Button-1>", complete_from_ui)

bottom_frame = Frame(window)
bottom_frame.pack(pady=10)

add_btn = Button(bottom_frame, text="Add", command=add_from_ui, width=10)
add_btn.grid(row=0, column=0, padx=5)

delete_btn = Button(
    bottom_frame, text="Delete", command=delete_from_ui, width=10
)
delete_btn.grid(row=0, column=1, padx=5)

edit_btn = Button(bottom_frame, text="Edit", command=edit_from_ui, width=10)
edit_btn.grid(row=0, column=2, padx=5)

save_btn = Button(bottom_frame, text="Save", command=save_tasks, width=10)
save_btn.grid(row=0, column=3, padx=5)

delete_all_btn = Button(
    bottom_frame, text="Delete All", command=delete_all_from_ui, width=10
)
delete_all_btn.grid(row=0, column=4, padx=5)

theme_btn = Button(
    bottom_frame, text="Dark Theme", command=toggle_theme, width=10
)
theme_btn.grid(row=1, column=0, columnspan=5, pady=8)

buttons = [
    top_add_btn,
    all_btn,
    pending_btn,
    completed_btn,
    add_btn,
    delete_btn,
    edit_btn,
    save_btn,
    delete_all_btn,
    theme_btn,
]

# ---------- START ----------

load_tasks()
refresh_list()

window.mainloop()