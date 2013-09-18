var GlobalEvent = _.extend({}, Backbone.Events);

var QualifierCode = Backbone.Model.extend({
    urlRoot: "/api/dev/qualifier_code/",
    url: function() {
        var origUrl = Backbone.Model.prototype.url.call(this);
        return origUrl + (origUrl.charAt(origUrl.length - 1) == '/' ? '' : '/');
    }
});

var AnnotationCode = Backbone.Model.extend({
    urlRoot: "/api/dev/annotation_code/",
    url: function() {
        var origUrl = Backbone.Model.prototype.url.call(this);
        return origUrl + (origUrl.charAt(origUrl.length - 1) == '/' ? '' : '/');
    }
});

var AnnotationCodeList = Backbone.Tastypie.Collection.extend({
    urlRoot: "/api/dev/annotation_code/",
    model: AnnotationCode
});

var Image = Backbone.Model.extend({
    urlRoot: "/api/dev/image",
    url: function() {
        var origUrl = Backbone.Model.prototype.url.call(this);
        return origUrl + (origUrl.charAt(origUrl.length - 1) == '/' ? '' : '/');
    }
});

var Images = Backbone.Tastypie.Collection.extend({
    model: Image,
    url: function(){
        return this.instanceUrl;
    },
    initialize: function(props){
        this.instanceUrl = props.url;
    }
});

var getBroadScaleClassificationCopyURL = function(annotationSetId) {
    return "/api/dev/annotation_set/" + annotationSetId + "/copy_wholeimage_classification/"
}

var getBroadScaleSimilarityStatusURL = function(annotationSetId) {
    return "/api/dev/annotation_set/" + annotationSetId + "/get_image_similarity_status/"
}

var similarImages;
var thumbnailImages;
var thumbnailsPerPage = 10;
var points = new PointAnnotations();
var broadScalePoints = new WholeImageAnnotations();
var annotationSets = new AnnotationSets();
var annotationCodeList = new AnnotationCodeList();
var currentImageInView;
var map;
var bidResult;
var selectedImageId = -1;
var projectId = -1;
var selectedThumbnailPosition = 0;

//yeah, it's a global.
var nested_annotation_list;
var plain_annotation_list;

OrchestratorView = Backbone.View.extend({
    el: $('div'),
    events: {
    },
    onLoadError: function(model, response, options) {
        $.pnotify({
            title: 'Error',
            text: "Failed to load the annotation code list. Try refreshing the page.",
            type: 'error', // success | info | error
            hide: true,
            icon: false,
            history: false,
            sticker: false
        });
    },
    initialize: function () {

        //look out for window resize events
        $(window).resize(function(e){
            //trigger an event to redraw
            GlobalEvent.trigger("screen_changed");
        });

        //load the data
        annotationSets.fetch({async:false, data: { project: projectId }, error: this.onLoadError});
        project.fetch({async: false, error: this.onLoadError});
        //annotationCodeList.fetch({async: false, data: {limit: 500}});
        annotationCodeList.fetch({
            async: false,
            data: { limit: 999 },
            success: function (model, response, options) {
                nested_annotation_list = classificationTreeBuilder(model.toJSON());
                plain_annotation_list = model.toJSON();
                projectId = project.id;
            },
            error: this.onLoadError
        });

        var ann_id = annotationSets.at(0).get('id')

        var bookmarkedImageId = -1;
        var bid = catami_getURLParameter("bid"); //get image id from bid param from URL
        var fetchOffset = 0;        
        if (bid && bid != 'null') bookmarkedImageId = bid;

        if (bookmarkedImageId != -1) { //if there's an image id, get position of image within the annotation set
            jQuery.ajax({
                url: '/api/dev/annotation_set/'
                        + ann_id + '/'
                        + bookmarkedImageId
                        + '/image_by_id/',
                success: function (result) {
                    bidResult = result;
                    selectedImageId = result.imageId;
                    fetchOffset = Math.floor(result.position / thumbnailsPerPage) * thumbnailsPerPage;                    
                },
                async: false
            });            
        }

        similarImages = new Images({ "url": "/api/dev/annotation_set/" + ann_id + "/similar_images/" });
        thumbnailImages = new Images({ "url": "/api/dev/annotation_set/" + ann_id + "/images/?limit=" + thumbnailsPerPage });
        fetchThumbnails(fetchOffset);
        createPagination(thumbnailImages.meta);

        //load the views
        this.breadcrumbNavigationView = new BreadcrumbNavigationView({});
        this.thumbnailStripView = new ThumbnailStripView({model : annotationSets});
        this.imagesAnnotateView = new ImageAnnotateView({ model: annotationSets });        
        this.chooseAnnotationView = new ChooseAnnotationView({});

        if (annotationSets.at(0).get('annotation_set_type') === 1){
            this.wholeImageAnnotationSelectorView = new WholeImageAnnotationSelectorView({});
            this.wholeImageControlBarView = new WholeImageControlBarView({});
            this.similarityImageView = new SimilarityImageView({});
        } else {
            //hide similarity for point view
            $('#SimilarImageTabButton').hide();

            this.pointControlBarView = new PointControlBarView({});
        }

        this.annotationStatusView = new AnnotationStatusView({});

        //render the views
        this.render();
    },
    render: function () {
        var image = thumbnailImages.first();
        selectedImageId = image.get('id');

        this.assign(this.breadcrumbNavigationView,'#BreadcrumbContainer');
        this.assign(this.thumbnailStripView, '#ThumbnailStripContainer');
        this.assign(this.imagesAnnotateView, '#ImageContainer');
        this.assign(this.chooseAnnotationView, '#ChooseAnnotationContainer');
        this.assign(this.annotationStatusView, '#AnnotationStatusContainer');

        if (annotationSets.at(0).get('annotation_set_type') === 1){
            this.assign(this.wholeImageAnnotationSelectorView, '#whole-image-annotation-selector');
            this.assign(this.similarityImageView, '#ImageSimilarityContainer');
            this.assign(this.wholeImageControlBarView, '#ControlBarContainer');
        } else {
            this.assign(this.pointControlBarView, '#ControlBarContainer');
        }
        
        var web_location = image.get('web_location');        
        
        if (bidResult) {
            selectedImageId = bidResult.imageId;
            web_location = bidResult.web_location
            bidResult = null;//reset
        }
        GlobalEvent.trigger("thumbnail_selected_by_id", selectedImageId, web_location);
    },
    assign : function (view, selector) {
        view.setElement($(selector)).render();
    }

});


BreadcrumbNavigationView = Backbone.View.extend({
    el: $('div'),
    initialize: function () {
    },
    render: function(){
        var annotationSetVariables = {
            "name": project.get("name"),
            "id": project.get("id")
        };

        // Compile the template using underscore
        var breadcrumbTemplate = _.template($("#BreadcrumbTemplate").html(), annotationSetVariables);

        // Load the compiled HTML into the Backbone "el"
        this.$el.html(breadcrumbTemplate);

        return this;
    },
    events: {}
});

WholeImageAnnotationSelectorView = Backbone.View.extend({
    el: "#whole-image-annotation-selector",
    model: new WholeImageAnnotation(),
    events: {
    },
    initialize: function () {},
    render: function () {
        var wholeImageTemplate = "";

        wholeImageTemplate += _.template($("#WholeImageAnnotationTemplate").html(), {});

        // // Load the compiled HTML into the Backbone "el"
        this.$el.html(wholeImageTemplate);
        return this.el;
    }
});

//shown only for points annotations
PointControlBarView = Backbone.View.extend({
    initialize: function () {},
    render: function () {
        var imageZoomControlTemplate = _.template($("#PointControlBarTemplate").html(), {});

        // Load the compiled HTML into the Backbone "el"
        this.$el.html(imageZoomControlTemplate);

        $("#ImageContainer").panzoom({
            $zoomIn: $(".zoom-in"),
            $zoomOut: $(".zoom-out"),
            $zoomRange: $(".zoom-range"),
            $reset: $(".reset")
        });

        $('#hide_points_button').mousedown(function(){GlobalEvent.trigger("hide_points");});
        $('#hide_points_button').mouseup(function() {GlobalEvent.trigger("show_points");});

        //triggering the event for backbone so reference to this class get passed down the chain
        $('#deselect_points_button').click(function(){GlobalEvent.trigger("deselect_points");});

        return this.el;
    }
});

//shown only for whole image annotations
WholeImageControlBarView = Backbone.View.extend({
    initialize: function () {},
    render: function () {
        var imageZoomControlTemplate = _.template($("#WholeImageControlBarTemplate").html(), {});

        // // Load the compiled HTML into the Backbone "el"
        this.$el.html(imageZoomControlTemplate);

        $("#ImageContainer").panzoom({
            $zoomIn: $(".zoom-in"),
            $zoomOut: $(".zoom-out"),
            $zoomRange: $(".zoom-range"),
            $reset: $(".reset")
        });

        return this.el;
    }
});

ImageZoomControlView = Backbone.View.extend({
    initialize: function () {},
    render: function () {
        var imageZoomControlTemplate = _.template($("#ImageZoomControlTemplate").html(), {});

        // // Load the compiled HTML into the Backbone "el"
        this.$el.html(imageZoomControlTemplate);

        $("#ImageContainer").panzoom({
            $zoomIn: $(".zoom-in"),
            $zoomOut: $(".zoom-out"),
            $zoomRange: $(".zoom-range"),
            $reset: $(".reset")
        });

        return this.el;
    }
});

ImagePointsControlView = Backbone.View.extend({
    initialize: function () {},
    render: function () {
        var imagePointsControlTemplate = _.template($("#ImagePointsControlTemplate").html(), {});

        // // Load the compiled HTML into the Backbone "el"
        this.$el.html(imagePointsControlTemplate);

        $('#hide_points_button').mousedown(function(){GlobalEvent.trigger("hide_points");});
        $('#hide_points_button').mouseup(function() {GlobalEvent.trigger("show_points");});

        //triggering the event for backbone so reference to this class get passed down the chain
        $('#deselect_points_button').click(function(){GlobalEvent.trigger("deselect_points");});

        return this.el;
    }
});


// helper functions, to be (possibly) removed pending some API/server changes

function getUsefulCaabRoot(caab_code_id){
    // returns either Biota, Substrate, Relief of Bedform
    var rootTypeText = ['Biota', 'Substrate', 'Relief', 'Bedforms'];
    var caabCodeRoots = ['80000000','82001000','82003000','82002000'];
    var return_code;
    
    if (plain_annotation_list.length === 0){
        // annotation list has not be initialised. This is bad
        return null;
    }
    var currentCode = plain_annotation_list[parseInt(caab_code_id,10)-1];

    if (currentCode.caab_code === '82000000'){
        // Physical ... not useful as roots for broad classification
        return '82000000';
    }

    if (currentCode.caab_code === '00000000'){
        //Not Considered ... not useful as roots for broad classification
        return '00000000';
    }

    if (currentCode.caab_code === '00000001'){
        //unscorable ... not useful as roots for broad classification
        return '00000001';
    }

    if (currentCode.caab_code !== caabCodeRoots[0] && currentCode.caab_code !== caabCodeRoots[1] &&
        currentCode.caab_code !== caabCodeRoots[2] && currentCode.caab_code !== caabCodeRoots[3]){

        parent_text = currentCode.parent.split('/');
        parent_id = parent_text[parent_text.length-2];
        return_code  = getUsefulCaabRoot(parent_id);
    } else {
        return currentCode.caab_code;
    }

    return return_code;
}


function loadPage(offset) {
    fetchThumbnails(offset);
    orchestratorView.thumbnailStripView.render();

    var image = thumbnailImages.first();
    selectedImageId = image.get('id');
    GlobalEvent.trigger("thumbnail_selected_by_id", selectedImageId, image.get('web_location'));
}

function fetchThumbnails(offset) {
    var off = {};
    if (offset) off = offset;
    thumbnailImages.fetch({
        data: {
            offset: off,
        },
        async: false,
        success: function (model, response, options) {
            currentOffset = offset;
            //alert('currentOffset : ' + currentOffset + ' after fetching meta : ' + thumbnailImages.meta.toSource());
        },
        error: function (model, response, options) {
            alert('Error fetching thumbnails : ' + response);
        }
    });
}

function createPagination(meta) {
    //Create pagination
    var options = thumbnailPaginationOptions(meta);
    $('#pagination').bootstrapPaginator(options);
}

function createBookmark() {
    var url = location.protocol + '//' + location.hostname + (location.port ? ':' + location.port : '') 
              + "/projects/" + projectId + "/annotate/?bid=";
    window.prompt("Bookmark URL Generated", url + selectedImageId);
}


// helper functions, to be removed pending some API/server
function caab_as_node(object){
    var node = {};
    node.name = object.code_name;
    node['cpccode'] = object.cpc_code;
    node['color'] = '#'+object.point_colour;
    node['caabcode_object'] = object.caab_code;
    node['caabcode_id'] = object.id;
    return node;
}


function classificationTreeBuilder(jsonData){
    // takes the json of caab code objects from the catami API
    // and converts it from a list of objects with parent information
    // to a JSON Tree with child arrays
    var new_array = [];

    var lookup = [];
    for (var i = 0, len = jsonData.length; i < len; i++) {
      var temp =  jsonData[i];
      lookup[jsonData[i].id] = temp;
    }
    for (var index = 1; index < lookup.length; index++){
      new_array.push(caab_as_node(lookup[index]));
    }

    //list is now ordererd so we build the tree starting at the bottom and working up

    for (index = lookup.length - 1; index > 0; index--){
        // get the ID of the parent from the parent url
        if (lookup[index].parent !== null) {
          parent_text = lookup[index].parent.split('/');
          parent_id = parent_text[parent_text.length-2];
          if (parent_id > -1){
            if (new_array[parent_id-1].children === undefined){
                new_array[parent_id-1].children = [];
            }
            new_array[parent_id-1].children.push(new_array[index-1]);
          }
        }
    }

    // we accululated the children to parent nodes from the bottom up. So
    // everything ends up the top node
    return new_array[0];
}


function buildList(node, isSub){
    var html = '';
    if (isSub === false){html += '<ul class="accordion">';}

    try{
        if(node.children){
            html += '<li>';

            if (parseInt(node.caabcode_id,10) === 2) {
                html += '<a href="#biota_root_node" data-id=' + node.caabcode_id + '>' + node.name + '</a>';
            } else if (parseInt(node.caabcode_id,10) === 239){
                html += '<a href="#substrate_root_node" data-id=' + node.caabcode_id + '>' + node.name + '</a>';
            } else if (parseInt(node.caabcode_id,10) === 256){
                html += '<a href="#relief_root_node" data-id=' + node.caabcode_id + '>' + node.name + '</a>';
            } else if (parseInt(node.caabcode_id,10) === 264){
                html += '<a href="#bedforms_root_node" data-id=' + node.caabcode_id + '>' + node.name + '</a>';
            } else if (parseInt(node.caabcode_id,10) === 1){
                html += '<a href="#overall_root_node" data-id=' + node.caabcode_id + '>' + node.name + '</a>';
            } else {
                html += '<a href="#" data-id=' + node.caabcode_id + '>' + node.name + '</a>';
            }
            html += '<ul>';
            for (var i = node.children.length - 1; i >= 0; i--) {
                html += buildList(node.children[i], true);
            }
            html += '</ul>';
        } else {
            html += '<li>';
            html += '<a class="endpoint" href="#" data-id=' + node.caabcode_id + '>' + node.name + '</a>';
        }
        html += '</li>';
    } catch(e){
        //node.children is undefined.  Usually this means you need to load the catami classification table
        html += '<div class="alert alert-error"><p>I\'ve hit a problem making the annotation view.  <br>Please contact the CATAMI admin team for help.</p></div';
    }
    if (isSub === false){html += '</ul>';}
    return html;
}

var spinnerOpts = {
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
        color: '#000',
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
        left: 'auto'
        // Top position relative to parent in px
        //left: '-10px' // Left position relative to parent in px
    };

/*
var spinnerOpts = {
  lines: 17, // The number of lines to draw
  length: 20, // The length of each line
  width: 13, // The line thickness
  radius: 4, // The radius of the inner circle
  corners: 0.8, // Corner roundness (0..1)
  rotate: 0, // The rotation offset
  direction: 1, // 1: clockwise, -1: counterclockwise
  color: '#000', // #rgb or #rrggbb
  speed: 1.7, // Rounds per second
  trail: 44, // Afterglow percentage
  shadow: false, // Whether to render a shadow
  hwaccel: false, // Whether to use hardware acceleration
  className: 'spinner', // The CSS class to assign to the spinner
  zIndex: 2e9, // The z-index (defaults to 2000000000)
  top: 'auto', // Top position relative to parent in px
  left: 'auto' // Left position relative to parent in px
};*/
