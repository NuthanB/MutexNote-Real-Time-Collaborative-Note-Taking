from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit
import threading
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = '13221334'  # Set a secret key for session management
socketio = SocketIO(app)

# Introduce lock variables
editing_lock = False
wait_queue = []
editing_user = None
current_user_start_time = None


def get_editing_user():
    return editing_user

def set_editing_user(sid):
    global editing_user 
    editing_user = sid

def clear_editing_user():
    global editing_user 
    global editing_lock
    editing_lock = False
    editing_user=None

@app.route('/stop_timer', methods=['POST', 'GET'])
def stop_timer():
    global editing_lock
    global editing_user
    global current_user_start_time

    print(f"Timer expired for {editing_user}, transferring access to the next user.")
    editing_user = None
    editing_lock = False

    # Check if there are users in the wait queue
    if wait_queue:
        next_user = wait_queue.pop(0)
        set_editing_user(next_user)
        editing_lock = True
        socketio.emit('update_editing_status', {'editing_user': editing_user, 'editing_lock': editing_lock})
    else:
        socketio.emit('update_editing_status', {'editing_user': None, 'editing_lock': editing_lock})
        current_user_start_time = None
    return {'status': 'success'} 

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    emit('update_editing_status', {'editing_user': editing_user, 'editing_lock': editing_lock})

@socketio.on('disconnect')
def handle_disconnect():
    if editing_user == request.sid:
        set_editing_user(None)
        editing_lock = False 
        emit('update_editing_status', {'editing_user': None, 'editing_lock': editing_lock}, broadcast=True)

@socketio.on('request_editing')
def handle_request_editing():
    
    global editing_lock
    global editing_user
    global current_user_start_time

    print(f"Received request_editing from {request.sid}, editing_user: {editing_user}, editing_lock: {editing_lock}")

    if editing_user is None and not editing_lock:
        set_editing_user(request.sid)
        editing_user = request.sid
        editing_lock = True
        emit('update_editing_status', {'editing_user': editing_user, 'editing_lock': editing_lock}, broadcast=True)
        
    else:

        print(request.sid)
        if request.sid not in wait_queue:
            wait_queue.append(request.sid)
            print(wait_queue)

        emit('update_editing_status', {'editing_user': editing_user, 'editing_lock': editing_lock}, room=request.sid)

    print(f"Updated editing status. New editing_user: {editing_user}, editing_lock: {editing_lock}")

@socketio.on('release_editing')
def handle_release_editing():
    global editing_lock
    global editing_user
    global current_user_start_time

    print(f"Received release_editing from {request.sid}, editing_user: {editing_user}, editing_lock: {editing_lock}")

    if editing_user == request.sid:
        set_editing_user(None)
        editing_lock = False
        emit('update_editing_status', {'editing_user': None, 'editing_lock': editing_lock}, broadcast=True)

        # Cancel the current user's timer
        current_user_start_time = None
        print(f"Released editing rights for {request.sid}")

        # Check if there are users in the wait queue
        if wait_queue:
            next_user = wait_queue.pop(0)
            set_editing_user(next_user)
            editing_lock = True
            emit('update_editing_status', {'editing_user': editing_user, 'editing_lock': editing_lock}, broadcast=True)
            
    else:
        print(f"Attempted to release editing rights, but user {request.sid} does not have them. Editing lock: {editing_lock}")

@socketio.on('update_text')
def handle_update_text(data):
    if editing_user == request.sid:
        print(request.sid)
        emit('update_text', data, broadcast=True)

if __name__ == '__main__':
    # Enable debug mode and listen on all interfaces
    app.debug = True
    socketio.run(app, host='0.0.0.0')

