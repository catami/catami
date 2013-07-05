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


