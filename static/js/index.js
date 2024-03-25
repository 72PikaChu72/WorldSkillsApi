document.getElementById('Logout').addEventListener('click', function() {
    
    fetch('/logout', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${document.cookie.split(';')[0].split('=')[1]}==`
        }
    })
    document.cookie = 'bearer=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
})