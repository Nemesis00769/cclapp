function computePublicKey() {
    let privateKey = $("#manualPrivateKey").val().trim();
    let G = 5;  // Generator
    let P = 23; // Prime modulus

    if (!privateKey || isNaN(privateKey)) {
        alert("Please enter a valid private key.");
        return;
    }

    let publicKey = BigInt(G) ** BigInt(privateKey) % BigInt(P);
    $("#manualPublicKey").val(publicKey.toString()); // Show calculated public key
}

function computeSecret() {
    let privateKey = $("#manualPrivateKey").val().trim();
    let receivedPublicKey = $("#receivedPublicKey").val().trim();
    let P = 23; // Prime modulus

    if (!privateKey || !receivedPublicKey || isNaN(privateKey) || isNaN(receivedPublicKey)) {
        alert("Please enter both a valid private key and received public key.");
        return;
    }

    let sharedSecret = BigInt(receivedPublicKey) ** BigInt(privateKey) % BigInt(P);
    $("#sharedSecret").text(sharedSecret.toString());
}

    $.ajax({
        url: "/compute_secret",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({
            private_key: privateKey,
            received_public_key: receivedPublicKey
        }),
        success: function(data) {
            $("#sharedSecret").text(data.shared_secret);
        },
        error: function() {
            alert("Error computing the shared secret. Please check your inputs.");
        }
    });



function encryptMessage() {
    const message = $('#message').val();
    let sharedSecret = $('#sharedSecret').text(); // this is the computed secret
    const manualSecret = $('#manualSecretForEncryption').val(); // user-entered secret

    // If manual secret is provided, use that instead
    if (manualSecret.trim() !== '') {
        sharedSecret = manualSecret;
    }

    if (!message || !sharedSecret) {
        alert("Please enter a message and either compute or enter a shared secret.");
        return;
    }

    $.ajax({
        url: '/encrypt',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ message: message, shared_secret: sharedSecret }),
        success: function(response) {
            $('#encryptedMessage').text(response.encrypted_message);
            alert("Message Encrypted and Stored!");
        },
        error: function(err) {
            alert("Encryption failed: " + err.responseJSON.error);
        }
    });
}


function decryptMessage() {
    const encryptedText = document.getElementById("decryptMessageTextarea").value.trim();
    const secret = document.getElementById("manualSharedSecret").value.trim();

    $.post('/decrypt', { encrypted_message: encryptedText, shared_secret: secret }, function (data) {
        $('#decryptedMessage').text(data.decrypted_message || data);
    }).fail(function (err) {
        $('#decryptedMessage').text("Error during decryption");
        console.error(err);
    });
}

function copyText(button) {
    let messageText = button.previousElementSibling.textContent; // Get text from span
    navigator.clipboard.writeText(messageText).then(() => {
        button.textContent = "✔ Copied!";
        setTimeout(() => {
            button.textContent = "📋 Copy";
        }, 1500);
    }).catch(err => {
        console.error("Failed to copy text: ", err);
    });
}




