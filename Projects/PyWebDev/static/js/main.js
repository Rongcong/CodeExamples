$(document).ready(function() {
	$.ajax({
		type: "GET",
		contentType: "application/json; charset=UTF-8",
		url: "/api/v1/user",
		success: function(data) {
			var msg = $("<p> Logged in as" + data["firstname"] + " " + data["lastname"] + "</p>");
			$("head").append(msg);
		},
		error: function(response) {
		}
	});


	$("#nav_logout").click(function() {
		$.ajax({
			type: "POST",
			contentType: "application/json; charset=UTF-8",
			url: "/api/v1/logout",
			success: function(data) {
				window.location.href = "/";
			},
			error: function(response) {
				error = JSON.parse(response.responseText);
				for (var i = 0; i < error["errors"].length; i++) {
					var e = $("<p class='error'>" + error["errors"][i]["message"] + "</p>");
					$("head").append(e);
				}
			}
		});

	});
});
