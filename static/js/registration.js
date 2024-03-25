document.getElementById("registration_form").addEventListener("submit", function(event) {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const first_name = document.getElementById("first_name").value;
    const last_name = document.getElementById("last_name").value;

    fetch("/registration", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            email: email,
            password: password,
            first_name: first_name,
            last_name: last_name
        })
    }).then(response => response.json()).then(data => {
        if(data['success']){
            document.cookie = `bearer=${data['token']}; path=/;`
            alert("Регистрация прошла успешно!")
        }
        else{
            alert(data['message'])
        }
    }
    )}
)
