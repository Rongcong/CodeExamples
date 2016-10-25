$(document).ready(function() {
    window.onpopstate = function(event) {
        if (event.state === null) {
	    	return;
        }
        var id = event.state.stateVariable;
		change_pic(id);
    }

    history.replaceState({stateVariable: picid, type: 1}, "title", "pic?picid=" + picid);
    change_pic(picid);
});
