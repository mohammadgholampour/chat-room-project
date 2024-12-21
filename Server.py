from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# یک دیکشنری برای ذخیره نام‌های کاربری
users = {}

@app.route('/')
def index():
    return render_template('index.html')  # بارگذاری صفحه HTML

# دریافت و ذخیره نام کاربری
@socketio.on('set_username')
def handle_username(username):
    users[request.sid] = username  # ذخیره نام کاربری با شناسه ارتباط
    send(f"{username} has joined the chat!", broadcast=True)  # ارسال پیامی به همه کاربران

# دریافت پیام متنی
@socketio.on('message')
def handle_message(message):
    username = users.get(request.sid, "Unknown")  # دریافت نام کاربری با استفاده از شناسه
    send(f"{username}: {message}", broadcast=True)  # ارسال پیام به همه کاربران

# دریافت فایل
@socketio.on('file')
def handle_file(data):
    username = users.get(request.sid, "Unknown")
    file_name = data['file_name']
    file_data = data['file_data']
    
    # ارسال فایل به همه کاربران
    emit('file', {'file_name': file_name, 'file_data': file_data, 'username': username}, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="localhost", port=5000)
