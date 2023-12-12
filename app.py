# app.py
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = '13221334'  # Set a secret key for session management
socketio = SocketIO(app)

# Introduce a lock variable
editing_lock = False

def get_editing_user():
    return session.get('editing_user')

def set_editing_user(sid):
    session['editing_user'] = sid
    print(session['editing_user'])

def clear_editing_user():
    session.pop('editing_user', None)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    emit('update_editing_status', {'editing_user': get_editing_user(), 'editing_lock': editing_lock})

@socketio.on('disconnect')
def handle_disconnect():
    if get_editing_user() == request.sid:
        clear_editing_user()
        emit('update_editing_status', {'editing_user': None, 'editing_lock': editing_lock}, broadcast=True)

@socketio.on('request_editing')
def handle_request_editing():
    global editing_lock  # Declare it as global only here
    print(f"Received request_editing from {request.sid}, editing_user: {get_editing_user()}, editing_lock: {editing_lock}")
    if get_editing_user() is None and not editing_lock:
        set_editing_user(request.sid)
        editing_lock = True
        emit('update_editing_status', {'editing_user': get_editing_user(), 'editing_lock': editing_lock}, broadcast=True)
    else:
        emit('update_editing_status', {'editing_user': get_editing_user(), 'editing_lock': editing_lock}, room=request.sid)
    print(f"Updated editing status. New editing_user: {get_editing_user()}, editing_lock: {editing_lock}")

@socketio.on('release_editing')
def handle_release_editing():
    global editing_lock  # Declare it as global only here
    print(f"Received release_editing from {request.sid}, editing_user: {get_editing_user()}, editing_lock: {editing_lock}")
    if get_editing_user() == request.sid:
        clear_editing_user()
        editing_lock = False
        emit('update_editing_status', {'editing_user': None, 'editing_lock': editing_lock}, broadcast=True)
        print(f"Released editing rights for {request.sid}")
    else:
        print(f"Attempted to release editing rights, but user {request.sid} does not have them. Editing lock: {editing_lock}")

@socketio.on('update_text')
def handle_update_text(data):
    if get_editing_user() == request.sid:
        emit('update_text', data, broadcast=True)

if __name__ == '__main__':
    # Enable debug mode and listen on all interfaces
    app.debug = True
    socketio.run(app, host='0.0.0.0')
