async function registerReq(data) {
	try {
		let res = await fetch(`/api/register`, {
			method: 'POST',
			headers: {'Content-Type': 'application/json'},
			body: JSON.stringify(data)
		});
		return await res.json();
	} catch (error) {
		return [];
	}
}

var button1 = document.getElementById('reg_btn');
button1.addEventListener("click", async function(){
	var username = document.getElementById('username').value;
	var password1 = document.getElementById('password1').value;
    var password2 = document.getElementById('password2').value;
	if (username.match(/^([a-zA-Z0-9_-]){1,50}$/) && password1.match(/^([^]){1,50}$/)){
        if (password1 == password2){
            var data = {'username':username, 'password1':password1, 'password2':password2}
            var response = await registerReq(data);
            if ('error' in response){
                alert(response.error);
            } else {
                if ('redirect' in response){
                    window.location.href = response.redirect;
                } else {
                    alert('Ok. You can go to /home now');
                }
            }
        } else {
            alert("Passwords don't match");
        }
	} else {
		alert('Wrong format of the username or password');
	}
})
