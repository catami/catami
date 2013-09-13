ThumbnailStripView = Backbone.View.extend({
    model: AnnotationSets,
    el: $('div'),
    initialize: function () {
        //bind to the global event, so we can get events from other views
        GlobalEvent.on("thumbnail_selected_by_id", this.thumbnailSelectedById, this);
        GlobalEvent.on("update_annotation", this.updateAnnotation, this);
        GlobalEvent.on("thumbnails_loaded", this.render, this);
        GlobalEvent.on("annotation_set_has_changed", this.buildAnnotationStatus, this);
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

        this.buildAnnotationStatus();
    },
    buildAnnotationStatus: function () {

        var parent = this;

        var localMap = { "images": [] }; //reset map

        var annotationSetTypes = ["fine scale", "broad scale"];

        // enforcing only one annotation set per project for the time being, so
        // can assume the first one
        var annotationSet = annotationSets.at(0);
        var annotationSetType = annotationSetTypes[annotationSet.get('annotation_set_type')];

        var imageIds = "";
        thumbnailImages.each(function (image) {
            imageIds += image.get('id') + ',';
        });

        imageIds = imageIds.substring(0, imageIds.length - 1); //remove trailing comma
        var imageAnnotations;
        if (annotationSetType === "broad scale")
            imageAnnotations = new WholeImageAnnotations({ "url": "/api/dev/whole_image_annotation/" });
        else imageAnnotations = new PointAnnotations({ "url": "/api/dev/point_annotation/" });
        imageAnnotations.fetch({
            //async: false,
            data: {
                annotation_set: annotationSet.get('id'),
                image__in: imageIds,
                limit: 200
            },
            success: function (model, response, options) {
                //loop through the points and get caab       
                imageAnnotations.each(function (annotation) {
                    var imageId = catami_getIdFromUrl(annotation.get('image'));
                    var code = annotation.get('annotation_caab_code');
                    var name = annotation.get('annotation_caab_name');
                    var annotId = annotation.get('id');
                    if (typeof code != 'undefined') {
                        var imageFound = false;
                        $.each(localMap.images, function (i, im) {
                            if (im.id == imageId) { //image found, add annotation to image                                    
                                var annot_new = {
                                    "id": annotId,
                                    "code": code,
                                    "name": name
                                }
                                im.annotations.push(annot_new);
                                imageFound = true;
                                return;
                            }
                        });
                        if (!imageFound) { //create image with annotation if image not found                           
                            var image_new = {
                                "id": imageId,
                                "annotations": [
                                    {
                                        "id": annotId,
                                        "code": code,
                                        "name": name
                                    }
                                ]
                            }
                            localMap.images.push(image_new);
                        }
                    }
                });

                map = localMap;
                parent.renderAnnotationStatus();
            }
        });

    },
    updateAnnotation: function (imageId, annotId, code, name) {
        updateAnnotation(imageId, annotId, code, name);
        this.renderAnnotationStatus();
    },
    renderAnnotationStatus: function () {
        // enforcing only one annotation set per project for the time being, so
        // can assume the first one
        var annotationSet = annotationSets.at(0);
        var images = annotationSet.get("images");
        for (var i = 0; i < images.length; i++) {
            var im = images[i].split("/"); //value of format  "/api/dev/image/12/", need to split to get image id
            var imid = im[im.length - 2];
            var count = 0;
            $.each(map.images, function (i, image) {
                if (image.id == imid) { //find respective image, and check if annotation is done
                    count = countAnnotated(image);
                    return;
                }
            });
            $('#image_' + imid).text(count);
        }
    },
    thumbnailSelectedByEvent: function (event) {
        selectedImageId = $(event.currentTarget).data("id");
        var webLocation = $(event.currentTarget).data("web_location");
        GlobalEvent.trigger("thumbnail_selected_by_id", selectedImageId, webLocation);
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