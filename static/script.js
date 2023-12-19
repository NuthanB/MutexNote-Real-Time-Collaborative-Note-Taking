// static/script.js
document.addEventListener('DOMContentLoaded', function () {
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    var timerSeconds = 60; 

    socket.on('update_editing_status', function(data) {
        // Update the editing status based on the data received
        console.log('Received update_editing_status:', data);

        if (data.editing_user && data.editing_user === socket.id) {
            // The current user has editing rights
            enableEditing();
            startTimer();
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
        stopTimer();
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
    

    
    function startTimer() {
        var timerElement = document.getElementById('timer');
        timerElement.textContent = 'Timer: 1:00';

        var timerInterval = setInterval(function() {
            timerSeconds--;

            var minutes = Math.floor(timerSeconds / 60);
            var seconds = timerSeconds % 60;

            timerElement.textContent = `Timer: ${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;

            if (timerSeconds <= 0) {
                clearInterval(timerInterval);
                timerElement.textContent = 'Timer: 0:00';
                disableEditing();
                stopTimer(); // Disable editing after the timer reaches 0
                stopTimerOnServer();
            }
        }, 1000);
    }

    function stopTimer() {
        var timerElement = document.getElementById('timer');
        timerElement.textContent = 'Timer: 1:00';
        timerSeconds = 60;  // Reset timer value
    }

    function stopTimerOnServer() {
        // Send an AJAX request to the server to stop the timer
        fetch('/stop_timer', {
            method: 'GET',
        })
        .then(response => response.json())
        .then(data => {
            console.log('Server response:', data);
            // Handle the server's response as needed
        })
        .catch(error => {
            console.error('Error stopping timer on the server:', error);
        });
    }
});
