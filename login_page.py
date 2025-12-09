"""login_page.py

Modular login UI builder used by the main application.
"""
from tkinter import Frame, Label, Button, Entry, PhotoImage, StringVar, messagebox, Toplevel
import sqlite3
from Database import db_utils


def build_login_frame(parent, db_path, on_login_success=None, on_show_register=None):
    """Create and return a Frame for login UI.

    on_login_success: optional callable invoked when login succeeds
    on_show_register: optional callable to show register screen
    """
    frame = Frame(parent, bg="#525561")

    frame._backgroundImage = PhotoImage(file="assets/image_1.png")
    bg_imageLogin = Label(frame, image=frame._backgroundImage, bg="#525561")
    bg_imageLogin.place(x=120, y=28)

    frame._header_left = PhotoImage(file="assets/headerText_image.png")
    Label(bg_imageLogin, image=frame._header_left, bg="#272A37").place(x=60, y=45)
    Label(bg_imageLogin, text="Electric Bill Calculator", fg="#FFFFFF",
          font=("yu gothic ui bold", 20 * -1), bg="#272A37").place(x=110, y=45)

    Label(bg_imageLogin, text="Login to continue", fg="#FFFFFF",
          font=("yu gothic ui Bold", 28 * -1), bg="#272A37").place(x=75, y=121)

    email_var = StringVar()
    pwd_var = StringVar()

    frame._email_img = PhotoImage(file="assets/email.png")
    email_container = Label(bg_imageLogin, image=frame._email_img, bg="#272A37")
    email_container.place(x=76, y=242)
    Label(email_container, text="Email account", fg="#FFFFFF",
          font=("yu gothic ui SemiBold", 13 * -1), bg="#3D404B").place(x=25, y=0)
    Entry(email_container, bd=0, bg="#3D404B", highlightthickness=0, font=("yu gothic ui SemiBold", 16 * -1),
          textvariable=email_var).place(x=8, y=17, width=354, height=27)

    frame._pwd_img = PhotoImage(file="assets/email.png")
    pwd_container = Label(bg_imageLogin, image=frame._pwd_img, bg="#272A37")
    pwd_container.place(x=80, y=330)
    Label(pwd_container, text="Password", fg="#FFFFFF", font=("yu gothic ui SemiBold", 13 * -1),
          bg="#3D404B").place(x=25, y=0)
    Entry(pwd_container, bd=0, bg="#3D404B", highlightthickness=0, font=("yu gothic ui SemiBold", 16 * -1),
          textvariable=pwd_var, show='•').place(x=8, y=17, width=354, height=27)

    frame._submit_img = PhotoImage(file="assets/button_1.png")

    def login():
        if not (email_var.get().strip() and pwd_var.get()):
            messagebox.showinfo("Failed", "Please enter email and password")
            return
        conn = sqlite3.connect(db_path)
        ok = db_utils.verify_user(conn, email_var.get().strip(), pwd_var.get())
        conn.close()
        if ok:
            messagebox.showinfo("Success", "Logged in Successfully :)")
            if callable(on_login_success):
                on_login_success()
        else:
            messagebox.showinfo("Failed", "Email or password incorrect")

    Login_button_1 = Button(bg_imageLogin, image=frame._submit_img, borderwidth=0, highlightthickness=0,
                            relief="flat", activebackground="#272A37", cursor="hand2", command=login)
    Login_button_1.place(x=120, y=445, width=333, height=65)

    def forgot_password():
        win = Toplevel()
        window_width = 350
        window_height = 350
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        position_top = int(screen_height / 4 - window_height / 4)
        position_right = int(screen_width / 2 - window_width / 2)
        win.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')
        win.title('Forgot Password')
        win.configure(background='#272A37')
        win.resizable(False, False)

        email_entry3 = Entry(win, bg="#3D404B", font=("yu gothic ui semibold", 12), highlightthickness=1, bd=0)
        email_entry3.place(x=40, y=80, width=256, height=50)
        email_entry3.config(highlightbackground="#3D404B", highlightcolor="#206DB4")
        Label(win, text='• Email', fg="#FFFFFF", bg='#272A37', font=("yu gothic ui", 11, 'bold')).place(x=40, y=50)

        new_password_entry = Entry(win, bg="#3D404B", font=("yu gothic ui semibold", 12), show='•', highlightthickness=1, bd=0)
        new_password_entry.place(x=40, y=180, width=256, height=50)
        new_password_entry.config(highlightbackground="#3D404B", highlightcolor="#206DB4")
        Label(win, text='• New Password', fg="#FFFFFF", bg='#272A37', font=("yu gothic ui", 11, 'bold')).place(x=40, y=150)

        def change_password():
            if not email_entry3.get().strip() or not new_password_entry.get():
                messagebox.showerror("Error", "All Fields are required")
                return
            conn = sqlite3.connect(db_path)
            exists = db_utils.user_exists(conn, email_entry3.get().strip())
            if not exists:
                messagebox.showerror("Error", "Email does not exist")
                conn.close()
                return
            db_utils.update_password(conn, email_entry3.get().strip(), new_password_entry.get())
            conn.close()
            messagebox.showinfo('Confirmed', "Password changed successfully :)")
            win.destroy()

        update_pass = Button(win, fg='#f8f8f8', text='Update Password', bg='#1D90F5',
                             font=("yu gothic ui", 12, "bold"), cursor='hand2', relief="flat", bd=0,
                             highlightthickness=0, activebackground="#1D90F5", command=change_password)
        update_pass.place(x=40, y=260, width=256, height=45)

    forgotPassword = Button(bg_imageLogin, text="Forgot Password", fg="#206DB4",
                            font=("yu gothic ui Bold", 15 * -1), bg="#272A37", bd=0,
                            activebackground="#272A37", activeforeground="#ffffff", cursor="hand2",
                            command=forgot_password)
    forgotPassword.place(x=210, y=400, width=150, height=35)

    def go_to_signup():
        if callable(on_show_register):
            on_show_register()

    signUp = Button(bg_imageLogin, text="Sign Up", fg="#206DB4",
                    font=("yu gothic ui Bold", 15 * -1), bg="#272A37", bd=0,
                    activebackground="#272A37", activeforeground="#ffffff", cursor="hand2",
                    command=go_to_signup)
    signUp.place(x=90, y=400, width=100, height=35)

    return frame


if __name__ == "__main__":
    from tkinter import Tk

    root = Tk()
    root.geometry('1240x650+100+100')
    frm = build_login_frame(root, "Database/AccountSystem.db", on_login_success=lambda: print("login ok"))
    frm.pack(fill='both', expand=True)
    root.mainloop()
    
