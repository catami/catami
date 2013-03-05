/***********************************************************************************************************************
 * Class: CollectionAPI
 * Creating lists of collections and worksets.
 *
 * @param preview_fnc
 * @param select_fnc
 * @constructor
 **********************************************************************************************************************/
var collection_config_defaults = {
    api_baseurl : '/api/dev/collection/',
    linkurl : "/collections/",
    preview_fnc : false,
    select_fnc : false
};


function CollectionAPI(settings) {

    // Set default config params
    var config = {
        api_baseurl : '/api/dev/collection/',
        linkurl : "/collections/",
        preview_fnc : false,
        select_fnc : false
    };
    if (settings.config) $.extend(config, settings.config);  // replace defaults with input arguments


    var listconfig = {
        itemorder : 'actions,info,name,creation_info,description',
        //actions   : 'preview,select,more',
        //info      : 'date,owner,access',
        format    : 'cl-nested-list',
        nested    : true
    }
    if (settings.listconfig) $.extend(listconfig, settings.listconfig);  // replace defaults with input arguments


    var cssconf = getCSS(listconfig.format);
    if (settings.css_collection) $.extend(cssconf.collection, settings.css_collection);  // replace defaults with input arguments
    if (settings.css_workset) $.extend(cssconf.workset, settings.css_workset);  // replace defaults with input arguments



    /* Public methods
     ******************************************************************************************************************/
    /**
     * Method: getFullCollectionList
     * Get full nested list of Collections and Worksets
     *
     * @param filter
     * @param outputelement
     * @return {*}
     */
    this.getCollectionList = function(filter, outputelement) {

        outputelement = ((typeof outputelement !== 'undefined') ? outputelement : false);
        filter = ((typeof filter !== 'undefined') ? '?'+filter : '');

        var list = createCollectionList(filter, cssconf.collection);

        if (outputelement) {
            if (!$(outputelement).hasClass(listconfig.format)) $(outputelement).addClass(listconfig.format);
            $(outputelement).html(list);
        }
        return list;
    }


    this.getCollectionInfo = function(id, outputelement) {

        var api_url = config.api_baseurl+'?id='+id;
        var clinfo = '';
        var fieldlist = listconfig.itemorder.split(',');

        $.ajax({
            dataType: "json",
            async: false,  // prevent asyncronous mode to allow setting of variables within function
            url: api_url ,
            success: function(cl){
                var clobj = cl.objects[0];
                for (var i in fieldlist) {
                    clinfo += getCollectionField (clobj,fieldlist[i], cssconf.collection);
                }
            }
        });
        if (outputelement) {
            if (!$(outputelement).hasClass(listconfig.format)) $(outputelement).addClass(listconfig.format);
            $(outputelement).html(clinfo);
        }
        return clinfo;
    }


    /**
     * Method: collapseList
     * Collapse nested list from getFullCollectionList()
     */
    this.collapseList = function()  {
        $('li > ul.list-sub').each(function(i) {
            var parent_li = $(this).parent('li');           // Find this list's parent list item.
            parent_li.addClass('parent');                   // Style the list item as parent.
            var sub_ul = $(this).remove();                  // Temporarily remove the child-list from the parent

            // Add toggle function to list-toggle class
            parent_li.find('.list-toggle').click(function() {
                sub_ul.toggle();
            });
            parent_li.append(sub_ul);                       // Reattach child-list.
        });

        $('ul.list-main ul.list-sub').hide(); // Hide child lists.
    }


    /* Private methods
     ******************************************************************************************************************/
    /**
     *
     * @param api_url
     * @param parent_id
     * @return {String}
     */
    var createCollectionList = function(filter, css) {

        var list = '';

        $.ajax({
            dataType: "json",
            async: false,  // prevent asyncronous mode to allow setting of variables within function
            url: config.api_baseurl+filter ,
            success: function(cl){
                if (cl.objects.length > 0) {
                    list += '<ul class="'+css.listname+'">';
                    for (var i = 0; i < cl.objects.length; i++) {
                        list += createListItem(cl.objects[i], css, filter);
                    }
                    list += '</ul>';
                }
                else if (!parent_id) {
                    list += '<p class="alert alert-error">There are no collections to display.</p>'
                }
            }
        });
        return list;
    }

    /**
     *
     * @param clobj
     * @param api_url
     * @param parent_id
     * @return {String}
     */
    var createListItem = function(clobj, css, filter) {
        var fieldlist = listconfig.itemorder.split(',');

        var listitem = '<li>';

        for (var i in fieldlist) {
            listitem += getCollectionField (clobj,fieldlist[i], css);
        }

        if ( clobj.parent_id == null && listconfig.nested) { // This item is a parent Collection
            listitem += createCollectionList(filter+'&parent='+clobj.id, cssconf.workset); // Recursive call to create nested workset list (if available)
        }
        listitem += '</li>';


        return listitem;
    }


    /**
     *
     * @param field : actions|info|name|creation|description
     * @param css
     */
    var getCollectionField = function(clobj,field, css) {

        var fieldtext = '';
        var link = (clobj.parent_id)
            ? config.linkurl + clobj.parent_id + '/' + clobj.id + '/'   // child collection (i.e: workset)
            : config.linkurl + clobj.id+'/';                            // parent collection



        if (field=='actions') {
            fieldtext += '<span class="'+css[field]+'">';
            if (config.preview_fnc) {
                fieldtext += '<a class="'+css.actionitem+'" onclick="'+config.preview_fnc.format(clobj['id'])+';" rel="btn-tooltip" title="Preview"><i class="icon-eye-open"></i></a>';
            }
            if (config.select_fnc) {
                fieldtext += '<a class="'+css.actionitem+'" onclick="'+config.select_fnc.format(clobj['id'])+';" rel="btn-tooltip" title="Select"><i class="icon-external-link"></i></a>';
            } else {
                fieldtext += '<a class="'+css.actionitem+'" href="'+link+'" rel="btn-tooltip" title="Select"><i class="icon-external-link"></i></a>';
            }

            // TODO: populate these actions from something more configurable, dynamic and D.R.Y.
            fieldtext += '<a class="'+css.actionitem+' dropdown-toggle" data-toggle="dropdown" rel="btn-tooltip" title="More..."><b class="caret"></b></a>';
            if ( clobj.parent_id == null ) { // This item is a parent Collection
                fieldtext += '<ul class="dropdown-menu">';
                fieldtext += '<li class="nav-header">Jump to:</li>';
                fieldtext += '<li><a href="'+link+'#map" title="View Workset map"><i class="icon-globe"></i> Map view</a></li>';
                fieldtext += '<li><a href="'+link+'#thm" title="View Workset images"><i class="icon-picture"></i> Thumbnail view</a></li>';
                fieldtext += '<li class="nav-header">Data Tasks:</li>';
                fieldtext += '<li><a href="'+link+'#NewWorksetModal" title="Create new Workset"><i class="icon-plus"></i> Create new Workset</a></li>';
                fieldtext += '<li><a href="'+link+'#dwn" title="Download Data"><i class="icon-download-alt"></i> Download</a></li>';
                fieldtext += '</ul>';

            } else { // This item is a child Collection (i.e: a Workset)
                fieldtext += '<ul class="dropdown-menu">';
                fieldtext += '<li class="nav-header">Jump to:</li>';
                fieldtext += '<li><a href="'+link+'#map" title="View Collection map"><i class="icon-globe"></i> Map view</a></li>';
                fieldtext += '<li><a href="'+link+'#thm" title="View Collection images"><i class="icon-picture"></i> Thumbnail view</a></li>';
                fieldtext += '<li class="nav-header">Data Tasks</li>';
                fieldtext += '<li><a href="/imageview" class="imageframe" data-fancybox-group="group'+clobj.id+'" data-fancybox-type="iframe" title="Annotate Workset"><i class="icon-tag"></i> Annotate Workset</a></li>';
                fieldtext += '<li><a href="'+link+'#dwn" title="Download Data"><i class="icon-download-alt"></i> Download</a></li>';
                fieldtext += '</ul>';
            }
            fieldtext += '</span>';

        } else if (field=='info') {
            var collectiontype = (clobj.parent_id) ? 'Workset' : 'Collection';

            fieldtext += '<span class="'+css[field]+'">';
            fieldtext += '<span class="'+css.infoitem+'"  rel="btn-tooltip" title="This item is a '+collectiontype+'">'+collectiontype+'</span> ';
            fieldtext += '<span class="'+css.infoitem+'"  rel="btn-tooltip" title="This '+collectiontype+' was created on '+clobj['creation_date']+'">'+clobj['creation_date'].substr(0,10)+'</span> ';
            fieldtext += '<span class="'+css.infoitem+'"  rel="btn-tooltip" title="This '+collectiontype+' is owned by '+clobj.owner.username+'">'+clobj.owner.username+'</span> ';
            fieldtext += '<span class="'+css.infoitem+'"  rel="btn-tooltip" title="This '+collectiontype+' contains '+clobj.image_count+' images">'+clobj.image_count+'</span> ';
            if (clobj.is_public) {
                fieldtext += '<span class="'+css.infoitem+' btn-danger" rel="btn-tooltip" title="This '+collectiontype+' is publicly accessible">Public</span> ';
            } else {
                fieldtext += '<span class="'+css.infoitem+' btn-success" rel="btn-tooltip" title="This '+collectiontype+' is private">Private</span> ';
            }
            fieldtext += '</span>';

        } else if (field && clobj[field]) {
            fieldtext += '<span class="'+css[field]+'">';
            fieldtext += clobj[field];
            fieldtext += '</span>';

        }


        return fieldtext;
    }

    function getCSS(format) {
        var cssconf = {};

        if (format=='cl-nested-list') {
            cssconf = {
                collection : {
                    listname : 'list-main',
                    actions : 'claction btn-group pull-right',
                    actionitem : 'clactionitem btn btn-primary btn-mini',
                    info : 'clinfo btn-group pull-right',
                    infoitem : 'clinfoitem btn btn-mini disabled',
                    creation_info : 'clcreation list-toggle',
                    description : 'cldescription shorten',
                    name : 'clname list-toggle'
                }
            }
            cssconf.workset = $.extend({},cssconf.collection);
            $.extend(cssconf.workset, {
                listname : 'list-sub well',
                actionitem: 'clactionitem btn btn-mini'
            });
        } else if (format=='cl-info-inline'){
            cssconf = {
                collection : {
                    listname : 'list-main',
                    actions : 'claction btn-group pull-right',
                    actionitem : 'clactionitem btn btn-primary btn-mini',
                    info : 'clinfo btn-group pull-right',
                    infoitem : 'clinfoitem btn btn-mini disabled',
                    creation_info : 'clcreation list-toggle',
                    description : 'cldescription shorten',
                    name : 'clname list-toggle'
                }
            }
        }

        return cssconf;
    }
}

/*
function CollectionInfo(settings) {
    // Set default config params
    var config = $.extend({},collection_config_defaults);  // clone copy of config
    if (settings) $.extend(config, settings);  // replace defaults with input arguments

    var infoclass = 'btn btn-mini disabled ';


    this.getCollectionInfo = function(id,outputelement) {
        nolinks = ((typeof nolinks !== 'undefined') ? nolinks : true);
        var api_url = config.api_baseurl+'?id='+id;
        var clinfo = '';
        $.ajax({
            dataType: "json",
            async: false,  // prevent asyncronous mode to allow setting of variables within function
            url: api_url ,
            success: function(cl){
                var clobj = cl.objects[0];
                var link = ((clobj.parent == 'none') ? config.linkurl+clobj.id+'/' : link = config.linkurl+clobj.parent+'/'+clobj.id + '/');

                clinfo += '<span class="clactions btn-group">';
                if (config.preview_fnc) clinfo += '<a class="btn" onclick="'+config.select_fnc+'('+clobj.id+');" rel="btn-tooltip" title="Preview"><i class="icon-eye-open"></i></a>';
                if (config.select_fnc) clinfo += '<a class="btn" onclick="'+config.preview_fnc+'('+clobj.id+');" rel="btn-tooltip" title="Select"><i class="icon-external-link"></i></a>';
                clinfo += '</span> ';

                clinfo += '<span class="clinfo btn-group  btn-group-vertical pull-right">';
                if (clobj.is_public) {
                    clinfo += '<span class="clinfoaccess '+infoclass+' btn-danger" rel="btn-tooltip" title="This item is publicly accessible">Public</span> ';
                } else {
                    clinfo += '<span class="clinfoaccess '+infoclass+' btn-success" rel="btn-tooltip" title="This item is private">Private</span> ';
                }
                clinfo += '<span class="clinfoowner '+infoclass+'" rel="btn-tooltip" title="This item is owned by '+clobj.owner.username+'">'+clobj.owner.username+'</span> ';
                clinfo += '<span class="clinfodate '+infoclass+'" rel="btn-tooltip" title="This item was created on '+clobj.creation_date+'">'+clobj.creation_date.substr(0,10)+'</span> ';
                //clinfo += '<span class="clinfoaccess">'+(clobj.is_public ? 'Public': 'Private') +'</span> ';
                clinfo += '</span> ';

                clinfo += '<span class="clname">' + clobj.name + '</span> ';
                clinfo += '<br><span class="clcreation">' + clobj.creation_info+'</span> ';
                if (clobj.description) clinfo += '<br><span class="cldescription">'+clobj.description+'</span>'
            }
        })
        if (outputelement) {
            $(outputelement).html(clinfo);
        }
        return clinfo;
    }
}
*/

//first, checks if it isn't implemented yet
if (!String.prototype.format) {
    String.prototype.format = function() {
        var args = arguments;
        return this.replace(/{(\d+)}/g, function(match, number) {
            return typeof args[number] != 'undefined'
                ? args[number]
                : match
                ;
        });
    };
}