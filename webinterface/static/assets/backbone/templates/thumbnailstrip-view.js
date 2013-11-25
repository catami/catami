ThumbnailStripView = Backbone.View.extend({
    model: AnnotationSets,
    el: $('div'),
    initialize: function () {
        //bind to the global event, so we can get events from other views
        GlobalEvent.on("thumbnail_selected_by_id", this.thumbnailSelectedById, this);
        GlobalEvent.on("update_annotation", this.updateAnnotation, this);
        GlobalEvent.on("thumbnails_loaded", this.render, this);
        GlobalEvent.on("annotation_set_has_changed", this.updateAnnotation, this);
    },
    render: function () {
        //get all the images to be rendered
        var imageTemplate = generateAllThumbnailTemplates(thumbnailImages);

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

        this.updateAnnotation();
    },
    updateAnnotation: function () {
        var parent = this;
        var annotationSetTypes = ["fine scale", "broad scale"];

        // enforcing only one annotation set per project for the time being, so
        // can assume the first one
        var annotationSet = annotationSets.at(0);
        var annotationSetType = annotationSetTypes[annotationSet.get('annotation_set_type')];
        var annotationSetId = annotationSet.get('id');
        var url = "";
        if (annotationSetType === "broad scale")
            url = "/api/dev/whole_image_annotation/" + annotationSetId + "/count_annotations/";
        else
            url = "/api/dev/point_annotation/" + annotationSetId + "/count_annotations/";
        $.ajax({
            url: url,
            dataType: "json",
            //async: false,
            success: function (response, textStatus, jqXHR) {
                map = response;
                parent.renderAnnotationStatus();
            }
        });

        this.renderAnnotationStatus();
    },
    renderAnnotationStatus: function () {
        for (imid in map) {
            $('#image_' + imid).text(map[imid]);
        }
    },
    thumbnailSelectedByEvent: function (event) {
        selectedImageId = $(event.currentTarget).data("id");
        var webLocation = $(event.currentTarget).data("web_location");
        GlobalEvent.trigger("thumbnail_selected_by_id", selectedImageId, webLocation);
        GlobalEvent.trigger("annotation_set_has_changed"); //XXX triggering this event to fetch new image stats and redraw chart for image progress
    },
    thumbnailSelectedById: function (id, webLocation) {

        $("#thumbnail-pane .wrapper").each(function (index, value) {
            $(this).find('.description').html("");
        });
        $('#' + id).find('.description').html("<i class='icon-chevron-sign-right icon-2x'></i>");

        //$('#Image').attr("src", webLocation);
        //$('#Image').attr("data-src", webLocation);
    },
    events: {
        'click .wrapper': 'thumbnailSelectedByEvent'
    }
});

function generateAllThumbnailTemplates(thumbnailImages) {
    var template = ""
    var i = 0;
    thumbnailImages.each(function (image) {
        template += generateThumbnailTemplate(image, i);
        i++;
    });
    return template;
}
function generateThumbnailTemplate(image) {
    var id = image.get('id');
    var statusVariables = { //initialise span for annotated flag using image ids as span id
        "image_id": "image_" + id,
        "status": ""
    }
    statusTemplate = _.template($("#StatusTemplate").html(), statusVariables);

    var imageVariables = {
        "thumbnailId": id,
        "thumbnail_location": image.get('thumbnail_location'),
        "web_location": image.get('web_location'),
        "annotation_status": statusTemplate
    };
    return _.template($("#ThumbnailTemplate").html(), imageVariables);
}