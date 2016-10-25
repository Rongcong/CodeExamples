
function check_errors(route, user_info) {
    var error_msg_list = [];

    if ("username" in user_info) {
        if (route == "user" || route == "user_edit") {

            if (user_info["username"].length > 20) {
                error_msg_list.push("Username must be no longer than 20 characters");
            }

            if (user_info["username"].length < 3) {
                error_msg_list.push("Usernames must be at least 3 characters long");
            }

            if (user_info["username"].search(/^[\w]*$/) == -1) {
                error_msg_list.push("Usernames may only contain letters, digits, and underscores");
            }
        }
    }



    if ("password1" in user_info) {
        if (route == "user_edit" && user_info["password1"] == "" && user_info["password2"] == "") {
        }

        else if (route == "user" || route == "user_edit") {
            if (user_info["password1"].length < 8) {
                error_msg_list.push("Passwords must be at least 8 characters long");
            }
            if (user_info["password1"].search(/^[\w]*$/) == -1) {
                error_msg_list.push("Passwords may only contain letters, digits, and underscores");
            }

            if ((user_info["password1"].search(/^.*[a-z].*\d.*$/i) == -1) && (user_info["password1"].search(/^.*\d.*[a-z].*$/i) == -1)) {
                error_msg_list.push("Passwords must contain at least one letter and one number");
            }

            if (user_info["password1"] != user_info["password2"]) {
                error_msg_list.push("Passwords do not match");
            }
        }
    }



    if ("email" in user_info) {
        if (route == "user" || route == "user_edit") {
            if (user_info["email"].length > 40) {
                error_msg_list.push("Email must be no longer than 40 characters");
            }

            if (user_info["email"].search(/[^@]+@[^@]+\.[^@]+/) == -1) {
                error_msg_list.push("Email address must be valid");
            }
        }
    }


    if ("firstname" in user_info) {
        if (route == "user" || route == "user_edit") {
            if (user_info["firstname"].length > 20) {
                error_msg_list.push("Firstname must be no longer than 20 characters");
            }
        }
    }


    if ("lastname" in user_info) {
        if (route == "user" || route == "user_edit") {
            if (user_info["lastname"].length > 20) {
                error_msg_list.append("Lastname must be no longer than 20 characters");
            }
        }
    }

    return error_msg_list;
}


