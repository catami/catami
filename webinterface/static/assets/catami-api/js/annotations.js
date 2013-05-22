function AnnotationAPI (usrsettings) {
    var settings = {
        api_tag_baseurl: '/api/dev/annotation_code/',
        api_pts_baseurl: '/api/dev/point_annotation/',
        linkurl: ""
    }
    if (usrsettings.settings) $.extend(settings, usrsettings.settings);  // override defaults with input arguments

    var config = {
        theme: 'as-default',
        format: ''
    }
    if (usrsettings.config) $.extend(config, usrsettings.config);  // override defaults with input arguments
    //if (!config.format) getFormat(config.theme);

    // variable to reference current ajax object
    var ajaxobj = '';

    // Initialise meta info
    this.meta_tags = {
        limit: '',
        next: '',
        offset: '',
        previous: '',
        total_count: '',
        start: '',
        end: ''
    }

    // Initialise meta info
    this.meta_pts = {
        limit: '',
        next: '',
        offset: '',
        previous: '',
        total_count: '',
        start: '',
        end: ''
    }


    this.clearTags = function (outputelement) {
        if (typeof(ajaxobj)=='object') ajaxobj.abort(); // cancel previous request (in case it is still loading to prevent asynchronous munging of data)
        $(outputelement).html('');
    }

    this.annotationCodeList = {};

    this.getTags = function (filter, outputelement) {
        filter = ((typeof filter !== 'undefined') ? '?' + filter : '');
        var parent = this;
        var list = '';
        ajaxobj = $.ajax({
            dataType: "json",
            async: false,  // prevent asyncronous mode to allow setting of variables within function
            url: settings.api_tag_baseurl + filter,
            success: function (objs) {

                var obj = {};
                $.extend(parent.meta_tags, objs.meta);
                parent.meta_tags.start = objs.meta.offset+1;
                parent.meta_tags.end = Math.min((objs.meta.offset + objs.meta.limit), objs.meta.total_count);
                if (objs.objects.length > 0) {
                    parent.annotationCodeList = objs.objects;
                    for (var i = 0; i < objs.objects.length; i++) {
                        obj = getTagObj(objs.objects[i]);
                        list += formatObj(config.format, obj);
                    }
                }
                else {
                    list = '<p class="alert alert-error">No items to display.</p>';
                }
            }
        });
        if (outputelement) {
            if (!$(outputelement).hasClass(config.theme)) $(outputelement).addClass(config.theme);
            $(outputelement).append(list);
        }
        return list;
    }


    this.getNewTags = function (filter, outputelement) {
        this.clearTags(outputelement);
        this.getTags(filter, outputelement);
    }


    this.getTagInfo = function (uri) {
        var taginfo = {};
        ajaxobj = $.ajax({
            dataType: "json",
            async: false,  // prevent asyncronous mode to allow setting of variables within function
            url: uri,
            success: function (obj) {
                taginfo = obj;
            }
        });
        return taginfo;
    }

    this.getAnnotationPoints = function (filter) {
        filter = ((typeof filter !== 'undefined') ? '?' + filter : '');
        var parent = this;
        var list = [];
        ajaxobj = $.ajax({
            dataType: "json",
            async: false,  // prevent asyncronous mode to allow setting of variables within function
            url: settings.api_pts_baseurl + filter,
            success: function (objs) {
                var obj = {};
                $.extend(parent.meta_pts, objs.meta);
                parent.meta_pts.start = objs.meta.offset+1;
                parent.meta_pts.end = Math.min((objs.meta.offset + objs.meta.limit), objs.meta.total_count);
                if (objs.objects.length > 0) {
                    for (var i = 0; i < objs.objects.length; i++) {
                        obj = getPtObj(objs.objects[i]);
                        list.push(obj);
                    }
                }
            }
        });
        return list;
    }




    /**
     *
     * @param obj
     * @return {Object}
     */
    function getTagObj(obj) {
        return {
            id: obj.id,
            code_name: obj.code_name,
            caab_code: obj.caab_code,
            cpc_code: obj.cpc_code,
            description: obj.description,
            parent: obj.parent,
            parent_id: obj.parent_id,
            point_colour: obj.point_colour,
            resource_uri: obj.resource_uri
        };
    }

    function getPtObj(obj) {
        return {
            id: obj.id,
            annotation_set: obj.annotation_set,
            image: obj.image,
            label: obj.label,
            level: obj.level,
            qualifiers: obj.qualifiers,
            x: obj.x,
            y: obj.y,
            resource_uri: obj.resource_uri,
            cssid: 'AnnotionPoint'+obj.id,
            scored: (obj.label !== '/api/dev/annotation_code/1/') ? true : false,
            selected: false
        }
    }

    /**
     *
     * @param format
     * @param obj
     * @return {String|XML|void}
     */
    function formatObj(format, obj) {
        return format.replace(/{\[(.*?)\]}/g, function (match, string) {
            return typeof obj[string] != 'undefined'
                ? obj[string]
                : match;
        });
    }
}


/**************************************************************************************************
 *
 * @param usrsettings
 * @constructor
 */

function AnnotationSetAPI (usrsettings) {
    var settings = {
        api_baseurl: '/api/dev/point_annotation_set/',
        linkurl: ""
    }
    if (usrsettings.settings) $.extend(settings, usrsettings.settings);  // override defaults with input arguments

    var config = {
        theme: 'as-default',
        format: ''
    }
    if (usrsettings.config) $.extend(config, usrsettings.config);  // override defaults with input arguments
    //if (!config.format) getFormat(config.theme);

    // variable to reference current ajax object
    var ajaxobj = '';

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

    this.clearAnnotationSets = function (outputelement) {
        if (typeof(ajaxobj)=='object') ajaxobj.abort(); // cancel previous request (in case it is still loading to prevent asynchronous munging of data)
        $(outputelement).html('');
    }


    this.getAnnotationSets = function (filter, outputelement) {
        filter = ((typeof filter !== 'undefined') ? '?' + filter : '');
        var parent = this;
        var list = '';
        ajaxobj = $.ajax({
            dataType: "json",
            async: false,  // prevent asyncronous mode to allow setting of variables within function
            url: settings.api_baseurl + filter,
            success: function (objs) {
                var obj = {};
                $.extend(parent.meta, objs.meta);
                parent.meta.start = objs.meta.offset+1;
                parent.meta.end = Math.min((objs.meta.offset + objs.meta.limit), objs.meta.total_count);
                if (objs.objects.length > 0) {
                    for (var i = 0; i < objs.objects.length; i++) {
                        obj = getAsObj(objs.objects[i]);
                        list += formatObj(config.format, obj);
                    }
                }
                else {
                    list = '<p class="alert alert-error">No items to display.</p>';
                }
            }
        });
        if (outputelement) {
            if (!$(outputelement).hasClass(config.theme)) $(outputelement).addClass(config.theme);
            $(outputelement).append(list);
        }
        return list;
    }


    this.getNewAnnotationSets = function (filter, outputelement) {
        this.clearAnnotationSets(outputelement);
        this.getAnnotationSets(filter, outputelement);
    }

    /**
     *
     * @param obj
     * @return {Object}
     */
    function getAsObj(obj) {
        return objout = {
            id: obj.id,
            collection: obj.collection,
            count: obj.count,
            methodology: obj.methodology,
            name: obj.name,
            owner: obj.owner,
            resource_uri: obj.resource_uri
        };
    }

    /**
     *
     * @param format
     * @param obj
     * @return {String|XML|void}
     */
    function formatObj(format, obj) {
        return format.replace(/{(.*?)}/g, function (match, string) {
            return typeof obj[string] != 'undefined'
                ? obj[string]
                : match;
        });
    }
}