import customtkinter as ctk
import socket
import threading
from tkinter import filedialog, messagebox
import os

class ClientGUI:
    def __init__(self, client_name):
        # تنظیمات GUI
        self.root = ctk.CTk()
        self.root.title("Chat Room")
        self.root.geometry("500x600")
        ctk.set_appearance_mode("dark")

        # اتصال به سرور
        self.client_name = client_name
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('localhost', 8080)
        self.socket.connect(self.server_address)

        # المان‌های رابط کاربری
        self.chat_display = ctk.CTkTextbox(self.root, width=480, height=400, state="disabled")
        self.chat_display.pack(pady=10)

        self.message_entry = ctk.CTkEntry(self.root, placeholder_text="Type your message here...", width=400)
        self.message_entry.pack(pady=10, side="left", padx=(20, 0))

        self.send_button = ctk.CTkButton(self.root, text="Send", command=self.send_message)
        self.send_button.pack(pady=10, side="left")

        self.file_button = ctk.CTkButton(self.root, text="Send File", command=self.send_file)
        self.file_button.pack(pady=10, side="left", padx=(10, 20))

        # ارسال نام کاربر به سرور
        self.socket.send(bytes(self.client_name, encoding='utf-8'))

        # اجرای نخ‌های ارسال و دریافت
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def send_message(self):
        message = self.message_entry.get()
        if message:
            try:
                self.socket.send(bytes(message, encoding='utf-8'))
                self.message_entry.delete(0, ctk.END)
            except:
                messagebox.showerror("Error", "Failed to send message!")
                self.root.quit()

    def send_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                file_name = os.path.basename(file_path)
                with open(file_path, 'rb') as file:
                    file_data = file.read()
                # ارسال پیام برای اعلام ارسال فایل
                self.socket.send(bytes(f"FILE:{file_name}", encoding='utf-8'))
                # ارسال محتوا
                self.socket.send(file_data)
                messagebox.showinfo("Success", "File sent successfully!")
            except:
                messagebox.showerror("Error", "Failed to send file!")

    def receive_messages(self):
        while True:
            try:
                data = self.socket.recv(4096).decode("utf-8")
                if data.startswith("FILE:"):
                    # دریافت اطلاعات فایل
                    file_name = data.split(":")[1]
                    file_data = self.socket.recv(4096)
                    save_path = filedialog.asksaveasfilename(initialfile=file_name)
                    if save_path:
                        with open(save_path, 'wb') as file:
                            file.write(file_data)
                        messagebox.showinfo("Success", f"File {file_name} received and saved!")
                else:
                    # پیام چت
                    self.chat_display.configure(state="normal")
                    self.chat_display.insert(ctk.END, data + "\n")
                    self.chat_display.configure(state="disabled")
            except:
                self.socket.close()
                break

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python ClientGUI.py [YourName]")
        exit()

    client_name = sys.argv[1]
    app = ClientGUI(client_name)
    app.run()
