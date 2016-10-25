$(document).ready(function() {
    window.onpopstate = function(event) {
        if (event.state === null) {
	    	return;
		}
        var id = event.state.stateVariable;
		if (event.state.type === 1) {
	    	change_pic(id);
    	} else {
	    	render_album(id);
		}
    }
    
    history.replaceState({stateVariable: albumid, type: 2}, "title", "album?albumid=" + albumid);
    render_album(albumid);
});

function render_album(albumid) {
    $(".content").empty();
    $(".header").empty()
    $.ajax({
        type: "GET",
        contentType: "application/json; charset=UTF-8",
        url: "/api/v1/album/" + albumid,

        success: function(data) {
            var title = $("<h1>" + data["title"] + "</h1>");
            var username = $("<h2>" + data["username"] + "</h2>");
            var lastupdated = $("<p> LastUpdated: " + data["lastupdated"] + "</p>");
            var editAlbum = $("<a class='btn btn-default' href='/album/edit?albumid=" + albumid + "'> Edit Album</a>");

            $(".header").append(title);
            $(".header").append(username);
            $(".header").append(lastupdated);
            
            $("<div class=\"col-md-12\"> </div>")
            	.append(editAlbum)
            	.appendTo($(".content"))

            for (var i = 0; i < data["pics"].length; i++) {
                var photo = $("<div class='col-md-3'> <div class=\"card\"> <a onclick='goto_new_pic(this.id.slice(4, -5))' id='pic_" + data["pics"][i].picid + "_link'>\
                    <div class='photo' style='background-image:url(static/images/" + data["pics"][i].picid + "." + data["pics"][i].format + ")'>\
                    </div>\
                    </a> <div class=\"card-block\"> <center class=\"card-text\"> "+ data["pics"][i].date + "</p> <center class=\"card-text\">\
                    " + data["pics"][i].caption + "</p></div></div></div>");
                $(".content").append(photo);
            }
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

