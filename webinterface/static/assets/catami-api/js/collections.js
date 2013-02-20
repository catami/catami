/**
 *
 * @param actionfunction1
 * @param actionfunction2
 * @constructor
 */
function CollectionList(actionfunction1, actionfunction2) {

    /******************************************************************************************************************\
     * Properties
    \******************************************************************************************************************/
    this.api_baseurl = '/api/dev/collection/?format=json';
    this.linkurl = '/collections/';
    this.actionfunction1 = ((typeof actionfunction1 !== 'undefined') ? actionfunction1 : false);
    this.actionfunction2 = ((typeof actionfunction2 !== 'undefined') ? actionfunction2 : false);

    var actionfunction = this.actionfunction1;

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

        var list = createCollectionList(this.api_baseurl+filter);

        if (outputelement) {
            $(outputelement).html(list);
        }
        return list;
    }

    this.getWorksetList = function(filter, parent_id, outputelement) {

        outputelement = ((typeof outputelement !== 'undefined') ? outputelement : false);
        filter = ((typeof filter !== 'undefined') ? '&'+filter : '');

        var list = createCollectionList(this.api_baseurl+filter, parent_id);

        if (outputelement) {
            $(outputelement).html(list);
        }
        return list;
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

        if ( !parent_id ) { // This item is a parent Collection
            link = linkurl+clobj.id+'/';
            actions += '<a href="'+link+'#map" title="View Collection map"><i class="icon-globe"></i></a>';
            actions += '<a href="'+link+'#thm" title="View Collection images"><i class="icon-eye-open"></i></a>';
            actions += '<a href="'+link+'#dwn" title="Download Data"><i class="icon-download-alt"></i></a>';

            sublist += createCollectionList(api_url, clobj.id); // Recursive call to create nested workset list (if available)

        } else { // This item is a child Collection (i.e: a Workset)
            link = linkurl+parent_id+'/'+clobj.id + '/';
            actions += '<a href="'+link+'#map" title="View Collection map"><i class="icon-globe"></i></a>';
            actions += '<a href="'+link+'#thm" title="View Collection images"><i class="icon-eye-open"></i></a>';
            actions += '<a href="{% url webinterface.views.all_subsets collection_item.id %}" class="imageframe" data-fancybox-group="{{listname}}{{forloop.counter}}" data-fancybox-type="iframe" title="Annotate Workset1"><i class="icon-tag"></i></a>';
            actions += '<a href="'+link+'#dwn" title="Download Data"><i class="icon-download-alt"></i></a>';
        }

        var listitem = '<li>';
        listitem += '<span class="clname"><a href="#_" onclick="'+actionfunction+'('+clobj.id+');">' + clobj.name + '</a> ('+clobj.creation_info+')</span> ';
        listitem += '<span class="clactions">'+actions+'</span> ';
        listitem += '<span class="cldate"><br>'+clobj.creation_date+'</span> ';
        listitem += '<span class="clowner">'+clobj.owner.username+'</span> ';
        if (clobj.description) listitem += '<span class="cldescription"><br>'+clobj.description+'</span>'
        listitem += sublist;
        listitem += '</li>';


        return listitem;
    }
}


