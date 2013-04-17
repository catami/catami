function ThumnailAPI(usrsettings) {
    var settings = {
        api_baseurl: '/api/dev/image/',
        linkurl: ""
    }
    if (usrsettings.settings) $.extend(settings, usrsettings.settings);  // override defaults with input arguments

    var config = {
        theme: 'th-default',
        format: '',
        shownav: true,
        navformat: ''
    }
    if (usrsettings.config) $.extend(config, usrsettings.config);  // override defaults with input arguments
    if (!config.format) getFormat(config.theme);

    var ajaxobj = ''; // variable to reference current ajax object

    // Initialise meta info
    this.meta = {
        limit: '',
        next: '',
        offset: '',
        previous: '',
        total_count: '',
        start: '',
        end: ''
    }


    /**
     *
     * @param outputelement
     */
    this.clearThumbnails = function (outputelement) {
        if (typeof(ajaxobj)=='object') ajaxobj.abort(); // cancel previous request (in case it is still loading to prevent asynchronous munging of data)
        $(outputelement).html('');
    }

    /**
     *
     * @param outputelement
     * @param filter
     */
    this.appendThumnails = function (outputelement, apistring) {


        var parent = this;
        var obj = {};
        ajaxobj = $.ajax({
            dataType: "json",
            async: false,  // prevent asyncronous mode to allow setting of variables within function
            url: apistring,
            success: function (img) {
                if (img.objects.length > 0) {
                    for (var i = 0; i < img.objects.length; i++) {
                        obj = getThObj(img.objects[i]);
                        $(outputelement).append(formatThObj(config.format, obj));
                    }
                }
                else {
                    $(outputelement).append('<p class="alert alert-error">No items to display.</p>');
                }
                $.extend(parent.meta, img.meta);
                parent.meta.start = img.meta.offset+1;
                parent.meta.end = Math.min((img.meta.offset + img.meta.limit), img.meta.total_count);
            }
        })
        //console.log(this.meta);
    }

    /**
     *
     * @param outputelement
     * @param filter
     */
    this.getNewThumbnails = function (outputelement, filter) {
        filter = ((typeof filter !== 'undefined') ? '?' + filter : '');
        this.clearThumbnails(outputelement);
        this.appendThumnails(outputelement, settings.api_baseurl + filter);
    }

    /**
     *
     * @param obj
     * @return {Object}
     */
    function getThObj(obj) {
        return objout = {
            id: obj.id,
            pose: obj.pose,
            resource_uri: obj.resource_uri,
            thumbnail_location: obj.thumbnail_location,
            web_location: obj.web_location,
            collection: obj.collection,
            measurements: obj.measurements
        };
    }

    /**
     *
     * @param format
     * @param obj
     * @return {String|XML|void}
     */
    function formatThObj(format, obj) {
        return format.replace(/{(.*?)}/g, function (match, string) {
            return typeof obj[string] != 'undefined'
                ? obj[string]
                : match;
        });
    }

    /**
     *
     * @param theme
     * @return {String}
     */
    function getFormat(theme) {
        if (theme == 'th-fancybox') {
            config.format = '<a class="th-fancybox" rel="gallery1" href="{web_location}"><img src="{thumbnail_location}"/></a>';
        }
        else {
            config.format = '<a class="'+theme+'" href="{web_location}"><img src="{thumbnail_location}"/></a>';
        }
    }
}