var FineScaleAnnotationSelectorView = Backbone.View.extend({
    el: "#fine-scale-annotation-selector",
    model: PointAnnotation,
    events: {
        'click #add_secondary_annotation': 'addSecondaryAnnotation',
        'click #fine_scale_label_secondary': 'editSecondaryLabel',
        'click #remove_secondary_annotation':'removeSecondaryAnnotation',
        'click #fine_scale_label': 'editPrimaryLabel'
    },
    initialize: function () {
        GlobalEvent.on("point_clicked", this.fineScalePointSelected, this);
        GlobalEvent.on("annotation_set_has_changed", this.selectedFineScalePointsAssigned, this);
        GlobalEvent.on("finescale_points_deselected", this.render, this);
        GlobalEvent.on("annotation_to_be_set", this.annotationChosen, this);
    },
    render: function () {

        var parent = this;

        var usefulRootCaabCode = 'None';
        var label = "Nothing Selected";
        var usefulRootCaabCodeSecondary = '';
        var labelSecondary = '';
        var pointId = '000';

        var fineScaleVariables = {
            "fineScaleClassParent": usefulRootCaabCode,
            "fineScaleClass": label,
            "fineScaleClassSecondaryParent": usefulRootCaabCodeSecondary,
            "fineScaleClassSecondary": labelSecondary,
            "model_id": pointId
        };

        var fineScaleItemTemplate = _.template($("#FineScaleAnnotionTemplate").html(), fineScaleVariables);

        $('.FineScaleEditBox').show();
        $('.BroadScaleEditBox').hide();

        parent.$el.html(fineScaleItemTemplate);

        $("#fine_scale_class_label").hide();
        $("#add_secondary_annotation").hide();

        if (labelSecondary === ''){
            $("#secondaryLabel").hide();
            $("#fineScaleBadge").hide();
        }

        return this;
    },
    fineScalePointSelected: function(){
        // var theClass = $(thePoint).attr('class');
        // var theCaabCode = $(thePoint).attr('caab_code');
        // var theCaabCode_id = $(thePoint).attr('id');

        // console.log(thePoint);
        // annotationCode = annotationCodeList.find(function(model) {
        //     return model.get('caab_code') === $(thePoint).attr('caab_code');
        // });
        // console.log('fineScalePointSelected ',annotationCode.get('cpc_code'),annotationCode.get('code_name'));

        var selectedPoints = $('.pointSelected');
        var mixedDisplayText = selectedPoints.length+' points selected: ';
        var labelSet ='';
        var mixedSet = 0;

        // if (selectedPoints.length === 1) {
        //     mixedSet = 0; // unmixed set
        // } else {
        //     mixedSet = 1; // mixed set
        // }

        // need to check we are looking at multiple selection points with the same code
        // if so, we can simplify how we draw the annotation selection

        var initialPoint = points.get(selectedPoints[0].id);
        $.each(selectedPoints, function(index, point) {
            var localPoint = points.get(point.id);
            console.log(index, initialPoint.get('annotation_caab_code'), localPoint.get('annotation_caab_code'));
            if (initialPoint.get('annotation_caab_code') !== localPoint.get('annotation_caab_code')){
                //this is a mixed set
                mixedSet = 1;
            }
        });

        if (mixedSet === 0){
            console.log('unmixed set');
            var localPoint = points.get(selectedPoints[0].id);
            if ( localPoint.get('annotation_caab_code') === ''){
                $('#fine_scale_label').text('Select a CAAB code...');
            } else {
                annotationCode = annotationCodeList.find(function(model) {
                    return model.get('caab_code') === localPoint.get('annotation_caab_code');
                });
                
                $('#fine_scale_label').text(annotationCode.get('code_name')+' ');
                console.log('selectedPoints.length',selectedPoints.length);
                if (selectedPoints.length >1) {
                    $('#fine_scale_label').append('<div class="label label-info"> x'+selectedPoints.length+'</div>');
                }
                if (localPoint.get('annotation_caab_code_secondary') !== '') {
                    annotationCode = annotationCodeList.find(function(model) {
                        return model.get('caab_code') === localPoint.get('annotation_caab_code_secondary');
                    });

                    $("#secondaryLabel").show();
                    $("#fine_scale_label_secondary").text(annotationCode.get('code_name')+' ');
                    $("#remove_secondary_annotation").show();
                    $("#fineScaleBadge").show();
                } else {
                    if (!$("#remove_secondary_annotation").is(':visible')){
                        $("#add_secondary_annotation").show();
                    }
                }
                $("#fine_scale_class_label").show();
            }
        } else {
            console.log('mixed set');
            $.each(selectedPoints, function(index, point) {
                var localpoint = points.get(point.id);
                var local_caabcode = localpoint.get('annotation_caab_code');
                $('#fine_scale_label').text(mixedDisplayText);

                if(local_caabcode !== ''){
                    annotationCode = annotationCodeList.find(function(model) {
                        return model.get('caab_code') === localpoint.get('annotation_caab_code');
                    });
                    labelSet +='<div class="label label-info">'+annotationCode.get('cpc_code')+'</div>';
                } else {
                    labelSet +='<div class="label label-info">None</div>';
                }
            });
        }

        this.editPrimaryLabel();

        $('#fine_scale_label').append(labelSet);

       // $('#fine_scale_label').text(displayText);

    },
    selectedFineScalePointsAssigned: function() {
        var selectedPoints = $('.pointSelected');

        // all selected points will now be the same value. No need to iterate through the set
        var localPoint = points.get(selectedPoints[0].id);
        
        annotationCode = annotationCodeList.find(function(model) {
            return model.get('caab_code') === localPoint.get('annotation_caab_code');
        });
        
        $('#fine_scale_label').text(annotationCode.get('code_name')+' ');
        if (selectedPoints.length > 1){
            $('#fine_scale_label').append('<div class="label label-info"> x'+selectedPoints.length+'</div>');
        }
        $("#fine_scale_class_label").show();
        if (!$("#remove_secondary_annotation").is(':visible')){
            $("#add_secondary_annotation").show();
        }
    },
    addSecondaryAnnotation: function() {
        console.log('addSecondaryAnnotation');
        var selectedPoints = $('.pointSelected');
        //save the annotations
        //only need a callback function if points greater than 0
        var afterAllSavedCallback;
        if(selectedPoints.length > 0)
            afterAllSavedCallback = _.after(selectedPoints.length, function() {
                var localPoint = points.get(selectedPoints[0].id);
                        
                annotationCode = annotationCodeList.find(function(model) {
                    return model.get('caab_code') === localPoint.get('annotation_caab_code_secondary');
                });

                $("#secondaryLabel").show();
                $("#fine_scale_label_secondary").text(annotationCode.get('code_name')+' ');
                $("#remove_secondary_annotation").show();
                $("#add_secondary_annotation").hide();
                $("#fineScaleBadge").show();
            });


        $.each(selectedPoints, function(index, localPoint) {
            //need to specify the properties to patch
            var properties = { 'annotation_caab_code_secondary': '00000000' };
            var theXHR = points.get(localPoint.id).save(properties, {
                patch: true,
                headers: {"cache-control": "no-cache"},
                success: function (model, xhr, options) {
                    afterAllSavedCallback();
                },
                error: function (model, xhr, options) {
                }
            });
        });

    },
    editSecondaryLabel: function() {
        console.log('editSecondaryLabel');
        this.closeEditPrimaryLabel();

        $("#secondaryLabel").show();
        $("#fineScaleBadge").show();
        $("#secondaryLabel").addClass('fineScaleItemSelected');
    },
    closeEditSecondaryLabel: function() {
        $("#secondaryLabel").removeClass('fineScaleItemSelected');
    },
    editPrimaryLabel: function() {
        console.log('editPrimaryLabel');
        this.closeEditSecondaryLabel();
        $("#primarylabel").addClass('fineScaleItemSelected');
    },
    closeEditPrimaryLabel: function() {
        $("#primarylabel").removeClass('fineScaleItemSelected');
    },
    removeSecondaryAnnotation: function(){
        console.log('removeSecondaryAnnotation');
        var selectedPoints = $('.pointSelected');
        //save the annotations
        //only need a callback function if points greater than 0
        var afterAllSavedCallback;
        if(selectedPoints.length > 0)
            afterAllSavedCallback = _.after(selectedPoints.length, function() {

                $("#secondaryLabel").hide();
                $("#fine_scale_label_secondary").text(annotationCode.get('code_name')+' ');
                $("#remove_secondary_annotation").hide();
                $("#add_secondary_annotation").show();
                $("#fineScaleBadge").hide();
            });


        $.each(selectedPoints, function(index, localPoint) {
            //need to specify the properties to patch
            var properties = { 'annotation_caab_code_secondary': '' };
            var theXHR = points.get(localPoint.id).save(properties, {
                patch: true,
                headers: {"cache-control": "no-cache"},
                success: function (model, xhr, options) {
                    afterAllSavedCallback();
                },
                error: function (model, xhr, options) {
                }
            });
        });
    },
    annotationChosen: function(caab_code_id) {
        var parent = this;

        //get the selected points
        var selectedPoints = $('.pointSelected');
        caab_object = annotationCodeList.get(caab_code_id);

        //only need a callback function if points greater than 0
        var afterAllSavedCallback;
        if(selectedPoints.length > 0)
            afterAllSavedCallback = _.after(selectedPoints.length, function() {
                //send out an event for all the other listeners
                GlobalEvent.trigger("annotation_set_has_changed");
            });

        //save the annotations
        $.each(selectedPoints, function(index, pointSpan) {

            //need to specify the properties to patch
            var properties  = {};

            if ($("#primarylabel").hasClass('fineScaleItemSelected')){
                properties = { 'annotation_caab_code': caab_object.get('caab_code') };
            }
            if ($("#secondaryLabel").hasClass('fineScaleItemSelected')){
                properties = { 'annotation_caab_code_secondary': caab_object.get('caab_code') };
            }

            var theXHR = points.get(pointSpan.id).save(properties, {
                patch: true,
                headers: {"cache-control": "no-cache"},
                success: function (model, xhr, options) {

                    //show label on annotated point
                    var idOfSaved = model.get("id");
                    $('#'+idOfSaved).addClass('pointLabelledStillSelected'); //this means the point stays selected, we are just assigning the class to this point to keep that state
                    $('#'+idOfSaved).attr('title', annotationCodeList.get(caab_code_id).get("code_name"));
                    $('#'+idOfSaved).attr('caab_code', caab_object.get('caab_code'));
                    $('#'+idOfSaved).tooltip("destroy");
                    $('#'+idOfSaved).tooltip("show");
                    
                    if ($("#primarylabel").hasClass('fineScaleItemSelected')){
                        $("#fine_scale_label").text(caab_object.get('code_name')+' ');
                    }
                    if ($("#secondaryLabel").hasClass('fineScaleItemSelected')){
                        $("#fine_scale_label_secondary").text(caab_object.get('code_name')+' ');
                    }
                    GlobalEvent.trigger("image_points_updated", this);
                    afterAllSavedCallback();
                },
                error: function (model, xhr, options) {
                    if (theXHR.status == "201" || theXHR.status == "202") {
                        alert("202");

                        //show label on annotated point
                        var idOfSaved = model.get("id");
                        $('#'+idOfSaved).addClass('pointLabelledStillSelected'); //this means the point stays selected, we are just assigning the class to this point to keep that state
                        $('#'+idOfSaved).attr('title', annotationCodeList.get(caab_code_id).get("code_name"));
                        $('#'+idOfSaved).attr('caab_code', caab_object.get('caab_code'));
                        $('#'+idOfSaved).tooltip("destroy");
                        $('#'+idOfSaved).tooltip("show");

                        GlobalEvent.trigger("image_points_updated", this);
                        afterAllSavedCallback();

                    } else if(theXHR.status == "401") {
                        $.pnotify({
                            title: 'You don\'t have permission to annotate this image.',
                            text: theXHR.response,
                            type: 'error', // success | info | error
                            hide: true,
                            icon: false,
                            history: false,
                            sticker: false
                        });
                    }
                    else {
                        $.pnotify({
                            title: 'Failed to save your annotations to the server.',
                            text: theXHR.response,
                            type: 'error', // success | info | error
                            hide: true,
                            icon: false,
                            history: false,
                            sticker: false
                        });
                    }
                }
            });
        });

        GlobalEvent.trigger("annotation_triggered");
    }
});