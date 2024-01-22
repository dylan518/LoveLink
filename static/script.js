// Called when Google JavaScript API Library is loaded
function startApp() {
    gapi.load('auth2', function () {
        // Initialize Google Auth2
        auth2 = gapi.auth2.init({
            client_id: '1038325471078-255fgp3191kfd7sfrsbqqcbiim4vonq1.apps.googleusercontent.com'
            // Request scopes in addition to 'profile' and 'email'
            // scope: 'additional_scope'
        });
        attachSignin(document.getElementById('signin-button'));
    });
}

// Attach the sign-in process to the custom button
function attachSignin(element) {
    auth2.attachClickHandler(element, {},
        function (googleUser) {
            onSignIn(googleUser);
        }, function (error) {
            console.log(JSON.stringify(error, undefined, 2));
        });
}

// Handle successful sign-ins.
function onSignIn(googleUser) {
    var profile = googleUser.getBasicProfile();
    var id_token = googleUser.getAuthResponse().id_token;
    console.log('ID Token: ' + id_token);

    // Send the ID token to your server with an HTTPS POST request.
    fetch('/token-signin', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ idtoken: id_token })
    })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (data.status === 'success') {
                // Handle successful sign-in on client side.
                document.getElementById('user-info').innerText = 'Hello, ' + profile.getName();
            } else {
                console.error('Failed to authenticate user.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// Sign out the user
function signOut() {
    var auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut().then(function () {
        console.log('User signed out.');
        document.getElementById('user-info').innerText = '';
    });
}
function onSignIn(googleUser) {
    var id_token = googleUser.getAuthResponse().id_token;
    console.log('ID Token: ' + id_token);

    // Send the ID token to your server with an HTTPS POST request.
    fetch('/token-signin', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ idtoken: id_token })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Handle successful sign-in on client side.
                // Display user's name and email in 'user-info' div
                document.getElementById('user-info').innerHTML = 'Hello, ' + data.name + ' (' + data.email + ')';
            } else {
                console.error('Failed to authenticate user.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// Load the Google auth2 library
startApp();
