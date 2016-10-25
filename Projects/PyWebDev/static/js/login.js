$(document).ready(function() {
	$("#login_user").submit(function(event) {
		event.preventDefault();
		var username = $("#login_username_input").val();
		var password = $("#login_password_input").val();
		$(".error_block").empty();

		$.ajax({
			type: "POST",
			contentType: "application/json; charset=UTF-8",
			url: "api/v1/login",
			data: JSON.stringify({
				"username": username,
				"password": password
			}),

			success: function(data) {
				var results = new RegExp('[\?]url=([^&#]*)').exec(window.location.href);
				if (results == null) {
					window.location.href = "/";
				}
				else {
					window.location.href = results[1];
				}
			},
			
			error: function(response) {
				error = JSON.parse(response.responseText);
				for (var i = 0; i < error["errors"].length; i++) {
					var e = $("<p class='error'>" + error["errors"][i]["message"] + "</p>");
					$(".error_block").append(e);
				}
			}
		});
	});
});