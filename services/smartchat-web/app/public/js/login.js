async function loginReq(data) {
	try {
		let res = await fetch(`/api/login`, {
			method: 'POST',
			headers: {'Content-Type': 'application/json'},
			body: JSON.stringify(data)
		});
		return await res.json();
	} catch (error) {
		return [];
	}
}

var button1 = document.getElementById('login_btn');
button1.addEventListener("click", async function(){
	var username = document.getElementById('login-username').value;
	var password = document.getElementById('login-password').value;
	if (username.match(/^([a-zA-Z0-9_-]){1,50}$/) && password.match(/^([^]){1,50}$/)){
		var data = {'username':document.getElementById('login-username').value, 'password':document.getElementById('login-password').value}
		var response = await loginReq(data);
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
		alert('Wrong format of the username or password');
	}
})
