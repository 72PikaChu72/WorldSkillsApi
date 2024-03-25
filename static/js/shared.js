fetch('/files/shared', {
    method: 'GET',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${document.cookie.split(';')[0].split('=')[1]}==`
    }
}).then(response => response.json()).then(data => {
    if (data.length > 0) {
        document.getElementById('table').style.display = 'block'
        console.log(data)
    }
    else {
        alert('Unauthorised or no shared files')
    }
})