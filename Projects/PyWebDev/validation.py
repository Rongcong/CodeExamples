import re
import extensions

# route can be user, user_edit or login
# return a list of error messages
# code: 1. username is taken
#       2. username at least 3 characters long
#       3. username only contains letters, digits, underscores
#       4. password at least 8 characters long
#       5. password contain at least one letter and one number
#       6. password only contain letters, digits, underscores
#       7. password not match
#       8. email not valid
#       9. username max length 20
#       10. firstname max length 20
#       11. lastname max length 20
#       12. email max length 40
#       13. username does not exist
#       14. password incorrect

def check_errors(route, user_info):
    error_dict = {};
    if "username" in user_info:
        if (route == "user"):
            if (len(user_info["username"]) > 20):
                error_dict['9'] = 1;
            if (len(user_info["username"]) < 3):
                error_dict['2'] = 1;
            if (re.match(r"^[\w]*$", user_info["username"]) is None):
                error_dict['3'] = 1;
            if (extensions.does_username_exist(user_info["username"])):
                error_dict['1'] = 1;

    if "password1" in user_info:
        if user_info['password1'] == "" and user_info['password2'] == "" and route == 'user_edit':
	    pass
        elif (route == "user" or route == "user_edit"):
            if (len(user_info["password1"]) < 8):
		error_dict['4'] = 1;
            if (re.match(r"^[\w]*$", user_info["password1"]) is None):
                error_dict['6'] = 1;
            if ((re.match(r"^.*[a-zA-Z].*\d.*$", user_info["password1"]) is None) and (re.match(r"^.*\d.*[a-zA-Z].*$", user_info["password1"]) is None)):
                error_dict['5'] = 1;
            if (user_info["password1"] != user_info["password2"]):
                error_dict['7'] = 1;

    if "email" in user_info:
        if (route == "user" or route == 'user_edit'):
            if (len(user_info["email"]) > 40):
                error_dict['12'] = 1;
            if not re.match(r"[^@]+@[^@]+\.[^@]+", user_info["email"]):
                error_dict['8'] = 1;

    if "firstname" in user_info:
        if (route == "user" or route == 'user_edit'):
            if (len(user_info["firstname"]) > 20):
                error_dict['10'] = 1;

    if "lastname" in user_info:
        if (route == "user" or route == 'user_edit'):
            if (len(user_info["lastname"]) > 20):
                error_dict['11'] = 1;

    if (route == "login"):
        if (not extensions.does_username_exist(user_info["username"])):
            error_dict['13'] = 1;
        else:
            if not extensions.check_login(username=user_info["username"], password=user_info["password"]):
                error_dict['14'] = 1;

    return error_dict;

