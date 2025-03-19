import sqlite3
from os import path
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import subprocess


# Search function
def on_search():
    search_query = search_entry.get()
    load_data_from_db(tree, search_query)


# Function to load data from the database and populate the Treeview
def load_data_from_db(tree, search_query=""):
    # Clear existing rows in the Treeview
    for item in tree.get_children():
        tree.delete(item)

    # Create connection to the SQLite database
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()

    # SQL query to fetch data, with optional search
    if search_query:
        cursor.execute("SELECT title, director, release_year, genre, duration, rating, language, country, description FROM movies WHERE title LIKE ?", ('%' + search_query + '%',))
    else:
        cursor.execute("SELECT title, director, release_year, genre, duration, rating, language, country, description FROM movies")

    rows = cursor.fetchall()

    # Insert rows into the Treeview
    for row in rows:
        tree.insert("", "end", values=row)

    # Close the connection
    conn.close()


# Function to validate the data
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


# Function to clear input fields
def clear_entries():
    for entry in entries.values():
        entry.delete(0, tk.END)

# Avab добавление данных в отдельном файле
def add_data():
    subprocess.run(["python", "01.py"])


# Function to insert data into the database
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


# Function to update the Treeview with all data
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

def load_data_from_db(tree, search_query=""):
    # Puhasta Treeview tabel enne uute andmete lisamist
    for item in tree.get_children():
        tree.delete(item)

    # Loo ühendus SQLite andmebaasiga
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()

    # Tee päring andmebaasist andmete toomiseks, koos ID-ga, kuid ID ei kuvata
    if search_query:
        cursor.execute("SELECT id, title, director, release_year, genre, duration, rating, language, country, description FROM movies WHERE title LIKE ?", ('%' + search_query + '%',))
    else:
        cursor.execute("SELECT id, title, director, release_year, genre, duration, rating, language, country, description FROM movies")

    rows = cursor.fetchall()

    # Lisa andmed tabelisse (Treeview), kuid ID-d ei kuvata
    for row in rows:
        tree.insert("", "end", values=row[1:], iid=row[0])  # iid määratakse ID-ks

    # Sulge ühendus andmebaasiga
    conn.close()

# Funktsioon, mis näitab valitud rea ID-d ja avab muutmise vormi
def on_update():
    selected_item = tree.selection()  # Võta valitud rida
    if selected_item:
        record_id = selected_item[0]  # iid (ID)
        open_update_window(record_id)
    else:
        messagebox.showwarning("Valik puudub", "Palun vali kõigepealt rida!")

# Funktsioon, mis avab uue akna andmete muutmiseks
def open_update_window(record_id):
    # Loo uus aken
    update_window = tk.Toplevel(root)
    update_window.title("Muuda filmi andmeid")

    # Loo andmebaasi ühendus ja toomine olemasolevad andmed
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    cursor.execute("SELECT title, director, release_year, genre, duration, rating, language, country, description FROM movies WHERE id=?", (record_id,))
    record = cursor.fetchone()
    conn.close()

    # Veergude nimed ja vastavad sisestusväljad
    labels = ["Pealkiri", "Režissöör", "Aasta", "Žanr", "Kestus", "Reiting", "Keel", "Riik", "Kirjeldus"]
    entries = {}

    for i, label in enumerate(labels):
        tk.Label(update_window, text=label).grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)
        entry = tk.Entry(update_window, width=50)
        entry.grid(row=i, column=1, padx=10, pady=5)
        entry.insert(0, record[i])
        entries[label] = entry

    # Salvestamise nupp
    save_button = tk.Button(update_window, text="Salvesta", command=lambda: update_record(record_id, entries, update_window))
    save_button.grid(row=len(labels), column=0, columnspan=2, pady=10)

# Funktsioon, mis uuendab andmed andmebaasis
def update_record(record_id, entries, window):
    # Koguge andmed sisestusväljadest
    title = entries["Pealkiri"].get()
    director = entries["Režissöör"].get()
    release_year = entries["Aasta"].get()
    genre = entries["Žanr"].get()
    duration = entries["Kestus"].get()
    rating = entries["Reiting"].get()
    language = entries["Keel"].get()
    country = entries["Riik"].get()
    description = entries["Kirjeldus"].get()

    # Andmete uuendamine andmebaasis
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE movies
        SET title=?, director=?, release_year=?, genre=?, duration=?, rating=?, language=?, country=?, description=?
        WHERE id=?
    """, (title, director, release_year, genre, duration, rating, language, country, description, record_id))
    conn.commit()
    conn.close()

    # Värskenda Treeview tabelit
    load_data_from_db(tree)

    # Sulge muutmise aken
    window.destroy()

    messagebox.showinfo("Salvestamine", "Andmed on edukalt uuendatud!")

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

# Create search frame
search_frame = tk.Frame(root)
search_frame.grid(row=len(labels)+1, column=0, columnspan=2, pady=10)

search_label = tk.Label(search_frame, text="Otsi filmi pealkirja järgi:")
search_label.grid(row=0, column=0)

search_entry = tk.Entry(search_frame)
search_entry.grid(row=0, column=1, padx=10)

search_button = tk.Button(search_frame, text="Otsi", command=on_search)
search_button.grid(row=0, column=2)


open_button = tk.Button(root, text="Lisa andmeid", command=add_data)
open_button.grid(row=len(labels)+3, column=0, columnspan=2, pady=20)

# Lisa Uuenda nupp, mis näitab selekteeritud rea ID-d
update_button = tk.Button(root, text="Uuenda", command=on_update)
update_button.grid(row=len(labels)+4, column=0, columnspan=2, pady=10)

# Create a frame for the Treeview widget
frame = tk.Frame(root)
frame.grid(row=len(labels)+2, column=0, columnspan=2, pady=20, sticky="nsew")

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
