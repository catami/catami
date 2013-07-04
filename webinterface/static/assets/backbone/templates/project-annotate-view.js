var GlobalEvent = _.extend({}, Backbone.Events);

ProjectAnnotateView = Backbone.View.extend({
    model: AnnotationSets,
    el: $('div'),
    initialize: function () {
        //bind to the blobal event, so we can get events from other views
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

ImageAnnotateView = Backbone.View.extend({
    model: AnnotationSets,
    el: $('div'),
    initialize: function () {
        //bind to the blobal event, so we can get events from other views
        GlobalEvent.on("thumbnail_selected", this.thumbnailSelected, this);
    },
    renderSelected: function (selected) {
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
    events: {
        "thumbnail_selected": "thumbnailSelected"
    },
    thumbnailSelected: function(selectedPosition) {
        this.renderSelected(selectedPosition);
    }
});


