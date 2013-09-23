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
        var displayText = selectedPoints.length+' points selected: ';
        var labelSet ='';

        $.each(selectedPoints, function(index, point) {
            var localpoint = points.get(point.id);
            var local_caabcode = localpoint.get('annotation_caab_code');
            $('#fine_scale_label').text(displayText);

            if(local_caabcode !== ''){
                annotationCode = annotationCodeList.find(function(model) {
                    return model.get('caab_code') === localpoint.get('annotation_caab_code');
                });
                labelSet +='<div class="label label-info">'+annotationCode.get('cpc_code')+'</div>';
            } else {
                labelSet +='<div class="label label-info">None</div>';
            }
        });

        $('#fine_scale_label').append(labelSet);

       // $('#fine_scale_label').text(displayText);

    },
    selectedFineScalePointsAssigned: function() {
        console.log('selectedFineScalePointsAssigned');
        var selectedPoints = $('.pointSelected');

        // all selected points will now be the same value. No need to iterate through the set
        var localPoint = points.get(selectedPoints[0].id);
        
        annotationCode = annotationCodeList.find(function(model) {
            return model.get('caab_code') === localPoint.get('annotation_caab_code');
        });
        
        $('#fine_scale_label').text(annotationCode.get('code_name')+' ');
        $('#fine_scale_label').append('<div class="label label-info"> x'+selectedPoints.length+'</div>');
        $("#fine_scale_class_label").show();
        $("#add_secondary_annotation").show();

    },
    addSecondaryAnnotation: function() {
        console.log('addSecondaryAnnotation');
    },
    editSecondaryLabel: function() {
        console.log('editSecondaryLabel');
    },
    editPrimaryLabel: function() {
        console.log('editPrimaryLabel');
    },
    removeSecondaryAnnotation: function(){
        console.log('removeSecondaryAnnotation');
       
    }
});