// static/script.js
document.addEventListener('DOMContentLoaded', function () {
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    socket.on('update_editing_status', function(data) {
        // Update the editing status based on the data received
        console.log('Received update_editing_status:', data);

        if (data.editing_user && data.editing_user === socket.id) {
            // The current user has editing rights
            enableEditing();
            console.log('You have editing rights.');
        } else {
            // Another user has editing rights, or no user has editing rights
            disableEditing();
            console.log('You do not have editing rights.');
        }
    });

    socket.on('update_text', function(data) {
        // Update the text area content based on the data received
        document.getElementById('editor').value = data.text;
    });

    document.getElementById('editButton').addEventListener('click', function() {
        console.log('Sending request_editing');
        socket.emit('request_editing');
    });

    document.getElementById('releaseButton').addEventListener('click', function() {
        console.log('Sending release_editing');
        socket.emit('release_editing');
    });

    document.getElementById('editor').addEventListener('input', function() {
        // Send the updated text to the server
        socket.emit('update_text', {'text': this.value});
    });

    function enableEditing() {
        // Enable editing in the UI (e.g., by removing the 'readonly' attribute)
        document.getElementById('editor').removeAttribute('readonly');
    }

    function disableEditing() {
        // Disable editing in the UI (e.g., by adding the 'readonly' attribute)
        document.getElementById('editor').setAttribute('readonly', 'readonly');
    }
});
