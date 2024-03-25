document.getElementById("grantaccess_form").addEventListener("submit", function(event) {
    event.preventDefault();
    fetch('/files/'+document.getElementById("file").value+'/accesses', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${document.cookie.split(';')[0].split('=')[1]}==`
        },
        body: JSON.stringify({
            email: document.getElementById("email").value
        })
    }).then(response => {
        if (response.status == 200) {
            alert('Access granted')
        }
        else {
            alert('Wrong email or file does not exist')
        }
        return response.json()
    }).catch(error => {
        console.error('Error:', error)
    })
})