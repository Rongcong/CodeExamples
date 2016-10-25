$(document).ready(function() {
	$("#new_user").submit(function(event) {
		event.preventDefault();
		$(".error_block").empty();
		var user_info = {};
		user_info["username"] = $("#new_username_input").val();
		user_info["firstname"] = $("#new_firstname_input").val();
		user_info["lastname"] = $("#new_lastname_input").val();
		user_info["password1"] = $("#new_password1_input").val();
		user_info["password2"] = $("#new_password2_input").val();
		user_info["email"] = $("#new_email_input").val();

		var error_msg_list = check_errors("user", user_info);
		if (error_msg_list.length > 0) {
			for (i = 0; i < error_msg_list.length; i++) {
				var e = $("<p class='error'>" + error_msg_list[i] + "</p>");
				$(".error_block").append(e);
			}
			return;
		}

		$.ajax({
			type: "POST",
			contentType: "application/json; charset=UTF-8",
			url: "api/v1/user",
			data: JSON.stringify(user_info),
			success: function(data) {
				window.location.href = "/login";
			},
			error: function(response) {
				error = JSON.parse(response.responseText);

				for (var i = 0; i < error["errors"].length; i++) {
					var e = $("<p class='error'>" + error["errors"][i]["message"] + "</p>");
					$(".error_block").append(e);
				}
				return;
			}
		})
	});

});