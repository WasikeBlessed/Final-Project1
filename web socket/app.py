from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a secure secret key
socketio = SocketIO(app)  # Initialize Flask-SocketIO

# Flask route for the homepage
@app.route('/')
def index():
    return render_template('index.html')  # Load the client-side HTML file

# WebSocket event for handling client connection
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('message', {'data': 'Welcome to the WebSocket server!'})  # Send a welcome message

# WebSocket event for handling messages from the client
@socketio.on('send_message')
def handle_message(data):
    print(f"Received message: {data['message']}")
    emit('response', {'data': f"Server received your message: {data['message']}"})  # Send a response

# WebSocket event for handling client disconnection
@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True)  # Use `socketio.run` instead of `app.run` for WebSocket support
