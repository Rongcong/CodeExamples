function goto_new_pic(picid) {
    if (picid === "") {
        return;
    }
    var statePic = {stateVariable: picid, type: 1};
    history.pushState(statePic, "title", "pic?picid=" + picid);
    change_pic(picid);
    return;
}

function change_pic(picid) {
    $(".content").empty();
    $(".header").empty();
    $.ajax({
        type: "GET",
        contentType: "application/json; charset=UTF-8",
        url: "/api/v1/pic/" + picid,

        success: function(data) {
            var albumid = data["albumid"];
            var username;

            var picture = $("<img class='center-block' src='static/images/" + picid + "." + data["format"] + "'alt=''>");
            $(".content").append(picture);

            var prev_pic = $("<li class = \"previous\"> <a onclick='goto_new_pic(" + "\"" + data["prev"] + "\"" + ")' id='prev_pic'>Previous</a> </li>");
            var next_pic = $("<li class = \"next\"> <a onclick='goto_new_pic(" + "\"" + data["next"] + "\"" + ")' id='next_pic'>Next</a> </li>");

            $("<ul class = \"pager\"> </ul>")
                .append(prev_pic)
                .append(next_pic)
                .appendTo($(".content"))

             $("<div class=\"container page-form\"> </div>")
                .append($("<center id='pic_" + picid + "_caption'>" + data["caption"] + "</center>"))
                .appendTo($(".content"));

            $.ajax({
                type: "GET",
                contentType: "application/json; charset=UTF-8",
                url: "/api/v1/user",
                success: function(user_data) {
                    username = user_data["username"];

                    $.ajax({
                        type: "GET",
                        contentType: "application/json; charset=UTF-8",
                        url: "/api/v1/album/" + albumid,
                        success: function(album_data) {
                            if (username == album_data["username"]) {
                                $(".content").append($("<div class=\"form-group\"> </div>"))
                                    .append($("<input class=\"form-control\" id='pic_caption_input'></input>")); 
                            }

                            var title = $("<h1>" + album_data["title"] + "</h1>");
                            var username = $("<h2>" + album_data["username"] + "</h2>");
                            var lastupdated = $("<p> LastUpdated: " + album_data["lastupdated"] + "</p>");
                            var access = $("<p> Access: " + album_data["access"] + "</p>");

                            $(".header").append(title);
                            $(".header").append(username);
                            $(".header").append(access);
                            $(".header").append(lastupdated);

                            if (own_pic) {
                                caption = $("<input class=\"form-control\" id='pic_caption_input' value='" + data["caption"] + "'></input>"); 
                                $("<div class=\"container page-form\"> </div>")
                                    .append($("<center id = id='pic_" + picid + "_caption'>" + data["caption"] + "</center>")
                                        .append($("<div class=\"form-group\"> </div>")
                                            .append(caption)))
                                    .appendTo($(".content"))
                            }
                            else {
                                caption = $("<center id='pic_" + picid + "_caption'>" + data["caption"] + "</center>");
                                $("<div class=\"container page-form\"> </div>")
                                    .append(caption)
                                    .appendTo($(".content"))
                            }
                            //$(".content").append(caption);

                            $("#pic_caption_input").keypress(function(e){
                                var keyCode = e.which || e.keyCode;

                                // The user presses enter
                                if (keyCode == 13) {
                                    var pic_info = {"caption": $("#pic_caption_input").val(),
                                                    "albumid": data["albumid"],
                                                    "format": data["format"],
                                                    "next": data["next"],
                                                    "prev": data["prev"],
                                                    "picid": data["picid"]};

                                    $.ajax({
                                        type: "PUT",
                                        contentType: "application/json; charset=UTF-8",
                                        url: "/api/v1/pic/" + picid,
                                        data: JSON.stringify(pic_info),
                                        success: function(response) {
                                            window.alert("Caption changed successfully!");
                                            $("#pic_" + picid + "_caption").text($("#pic_caption_input").val());
                                            return;
                                        },
                                        error: function(response) {
                                            error = JSON.parse(response.responseText);
                                            for (var i = 0; i < error["errors"].length; i++) {
                                                var e = $("<p class='error'>" + error["errors"][i]["message"] + "</p>");
                                                $(".content").append(e);
                                            }
                                            return;
                                        }
                                    });
                                }
                            });
                        }  // Get album should not fail
                    });
                },
                // Get user fail, not show input box, do not show error message
                error: function() {
                    return;
                }
            });
        },
        // Only get pic fail should return error message
        error: function(response) {
            error = JSON.parse(response.responseText);
            for (var i = 0; i < error["errors"].length; i++) {
                var e = $("<p class='error'>" + error["errors"][i]["message"] + "</p>");
                $(".content").append(e);
            }
            return;
        }
    }); 
}

