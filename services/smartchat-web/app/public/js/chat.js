async function sendMessage(data) {
	try {
		let res = await fetch(`/api/sendmessage`, {
			method: 'POST',
			headers: {'Content-Type': 'application/json'},
			body: JSON.stringify(data)
		});
		return await res.json();
	} catch (error) {
		return [];
	}
}

var button = document.getElementById("send_btn");
button.addEventListener("click", async function(){
    var room_name = window.location.search.substr(1).split('=')[1];
    var message = document.getElementById('message_form').value;
    var data = {"roomname": room_name, 'message': message};
    var response = await sendMessage(data);
    if ('error' in response){
        alert(response.error);
    } else {
        location.reload();
    }
})
