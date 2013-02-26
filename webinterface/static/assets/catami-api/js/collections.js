/***********************************************************************************************************************
 * Class: CollectionList
 * Creating lists of collections and worksets.
 *
 * @param preview_fnc
 * @param select_fnc
 * @constructor
 **********************************************************************************************************************/
var collection_global_config = {
    api_baseurl : '/api/dev/collection/',
    linkurl : "/collections/",
    preview_fnc : false,
    select_fnc : false
};

function CollectionList(settings) {

    // Set default config params
    var config = jQuery.extend({},collection_global_config);
    if (settings) $.extend(config, settings);  // replace defaults with input arguments



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
    this.getFullCollectionList = function(filter, outputelement) {

        outputelement = ((typeof outputelement !== 'undefined') ? outputelement : false);
        filter = ((typeof filter !== 'undefined') ? '?'+filter : '');

        var list = createCollectionList(config.api_baseurl+filter);

        if (outputelement) {
            $(outputelement).html(list);
        }
        return list;
    }

    /**
     * Method: getWorksetList
     *
     *
     * @param filter
     * @param parent_id
     * @param outputelement
     * @return {*}
     */
    this.getWorksetList = function(filter, parent_id, outputelement) {

        outputelement = ((typeof outputelement !== 'undefined') ? outputelement : false);
        filter = ((typeof filter !== 'undefined') ? '?'+filter : '');

        var list = createCollectionList(config.api_baseurl+filter, parent_id);

        if (outputelement) {
            $(outputelement).html(list);
        }
        return list;
    }

    /**
     * Method: collapseList
     * Collapse nested list from getFullCollectionList()
     */
    this.collapseList = function()  {
        $('li > ul.collapsibleSubList').each(function(i) {
            var parent_li = $(this).parent('li');           // Find this list's parent list item.
            parent_li.addClass('parent');                   // Style the list item as parent.
            var sub_ul = $(this).remove();                  // Temporarily remove the child-list from the parent

            // Add toggle function to list-toggle class
            parent_li.find('.list-toggle').click(function() {
                sub_ul.toggle();
            });
            parent_li.append(sub_ul);                       // Reattach child-list.
        });

        $('ul.collapsibleList ul.collapsibleSubList').hide(); // Hide child lists.
    }


    /* Private methods
     ******************************************************************************************************************/
    /**
     *
     * @param api_url
     * @param parent_id
     * @return {String}
     */
    var createCollectionList = function(api_url, parent_id) {

        parent_id = ((typeof parent_id !== 'undefined') ? parent_id : false);
        var ul_id = '';
        if (parent_id) {
            api_url = api_url+'&parent='+parent_id;
            ul_id = 'class="collapsibleSubList well"';
        } else {
            ul_id = 'class="collapsibleList"';
        }

        var list = '';

        $.ajax({
            dataType: "json",
            async: false,  // prevent asyncronous mode to allow setting of variables within function
            url: api_url ,
            success: function(cl){
                if (cl.objects.length > 0) {
                    list += '<ul '+ul_id+'>';
                    for (var i = 0; i < cl.objects.length; i++) {
                        list += createListItem(cl.objects[i], api_url, parent_id);
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
    var createListItem = function(clobj, api_url, parent_id) {
        var link = '';
        var actions = '';
        var sublist = '';
        var itemtype = '';
        var actionclass = 'btn '; // btn-small
        var infoclass = 'btn btn-mini disabled ';

        if ( !parent_id ) { // This item is a parent Collection
            link = config.linkurl+clobj.id+'/';
            actions += '<li class="nav-header">Jump to:</li><li><a href="'+link+'#map" title="View Workset map"><i class="icon-globe"></i> Map view</a></li>';
            actions += '<li><a href="'+link+'#thm" title="View Workset images"><i class="icon-picture"></i> Thumbnail view</a></li>';
            actions += '<li class="nav-header">Data Tasks:</li><li><a href="'+link+'#NewWorksetModal" title="Create new Workset"><i class="icon-plus"></i> Create new Workset</a></li>';
            actions += '<li><a href="'+link+'#dwn" title="Download Data"><i class="icon-download-alt"></i> Download</a></li>';

            actionclass += 'btn-primary ';
            itemtype = 'Collection';

            sublist += createCollectionList(api_url, clobj.id); // Recursive call to create nested workset list (if available)

        } else { // This item is a child Collection (i.e: a Workset)
            link = config.linkurl+parent_id+'/'+clobj.id + '/';
            actions += '<li class="nav-header">Jump to:</li><li><a href="'+link+'#map" title="View Collection map"><i class="icon-globe"></i> Map view</a></li>';
            actions += '<li><a href="'+link+'#thm" title="View Collection images"><i class="icon-picture"></i> Thumbnail view</a></li>';
            actions += '<li class="nav-header">Data Tasks</li><li><a href="/imageview" class="imageframe" data-fancybox-group="group'+clobj.id+'" data-fancybox-type="iframe" title="Annotate Workset"><i class="icon-tag"></i> Annotate Workset</a></li>';
            actions += '<li><a href="'+link+'#dwn" title="Download Data"><i class="icon-download-alt"></i> Download</a></li>';

            itemtype = 'Workset';

            //actionclass += 'btn-mini';
        }

        var listitem = '<li>';
        listitem += '<span class="btn-toolbar clactions">';
        listitem += '<span class="btn-group">';
        listitem += '<span class="cldate '+infoclass+'"  rel="btn-tooltip" title="This item was created on '+clobj.creation_date+'">'+clobj.creation_date.substr(0,10)+'</span> ';
        listitem += '<span class="clowner '+infoclass+'"  rel="btn-tooltip" title="This item is owned by '+clobj.owner.username+'">'+clobj.owner.username+'</span> ';
        if (clobj.is_public) {
            listitem += '<span class="claccess '+infoclass+' btn-danger" rel="btn-tooltip" title="This item is publicly accessible">Public</span> ';
        } else {
            listitem += '<span class="claccess '+infoclass+' btn-success" rel="btn-tooltip" title="This item is private">Private</span> ';
        }
        listitem += '</span> ';
        listitem += '<span class="btn-group">';
        if (config.preview_fnc) listitem += '<button class="'+actionclass+'" onclick="'+config.preview_fnc+'('+clobj.id+');" rel="btn-tooltip" title="Preview"><i class="icon-eye-open"></i></button>';
        if (config.select_fnc) {
            listitem += '<button class="'+actionclass+'" onclick="'+config.select_fnc+'('+clobj.id+');" rel="btn-tooltip" title="Select"><i class="icon-external-link"></i></button>';
        } else {
            listitem += '<a class="'+actionclass+'" href="'+link+'" rel="btn-tooltip" title="Select"><i class="icon-external-link"></i></a>';
        }
        listitem += '<button class="'+actionclass+' dropdown-toggle" data-toggle="dropdown" rel="btn-tooltip" title="More..."><b class="caret"></b></button>';
        listitem += '<ul class="dropdown-menu">'+actions+'</ul>';
        listitem += '</span></span>';
        listitem += '<span class="clname list-toggle" >'+itemtype+': ' + clobj.name + ' ('+clobj.creation_info+')</span> ';
        //listitem += '<span class="cldate">'+clobj.creation_date.substr(0,10)+'</span> ';
        if (clobj.description) listitem += '<span class="cldescription"><br>'+clobj.description+'</span>'
        listitem += sublist;
        listitem += '</li>';


        return listitem;
    }
}


function CollectionInfo(settings) {
    // Set default config params
    var config = jQuery.extend({},collection_global_config);
    if (settings) $.extend(config, settings);  // replace defaults with input arguments



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
                if (config.preview_fnc) clinfo += '<button class="btn" onclick="'+config.select_fnc+'('+clobj.id+');" rel="btn-tooltip" title="Preview"><i class="icon-eye-open"></i></button>';
                if (config.select_fnc) clinfo += '<button class="btn" onclick="'+config.preview_fnc+'('+clobj.id+');" rel="btn-tooltip" title="Select"><i class="icon-external-link"></i></button>';
                clinfo += '</span> ';
                clinfo += '<span class="clname">' + clobj.name + ' ('+clobj.creation_info+')</span> ';
                clinfo += '<span class="cldate">'+(clobj.creation_date)+'</span> ';
                clinfo += '<span class="clowner">'+clobj.owner.username+'</span> ';
                clinfo += '<span class="claccess">'+(clobj.is_public ? 'Public': 'Private') +'</span> ';
                if (clobj.description) clinfo += '<span class="cldescription">'+clobj.description+'</span>'
            }
        })
        if (outputelement) {
            $(outputelement).html(clinfo);
        }
        return clinfo;
    }
}
