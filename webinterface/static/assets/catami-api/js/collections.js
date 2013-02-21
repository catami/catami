/**
 *
 * @param actionfunction1
 * @param actionfunction2
 * @constructor
 */
function CollectionList(actionfunction1, actionfunction2) {

    /******************************************************************************************************************\
     * Class globals
    \******************************************************************************************************************/
    var api_baseurl = '/api/dev/collection/?format=json';
    var linkurl = '/collections/';
    var actionfunction1 = ((typeof actionfunction1 !== 'undefined') ? actionfunction1 : false);
    var actionfunction2 = ((typeof actionfunction2 !== 'undefined') ? actionfunction2 : false);


    /******************************************************************************************************************\
     * Public methods
    \******************************************************************************************************************/
    /**
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

    this.getWorksetList = function(filter, parent_id, outputelement) {

        outputelement = ((typeof outputelement !== 'undefined') ? outputelement : false);
        filter = ((typeof filter !== 'undefined') ? '&'+filter : '');

        var list = createCollectionList(api_baseurl+filter, parent_id);

        if (outputelement) {
            $(outputelement).html(list);
        }
        return list;
    }


    this.collapseList = function()  {
        // Find list items representing folders and
        // style them accordingly.  Also, turn them
        // into links that can expand/collapse the
        // tree leaf.
        $('li > ul.collapsibleSubList').each(function(i) {
            // Find this list's parent list item.
            var parent_li = $(this).parent('li');

            // Style the list item as folder.
            parent_li.addClass('parent');

            // Temporarily remove the list from the
            // parent list item, wrap the remaining
            // text in an anchor, then reattach it.
            var sub_ul = $(this).remove();
            //parent_li.wrapInner('<a/>').find('a').click(function() {
            parent_li.find('span.clname').click(function() {
                // Make the anchor toggle the leaf display.
                sub_ul.toggle();
            });
            parent_li.append(sub_ul);
        });

        // Hide all lists except the outermost.
        $('ul.collapsibleList ul.collapsibleSubList').hide();
    }


    /******************************************************************************************************************\
     * Private methods
    \******************************************************************************************************************/
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
                /*else {
                 list = '<p class="alert alert-error">There are no collections</p>'
                 }*/
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
        var linkurl = '/collections/';
        var link = '';
        var actions = '';
        var sublist = '';
        var actionclass = 'btn dropdown-toggle ';

        if ( !parent_id ) { // This item is a parent Collection
            link = linkurl+clobj.id+'/';
            actions += '<li><a href="'+link+'#map" title="View Collection map"><i class="icon-globe"></i> View Collection on map</a></li>';
            actions += '<li><a href="'+link+'#thm" title="View Collection images"><i class="icon-eye-open"></i> View Collection images</a></li>';
            actions += '<li><a href="'+link+'#dwn" title="Download Data"><i class="icon-download-alt"></i> Download Collection</a></li>';

            actionclass += 'btn-primary';

            sublist += createCollectionList(api_url, clobj.id); // Recursive call to create nested workset list (if available)

        } else { // This item is a child Collection (i.e: a Workset)
            link = linkurl+parent_id+'/'+clobj.id + '/';
            actions += '<li><a href="'+link+'#map" title="View Collection map"><i class="icon-globe"></i> View Workset on map</a></li>';
            actions += '<li><a href="'+link+'#thm" title="View Collection images"><i class="icon-eye-open"></i> View Workset images</a></li>';
            actions += '<li><a href="/imageview" class="imageframe" data-fancybox-group="group'+clobj.id+'" data-fancybox-type="iframe" title="Annotate Workset"><i class="icon-tag"></i> Annotate Workset</a></li>';
            actions += '<li><a href="'+link+'#dwn" title="Download Data"><i class="icon-download-alt"></i> Download Workset</a></li>';

            //actionclass += 'btn-mini';
        }

        var listitem = '<li>';
        listitem += '<span class="clname"><a href="#_" onclick="'+actionfunction1+'('+clobj.id+');">' + clobj.name + '</a> ('+clobj.creation_info+')</span> ';
        listitem += '<span class="clactions"><div class="btn-group"><a class="'+actionclass+'" href="'+link+'">View</a><button class="'+actionclass+'" data-toggle="dropdown"><b class="caret"></b></button><ul class="dropdown-menu"><li class="nav-header">Data Tasks</li>'+actions+'</ul></div></span> ';
        listitem += '<span class="cldate"><br>'+clobj.creation_date+'</span> ';
        listitem += '<span class="clowner">'+clobj.owner.username+'</span> ';
        listitem += '<span class="claccess">'+(clobj.is_public ? 'Public': 'Private') +'</span> ';
        if (clobj.description) listitem += '<span class="cldescription"><br>'+clobj.description+'</span>'
        listitem += sublist;
        listitem += '</li>';


        return listitem;
    }
}

