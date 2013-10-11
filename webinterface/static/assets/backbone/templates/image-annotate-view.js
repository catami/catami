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
        GlobalEvent.on("point_mouseover", this.pointMouseOver, this);
        GlobalEvent.on("point_mouseout", this.pointMouseOut, this);
        GlobalEvent.on("annotation_to_be_set", this.annotationChosen, this);
        GlobalEvent.on("refresh_point_labels_for_image", this.refreshPointLabelsForImage, this);
        GlobalEvent.on("hide_points", this.hidePoints, this);
        GlobalEvent.on("show_points", this.showPoints, this);
        GlobalEvent.on("deselect_points", this.deselectPoints, this);
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

        return this;
    },
    /**
     * Refreshes the mouse over labels for points on an image.
     */
    refreshPointLabelsForImage: function() {
        //get all the points on the image
        var allPoints = $('#ImageContainer > span');

        //loop through
        $.each(allPoints, function(index, pointSpan) {

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
            if ((annotationCodeSecondary == '' || annotationCodeSecondary == null) && (annotationCode != '' && annotationCode != null)){

                if(pointIsSelected)
                    $(pointSpan).text("");
                else
                    $(pointSpan).text(annotationCode.get("cpc_code"));

                $(pointSpan).attr('title', annotationCode.get("code_name"));

            } else if (annotationCodeSecondary != '' && annotationCodeSecondary != null && annotationCode != '' && annotationCode != null) {

                if(pointIsSelected)
                    $(pointSpan).text("");
                else
                    $(pointSpan).text(annotationCode.get("cpc_code")+'/'+annotationCodeSecondary.get("cpc_code"));

                $(pointSpan).attr('title', annotationCode.get("code_name")+'/'+annotationCodeSecondary.get("code_name"));
            }

            // if the point is currently selected, show the label
            if(pointIsSelected){
                $(pointSpan).tooltip("destroy");
                $(pointSpan).tooltip("show");
            }
        });
    },
    renderPointsForImage: function() {

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

                    var annotationCode = annotationCodeList.find(function(model) {
                        return model.get('caab_code')===point.get('annotation_caab_code');
                    });

                    var annotationCodeSecondary = '';

                    if (point.get('annotation_caab_code_secondary') !== '') {
                        annotationCodeSecondary = annotationCodeList.find(function(model) {
                            return model.get('caab_code')===point.get('annotation_caab_code_secondary');
                        });
                    }

                    var labelClass = (label === "") ? 'pointNotAnnotated' : 'pointAnnotated';

                    var span = $('<span>');
                    span.attr('id', pointId);
                    span.attr('class', labelClass);
                    span.css('top', point.get('y')*$('#Image').height()-6);
                    span.css('left', point.get('x')*$('#Image').width()-6) ;
                    span.css('z-index', 10000);
                    //span.attr('caab_code', label);
                    span.attr('rel', 'tooltip');
                    span.attr('data-container','#ImageAppContainer');

                    if (labelClass == 'pointAnnotated'){
                        span.text(annotationCode.get("cpc_code"));
                        if (annotationCodeSecondary == ''){
                            span.text(annotationCode.get("cpc_code"));
                            span.attr('title', annotationCode.get("code_name"));
                        } else {
                            span.text(annotationCode.get("cpc_code")+'/'+annotationCodeSecondary.get("cpc_code"));
                            span.attr('title', annotationCode.get("code_name")+'/'+annotationCodeSecondary.get("code_name"));

                        }
                    }

                    span.appendTo('#ImageContainer');
                    span.tooltip();
                });

                $("[rel=tooltip]").tooltip();

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

        $("[rel=tooltip]").tooltip();

    },
    thumbnailSelectedWithId: function(ImageId) {

        //destroy the tooltips
        this.pointMouseOut();

        this.renderSelectedImageById(ImageId);

        var parent = this;
        //now we have to wait for the image to load before we can draw points
        $("#Image").imagesLoaded(function() {
            parent.renderPointsForImage();
        });

    },
    thumbnailSelected: function(selectedPosition) {

        //destroy the tooltips
        this.pointMouseOut();

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

        //var theCaabCode = $(thePoint).attr('caab_code');
        var annotationCode = PointUtil.getAnnotationCodeForPointId($(thePoint).attr('id'));
        var theCaabCode = (annotationCode == null) ? "" : annotationCode.get("caab_code");


        if(theClass == 'pointSelected' && theCaabCode == ""){
            $(thePoint).attr('class', 'pointNotAnnotated');
        } else if(theClass == 'pointSelected' && theCaabCode != ""){
            $(thePoint).attr('class', 'pointAnnotated');
        } else if(theClass == 'pointSelected pointLabelledStillSelected'){
            $(thePoint).attr('class', 'pointAnnotated');
        }else {

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
        var pointsSelected =  $('.pointSelected');
        if(pointsSelected.length == 0) {
            this.disableAnnotationSelector();
            GlobalEvent.trigger('finescale_points_deselected');
        }
        //else
            //this.enableAnnotationSelector();

        //refresh the point labels
        this.refreshPointLabelsForImage();
    },
    pointMouseOver: function(thePoint) {

        // get the codes of the hovered point
        var pointId = $(thePoint).attr('id');
        var point = points.find(function(model) {
            return model.get('id') == pointId;
        });

        var thePointCaabCode = point.get('annotation_caab_code');
        var thePointCaabCodeSecondary = point.get('annotation_caab_code_secondary');

        //get points which have the same caab code assigned
        var samePoints = points.filter(
            function(point) {

                // if there is not caab code for the point, don't look for others
                if(thePointCaabCode == "")
                    return false;

                // if secondary is blank, only look at primary
                if(thePointCaabCodeSecondary == "")
                    return (point.get("annotation_caab_code") == thePointCaabCode || point.get("annotation_caab_code_secondary") == thePointCaabCode);
                else // search all
                    return (point.get("annotation_caab_code") == thePointCaabCode || point.get("annotation_caab_code") == thePointCaabCodeSecondary ||
                            point.get("annotation_caab_code_secondary") == thePointCaabCode || point.get("annotation_caab_code_secondary") == thePointCaabCodeSecondary);
            }
        );

        //show the labels
        for(var i = 0; i < samePoints.length; i++) {
            $("#"+samePoints[i].get("id")).tooltip('show');
        }
    },
    pointMouseOut: function() {
        //remove labels from all points
        points.each(function(point) {
            $("#"+point.get("id")).tooltip('destroy');
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
            //var theCaabCode = $(pointSpan).attr('caab_code');
            var annotationCode = PointUtil.getAnnotationCodeForPointId($(pointSpan).attr('id'));
            var theCaabCode = (annotationCode == null) ? "" : annotationCode.get("caab_code");

            if(theCaabCode === "") {
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
    enableAnnotationSelector: function(){
        $('.AnnotationChooserBox').removeClass('disable');
        $('a[href=#overall_root_node]').trigger('activate-node');
    },
    disableAnnotationSelector: function(){
        $('.AnnotationChooserBox').addClass('disable');
        this.closeAnnotationSelector();
    },
    closeAnnotationSelector: function() {
        $('#annotation-chooser').find('ul').each(function(index,item){
            if (index > 0){
                $(item).hide();
            }
        });
    }
});