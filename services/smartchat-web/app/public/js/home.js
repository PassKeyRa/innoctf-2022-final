async function createRoom(data) {
	try {
		let res = await fetch(`/api/createroom`, {
			method: 'POST',
			headers: {'Content-Type': 'application/json'},
			body: JSON.stringify(data)
		});
		return await res.json();
	} catch (error) {
		return [];
	}
}

var button = document.getElementById("room_btn");
button.addEventListener("click", async function(){
	var room_name = document.getElementById('room-name').value;
    var data = {"roomname": room_name};
    var response = await createRoom(data);
    if ('error' in response){
        alert(response.error);
    } else {
        location.reload();
    }
})