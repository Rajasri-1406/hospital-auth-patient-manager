document.getElementById("search").addEventListener("click", function() {
    let patientId = document.getElementById("patient_id").value;
    fetch('/search', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({patient_id: patientId})
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            document.getElementById("name").value = data.name;
            document.getElementById("dob").value = data.dob;
            document.getElementById(data.gender.toLowerCase()).checked = true;
            document.getElementById("age").value = data.age;
            document.getElementById("address").value = data.address;
            document.getElementById("phone").value = data.phone;
            document.getElementById("patient_type").value = data.patient_type;
        }
    });
});

document.getElementById("enable").addEventListener("click", function() {
    document.querySelectorAll("input, textarea, select").forEach(element => {
        element.disabled = false;
    });

    // Enable all action buttons
    document.getElementById("save").disabled = false;
    document.getElementById("clear").disabled = false;
    document.getElementById("update").disabled = false;
    document.getElementById("delete").disabled = false;
    document.getElementById("commit").disabled = false;
});

document.getElementById("save").addEventListener("click", function() {
    let formData = new FormData(document.getElementById("patient-form"));
    fetch('/save', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        // Check if the response is not HTML (i.e., response is JSON)
        if (response.ok) {
            return response.json();  // parse JSON if the response is successful
        } else {
            return response.text();  // else return the raw HTML error message
        }
    })
    .then(data => {
        if (typeof data === 'string') {
            alert('Error: ' + data);  // handle HTML response as error
        } else {
            alert(data.status);  // handle JSON response normally
        }
    })
    .catch(error => {
        alert('Error saving data: ' + error);
    });
});

document.getElementById("clear").addEventListener("click", function() {
    document.querySelectorAll("input, textarea, select").forEach(element => {
        if (element.id !== "patient_id") {
            element.value = '';
            element.checked = false;
        }
    });
});

document.getElementById("update").addEventListener("click", function() {
    let formData = new FormData(document.getElementById("patient-form"));
    fetch('/update', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        alert(data.status);
    });
});

document.getElementById("delete").addEventListener("click", function() {
    let patientId = document.getElementById("patient_id").value;
    fetch('/delete', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({patient_id: patientId})
    })
    .then(response => response.json())
    .then(data => {
        alert(data.status);
    });
});


// Commit Button
document.getElementById("commit").addEventListener("click", function() {
    let formData = new FormData(document.getElementById("patient-form"));
    fetch('/commit', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())  // Ensure the response is treated as JSON
    .then(data => {
        alert(data.status);  // Show status from the response
        // Disable buttons after commit
        document.querySelectorAll("button").forEach(button => {
            if (button.id !== "search" && button.id !== "commit") {
                button.disabled = true;
            }
        });
    })
    .catch(error => {
        alert('Error committing data: ' + error);  // Handle errors
    });
});
