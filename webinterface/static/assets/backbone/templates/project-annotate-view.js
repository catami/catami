var GlobalEvent = _.extend({}, Backbone.Events);

var AnnotationCode = Backbone.Model.extend({
    urlRoot: "/api/dev/annotation_code/"
});

var AnnotationCodeList = Backbone.Tastypie.Collection.extend({
    urlRoot: "/api/dev/annotation_code/",
    model: AnnotationCode
});

//yeah, it's a global.
var annotation_code_list = new AnnotationCodeList();

ChooseAnnotationView = Backbone.View.extend({
    model: AnnotationCodeList,
    el: $('div'),
    initialize: function () {
        // var annotation_code_list = new AnnotationCodeList();
        annotation_code_list.fetch({
            data: { limit: 999 },
            success: function (model, response, options) {},
            error: function (model, response, options) {}
        });

        GlobalEvent.on("annotation_chosen", this.annotationChosen, this);
        this.render();
    },
    render: function() {
        // Compile the template using underscore
        var chooseAnnotationTemplate = _.template($("#ChooseAnnotationTemplate").html(), null);

        // Load the compiled HTML into the Backbone "el"
        this.$el.html(chooseAnnotationTemplate);

        return this;
    },
    events: {
        'mouseenter': 'mouse_entered',
        'mouseleave': 'mouse_exited'
    },
    mouse_entered: function() {
        // selected annotations remain editable until mouse exit
    },
    mouse_exited: function() {
        // selected annotations rare now set with the current annotation code
        GlobalEvent.trigger("annotation_to_be_set", this.current_annotation);
    },
    annotationChosen: function(annotationCode){
          //alert(annotationCode);
          this.current_annotation = annotationCode;
          this.$('#current_annotation_label').text(annotationCode);
          // this.$('#goto_parent_button').text('Parent of '+annotationCode);
    }
});

ChooseAnnotationView.current_annotation = null;

ProjectAnnotateView = Backbone.View.extend({
    model: AnnotationSets,
    el: $('div'),
    initialize: function () {
        //bind to the global event, so we can get events from other views
        GlobalEvent.on("thumbnail_selected", this.thumbnailSelected, this);

        this.render();
        this.configElastiSlide();
    },
    render: function () {

        //ge tall the images to be rendered
        var imageTemplate = "";

        // enforcing only one annotation set per project for the time being, so
        // can assume the first one
        var annotationSet = annotationSets.at(0);
        var images = annotationSet.get("generic_images");

        for(var i=0; i < images.length; i++) {
            var imageVariables = {
                "thumbnail_location": images[i].thumbnail_location
            };
            imageTemplate += _.template($("#ThumbnailTemplate").html(), imageVariables);
        }

        //render the items to the main template
        var annotationSetVariables = {
            "thumbnails": imageTemplate
        };

        // Compile the template using underscore
        var projectTemplate = _.template($("#ProjectAnnotateTemplate").html(), annotationSetVariables);

        // Load the compiled HTML into the Backbone "el"
        this.$el.html(projectTemplate);

        return this;
    },
    configElastiSlide: function() {
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
    model: AnnotationSets,
    el: $('div'),
    events: {
        "thumbnail_selected": "thumbnailSelected"
    },
    initialize: function () {
        //bind to the blobal event, so we can get events from other views
        GlobalEvent.on("thumbnail_selected", this.thumbnailSelected, this);
        GlobalEvent.on("screen_changed", this.screenChanged, this);
        GlobalEvent.on("point_clicked", this.pointClicked, this);
        GlobalEvent.on("annotation_to_be_set", this.annotationChosen, this);
    },
    renderSelectedImage: function (selected) {
        //ge tall the images to be rendered
        var imageTemplate = "";

        // enforcing only one annotation set per project for the time being, so
        // can assume the first one
        var annotationSet = annotationSets.at(0);
        var image = annotationSet.get("generic_images")[selected];

        var imageVariables = {
            "web_location": image.web_location
        };
        imageTemplate += _.template($("#ImageTemplate").html(), imageVariables);

        // Load the compiled HTML into the Backbone "el"
        this.$el.html(imageTemplate);

        return this;
    },
    renderPointsForImage: function(selected) {

        //get the selected image
        var annotationSet = annotationSets.at(0);
        var image = annotationSet.get("generic_images")[selected];

        //based on that image query the API for the points
        points.fetch({
            data: { limit: 100, image: image.id, generic_annotation_set: annotationSet.get('id') },
            success: function (model, response, options) {

                //loop through the points and apply them to the image
                points.each(function (point) {
                    var pointId = point.get('id');
                    var label = point.get('annotation_caab_code');
                    var labelClass = (label == "00000000") ? 'pointNotAnnotated' : 'pointAnnotated';

                    annotation_object = annotation_code_list.find(function(model) {
                        return model.get('caab_code')===point.get('annotation_caab_code');
                    });

                    var span = $('<span>');
                    span.attr('id', pointId);
                    span.attr('class', labelClass);
                    span.css('top', point.get('y')*$('#Image').height());
                    span.css('left', point.get('x')*$('#Image').width());
                    span.attr('caab_code', label);

                    if (labelClass === 'pointAnnotated'){
                        span.text(annotation_object.id);
                    }

                    //span.attr('onclick', function() {
                    //    GlobalEvent.trigger("point_clicked");
                    //});

                    span.appendTo('#ImageContainer');
                });

                $('span').click(function(){
                    GlobalEvent.trigger("point_clicked", this);
                });

            },
            error: function (model, response, options) {
                alert('Fetch failed: ' + response.status);
            }
        });
    },
    thumbnailSelected: function(selectedPosition) {
        selectedThumbnailPosition = selectedPosition;
        this.renderSelectedImage(selectedPosition);

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

        if(theClass == 'pointSelected' && theCaabCode == '00000000')
            $(thePoint).attr('class', 'pointNotAnnotated');
        else if(theClass == 'pointSelected' && theCaabCode != '00000000')
            $(thePoint).attr('class', 'pointAnnotated');
        else
            $(thePoint).attr('class', 'pointSelected');
    },
    annotationChosen: function(caab_code_id) {
        //get the selected points
        var selectedPoints = $('.pointSelected');
        caab_object = annotation_code_list.get(caab_code_id);

        //save the annotations
        $.each(selectedPoints, function(index, pointSpan) {
            //need to specify the properties to patch
            var properties = { 'annotation_caab_code': caab_object.get('caab_code') };

            var theXHR = points.get(pointSpan.id).save(properties, {
                patch: true,
                success: function (model, xhr, options) {

                    //change the point to annotated
                    var idOfSaved = model.get("id");
                    $('#'+idOfSaved).attr('class', 'pointAnnotated');
                    $('#'+idOfSaved).text(caab_code_id);

                },
                error: function (model, xhr, options) {
                    if (xhr.status == "201" || xhr.status == "202") {
                        //change the point to annotated
                        var idOfSaved = model.get("id");
                        $('#'+idOfSaved).attr('class', 'pointAnnotated');
                    }
                    else {
                        alert("An error occurred. " + theXHR.error_message);
                    }
                }
            });
        });
    }
});



