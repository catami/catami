// events triggered
// point_selected:  a fine scale point in selected in the main image view
// point_clicked:  a fine scale point in clicked in the main image view
// point_mouseover: mouse over event happened for a fine scale point in the image view

ImageAnnotateView = Backbone.View.extend({
    model: new PointAnnotation(),
    el: $('div'),
    events: {
        "thumbnail_selected": "thumbnailSelected"
    },
    initialize: function () {
        var parent = this;

        //bind to the global event, so we can get events from other views
        GlobalEvent.on("thumbnail_selected", this.thumbnailSelected, this);
        GlobalEvent.on("thumbnail_selected_by_id", this.thumbnailSelectedWithId, this);
        GlobalEvent.on("screen_changed", this.screenChanged, this);
        GlobalEvent.on("point_clicked", this.pointClicked, this);
        GlobalEvent.on("point_shift_clicked", this.pointShiftClicked, this);
        GlobalEvent.on("point_mouseover", this.pointMouseOver, this);
        GlobalEvent.on("point_mouseout", this.pointMouseOut, this);
        GlobalEvent.on("annotation_to_be_set", this.annotationChosen, this);
        GlobalEvent.on("refresh_point_labels_for_image", this.refreshPointLabelsForImage, this);
        GlobalEvent.on("hide_points", this.hidePoints, this);
        GlobalEvent.on("show_points", this.showPoints, this);
        GlobalEvent.on("deselect_points", this.deselectPoints, this);
    },
    resetLassoCanvas: function() {
        // a helper function for matching the lasso canvas to the image size
        var imageCanvas = $('#CanvasImage')[0];
        var lassoCanvas = $('#CanvasImage2')[0];

        lassoCanvas.width = imageCanvas.width;
        lassoCanvas.height = imageCanvas.height;

        return lassoCanvas;
    },
    findLassoPoints: function() {
        var parent = this;

        // get the canvas context
        var canvas = $('#CanvasImage2')[0];
        var context = canvas.getContext('2d');

        // iterate through the points, and find if the canvas context for that point is the colour of the lasso fill, if so add the point to a similar points list
        var samePoints = [];
        for (var i = 0; i < points.length; i++) {

            var x = points.at(i).get("x");
            var y = points.at(i).get("y");

            //translate the xy percentage points into a pixel location based on the image size
            var width = canvas.width;
            var height = canvas.height;

            var xPixel = Math.round(x * width);
            var yPixel = Math.round(y * height);

            var pointColour = context.getImageData(xPixel, yPixel, 1, 1).data;

            // check if the point is pink
            if (pointColour[0] == 255 &&
                pointColour[1] == 192 &&
                pointColour[2] == 203 &&
                pointColour[3] == 255) {

                samePoints.push(points.at(i));
            }
        }

        // go off and select the points
        for (var i = 0; i < samePoints.length; i++) {
            var point = samePoints[i];
            parent.selectPoint("#" + point.get("id"));
        }

    },
    initializeLasso: function () {
        var parent = this;

        // the context of the lassoo canvas - will be set on mouse down as well incase of image resizes outside image load
        var canvas = parent.resetLassoCanvas();
        var context = canvas.getContext('2d');

        // needed to specify the state of drawing the line
        this.started = false;

        // This is called when you start holding down the mouse button.
        // This starts the pencil drawing.
        $("#CanvasImage2").mousedown(function (ev) {

            // get the context for the canvas - reset on mousedown
            context = parent.resetLassoCanvas().getContext('2d');

            // need to offset the mousepoint on the screen for the image coordinates
            if (ev.layerX || ev.layerX == 0) { // Firefox
                ev._x = ev.layerX;
                ev._y = ev.layerY;
            } else if (ev.offsetX || ev.offsetX == 0) { // Opera
                ev._x = ev.offsetX;
                ev._y = ev.offsetY;
            }

            // properties etc for the line
            context.strokeStyle = 'pink';
            context.fillStyle = 'pink';
            context.lineWidth = 8;
            context.beginPath();
            context.moveTo(ev._x, ev._y);

            // the drawing has started
            this.started = true;
        });

        // This function is called every time you move the mouse. Obviously, it only
        // draws if the tool.started state is set to true (when you are holding down
        // the mouse button).
        $("#CanvasImage2").mousemove(function (ev) {

            // need to offset the mousepoint on the screen for the image coordinates
            if (ev.layerX || ev.layerX == 0) { // Firefox
                ev._x = ev.layerX;
                ev._y = ev.layerY;
            } else if (ev.offsetX || ev.offsetX == 0) { // Opera
                ev._x = ev.offsetX;
                ev._y = ev.offsetY;
            }

            // if we are drawing then keep drawing
            if (this.started) {
                context.lineTo(ev._x, ev._y);
                context.stroke();
            }
        });

        // This is called when you release the mouse button.
        $("#CanvasImage2").mouseup(function (ev) {

            if (this.started) {
                $("#CanvasImage2").mousemove();

                // cut off the line
                context.closePath();
                context.fill();

                // time to stop
                this.started = false;

                // go off and select the points within the lasso
                parent.findLassoPoints();

                //clear the canvas
                context.clearRect(0, 0, canvas.width, canvas.height);
            }
        });
    },
    renderSelectedImageById: function (id) {

        //get all the images to be rendered
        var imageTemplate = "";
        var imageVariables = {
            "web_location": $('#' + id).data("web_location")
        };

        imageTemplate += _.template($("#ImageTemplate").html(), imageVariables);

        // Load the compiled HTML into the Backbone "el"
        this.$el.html(imageTemplate);
        $('.FineScaleEditBox').show();

        this.initializeLasso();

        return this;
    },
    renderSelectedImage: function (selected) {
        //get all the images to be rendered
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

        this.initializeLasso();

        return this;
    },
    /**
     * Refreshes the mouse over labels for points on an image.
     */
    refreshPointLabelsForImage: function () {
        //get all the points on the image
        var allPoints = $('#ImageContainer > span');

        //loop through
        $.each(allPoints, function (index, pointSpan) {

            // get the point from the collection
            var point = PointUtil.getPointWithId(pointSpan.id);

            //get the primary annotation for the point
            var annotationCode = PointUtil.getAnnotationCodeForPoint(point);

            //get the secondary annotation for the point
            var annotationCodeSecondary = PointUtil.getSecondaryAnnotationCodeForPoint(point);

            // check if a point is selected or not
            var classes = $(pointSpan).attr('class').split(/\s+/);
            var pointIsSelected = $.inArray("pointSelected", classes) > -1 ? true : false;

            // update the labels for the point
            // if a point is currently selected, then we don't want to populate the text, only the title,
            // otherwise we get spinny text on points
            if ((annotationCodeSecondary == '' || annotationCodeSecondary == null) && (annotationCode != '' && annotationCode != null)) {

                if (pointIsSelected)
                    $(pointSpan).text("");
                else
                    $(pointSpan).text(annotationCode.get("cpc_code"));

                $(pointSpan).attr('title', annotationCode.get("code_name"));

            } else if (annotationCodeSecondary != '' && annotationCodeSecondary != null && annotationCode != '' && annotationCode != null) {

                if (pointIsSelected)
                    $(pointSpan).text("");
                else
                    $(pointSpan).text(annotationCode.get("cpc_code") + '/' + annotationCodeSecondary.get("cpc_code"));

                $(pointSpan).attr('title', annotationCode.get("code_name") + '/' + annotationCodeSecondary.get("code_name"));
            }

            // if the point is currently selected, show the label
            if (pointIsSelected) {
                $(pointSpan).tooltip("destroy");
                $(pointSpan).tooltip("show");
            }
        });
    },
    renderPointsForImage: function () {

        //destroy all the tooltips before loading new points
        this.pointMouseOut();

        var parent = this;

        //get the selected image
        var annotationSet = annotationSets.at(0);
        //var image = annotationSet.get("images")[selected];

        this.disableAnnotationSelector();

        //query the API for the points for the current image

        points.fetch({
            data: { limit: 100, image: selectedImageId, annotation_set: annotationSet.get('id') },
            success: function (model, response, options) {

                //loop through the points and apply them to the image
                points.each(function (point) {
                    var pointId = point.get('id');
                    var label = point.get('annotation_caab_code');

                    var annotationCode = annotationCodeList.find(function (model) {
                        return model.get('caab_code') === point.get('annotation_caab_code');
                    });

                    var annotationCodeSecondary = '';

                    if (point.get('annotation_caab_code_secondary') !== '') {
                        annotationCodeSecondary = annotationCodeList.find(function (model) {
                            return model.get('caab_code') === point.get('annotation_caab_code_secondary');
                        });
                    }

                    var labelClass = (label === "") ? 'pointNotAnnotated' : 'pointAnnotated';

                    var span = $('<span>');
                    span.attr('id', pointId);
                    span.attr('class', labelClass);
                    span.css('top', point.get('y') * $('#Image').height() - 6);
                    span.css('left', point.get('x') * $('#Image').width() - 6);
                    span.css('z-index', 10000);
                    //span.attr('caab_code', label);
                    span.attr('rel', 'tooltip');
                    span.attr('data-container', '#ImageAppContainer');

                    if (labelClass == 'pointAnnotated') {
                        span.text(annotationCode.get("cpc_code"));
                        if (annotationCodeSecondary == '') {
                            span.text(annotationCode.get("cpc_code"));
                            span.attr('title', annotationCode.get("code_name"));
                        } else {
                            span.text(annotationCode.get("cpc_code") + '/' + annotationCodeSecondary.get("cpc_code"));
                            span.attr('title', annotationCode.get("code_name") + '/' + annotationCodeSecondary.get("code_name"));

                        }
                    }

                    span.appendTo('#ImageContainer');
                    span.tooltip();
                });

                $("[rel=tooltip]").tooltip();

                $("#ImageContainer").children('span').click(function (e) {

                    if (e.shiftKey) {
                        GlobalEvent.trigger("point_shift_clicked", this);
                    }
                    else {
                        GlobalEvent.trigger("point_clicked", this);
                    }

                });

                $("#ImageContainer").children('span').mouseover(function () {
                    GlobalEvent.trigger("point_mouseover", this);
                });

                $("#ImageContainer").children('span').mouseout(function () {
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

        $("[rel=tooltip]").tooltip();

    },
    thumbnailSelectedWithId: function (ImageId) {

        //destroy the tooltips
        this.pointMouseOut();

        this.renderSelectedImageById(ImageId);

        var parent = this;

        //now we have to wait for the image to load before we can draw points
        $("#Image").imagesLoaded(function () {

            //make the canvas the size of the image in question, so that we transfer all the data correctly
            $("#CanvasImage")[0].width = $("#Image").width();
            $("#CanvasImage")[0].height = $("#Image").height();

            //render the canvas image - from the image loaded into the img tag
            $("#CanvasImage").drawImage({
                source: $("#Image")[0],
                x: 0, y: 0,
                fromCenter: false
            });

            //reset the lasso canvas size to match the image canvas
            parent.resetLassoCanvas();

            parent.renderPointsForImage();

            // do the image segmentation if it is turned on
            var intelligentPointsKey = "catamiproject_" + project.get("id");
            var intelligentPoints = ($.cookie(intelligentPointsKey) == "true") ? true : false;

            if (intelligentPoints)
                setTimeout(imageSegmentation.segmentImage("#Image", 10), 1);

        });

    },
    thumbnailSelected: function (selectedPosition) {

        //destroy the tooltips
        this.pointMouseOut();

        selectedThumbnailPosition = selectedPosition;
        this.renderSelectedImage(selectedPosition);

        //turn the zoom off and reset the zoom button
        //this.zoomOff();
        //$('#ZoomToggle').removeClass('active');

        var parent = this;
        //now we have to wait for the image to load before we can draw points
        $("#Image").imagesLoaded(function () {

            //make the canvas the size of the image in question, so that we transfer all the data correctly
            $("#CanvasImage")[0].width = $("#Image").width();
            $("#CanvasImage")[0].height = $("#Image").height();

            //render the canvas image - from the image loaded into the img tag
            $("#CanvasImage").drawImage({
                source: $("#Image")[0],
                x: 0, y: 0,
                fromCenter: false
            });

            parent.renderPointsForImage(selectedPosition);

            // do the image segmentation if it is turned on
            var intelligentPointsKey = "catamiproject_" + project.get("id");
            var intelligentPoints = ($.cookie(intelligentPointsKey) == "true") ? true : false;

            if (intelligentPoints)
                setTimeout(imageSegmentation.segmentImage("#Image", 10), 1);
        });

    },
    screenChanged: function () {
        //loop through the points and apply them to the image
        points.each(function (point) {
            var pointId = point.get('id');
            var span = $('#' + pointId);

            span.css('top', point.get('y') * $('#Image').height());
            span.css('left', point.get('x') * $('#Image').width());
        });
    },
    pointClicked: function (thePoint) {

        this.selectPoint(thePoint);

        //refresh the point labels
        this.refreshPointLabelsForImage();
    },
    pointShiftClicked: function (thePoint) {

        // get intelligent points configuration from the cookie, disabled by default
        var intelligentPointsKey = "catamiproject_" + project.get("id");
        var intelligentPoints = ($.cookie(intelligentPointsKey) == "true") ? true : false;

        // if intelligent points is on then do the work
        if (intelligentPoints)
            this.selectSimilarPoints($(thePoint).attr('id'));

        // if it's not on, then tell the user
        else
            $('#similar-points-modal').modal('show');

        //refresh the point labels
        this.refreshPointLabelsForImage();
    },
    selectPoint: function (thePoint) {

        var theClass = $(thePoint).attr('class');

        //var theCaabCode = $(thePoint).attr('caab_code');
        var annotationCode = PointUtil.getAnnotationCodeForPointId($(thePoint).attr('id'));
        var theCaabCode = (annotationCode == null) ? "" : annotationCode.get("caab_code");

        if (theClass == 'pointSelected' && theCaabCode == "") {
            $(thePoint).attr('class', 'pointNotAnnotated');

            // there may be other points that are selected so fire off an event
            GlobalEvent.trigger("point_is_selected", this);
        } else if (theClass == 'pointSelected' && theCaabCode != "") {
            $(thePoint).attr('class', 'pointAnnotated');

            // there may be other points that are selected so fire off an event
            GlobalEvent.trigger("point_is_selected", this);
        } else if (theClass == 'pointSelected pointLabelledStillSelected') {
            $(thePoint).attr('class', 'pointAnnotated');

            // there may be other points that are selected so fire off an event
            GlobalEvent.trigger("point_is_selected", this);
        } else {

            //firstly we need to check if we need to deselect already labelled points
            $(".pointLabelledStillSelected").each(function (index, pointSpan) {
                $(pointSpan).attr('class', 'pointAnnotated');
            });

            //then we make the current points selected
            $(thePoint).attr('class', 'pointSelected');

            //hide the label, if there is one
            //$(thePoint).text("");
            GlobalEvent.trigger("point_is_selected", this);
        }

        //if there are no points selected we need to disable annotation selector
        var pointsSelected = $('.pointSelected');
        if (pointsSelected.length == 0) {
            this.disableAnnotationSelector();
            GlobalEvent.trigger('finescale_points_deselected');
        }
        //else
        //this.enableAnnotationSelector();
    },
    selectSimilarPoints: function (selectedPointId) {
        var parent = this;

        var preTime = new Date().getTime();

        //get point colour
        var selectedPoint = PointUtil.getPointWithId(selectedPointId);
        var selectedPointX = selectedPoint.get("x");
        var selectedPointY = selectedPoint.get("y");
        var selectedPointColour = imageSegmentation.getPointColour(selectedPointX, selectedPointY);

        var samePoints = [];
        for (var i = 0; i < points.length; i++) {

            var x = points.at(i).get("x");
            var y = points.at(i).get("y");

            var pointColour = imageSegmentation.getPointColour(x, y);

            if (pointColour[0] == selectedPointColour[0] &&
                pointColour[1] == selectedPointColour[1] &&
                pointColour[2] == selectedPointColour[2] &&
                pointColour[3] == selectedPointColour[3]) {

                samePoints.push(points.at(i));
            }

        }

        for (var i = 0; i < samePoints.length; i++) {
            var point = samePoints[i];
            parent.selectPoint("#" + point.get("id"));
        }

    },
    pointMouseOver: function (thePoint) {

        // get the codes of the hovered point
        var pointId = $(thePoint).attr('id');
        var point = points.find(function (model) {
            return model.get('id') == pointId;
        });

        var thePointCaabCode = point.get('annotation_caab_code');
        var thePointCaabCodeSecondary = point.get('annotation_caab_code_secondary');

        //get points which have the same caab code assigned
        var samePoints = points.filter(
            function (point) {

                // if there is not caab code for the point, don't look for others
                if (thePointCaabCode == "")
                    return false;

                // if secondary is blank, only look at primary
                if (thePointCaabCodeSecondary == "")
                    return (point.get("annotation_caab_code") == thePointCaabCode || point.get("annotation_caab_code_secondary") == thePointCaabCode);
                else // search all
                    return (point.get("annotation_caab_code") == thePointCaabCode || point.get("annotation_caab_code") == thePointCaabCodeSecondary ||
                        point.get("annotation_caab_code_secondary") == thePointCaabCode || point.get("annotation_caab_code_secondary") == thePointCaabCodeSecondary);
            }
        );

        //show the labels
        for (var i = 0; i < samePoints.length; i++) {
            $("#" + samePoints[i].get("id")).tooltip('show');
        }
    },
    pointMouseOut: function () {
        //remove labels from all points
        points.each(function (point) {
            $("#" + point.get("id")).tooltip('destroy');
        });
    },
    hidePoints: function () {
        //loop through the points and hide them
        points.each(function (point) {
            var pointId = point.get('id');
            var span = $('#' + pointId);

            span.css('visibility', 'hidden');
        });
    },
    showPoints: function () {
        //loop through the points and show them
        points.each(function (point) {
            var pointId = point.get('id');
            var span = $('#' + pointId);

            span.css('visibility', 'visible');
        });
    },
    zoomOn: function () {
        $("#Image").elevateZoom({zoomWindowPosition: 1});
    },
    zoomOff: function () {
        $.removeData($("#Image"), 'elevateZoom');
        $('.zoomContainer').remove();
    },
    deselectPoints: function () {

        //deselect any points that are labelled and still selected
        $(".pointLabelledStillSelected").each(function (index, pointSpan) {
            $(pointSpan).attr('class', 'pointAnnotated');
        });

        //deselect any points that are selected
        $(".pointSelected").each(function (index, pointSpan) {
            //var theCaabCode = $(pointSpan).attr('caab_code');
            var annotationCode = PointUtil.getAnnotationCodeForPointId($(pointSpan).attr('id'));
            var theCaabCode = (annotationCode == null) ? "" : annotationCode.get("caab_code");

            if (theCaabCode === "") {
                $(pointSpan).attr('class', 'pointNotAnnotated');
            } else {
                $(pointSpan).attr('class', 'pointAnnotated');
            }
        });

        //refresh
        this.refreshPointLabelsForImage();
        this.disableAnnotationSelector();

        GlobalEvent.trigger('finescale_points_deselected');

    },
    enableAnnotationSelector: function () {
        $('.AnnotationChooserBox').removeClass('disable');
        $('a[href=#overall_root_node]').trigger('activate-node');
    },
    disableAnnotationSelector: function () {
        $('.AnnotationChooserBox').addClass('disable');
        this.closeAnnotationSelector();
    },
    closeAnnotationSelector: function () {
        $('#annotation-chooser').find('ul').each(function (index, item) {
            if (index > 0) {
                $(item).hide();
            }
        });
    }
});