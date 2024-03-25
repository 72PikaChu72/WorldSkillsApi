document.getElementById("authorization_form").addEventListener("submit", function(event) {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    fetch("/authorization", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            email: email,
            password: password
        })
    }).then(response => response.json()).then(data => {
        if(data['success']){
            document.cookie = `bearer=${data['token']}; path=/;`
            alert("Авторизация прошла успешно!")
        }
        else{
            alert(data['message'])
        }
    }
    )}
)
