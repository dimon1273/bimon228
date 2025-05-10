import base64
import io
import threading
from socket import socket, AF_INET, SOCK_STREAM

from customtkinter import *
from tkinter import filedialog
from PIL import Image


class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('400x300')
        self.label = None

        # menu frame
        self.menu_frame = CTkFrame(self, width=30, height=300)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)
        self.is_show_menu = False
        self.speed_animate_menu = -5
        self.btn = CTkButton(self, text='▶️', command=self.toggle_show_menu, width=30)
        self.btn.place(x=0, y=0)


        self.theme_switcher = CTkOptionMenu(
            self,
            values=["light", "dark"],
            command=self.change_theme,
            width=100
        )
        self.theme_switcher.place(x=50, y=5)
        self.theme_switcher.set("light")

        # main
        self.chat_field = CTkTextbox(self, font=('Arial', 14, 'bold'), state='disable')
        self.chat_field.place(x=0, y=0)
        self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення:', height=40)
        self.message_entry.place(x=0, y=0)
        self.send_button = CTkButton(self, text='>', width=50, height=40, command=self.send_message, fg_color='#335A66')
        self.send_button.place(x=0, y=0)

        self.username = 'Yaroslav'
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('26.37.53.140', 8080))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"Не вдалося підключитися до сервера: {e}")

        self.adaptive_ui()

    def change_theme(self, value):
        if value == 'dark':
            set_appearance_mode('dark')
            self.configure(fg_color="#222222")
            self.menu_frame.configure(fg_color="#333333")
        else:
            set_appearance_mode('light')
            self.configure(fg_color="#FFFFFF")
            self.menu_frame.configure(fg_color="#DDDDDD") 

    def save_name(self):
        new_name = self.entry.get().strip()
        if new_name:
            self.username = new_name
            self.add_message(f"your new name: {self.username}")

    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.speed_animate_menu *= -1
            self.btn.configure(text='>', fg_color='#335A66')
            self.show_menu()
        else:
            self.is_show_menu = True
            self.speed_animate_menu *= -1
            self.btn.configure(text='<', fg_color='#335A66')
            self.show_menu()
            # setting menu widgets
            self.label = CTkLabel(self.menu_frame, text='Імʼя')
            self.label.pack(pady=30)
            self.entry = CTkEntry(self.menu_frame)
            self.entry.pack()
            self.save_button = CTkButton(self.menu_frame, text='save', command=self.save_name, fg_color='#335A66')
            self.save_button.pack()

    def show_menu(self):
        self.menu_frame.configure(width=self.menu_frame.winfo_width() + self.speed_animate_menu)
        if not self.menu_frame.winfo_width() >= 200 and self.is_show_menu:
            self.after(10, self.show_menu)
        elif self.menu_frame.winfo_width() >= 40 and not self.is_show_menu:
            self.after(10, self.show_menu)
            if self.label and self.entry:
                self.label.destroy()
                self.entry.destroy()
                self.save_button.destroy()

    def adaptive_ui(self):
        self.menu_frame.configure(height=self.winfo_height())
        self.chat_field.place(x=self.menu_frame.winfo_width())
        self.chat_field.configure(width=self.winfo_width() - self.menu_frame.winfo_width(),
                                   height=self.winfo_height() - 40)
        self.send_button.place(x=self.winfo_width() - 50, y=self.winfo_height() - 40)
        self.message_entry.place(x=self.menu_frame.winfo_width(), y=self.send_button.winfo_y())
        self.message_entry.configure(
            width=self.winfo_width() - self.menu_frame.winfo_width() - self.send_button.winfo_width())

        self.after(50, self.adaptive_ui)

    def add_message(self, text):
        self.chat_field.configure(state='normal')
        self.chat_field.insert(END, text + '\n')
        self.chat_field.configure(state='disable')

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.add_message(f"{self.username}: {message}")
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                pass
        self.message_entry.delete(0, END)

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break
        self.sock.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        msg_type = parts[0]

        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                self.add_message(f"{author}: {message}")
        elif msg_type == "IMAGE":
            if len(parts) >= 4:
                author = parts[1]
                filename = parts[2]

                self.add_message(f"{author} надіслав(ла) зображення: {filename}")

        else:
            self.add_message(line)


win = MainWindow()
win.mainloop()