var GlobalEvent = _.extend({}, Backbone.Events);

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

var similarImages;
var points = new PointAnnotations();
var annotationSets = new AnnotationSets();
var annotationCodeList = new AnnotationCodeList();
var currentImageInView;

//yeah, it's a global.
var nested_annotation_list;
var plain_annotation_list;

var wholeImageAnnotations = new WholeImageAnnotations();

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
            },
            error: this.onLoadError
        });
        similarImages = new Images({"url": "/api/dev/annotation_set/" + annotationSets.at(0).get('id') + "/similar_images/"});

        //load the views
        this.thumbnailStripView = new ThumbnailStripView({model : annotationSets});
        this.imagesAnnotateView = new ImageAnnotateView({model : annotationSets});
        this.chooseAnnotationView = new ChooseAnnotationView({});
        this.imagePointsControlView = new ImagePointsControlView({});
        this.imageZoomControlView = new ImageZoomControlView({});

        if (annotationSets.at(0).get('annotation_set_type') === 1){
            this.wholeImageAnnotationSelectorView = new WholeImageAnnotationSelectorView({});
        } else {
            this.imagePointsPILSView = new ImagePointsPILSView({});
        }

        this.imagePointsPILSView = new ImagePointsPILSView({});
        this.similarityImageView = new SimilarityImageView({});

        //render the views
        this.render();

    },
    render: function () {
        this.assign(this.thumbnailStripView, '#ThumbnailStripContainer');
        this.assign(this.imagesAnnotateView, '#ImageContainer');
        this.assign(this.chooseAnnotationView, '#ChooseAnnotationContainer');
        this.assign(this.imagePointsControlView, '#ImagePointsControlContainer');
        this.assign(this.imageZoomControlView, '#ImageZoomControlContainer');

        if (annotationSets.at(0).get('annotation_set_type') === 1){
            this.assign(this.wholeImageAnnotationSelectorView, '#whole-image-annotation-selector');
            this.assign(this.similarityImageView, '#ImageSimilarityContainer');
        } else {
            this.assign(this.imagePointsPILSView, '#ImagePILSContainer');
        }

        //trigger an event for selecting the first thumbanil in the list
        GlobalEvent.trigger("thumbnail_selected", 0);
    },
    assign : function (view, selector) {
        view.setElement($(selector)).render();
    }

});

ChooseAnnotationView = Backbone.View.extend({
    model: AnnotationCodeList,
    el: $('div'),
    initialize: function () {

        GlobalEvent.on("annotation_chosen", this.annotationChosen, this);
        GlobalEvent.on("point_is_selected", this.initializeSelection, this);
        GlobalEvent.on("new_parent_node", this.new_parent_node, this);
        GlobalEvent.on("OpenToBiotaTree", this.openTreeToBiota, this);
        GlobalEvent.on("OpenToSubstrateTree", this.openTreeToSubstrate, this);
        GlobalEvent.on("OpenToReliefTree", this.openTreeToRelief, this);
        GlobalEvent.on("OpenToBedformTree", this.openTreeToBedform, this);

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
        this.initTreeToTopItem();

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
    },
    initTreeToTopItem: function(){
        //make the first item expanded
        $('ul.accordion > li').addClass('active', 'true');
        $('ul.accordion > li > ul').css('display', 'block');
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

        var annotationSetTypes = ["fine scale","broad scale"];

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
        }
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
            });
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

            if(theCaabCode === "") {
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

        $('#hide_points_button').mousedown(function(){GlobalEvent.trigger("hide_points");});
        $('#hide_points_button').mouseup(function() {GlobalEvent.trigger("show_points");});

        //triggering the event for backbone so reference to this class get passed down the chain
        $('#deselect_points_button').click(function(){GlobalEvent.trigger("deselect_points");});

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


WholeImageAnnotationSelectorView = Backbone.View.extend({
    el: "#whole-image-annotation-selector",
    model: WholeImageAnnotations,
    events: {
        "click #clear_all_broad_scale": "clearAllWholeImageAnnotations",
        "click #biota_annotation_label": "highlightInterfaceForBiota",
        "click #substrate_annotation_label": "highlightInterfaceForSubstrate",
        "click #relief_annotation_label": "highlightInterfaceForRelief",
        "click #bedform_annotation_label": "highlightInterfaceForBedform"
    },

    initialize: function () {

        var wholeImageTemplate = _.template($("#WholeImageAnnotationTemplate").html(),{});
        
        // Load the compiled HTML into the Backbone "el"
        this.$el.html(wholeImageTemplate);

        GlobalEvent.on("annotation_to_be_set", this.wholeImageAnnotationChosen, this);
        GlobalEvent.on("thumbnail_selected", this.thumbnailSelected, this);

        this.render();
        this.initAllAnnotations();
    },
    render: function () {
        var wholeImageTemplate = "";

        var wholeImageVariables = {};
        wholeImageTemplate += _.template($("#WholeImageAnnotationTemplate").html(), wholeImageVariables);

        // // Load the compiled HTML into the Backbone "el"
        this.$el.html(wholeImageTemplate);
        return this.el;
    },
    wholeImageAnnotationChosen: function(caab_code_id) {
        // an annotation has been selected in the annotation chooser
        // 
        var rootTypeText = ['Biota', 'Substrate', 'Relief', 'Bedforms'];
        var caabCodeRoots = ['80000000','82001000','82003000','82002000'];

        var usefulRootCaabCode = getUsefulCaabRoot(caab_code_id);
        var selectedCaabCode = plain_annotation_list[parseInt(caab_code_id,10)-1];

        if (selectedCaabCode.caab_code === '00000001'){
            // unscorable. Set all to unscorable
            $('#dominant_biota').text('Unscorable');
            $('#dominant_substrate').text('Unscorable');
            $('#relief').text('Unscorable');
            $('#bedform').text('Unscorable');
        } else {
            this.updatePointWithCaabcode(usefulRootCaabCode, selectedCaabCode);
        }
    },
    updatePointWithCaabcode: function(updateRootCaabCode, updateCaabCode){
        //update whole image point with selected caab_code
        // - first check to see if the class of code specified in 'updateRootCaabCode'
        //   already exists.  If it does, we just update that entry
        //
        // - If the class of code specified in updateRootCaabCode does not exist yet
        //   in the set then take the first unspecified whole image annotation and 
        //   set it with the selected caab_code
        var parent = this;

        //get the selected image
        var annotationSet = annotationSets.at(0);
        var image = annotationSet.get("images")[currentImageInView];
        //based on that image query the API for the points
        var whole_image_points = new WholeImageAnnotations();

        whole_image_points.fetch({
            data: { limit: 100, image: image.id, annotation_set: annotationSet.get('id') },
            success: function (model, response, options) {
                //loop through the points and apply them to the image
                var modelWasUpdated = 0;

                whole_image_points.each(function (whole_image_point) {
                    var annotationCode;
                    var pointId = whole_image_point.get('id');
                    var label = whole_image_point.get('annotation_caab_code');

                    if (label === ""){
                        annotationCode = annotationCodeList.find(function(model) {
                            return model.get('caab_code')==='00000000';
                        });
                    } else {
                        annotationCode = annotationCodeList.find(function(model) {
                            return model.get('caab_code') === whole_image_point.get('annotation_caab_code');
                        });
                    }


                    var modelRootCaabCode = getUsefulCaabRoot(annotationCode.get('id'));

                    if ((modelRootCaabCode === updateRootCaabCode) && updateRootCaabCode !== null) {

                        // update this ID with the new caab code 'updateCaabCode'
                        var properties = { 'annotation_caab_code': updateCaabCode.caab_code };
                        modelWasUpdated = 1;
                        var theXHR = whole_image_point.save(properties, {
                                patch: true,
                                headers: {"cache-control": "no-cache"},
                                success: function (model, xhr, options) {
                                    parent.renderPointsForImage(currentImageInView);
                                },
                                error: function (model, xhr, options) {
                                    if (theXHR.status == "201" || theXHR.status == "202") {
                                        //other trouble

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
                            });
                    }
                });

                if(modelWasUpdated === 0){
                    // then model was not updated, this broad scale class was not previously set.
                    // now we set it using the first available whole image point
                    var properties = { 'annotation_caab_code': updateCaabCode.caab_code };

                    whole_image_points.each(function (whole_image_point) {
                        var annotationCode;
                        var pointId = whole_image_point.get('id');
                        var label = whole_image_point.get('annotation_caab_code');

                        if (label === ""){
                            annotationCode = annotationCodeList.find(function(model) {
                                return model.get('caab_code')==='00000000';
                            });
                        } else {
                            annotationCode = annotationCodeList.find(function(model) {
                                return model.get('caab_code') === whole_image_point.get('annotation_caab_code');
                            });
                        }

                        var newModelRootCaabCode = getUsefulCaabRoot(updateCaabCode.id);
                        
                        if ((label === '' || label === '00000000') && parseInt(modelWasUpdated,10) === 0 && newModelRootCaabCode !== null){
                            // point is 'not considered', so we can use it
                            modelWasUpdated = 1;

                            var theXHR = whole_image_point.save(properties, {
                                patch: true,
                                headers: {"cache-control": "no-cache"},
                                success: function (model, xhr, options) {
                                    parent.renderPointsForImage(currentImageInView);
                                },
                                error: function (model, xhr, options) {
                                    if (theXHR.status == "201" || theXHR.status == "202") {
                                        //other trouble

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
                            });
                        }
                    });
                }
            },
            error: function (model, response, options) {
                $.pnotify({
                    title: 'Failed to load broad scale annotations for this image. Try refreshing the page.',
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
    renderPointsForImage: function(selected) {
        //get all whole image annotation points for selected image
        //and display them in the appropriate UI locations

        var rootTypeText = ['Biota', 'Substrate', 'Relief', 'Bedforms'];
        var caabCodeRoots = ['80000000','82001000','82003000','82002000'];

        var parent = this;

        //get the selected image
        var annotationSet = annotationSets.at(0);
        var image = annotationSet.get("images")[selected];

        // $('#dominant_biota').text('Not Considered');
        // $('#dominant_substrate').text('Not Considered');
        // $('#relief').text('Not Considered');
        // $('#bedform').text('Not Considered');

        //based on that image query the API for the points
        var whole_image_points = new WholeImageAnnotations();

        whole_image_points.fetch({
            data: { limit: 100, image: image.id, annotation_set: annotationSet.get('id') },
            success: function (model, response, options) {
                //loop through the points and apply them to the image
                whole_image_points.each(function (whole_image_point) {
                    var annotationCode;
                    var pointId = whole_image_point.get('id');
                    var label = whole_image_point.get('annotation_caab_code');
                    
                    if (label === ""){
                        annotationCode = annotationCodeList.find(function(model) {
                            return model.get('caab_code')==='00000000';
                        });
                    } else {
                        annotationCode = annotationCodeList.find(function(model) {
                            return model.get('caab_code')===whole_image_point.get('annotation_caab_code');
                        });
                    }

                    var usefulRootCaabCode = getUsefulCaabRoot(annotationCode.get('id'));

                    if (usefulRootCaabCode === caabCodeRoots[0]) {
                        // Biota
                        $('#dominant_biota').text(annotationCode.get('code_name'));
                    } else if (usefulRootCaabCode === caabCodeRoots[1]) {
                        // Substrate
                        $('#dominant_substrate').text(annotationCode.get('code_name'));
                    } else if (usefulRootCaabCode === caabCodeRoots[2]) {
                        // Relief
                        $('#relief').text(annotationCode.get('code_name'));
                    } else if (usefulRootCaabCode === caabCodeRoots[3]) {
                        // Bedforms
                        $('#bedform').text(annotationCode.get('code_name'));
                    }
                });

            },
            error: function (model, response, options) {
                $.pnotify({
                    title: 'Failed to load broad scale annotations for this image. Try refreshing the page.',
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
        currentImageInView = selectedPosition;

        this.initAllAnnotations();
        this.renderPointsForImage(selectedPosition);
    },
    highlightInterfaceForBiota: function(){
        $('a[href=#biota_root_node]').trigger('activate-node');
    },
    highlightInterfaceForSubstrate: function(){
        $('a[href=#substrate_root_node]').trigger('activate-node');
    },
    highlightInterfaceForRelief: function(){
        $('a[href=#relief_root_node]').trigger('activate-node');
    },
    highlightInterfaceForBedform: function(){
        $('a[href=#bedforms_root_node]').trigger('activate-node');
    },
    initAllAnnotations: function() {
        $('#dominant_biota').text('Not set');
        $('#dominant_substrate').text('Not set');
        $('#relief').text('Not set');
        $('#bedform').text('Not set');
    },
    clearAllWholeImageAnnotations: function(){
        //set all to 'not considered'
        var parent = this;
        //get the selected image
        var annotationSet = annotationSets.at(0);
        var image = annotationSet.get("images")[currentImageInView];
        //based on that image query the API for the points
        var whole_image_points = new WholeImageAnnotations();

        $('#dominant_biota').text('Not set');
        $('#dominant_substrate').text('Not set');
        $('#relief').text('Not set');
        $('#bedform').text('Not set');

        whole_image_points.fetch({
            data: { limit: 100, image: image.id, annotation_set: annotationSet.get('id') },
            success: function (model, response, options) {
                // 
                var properties = { 'annotation_caab_code': '' };

                whole_image_points.each(function (whole_image_point) {
                    var theXHR = whole_image_point.save(properties, {
                        patch: true,
                        headers: {"cache-control": "no-cache"},
                        success: function (model, xhr, options) {
                            console.log('Broad scale point was reset for ',image);
                        },
                        error: function (model, xhr, options) {
                            if (theXHR.status == "201" || theXHR.status == "202") {
                                //other trouble

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
                    });
                });
            },
            error: function (model, response, options) {
                $.pnotify({
                    title: 'Failed to load broad scale annotations for this image. Try refreshing the page.',
                    text: response.status,
                    type: 'error', // success | info | error
                    hide: true,
                    icon: false,
                    history: false,
                    sticker: false
                });
            }
        });

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

    if (currentCode.caab_code === '82000000' || currentCode.caab_code === '00000000'){
        // not useful as roots for broad classification
        return null;
    }

    if (currentCode.caab_code === '00000001'){
        //unscorable
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


SimilarityImageView = Backbone.View.extend({
    currentlySelectedImageIndex: null,
    currentlySelectedImage: null,
    model: Images,
    meta: {},
    initialize: function (options) {
        this.meta = options['meta']; //assign specified metadata to local var

        //bind to the event when a thumbnail is selected
        GlobalEvent.on("thumbnail_selected", this.renderSimilarImages, this);
    },
    renderSimilarImages: function (selected) {
        var parent = this;
        var annotationSet = annotationSets.at(0);
        var image = annotationSet.get("images")[selected];
        this.currentlySelectedImage = image;
        this.currentlySelectedImageIndex = selected;

        //Show a loading status
        $(this.el).empty();
        var loadingTemplate = _.template($("#ImageSimilarityTemplate").html(), { "images": "<div id=\"Spinner\"></div>" });
        this.$el.html(loadingTemplate);
        var target = document.getElementById('Spinner');
        var spinner = new Spinner(spinnerOpts).spin(target);

        //we need to fetch the similar images, and render them
        similarImages.fetch({
            cache: false,
            data: {image: image.id},
            success: function(model, response, options) {
                //remove the loading status
                $(parent.el).empty();

                //get all the images to be rendered
                var imageTemplate = "";

                similarImages.each(function (image, index, list) {
                    var imageVariables = {
                        "thumbnail_location": image.get('thumbnail_location'),
                        "web_location": image.get('web_location'),
                        "index": index
                    };
                    imageTemplate += _.template($("#SimilarityThumbnailTemplate").html(), imageVariables);
                });

                //if we have no images to show then tell the user
                if(imageTemplate == "")
                    imageTemplate = "<div class=\"alert alert-info\"> Could not find any images that look like this one, that you have not already classified.</div>"

                var thumbnailListVariables = { "images": imageTemplate };
                // Compile the template using underscore
                var thumbnailListTemplate = _.template($("#ImageSimilarityTemplate").html(), thumbnailListVariables);
                // Load the compiled HTML into the Backbone "el"

                parent.$el.html(thumbnailListTemplate);
            },
            error: function(model, response, options) {
                //remove the loading status
                $(parent.el).empty();
                var loadingTemplate = _.template($("#ImageSimilarityTemplate").html(), { "images": "<div class=\"alert alert-error\">An error occurred when trying to find similar images.</div>" });
                parent.$el.html(loadingTemplate);
            }
        });

        return this;
    },
    events: {
        'click .yesItsTheSame': 'applySameAnnotations'
    },
    applySameAnnotations: function(event) {
        //get the image
        var parent = this;
        var similarImageIndex = $(event.target).attr("id");
        var image = similarImages.at(similarImageIndex);

        $.get(
            getBroadScaleClassificationCopyURL(annotationSets.at(0).get('id')),
            { source_image: this.currentlySelectedImage.id, destination_image: image.get('id') }
        ).done(
            function(data) {
                $.pnotify({
                    title: 'Info',
                    text: 'Successfully copied broadscale classification.',
                    type: "success",
                    delay: 2000
                });

                parent.refreshView();
            }
        ).fail(
            function() {
                $.pnotify({
                    title: 'Error',
                    text: 'Failed to copy broadscale classification.',
                    type: "error",
                    delay: 2000
                });
            }
        );
    },
    refreshView: function() {
        $(this.el).empty();

        //refresh the thumbnails
        this.renderSimilarImages(this.currentlySelectedImageIndex);
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

        if (parseInt(node.caabcode_id,10) === 2) {
            html += '<a href="#biota_root_node" data-id=' + node.caabcode_id + '>' + node.name + '</a>';
        } else if (parseInt(node.caabcode_id,10) === 239){
            html += '<a href="#substrate_root_node" data-id=' + node.caabcode_id + '>' + node.name + '</a>';
        } else if (parseInt(node.caabcode_id,10) === 256){
            html += '<a href="#relief_root_node" data-id=' + node.caabcode_id + '>' + node.name + '</a>';
        } else if (parseInt(node.caabcode_id,10) === 264){
            html += '<a href="#bedforms_root_node" data-id=' + node.caabcode_id + '>' + node.name + '</a>';
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
