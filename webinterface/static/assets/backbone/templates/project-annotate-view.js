var GlobalEvent = _.extend({}, Backbone.Events);

var AnnotationCode = Backbone.Model.extend({
    urlRoot: "/api/dev/annotation_code/"
});

var AnnotationCodeList = Backbone.Tastypie.Collection.extend({
    urlRoot: "/api/dev/annotation_code/",
    model: AnnotationCode
});

ChooseAnnotationView = Backbone.View.extend({
    model: AnnotationCodeList,
    el: $('div'),
    initialize: function () {
        // annotation_code_list = AnnotationCodeList();
        // annotation_code_list.fetch();
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

    },
    annotationChosen: function(annotationCode){
          //alert(annotationCode);
          this.$('#current_annotation_label').text(annotationCode);
          this.$('#goto_parent_button').text('Parent of '+annotationCode);
    }
});

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
            };
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
        GlobalEvent.on("annotation_chosen", this.annotationChosen, this);
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

                    var labelClass = (label == "")
                        ? 'pointNotAnnotated'
                        : 'pointAnnotated';

                    var span = $('<span>');
                    span.attr('id', pointId);
                    span.attr('class', labelClass);
                    span.css('top', point.get('y')*$('#Image').height()-6);
                    span.css('left', point.get('x')*$('#Image').width()-6) ;
                    span.attr('caab_code', label);

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

        if(theClass == 'pointSelected' && theCaabCode == "")
            $(thePoint).attr('class', 'pointNotAnnotated');
        else if(theClass == 'pointSelected' && theCaabCode != "")
            $(thePoint).attr('class', 'pointAnnotated');
        else
            $(thePoint).attr('class', 'pointSelected');
    },
    annotationChosen: function(caab_code) {
        //get the selected points
        var selectedPoints = $('.pointSelected');

        //save the annotations
        $.each(selectedPoints, function(index, pointSpan) {
            console.log(pointSpan.id);
            //need to specify the properties to patch
            var properties = { 'annotation_caab_code': caab_code };

            var theXHR = points.get(pointSpan.id).save(properties, {
                patch: true,
                success: function (model, xhr, options) {

                    //change the point to annotated
                    var idOfSaved = model.get("id");
                    $('#'+idOfSaved).attr('class', 'pointAnnotated');

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
            })
        });
    }
});



