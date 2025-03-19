import sqlite3
from os import path
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


def validate_data():
    title = entries["Pealkiri"].get()
    release_year = entries["Aasta"].get()
    rating = entries["Reiting"].get()

    if not title:
        messagebox.showerror("Viga", "Pealkiri on kohustuslik!")
        return False
    if not release_year.isdigit():
        messagebox.showerror("Viga", "Aasta peab olema arv!")
        return False
    if rating and (not rating.replace('.', '', 1).isdigit() or not (0 <= float(rating) <= 10)):
        messagebox.showerror("Viga", "Reiting peab olema vahemikus 0 kuni 10!")
        return False

    messagebox.showinfo("Edu", "Andmed on kehtivad!")
    return True


# puhastab kõik sisestusväljad
def clear_entries():
    for entry in entries.values():
        entry.delete(0, tk.END)


# valideerib andmed ja lisab need andmebaasi
def insert_data():
    if validate_data():
        connection = sqlite3.connect("movies.db")
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO movies (title, director, release_year, genre, duration, rating, language, country, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entries["Pealkiri"].get(),
            entries["Režissöör"].get(),
            entries["Aasta"].get(),
            entries["Žanr"].get(),
            entries["Kestus"].get(),
            entries["Reiting"].get(),
            entries["Keel"].get(),
            entries["Riik"].get(),
            entries["Kirjeldus"].get()
        ))

        connection.commit()
        connection.close()

        messagebox.showinfo("Edu", "Andmed sisestati edukalt!")
        clear_entries()

        update_treeview()


def update_treeview():
    # Clear the existing rows in the Treeview
    for row in tree.get_children():
        tree.delete(row)

    # Fetch data from the database and update the Treeview
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movies")
    rows = cursor.fetchall()

    for row in rows:
        tree.insert("", "end", values=row[1:])  # Skip the id column

    conn.close()


# Create table and sample data
create_table = """
CREATE TABLE IF NOT EXISTS movies (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  director TEXT,
  release_year INTEGER,
  genre TEXT,
  duration INTEGER,
  rating REAL,
  language TEXT,
  country TEXT,
  description TEXT
);
"""

insert_into = """
INSERT INTO movies (title, director, release_year, genre, duration, rating, language, country, description) VALUES
('The Shawshank Redemption', 'Frank Darabont', 1994, 'Drama', 142, 9.3, 'English', 'USA', 'Two imprisoned men bond over a number of years.'),
('The Godfather', 'Francis Ford Coppola', 1972, 'Crime, Drama', 175, 9.2, 'English', 'USA', 'The aging patriarch of an organized crime dynasty transfers control of his empire to his reluctant son.'),
('The Dark Knight', 'Christopher Nolan', 2008, 'Action, Crime, Drama', 152, 9.0, 'English', 'USA', 'When the menace known as the Joker emerges from his mysterious past, he wreaks havoc and chaos on the people of Gotham.');
"""

try:
    filename = path.abspath(__file__)
    dbdir = filename.rstrip('BD_Tkinter.py')
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    print("Ühendus loodud")
    cursor.execute(create_table)
    cursor.execute(insert_into)
    conn.commit()

except sqlite3.Error as error:
    print("Tekkis viga andmebaasiga ühendamisel:", error)
finally:
    if conn:
        conn.close()

# Create Tkinter window
root = tk.Tk()
root.title("Filmi andmete sisestamine")

# Create labels and entry fields
labels = ["Pealkiri", "Režissöör", "Aasta", "Žanr", "Kestus", "Reiting", "Keel", "Riik", "Kirjeldus"]
entries = {}

for i, label in enumerate(labels):
    tk.Label(root, text=label).grid(row=i, column=0, padx=10, pady=5)
    entry = tk.Entry(root, width=40)
    entry.grid(row=i, column=1, padx=10, pady=5)
    entries[label] = entry

# Create button to insert data
submit_button = tk.Button(root, text="Sisesta andmed", command=insert_data)
submit_button.grid(row=len(labels), column=0, columnspan=2, pady=20)

# Create a frame for the Treeview widget
frame = tk.Frame(root)
frame.grid(row=len(labels)+1, column=0, columnspan=2, pady=20, sticky="nsew")

# Create Scrollbar widget
scrollbar = tk.Scrollbar(frame)
scrollbar.grid(row=0, column=1, sticky="ns")

# Create Treeview widget to display data
tree = ttk.Treeview(frame, yscrollcommand=scrollbar.set, columns=("title", "director", "year", "genre", "duration", "rating", "language", "country", "description"), show="headings")
tree.grid(row=0, column=0, sticky="nsew")

# Configure scrollbar to work with Treeview
scrollbar.config(command=tree.yview)

# Set column headings and width
tree.heading("title", text="Pealkiri")
tree.heading("director", text="Režissöör")
tree.heading("year", text="Aasta")
tree.heading("genre", text="Žanr")
tree.heading("duration", text="Kestus")
tree.heading("rating", text="Reiting")
tree.heading("language", text="Keel")
tree.heading("country", text="Riik")
tree.heading("description", text="Kirjeldus")

tree.column("title", width=150)
tree.column("director", width=100)
tree.column("year", width=60)
tree.column("genre", width=100)
tree.column("duration", width=60)
tree.column("rating", width=60)
tree.column("language", width=80)
tree.column("country", width=80)
tree.column("description", width=200)

# Load data into the Treeview
update_treeview()

# Show Tkinter window
root.mainloop()
