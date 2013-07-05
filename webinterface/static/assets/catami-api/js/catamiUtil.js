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


function catami_generatePaginationOptions(meta) {
    //meta: {limit next offset previous total_count}
    var limit = meta['limit'];
    var offset = meta['offset'];
    var total = meta['total_count'];
    //var next = meta['next'];
    //var prev = meta['previous'];
    var currentPage = 1 + Math.floor(offset / limit) + ((offset % limit == 0) ? 0 : 1);
    var maxPage = Math.floor(total / limit) + ((total % limit == 0) ? 0 : 1);

    //alert('limit: ' + limit + ' total: ' + total + ' currentPage: ' + currentPage + ' maxPage = ' + maxPage + ' next: ' + next + ' prev: ' + prev);
    var options = {
        currentPage: currentPage,
        totalPages: maxPage,
        size: "normal",
        alignment: "right",
        onPageClicked: function (e, originalEvent, type, page) {
            var newOffset = limit * (page - 1);
            loadPage(newOffset);                
        }
    }
    return options;
}

//function that gets URL parameters
catami_getURLParameter = function(name) {
    return decodeURI(
        (RegExp(name + '=' + '(.+?)(&|$)').exec(location.search) || [, null])[1]
    );
}

//function that gets ID from specified url, if none specified, get it from current location
catami_getIdFromUrl = function (url) {
    var v;
    if(url) v = url
    else v = location.pathname.split("/");
    //check url if it ends with a "/"
    var index = v.length - (endsWith(location.pathname, "/") ? 2 : 1);
    return v[index];
}

function endsWith(str, suffix) {
    return str.indexOf(suffix, str.length - suffix.length) !== -1;
};


function buttonLoading(id) {
    var opts = {
        lines: 15,
        // The number of lines to draw
        length: 5,
        // The length of each line
        width: 2,
        // The line thickness
        radius: 4,
        // The radius of the inner circle
        corners: 1,
        // Corner roundness (0..1)
        rotate: 0,
        // The rotation offset
        color: '#fff',
        // #rgb or #rrggbb
        speed: 1,
        // Rounds per second
        trail: 60,
        // Afterglow percentage
        shadow: false,
        // Whether to render a shadow
        hwaccel: false,
        // Whether to use hardware acceleration
        className: 'spinner',
        // The CSS class to assign to the spinner
        zIndex: 2e9,
        // The z-index (defaults to 2000000000)
        top: 'auto',
        // Top position relative to parent in px
        left: '-10px' // Left position relative to parent in px
    };

    var target = document.getElementById(id);

    //uncomment to put the button in enabled state
    var btn = $("#" + id);
    btn.button('loading');

    //clear the default loading text
    //btn.html('');

    //create the spinner
    var spinner = new Spinner(opts).spin();

    //add the spinner to button
    target.appendChild(spinner.el);
}

function buttonReset(id) {
    //uncomment to put the button in enabled state
    var btn = $("#" + id);
    btn.button('reset');
}