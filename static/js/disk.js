fetch('/files/disk', {
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
        alert('Unauthorised or no files')
    }
})
function deleteFile(id) {
    fetch('/files/'+id, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${document.cookie.split(';')[0].split('=')[1]}==`
        }
    }).then(response => response.json()).then(data => {
        if (data['success']) {
            alert('File deleted')
            window.location.reload()
        }
        else {
            alert('Unauthorised or no files')
        }
    })
}

function deleteAccess(id,access) {
    console.log()
    fetch('/files/'+id+'/accesses', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${document.cookie.split(';')[0].split('=')[1]}==`
        },
        body: JSON.stringify({email: access})
    }).then(response => response.json()).then(data => {
        alert('Access deleted')
        window.location.reload()
    })
}