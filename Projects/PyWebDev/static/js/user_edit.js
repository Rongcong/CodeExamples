$(document).ready(function() {
	$.ajax({
		type: "GET",
		contentType: "application/json; charset=UTF-8",
		url: "/api/v1/user",
		success: function(data) {
			$("#update_firstname_input").val(data["firstname"]);
			$("#update_lastname_input").val(data["lastname"]);
			$("#update_email_input").val(data["email"]);
		},
		error: function(error) {
			return;
		}
	});


	$("#update_user").submit(function(event) {
		event.preventDefault();
		$(".error_block").empty();
		var user_info = {};


		$.ajax({
			type: "GET",
			contentType: "application/json; charset=UTF-8",
			url: "/api/v1/user",
			success: function(data) {
				user_info["username"] = data["username"];

				user_info["firstname"] = $("#update_firstname_input").val();
				user_info["lastname"] = $("#update_lastname_input").val();
				user_info["password1"] = $("#update_password1_input").val();
				user_info["password2"] = $("#update_password2_input").val();
				user_info["email"] = $("#update_email_input").val();

				var error_msg_list = check_errors("user_edit", user_info);

				if (error_msg_list.length > 0) {
					for (i = 0; i < error_msg_list.length; i++) {
						var e = $("<p class='error'>" + error_msg_list[i] + "</p>");
						$(".error_block").append(e);
					}
					return;
				}

				$.ajax({
					type: "PUT",
					contentType: "application/json; charset=UTF-8",
					url: "/api/v1/user",
					data: JSON.stringify(user_info),
					success: function(data) {
						var e = $("<p> successfully save the message! </p>");
						$(".success_block").append(e);
						return;
					},

					error: function(response) {
						error = JSON.parse(response.responseText);

						for (i = 0; i < error["errors"].length; i++) {
							var e = $("<p class='error'>" + error["errors"][i]["message"] + "</p>");
							$(".error_block").append(e);
						}
						return;
					}
				});
			},
			error: function(response) {
				return;
			}
		});



	});

});