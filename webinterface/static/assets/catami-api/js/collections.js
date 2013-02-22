/***********************************************************************************************************************
 * Class: CollectionList
 * Creating lists of collections and worksets.
 *
 * @param preview_fnc
 * @param select_fnc
 * @constructor
 **********************************************************************************************************************/
function CollectionList(preview_fnc, select_fnc) {

    /* Class globals
     ******************************************************************************************************************/
    var api_baseurl = '/api/dev/collection/?format=json';
    var linkurl = '/collections/';
    var preview_fnc = ((typeof preview_fnc !== 'undefined') ? preview_fnc : false);
    var select_fnc = ((typeof select_fnc !== 'undefined') ? select_fnc : false);


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
        filter = ((typeof filter !== 'undefined') ? '&'+filter : '');

        var list = createCollectionList(api_baseurl+filter);

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
        filter = ((typeof filter !== 'undefined') ? '&'+filter : '');

        var list = createCollectionList(api_baseurl+filter, parent_id);

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
        var actionclass = 'btn '; // btn-small

        if ( !parent_id ) { // This item is a parent Collection
            link = linkurl+clobj.id+'/';
            actions += '<li class="nav-header">Jump to:</li><li><a href="'+link+'#map" title="View Workset map"><i class="icon-globe"></i> Map view</a></li>';
            actions += '<li><a href="'+link+'#thm" title="View Workset images"><i class="icon-picture"></i> Thumbnail view</a></li>';
            actions += '<li class="nav-header">Data Tasks:</li><li><a href="'+link+'#NewWorksetModal" title="Create new Workset"><i class="icon-plus"></i> Create new Workset</a></li>';
            actions += '<li><a href="'+link+'#dwn" title="Download Data"><i class="icon-download-alt"></i> Download</a></li>';
            actionclass += 'btn-primary';

            sublist += createCollectionList(api_url, clobj.id); // Recursive call to create nested workset list (if available)

        } else { // This item is a child Collection (i.e: a Workset)
            link = linkurl+parent_id+'/'+clobj.id + '/';
            actions += '<li class="nav-header">Jump to:</li><li><a href="'+link+'#map" title="View Collection map"><i class="icon-globe"></i> Map view</a></li>';
            actions += '<li><a href="'+link+'#thm" title="View Collection images"><i class="icon-picture"></i> Thumbnail view</a></li>';
            actions += '<li class="nav-header">Data Tasks</li><li><a href="/imageview" class="imageframe" data-fancybox-group="group'+clobj.id+'" data-fancybox-type="iframe" title="Annotate Workset"><i class="icon-tag"></i> Annotate Workset</a></li>';
            actions += '<li><a href="'+link+'#dwn" title="Download Data"><i class="icon-download-alt"></i> Download</a></li>';

            //actionclass += 'btn-mini';
        }

        var listitem = '<li>';
        listitem += '<span class="clname list-toggle">' + clobj.name + ' ('+clobj.creation_info+')</span> ';
        listitem += '<span class="clactions btn-group">';
        if (preview_fnc) listitem += '<button class="'+actionclass+' list-toggle" onclick="'+preview_fnc+'('+clobj.id+');" rel="btn-tooltip" title="Preview"><i class="icon-eye-open"></i></button>';
        listitem += '<a class="'+actionclass+'" href="'+link+'" rel="btn-tooltip" title="Select"><i class="icon-external-link"></i></a>';
        listitem += '<button class="'+actionclass+' dropdown-toggle" data-toggle="dropdown" rel="btn-tooltip" title="More..."><b class="caret"></b></button>';
        listitem += '<ul class="dropdown-menu">'+actions+'</ul>';
        listitem += '</span> ';
        listitem += '<span class="cldate"><br>'+(clobj.creation_date)+'</span> ';
        listitem += '<span class="clowner">'+clobj.owner.username+'</span> ';
        listitem += '<span class="claccess">'+(clobj.is_public ? 'Public': 'Private') +'</span> ';
        if (clobj.description) listitem += '<span class="cldescription"><br>'+clobj.description+'</span>'
        listitem += sublist;
        listitem += '</li>';


        return listitem;
    }
}

