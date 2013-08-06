var GlobalEvent = _.extend({}, Backbone.Events);

var AnnotationCode = Backbone.Model.extend({
    urlRoot: "/api/dev/annotation_code/"
});

var AnnotationCodeList = Backbone.Tastypie.Collection.extend({
    urlRoot: "/api/dev/annotation_code/",
    model: AnnotationCode
});

var points = new PointAnnotations();
var annotationSets = new AnnotationSets();
var annotationCodeList = new AnnotationCodeList();

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
            },
            error: this.onLoadError
        });

        //load the views
        this.thumbnailStripView = new ThumbnailStripView({model : annotationSets});
        this.imagesAnnotateView = new ImageAnnotateView({model : annotationSets});
        this.chooseAnnotationView = new ChooseAnnotationView({});
        this.imagePointsControlView = new ImagePointsControlView({});
        this.imageZoomControlView = new ImageZoomControlView({});
        this.imagePointsPILSView = new ImagePointsPILSView({});

        //render the views
        this.render();

    },
    render: function () {
        this.assign(this.thumbnailStripView, '#ThumbnailStripContainer');
        this.assign(this.imagesAnnotateView, '#ImageContainer');
        this.assign(this.chooseAnnotationView, '#ChooseAnnotationContainer');
        this.assign(this.imagePointsControlView, '#ImagePointsControlContainer');
        this.assign(this.imageZoomControlView, '#ImageZoomControlContainer');
        this.assign(this.imagePointsPILSView, '#ImagePILSContainer');

        //trigger an event for selecting the first thumbanil in the list
        GlobalEvent.trigger("thumbnail_selected", 0);
    },
    assign : function (view, selector) {
        view.setElement($(selector)).render();
    }

});

//yeah, it's a global.
var nested_annotation_list;

ChooseAnnotationView = Backbone.View.extend({
    model: AnnotationCodeList,
    el: $('div'),
    initialize: function () {

        GlobalEvent.on("annotation_chosen", this.annotationChosen, this);
        GlobalEvent.on("point_is_selected", this.initializeSelection, this);
        GlobalEvent.on("new_parent_node", this.new_parent_node, this);

        //this.render();
    },
    render: function() {
        // Compile the template using underscore
        var chooseAnnotationTemplate = _.template($("#ChooseAnnotationTemplate").html(), {});

        list_html = buildList(nested_annotation_list, false);

        // Load the compiled HTML into the Backbone "el"
        this.$el.html(chooseAnnotationTemplate);
        $('#annotation-chooser').append(list_html);
        this.clearSelection();

        $('#annotation-chooser ul').accordion();

        //make the first item expanded
        $('ul.accordion > li').addClass('active', 'true');
        $('ul.accordion > li > ul').css('display', 'block');

        return this;
    },
    events: {
        'mouseenter': 'mouse_entered',
        'mouseleave': 'mouse_exited',
        'click #assign_annotation_button': 'annotationFinalised',
        'click #annotation-chooser a': 'annotationChosen'
    },
    mouse_entered: function() {
        // selected annotations remain editable until mouse exit
    },
    mouse_exited: function() {
        // selected annotations rare now set with the current annotation code
        //GlobalEvent.trigger("annotation_to_be_set", this.current_annotation);
    },
    initializeSelection: function() {
        this.$('#assign_annotation_button').css('visibility', 'hidden');
        this.$('#current_annotation_label').text('Select Annotation...');
    },
    clearSelection: function(){
        this.$('#assign_annotation_button').css('visibility', 'hidden');
        this.$('#current_annotation_label').text('Annotation Selector');
    },
    annotationChosen: function(e){
        e.preventDefault();
        var annotation_code_id = $(e.currentTarget).data("id");
        GlobalEvent.trigger("annotation_to_be_set", annotation_code_id);
    },
    annotationFinalised: function(){
        //make it so
        this.$('#assign_annotation_button').css('visibility', 'hidden');
        GlobalEvent.trigger("annotation_to_be_set", this.current_annotation);
    },
    new_parent_node: function(new_parent_id){
        this.current_annotation = new_parent_id;
        var caab_object = annotationCodeList.get(new_parent_id);

        if (new_parent_id === '1'){
            this.$('#assign_annotation_button').css('visibility', 'hidden');
            this.$('#current_annotation_label').text(caab_object.get('code_name'));
        } else {
            this.annotationChosen(new_parent_id);
        }
    }
});
ChooseAnnotationView.current_annotation = null;

ThumbnailStripView = Backbone.View.extend({
    model: AnnotationSets,
    el: $('div'),
    initialize: function () {
        //bind to the global event, so we can get events from other views
        GlobalEvent.on("thumbnail_selected", this.thumbnailSelected, this);
        // this.wholeImageAnnotationSelectorView = new WholeImageAnnotationSelectorView();

        //this.render();

        //this.configElastiSlide();
    },
    render: function () {

        var annotationSetTypes = ["fine scale","broad scale"]

        //get tall the images to be rendered
        var imageTemplate = "";

        // enforcing only one annotation set per project for the time being, so
        // can assume the first one
        var annotationSet = annotationSets.at(0);

        var annotationSetType = annotationSetTypes[annotationSet.get('annotation_set_type')];

        var images = annotationSet.get("images");

        for(var i=0; i < images.length; i++) {
            var imageVariables = {
                "thumbnail_location": images[i].thumbnail_location
            };
            imageTemplate += _.template($("#ThumbnailTemplate").html(), imageVariables);
        }

        //render the items to the main template
        var annotationSetVariables = {
            "thumbnails": imageTemplate,
            "name": project.get("name"),
            "id": project.get("id")
        };

        // Compile the template using underscore
        var projectTemplate = _.template($("#ThumbnailStripTemplate").html(), annotationSetVariables);

        // Load the compiled HTML into the Backbone "el"
        this.$el.html(projectTemplate);

        this.configElastiSlide();

        return this;
    },
    configElastiSlide: function() {
        console.log("initialising");
        $( '#carousel' ).elastislide( {
            orientation : 'horizontal',
            minItems : 5,
            onClick : function( el, position, evt ) {
                //fire an event for backbone for backbone to pick up
                GlobalEvent.trigger("thumbnail_selected", position);
            }
        });
    },
    thumbnailSelected: function(position) {
        $( "#carousel li" ).each(function( localindex ) {
            if (localindex == position) {
                $(this).find('.description').html("<i class='icon-chevron-sign-down icon-2x'></i>");
            } else {
                $(this).find('.description').html("");
            }
        });
    },
    events: {
        "thumbnail_selected": "thumbnailSelected"
    }
});


var selectedThumbnailPosition = 0;

ImageAnnotateView = Backbone.View.extend({
    model: new PointAnnotation(),
    el: $('div'),
    events: {
        "thumbnail_selected": "thumbnailSelected"
    },
    initialize: function () {
        var parent = this;

        //bind to the blobal event, so we can get events from other views
        GlobalEvent.on("thumbnail_selected", this.thumbnailSelected, this);
        GlobalEvent.on("screen_changed", this.screenChanged, this);
        GlobalEvent.on("point_clicked", this.pointClicked, this);
        GlobalEvent.on("point_mouseover", this.pointMouseOver, this);
        GlobalEvent.on("point_mouseout", this.pointMouseOut, this);
        GlobalEvent.on("annotation_to_be_set", this.annotationChosen, this);
        GlobalEvent.on("refresh_point_labels_for_image", this.refreshPointLabelsForImage, this);
        GlobalEvent.on("hide_points", this.hidePoints, this);
        GlobalEvent.on("show_points", this.showPoints, this);
        GlobalEvent.on("deselect_points", this.deselectPoints, this);
    },
    renderSelectedImage: function (selected) {
        //ge tall the images to be rendered
        var imageTemplate = "";

        // enforcing only one annotation set per project for the time being, so
        // can assume the first one
        var annotationSet = annotationSets.at(0);
        var image = annotationSet.get("images")[selected];

        var imageVariables = {
            "web_location": image.web_location
        };
        imageTemplate += _.template($("#ImageTemplate").html(), imageVariables);

        // Load the compiled HTML into the Backbone "el"
        this.$el.html(imageTemplate);

        return this;
    },
    refreshPointLabelsForImage: function() {
        //checks annotated point list in view.  If any label has blank label text, then
        //get it from the relevant API call.
        //
        //labels are made blank when a previouslt labeled point is once again selected

        var annotatedPoints = $('.pointAnnotated');

        $.each(annotatedPoints, function(index, pointSpan) {
            // refresh annotated
            if ($(pointSpan).text() === ""){
                var newpoint = new PointAnnotation({id: pointSpan.id});
                newpoint.fetch({success:function(model) {
                    var annotation_object = annotationCodeList.find(function(listmodel) {
                        return listmodel.get('caab_code')===newpoint.get('annotation_caab_code');
                    });
                    $(pointSpan).text(annotation_object.id);
                }});
            }
        });
    },
    renderPointsForImage: function(selected) {
        var parent = this;

        //get the selected image
        var annotationSet = annotationSets.at(0);
        var image = annotationSet.get("images")[selected];

        //based on that image query the API for the points
        points.fetch({
            data: { limit: 100, image: image.id, annotation_set: annotationSet.get('id') },
            success: function (model, response, options) {

                //loop through the points and apply them to the image
                points.each(function (point) {
                    var pointId = point.get('id');
                    var label = point.get('annotation_caab_code');

                    var annotationCode = annotationCodeList.find(function(model) {
                        return model.get('caab_code')===point.get('annotation_caab_code');
                    });

                    var labelClass = (label === "")
                        ? 'pointNotAnnotated'
                        : 'pointAnnotated';

                    var span = $('<span>');
                    span.attr('id', pointId);
                    span.attr('class', labelClass);
                    span.css('top', point.get('y')*$('#Image').height()-6);
                    span.css('left', point.get('x')*$('#Image').width()-6) ;
                    span.css('z-index', 10000);
                    span.attr('caab_code', label);
                    span.attr('data-toggle', 'tooltip');

                    if (labelClass === 'pointAnnotated'){
                        span.text(annotationCode.id);
                        span.attr('title', annotationCode.get("code_name"));
                    }

                    span.appendTo('#ImageContainer');
                });

                $("#ImageContainer").children('span').click(function(){
                    GlobalEvent.trigger("point_clicked", this);
                });

                $("#ImageContainer").children('span').mouseover(function(){
                    GlobalEvent.trigger("point_mouseover", this);
                });

                $("#ImageContainer").children('span').mouseout(function(){
                    GlobalEvent.trigger("point_mouseout", this);
                });

                //update pils
                GlobalEvent.trigger("image_points_updated", this);

            },
            error: function (model, response, options) {
                $.pnotify({
                    title: 'Failed to load the points for this image. Try refreshing the page.',
                    text: response.status,
                    type: 'error', // success | info | error
                    hide: true,
                    icon: false,
                    history: false,
                    sticker: false
                });
            }
        });
    },
    thumbnailSelected: function(selectedPosition) {
        selectedThumbnailPosition = selectedPosition;
        this.renderSelectedImage(selectedPosition);

        //turn the zoom off and reset the zoom button
        //this.zoomOff();
        //$('#ZoomToggle').removeClass('active');

        var parent = this;
        //now we have to wait for the image to load before we can draw points
        $("#Image").imagesLoaded(function() {
            parent.renderPointsForImage(selectedPosition);
        });

    },
    screenChanged: function() {
        //loop through the points and apply them to the image
        points.each(function (point) {
            var pointId = point.get('id');
            var span = $('#'+pointId);

            span.css('top', point.get('y')*$('#Image').height());
            span.css('left', point.get('x')*$('#Image').width());
        });
    },
    pointClicked: function(thePoint) {
        var theClass = $(thePoint).attr('class');
        var theCaabCode = $(thePoint).attr('caab_code');

        if(theClass == 'pointSelected' && theCaabCode == ""){
            $(thePoint).attr('class', 'pointNotAnnotated');
        } else if(theClass == 'pointSelected' && theCaabCode != ""){
            $(thePoint).attr('class', 'pointAnnotated');
        } else {

            //firstly we need to check if we need to deselect already labelled points
            $(".pointLabelledStillSelected").each(function (index, pointSpan) {
                $(pointSpan).attr('class', 'pointAnnotated');
            });

            //then we make the current points selected
            $(thePoint).attr('class', 'pointSelected');
            //hide the label, if there is one
            $(thePoint).text("");
            GlobalEvent.trigger("point_is_selected", this);
        }

        this.refreshPointLabelsForImage();
    },
    pointMouseOver: function(thePoint) {
        //get points which have the same caab code assigned
        var samePoints = points.filter(
            function(point) {
                return point.get("annotation_caab_code") == $(thePoint).attr('caab_code');
            }
        );

        //show the labels
        for(var i = 0; i < samePoints.length; i++) {
            $("#"+samePoints[i].get("id")).tooltip('show');
        };
    },
    pointMouseOut: function(thePoint) {
        //remove labels from all points
        points.each(function(point) {
            $("#"+point.get("id")).tooltip('destroy');
        });
    },
    annotationChosen: function(caab_code_id) {
        var parent = this;

        //get the selected points
        var selectedPoints = $('.pointSelected');
        caab_object = annotationCodeList.get(caab_code_id);
        //save the annotations
        $.each(selectedPoints, function(index, pointSpan) {

            //need to specify the properties to patch
            var properties = { 'annotation_caab_code': caab_object.get('caab_code') };

            var theXHR = points.get(pointSpan.id).save(properties, {
                patch: true,
                headers: {"cache-control": "no-cache"},
                success: function (model, xhr, options) {

                    //show label on annotated point
                    var idOfSaved = model.get("id");
                    $('#'+idOfSaved).addClass('pointLabelledStillSelected'); //this means the point stays selected, we are just assigning the class to this point to keep that state
                    $('#'+idOfSaved).attr('title', annotationCodeList.get(caab_code_id).get("code_name"));
                    $('#'+idOfSaved).attr('caab_code', caab_object.get('caab_code'));
                    $('#'+idOfSaved).tooltip("destroy");
                    $('#'+idOfSaved).tooltip("show");

                    //change the point to annotated
                    //var idOfSaved = model.get("id");
                    //$('#'+idOfSaved).attr('class', 'pointAnnotated');
                    //$('#'+idOfSaved).text(caab_code_id);

                    //update the pil sidebar
                    GlobalEvent.trigger("image_points_updated", this);
                },
                error: function (model, xhr, options) {
                    if (theXHR.status == "201" || theXHR.status == "202") {
                        alert("202");

                        //show label on annotated point
                        var idOfSaved = model.get("id");
                        $('#'+idOfSaved).addClass('pointLabelledStillSelected'); //this means the point stays selected, we are just assigning the class to this point to keep that state
                        $('#'+idOfSaved).attr('title', annotationCodeList.get(caab_code_id).get("code_name"));
                        $('#'+idOfSaved).attr('caab_code', caab_object.get('caab_code'));
                        $('#'+idOfSaved).tooltip("destroy");
                        $('#'+idOfSaved).tooltip("show");

                        //var idOfSaved = model.get("id");
                        //$('#'+idOfSaved).attr('class', 'pointAnnotated');
                        //$('#'+idOfSaved).text(caab_code_id);

                        //update the pil sidebar
                        GlobalEvent.trigger("image_points_updated", this);
                    } else if(theXHR.status == "401") {
                        $.pnotify({
                            title: 'You don\'t have permission to annotate this image.',
                            text: theXHR.response,
                            type: 'error', // success | info | error
                            hide: true,
                            icon: false,
                            history: false,
                            sticker: false
                        });
                    }
                    else {
                        $.pnotify({
                            title: 'Failed to save your annotations to the server.',
                            text: theXHR.response,
                            type: 'error', // success | info | error
                            hide: true,
                            icon: false,
                            history: false,
                            sticker: false
                        });
                    }
                }
            })
        });
    },
    hidePoints: function () {
        //loop through the points and hide them
        points.each(function (point) {
            var pointId = point.get('id');
            var span = $('#'+pointId);

            span.css('visibility', 'hidden');
        });
    },
    showPoints: function () {
         //loop through the points and show them
        points.each(function (point) {
            var pointId = point.get('id');
            var span = $('#'+pointId);

            span.css('visibility', 'visible');
        });
    },
    zoomOn: function() {
        $("#Image").elevateZoom({zoomWindowPosition: 1});
    },
    zoomOff: function() {
        $.removeData($("#Image"), 'elevateZoom');
        $('.zoomContainer').remove();
    },
    deselectPoints: function () {

        //deselect any points that are labelled and still selected
        $(".pointLabelledStillSelected").each(function (index, pointSpan) {
            $(pointSpan).attr('class', 'pointAnnotated');
        });

        //deselect any points that are selected
        $(".pointSelected").each(function(index, pointSpan) {
            var theCaabCode = $(pointSpan).attr('caab_code');

            if(theCaabCode == "") {
                $(pointSpan).attr('class', 'pointNotAnnotated');
            } else {
                $(pointSpan).attr('class', 'pointAnnotated');
            }
        });

        //refresh
        this.refreshPointLabelsForImage();
    }
});

WholeImageAnnotationSelectorView = Backbone.View.extend({
    el: "#whole-image-annotation-selector",
    model: new WholeImageAnnotation(),
    events: {
    },
    initialize: function () {},
    render: function () {
        console.log("render WholeImageAnnotationSelectorView");
        var wholeImageTemplate = "";

        wholeImageTemplate += _.template($("#WholeImageAnnotationTemplate").html(), {});

        // // Load the compiled HTML into the Backbone "el"
        this.$el.html(wholeImageTemplate);
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

        $('#hide_points_button').mousedown(function(){GlobalEvent.trigger("hide_points")});
        $('#hide_points_button').mouseup(function() {GlobalEvent.trigger("show_points")});

        //triggering the event for backbone so reference to this class get passed down the chain
        $('#deselect_points_button').click(function(){GlobalEvent.trigger("deselect_points")});

        return this.el;
    }
});

ImagePointsPILSView = Backbone.View.extend({
    initialize: function () {
        //when points are updated, update the pils
        GlobalEvent.on("image_points_updated", this.updatePils, this);
    },
    render: function () {
        var imagePILSTemplate = _.template($("#ImagePILSTemplate").html(), {});

        // // Load the compiled HTML into the Backbone "el"
        this.$el.html(imagePILSTemplate);

        this.updatePils();

        return this.el;
    },
    updatePils: function() {

        var pilHtml = "";
        annotationCodeList.each(function (annotationCode) {
            var caab_code = annotationCode.get('caab_code');
            var count = points.filter(
                function(point) {
                    return point.get("annotation_caab_code") == caab_code;
                }
            ).length;

            if(count > 0) {
                pilHtml += "<li class='active'> <a>("+annotationCode.id+") "+annotationCode.get('code_name')+" <span class='badge badge-info'><b>"+ count +"</b></span> </a> </li>";
            }
        });

        if(pilHtml == "") {
            $("#LabelPils").empty();
            $("#LabelPils").append('<li class="active"> <a>This image is not labelled.</a> </li>');
        } else {
            $("#LabelPils").empty();
            $("#LabelPils").append(pilHtml);
        }

    }
});

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

    // html += '<li>';
    // html += '<a href="#">' + node.name + '</a>';

    if(node.children){
        html += '<li>';
        html += '<a href="#"data-id=' + node.caabcode_id + '>' + node.name + '</a>';
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

    if (isSub === false){html += '</ul>';}
    return html;
}