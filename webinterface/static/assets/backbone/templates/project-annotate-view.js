ProjectAnnotateView = Backbone.View.extend({
    model: AnnotationSets,
    el: $('div'),
    initialize: function () {
        this.render();
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
            imageTemplate += _.template($("#ImageTemplate").html(), imageVariables);
        }

        //render the items to the main template
        var annotationSetVariables = {
            "images": imageTemplate
        };

        // Compile the template using underscore
        var projectTemplate = _.template($("#ProjectAnnotateTemplate").html(), annotationSetVariables);

        // Load the compiled HTML into the Backbone "el"
        this.$el.html(projectTemplate);

        return this;
    },
    events: {

    }
});
