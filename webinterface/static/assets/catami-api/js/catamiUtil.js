//function that converts form to json
$.fn.catami_serializeObject = function () {
    var o = {};
    var a = this.serializeArray();
    $.each(a, function () {
        if (o[this.name]) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;
};


//function that gets URL parameters
catami_getURLParameter = function(name) {
    return decodeURI(
        (RegExp(name + '=' + '(.+?)(&|$)').exec(location.search) || [, null])[1]
    );
}

//function that gets deploymentID from url
catami_getDeploymentId = function () {
    var v = location.pathname.split("/");
    //check url if it ends with a "/"
    var index = v.length - (endsWith(location.pathname, "/") ? 2 : 1);
    return v[index];
}

function endsWith(str, suffix) {
    return str.indexOf(suffix, str.length - suffix.length) !== -1;
};