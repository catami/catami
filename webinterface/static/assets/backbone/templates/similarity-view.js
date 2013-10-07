SimilarityImageView = Backbone.View.extend({
    currentlySelectedImageID: null,
    currentlySelectedImage: null,
    model: Images,
    meta: {},
    initialize: function (options) {
        this.meta = options['meta']; //assign specified metadata to local var

        //bind to the event when a thumbnail is selected
        GlobalEvent.on("thumbnail_selected_by_id", this.renderSimilarImages, this);

        //when an annotation occurs, do some updates
        GlobalEvent.on("annotation_set_has_changed", this.renderSimilarityStatus, this);
    },
    renderSimilarImages: function (selected) {
        var parent = this;
        this.currentlySelectedImageID = selected;

        //Show a loading status
        $(this.el).empty();
        //var loadingTemplate = _.template($("#ImageSimilarityTemplate").html(), { "images": "<div id=\"Spinner\"></div>" });
        var loadingTemplate = _.template($("#ImageSimilarityTemplate").html(), { "images": "Loading similar images...", "controls": "" });
        this.$el.html(loadingTemplate);
        var target = document.getElementById('Spinner');
        //var spinner = new Spinner(spinnerOpts).spin(target);
        $('#SimilarImageBadge').html("<i class=\"icon-refresh icon-spin\"></i>");

        //we need to fetch the similar images, and render them
        similarImages.fetch({
            cache: false,
            data: {image: parent.currentlySelectedImageID},
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

                var controlsTemplate = "";

                //if we have no images to show then tell the user
                if(imageTemplate == "")
                    imageTemplate = "<div class=\"alert alert-info\"> Could not find any images that look like this one, that you have not already classified.</div>"
                else
                    controlsTemplate = $("#SimilaritySelectAllTemplate").html();

                var thumbnailListVariables = { "images": imageTemplate, "controls": controlsTemplate };

                // Compile the template using underscore
                var thumbnailListTemplate = _.template($("#ImageSimilarityTemplate").html(), thumbnailListVariables);
                // Load the compiled HTML into the Backbone "el"

                parent.$el.html(thumbnailListTemplate);

                parent.renderSimilarityStatus();
                $('#SimilarImageBadge').html(similarImages.size());
            },
            error: function(model, response, options) {
                //remove the loading status
                $(parent.el).empty();
                var loadingTemplate = _.template($("#ImageSimilarityTemplate").html(), { "images": "<div class=\"alert alert-error\">An error occurred when trying to find similar images.</div>", "controls": "" });
                parent.$el.html(loadingTemplate);

                $('#SimilarImageBadge').html("-");
            }
        });

        return this;
    },
    events: {
        'click .yesItsTheSame': 'similarModalButtonClicked',
        'mouseover .SimilarThumbnailContainer': 'mouseoverThumbnail',
        'mouseleave .SimilarThumbnailContainer': 'mouseleaveThumbnail',
        'click [id^=\'SimilarSameButton\']': 'similarSameButtonClicked',
        'click #SimilarSameAll': 'similarSameAll'
        //'click [id^=\'SimilarModalButton\']': 'similarModalButtonClicked'
    },
    applySameAnnotations: function(index) {
        //get the image
        var parent = this;
        //var similarImageIndex = $(event.target).attr("id");

        var similarImageIndex = index;
        var image = similarImages.at(similarImageIndex);

        $.get(
            getBroadScaleClassificationCopyURL(annotationSets.at(0).get('id')),
            { source_image: parent.currentlySelectedImageID, destination_image: image.get('id') }
        ).done(
            function(data) {
                parent.renderSimilarityStatus();

                //notify eveyone something has happened
                GlobalEvent.trigger("annotation_set_has_changed");
            }
        ).fail(
            function() {
                $.pnotify({
                    title: 'Error',
                    text: 'Failed to copy broad scale classification.',
                    type: "error",
                    delay: 2000
                });

                parent.renderSimilarityStatus();
            }
        );
    },
    renderSimilarityStatus: function() {
        var parent = this;

        similarImages.each(function (image, index, list) {

            $.get(getBroadScaleSimilarityStatusURL(annotationSets.at(0).get('id')),
                { source_image: parent.currentlySelectedImageID, comparison_image: image.get('id') }
            ).done(
                function(data) {

                    if(data.same == "true"){
                        $('#SimilarSameLayer'+index).show();
                    }
                    else {
                        $('#SimilarSameLayer'+index).hide();
                    }
                }
            )

        });
    },
    refreshView: function() {
        //$(this.el).empty();
        //refresh the thumbnails
        //this.renderSimilarImages(this.currentlySelectedImageID);
    },
    mouseoverThumbnail: function(event) {

        //get the id of the thumbnail
        var id = $(event.target).attr("id");
        //alert(id);

        //show the controls
        this.$("#SimilarSameButton" + id).show();
        this.$("#SimilarModalButton" + id).show();
    },
    mouseleaveThumbnail: function(event) {

        //get the id of the thumbnail
        var id = $(event.target).attr("id");

        //hide the controls
        this.$("#SimilarSameButton" + id).hide();
        this.$("#SimilarModalButton" + id).hide();
    },
    similarSameButtonClicked: function(event) {
        var id = $(event.target).attr("id");

        // if the id is undefined, you may be clicking on the icon in the button, so get the parent button id
        if(id == undefined)
            id = $(event.target).parent().attr("id");

        // get the index for the thumbanail
        id = id.replace("SimilarSameButton", '');

        //copy the annotation
        this.applySameAnnotations(id);
    },
    similarModalButtonClicked: function(event) {
        var similarImageIndex = $(event.target).attr("id");
        this.applySameAnnotations(similarImageIndex);
    },
    similarSameAll: function(event) {
        var parent = this;

        similarImages.each(function (image, index, list) {
            parent.applySameAnnotations(index);
        });
    }
});