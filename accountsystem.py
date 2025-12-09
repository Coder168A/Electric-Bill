"""accountsystem.py

Lightweight orchestrator that composes the modular login and register
frames into a single application window.
"""
from tkinter import Tk, Frame, messagebox
import sqlite3

from register_page import build_register_frame
from login_page import build_login_frame
from Database import db_utils
from electric_bill_gui import open_main_app


DB_PATH = "Database/AccountSystem.db"


def main():
    root = Tk()
    root.title('Electric Bill Account System')

    # center window
    height = 650
    width = 1240
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")

    # ensure DB/table exists
    conn = sqlite3.connect(DB_PATH)
    db_utils.ensure_table(conn)
    conn.close()

    # container frames
    sign_in = Frame(root)
    sign_up = Frame(root)
    success = Frame(root)
    account = Frame(root)
    for frame in (sign_in, sign_up, success, account):
           frame.grid(row=0, column=0, sticky="nsew")
    
    # Configure grid weights so frames expand to fill window
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    def show_frame(frame):
        frame.tkraise()

    # callback: after successful registration, show success screen
    def on_register_success():
        show_frame(success)

    # callback: from success screen, go to login
    def on_success_to_login():
        show_frame(sign_in)

    # callback: after successful login, show account system
    def on_login_success():
        show_frame(account)

    # callback: logout from account system back to login
    def on_logout():
        show_frame(sign_in)

    # build modular UIs inside the containers
    reg_frame = build_register_frame(sign_up, DB_PATH, on_show_login=lambda: show_frame(sign_in), on_register_success=on_register_success)
    reg_frame.pack(fill='both', expand=True)

    login_frame = build_login_frame(sign_in, DB_PATH, on_login_success=on_login_success, on_show_register=lambda: show_frame(sign_up))
    login_frame.pack(fill='both', expand=True)

    # build account/billing system frame
    account_frame = open_main_app(parent=account, on_logout=on_logout)
    account_frame.pack(fill='both', expand=True)

    # build success screen
    from tkinter import Label, Button
    success_frame = Frame(success, bg="#525561")
    success_frame.pack(fill='both', expand=True)
    
    Label(success_frame, text="Registration Successful!", fg="#FFFFFF", font=("Arial", 24, "bold"), bg="#525561").pack(pady=50)
    Label(success_frame, text="Your account has been created successfully.", fg="#FFFFFF", font=("Arial", 12), bg="#525561").pack(pady=10)
    Button(success_frame, text="Proceed to Login", command=on_success_to_login, bg="#206DB4", fg="white", font=("Arial", 12), padx=20, pady=10).pack(pady=20)

    # show login by default
    show_frame(sign_in)

    root.resizable(False, False)
    root.mainloop()


if __name__ == "__main__":
    main()

