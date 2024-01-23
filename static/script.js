function handleCredentialResponse(response) {
    console.log("Encoded JWT ID token: " + response.credential);

    fetch('/token-signin', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ idToken: response.credential })
    })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            if (data.status === 'success') {
                // Redirect to the interests page if login is successful
                window.location.href = '/interests';
            } else {
                // Handle login failure
                document.getElementById('user-info').innerText = 'Login failed: ' + data.message;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('user-info').innerText = 'Error: ' + error;
        });
}


// Function to initialize Google Identity Services
function initializeGoogleSignIn() {
    google.accounts.id.initialize({
        client_id: "1038325471078-255fgp3191kfd7sfrsbqqcbiim4vonq1.apps.googleusercontent.com",
        callback: handleCredentialResponse
    });

    google.accounts.id.renderButton(
        document.getElementById('buttonDiv'), // Ensure you have a div with id 'buttonDiv' in your HTML
        { theme: 'outline', size: 'large' }  // Customization attributes
    );

    google.accounts.id.prompt(); // Display the One Tap dialog
}

// Sign out the user
function signOut() {
    // Clear user info
    document.getElementById('user-info').innerText = '';

    // Implement additional sign-out functionality as needed
    console.log('User signed out.');
}

// Load the Google Identity Services library and initialize sign-in
window.onload = function () {
    initializeGoogleSignIn();
};

// Wait for the DOM to be fully loaded before fetching and displaying the user count
document.addEventListener('DOMContentLoaded', function () {
    fetchUserCount();
});

// Function to fetch and display the user count
function fetchUserCount() {
    fetch('/user-count')
        .then(response => response.json())
        .then(data => {
            // Ensure the element is present before trying to set its content
            var userCountElement = document.getElementById('user-count');
            if (userCountElement) {
                userCountElement.textContent = data.user_count;
            } else {
                console.error('Element #user-count not found on the page.');
            }
        })
        .catch(error => {
            console.error('Error fetching user count:', error);
        });
}
function submitInterest() {
    const interestName = document.getElementById('interest-name').value;
    if (!interestName) {
        displayMessage('Please enter a name.', 'error');
        return;
    }

    fetch('/add-interest', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: interestName })
    })
        .then(response => response.json())
        .then(data => {
            displayMessage(data.message, data.status === 'success' ? 'success' : 'error');
            if (data.status === 'success') {
                // Append the new interest to the interest list in the DOM
                const interestList = document.getElementById('interest-list');
                const interestItem = document.createElement('span');
                interestItem.className = 'interest-item';
                interestItem.innerHTML = `
                ${interestName}
                <button onclick="removeInterest('${interestName}');" class="remove-interest-btn">X</button>
            `;
                interestList.appendChild(interestItem);
                // Clear the input field
                document.getElementById('interest-name').value = '';
            }
        })
        .catch(error => {
            console.error('Error adding interest:', error);
            displayMessage('Failed to add interest.', 'error');
        });
}

function displayMessage(message, type) {
    const messageDiv = document.getElementById('submission-message');
    messageDiv.textContent = message;
    messageDiv.className = type; // You can use this class to style the message (e.g., color)

    // Set a timeout to clear the message after 1000 milliseconds (1 second)
    setTimeout(function () {
        messageDiv.textContent = '';
        messageDiv.className = '';
    }, 1000); // 1000 milliseconds = 1 second
}



// Fetch the user count when the window loads
window.onload = function () {
    initializeGoogleSignIn();
    fetchUserCount();
};

// Function to fetch and display the user count
function fetchUserCount() {
    return fetch('/user-count')
        .then(response => response.json())
        .then(data => {
            document.getElementById('user-count').textContent = data.user_count;
        })
        .catch(error => {
            console.error('Error fetching user count:', error);
            document.getElementById('user-count').textContent = 'Error fetching user count';
        });
}

function removeInterest(interestName) {
    fetch('/remove-interest', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: interestName })
    })
        .then(response => response.json())
        .then(data => {
            displayMessage(data.message, data.status === 'success' ? 'success' : 'error');
            if (data.status === 'success') {
                // Update the interface to reflect the interest removal
                const interestList = document.getElementById('interest-list');
                const interestItems = document.querySelectorAll('.interest-item');
                interestItems.forEach(item => {
                    if (item.textContent.trim().startsWith(interestName)) {
                        interestList.removeChild(item);
                    }
                });
            }
        })
        .catch(error => {
            console.error('Error removing interest:', error);
            displayMessage('Failed to remove interest.', 'error');
        });
}
function signOut() {
    // Redirect to the logout route that clears the session
    window.location.href = '/logout';
}