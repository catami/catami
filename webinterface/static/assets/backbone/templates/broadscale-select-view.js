var WholeImageAnnotationSelectorView = Backbone.View.extend({
    el: "#whole-image-annotation-selector",
    model: WholeImageAnnotations,
    events: {
        'click #clear_all_broad_scale': 'clearAllWholeImageAnnotations',
        'click #delete_all_broad_scale': 'deleteAllBroadScaleAnnotations',
        'click .dismiss_confirmation': 'dismissConfirmation',
        'click #confirm_delete': 'deleteBroadScaleAnnotation',
        'click .broadScaleRemoveButton': 'showDeleteConfirmation',
        'click #add_new_broadscale_annotation': 'addNewBroadscaleAnnotation',
        'click .wholeImageLabel': 'toggleAnnotationEditable',
        'click #confirm_clear_all': 'confirmClearAllBroadScaleAnnotation',
        'click #confirm_delete_all': 'confirmDeleteAllBroadScaleAnnotation',
        'click .percentValue': 'percentCoverageSelected',
        'click .broadScaleTools': 'toggleBroadScaleTools',
        'click #confirm_set_unscorable': 'confirmSetImageUnscorable',
        'click #set_image_unscorable': 'showUnscorableConfirmation'
    },
    initialize: function () {
        GlobalEvent.on("annotation_to_be_set", this.wholeImageAnnotationChosen, this);
        GlobalEvent.on("thumbnail_selected", this.thumbnailSelected, this);
        GlobalEvent.on("thumbnail_selected_by_id", this.render, this);
    },
    render: function () {

        // get and display points if we got 'em
        var parent = this;
        //get the selected image
        var annotationSet = annotationSets.at(0);
        //var image = annotationSet.get("images")[currentImageInView];
        //based on that image query the API for the points
        //var whole_image_points = new WholeImageAnnotations();
        var broadScaleAnnotationTemplate = "";

        broadScalePoints.fetch({
            data: { limit: 100, image: selectedImageId, annotation_set: annotationSet.get('id') },
            success: function (model, response, options) {

                parent.renderBroadScalePoints();

                //hide the delete/clear/confirm UI
                parent.$('.actionConfirmAlert').hide();
                parent.$('.editBroadScaleIndictor').hide();
                parent.$('.broadScaleControlContainer').hide();

                //hide spinner
            },
            error: function (model, xhr, options) {
                console.log(xhr);
            }
        });

        return this;
    },
    renderBroadScalePoints: function() {
        var parent = this;
        var broadScaleAnnotationTemplate = "";
        // show spinner (TBD)
        broadScalePoints.each(function (whole_image_point) {
            var annotationCode;
            var usefulRootCaabCode;
            var pointId = whole_image_point.get('id');
            var label = whole_image_point.get('annotation_caab_code');
            var fov_percentage = whole_image_point.get('coverage_percentage');

            if (fov_percentage < 0){fov_percentage='--';}

            if (label === ""){
                annotationCode = annotationCodeList.find(function(model) {
                    return model.get('caab_code')==='00000000';
                });
            } else {
                annotationCode = annotationCodeList.find(function(model) {
                    return model.get('caab_code')===whole_image_point.get('annotation_caab_code');
                });
            }

            if (label===""){
                label = "Not Set";
                usefulRootCaabCode = "No Group";
            } else {
                label = annotationCode.get('code_name');
                usefulRootCaabCodeID = getUsefulCaabRoot(annotationCode.get('id'));
                rootAnnotationCode = annotationCodeList.find(function(model) {
                    return model.get('caab_code')===usefulRootCaabCodeID;
                });
                
                if (!rootAnnotationCode){
                    usefulRootCaabCode = 'No Group';
                } else {
                    usefulRootCaabCode = rootAnnotationCode.get('code_name');
                }
            }

            var annotationVariables = {
                "broadScaleClassParent": usefulRootCaabCode,
                "broadScaleClass": label,
                "broadScalePercentage": fov_percentage+' %',
                "model_id": pointId
            };

            broadScaleAnnotationTemplate += _.template($("#BroadScaleItemTemplate").html(), annotationVariables);
        });

        var wholeImageVariables = { "broadScaleAnnotations": broadScaleAnnotationTemplate };
        var wholeImageTemplate = _.template($("#WholeImageAnnotationTemplate").html(), wholeImageVariables);
        $('.FineScaleEditBox').hide();
        $('.BroadScaleEditBox').show();
        // disable annotation view
        
        this.disableAnnotationSelector();

        parent.$el.html(wholeImageTemplate);

        return this;
    },
    wholeImageAnnotationChosen: function(caab_code_id) {
        // an annotation has been selected in the annotation chooser

        var parent = this;

        var usefulRootCaabCode = getUsefulCaabRoot(caab_code_id);
        var rootAnnotationCode = annotationCodeList.find(function(model) {
                                    return model.get('caab_code')===usefulRootCaabCode;
                                 });
        var selectedCaabCode = plain_annotation_list[parseInt(caab_code_id,10)-1];
        
        var caab_object = annotationCodeList.get(caab_code_id);

        // which annotations are tagged to be edited?
        var editableAnnotations = $('.editable');

        $.each(editableAnnotations, function(index, element) {

            var properties = { 'annotation_caab_code': caab_object.get('caab_code') };
            var pointId = $(element).data('model_id');
            var theXHR  = broadScalePoints.get(pointId).save(properties, {
                patch: true,
                headers: {"cache-control": "no-cache"},
                success: function (model, xhr, options) {
                    $(element).find('.wholeImageLabel').html('<i class="icon-edit editBroadScaleIndictor pull-left"></i>'+caab_object.get('code_name'));
                    $(element).find('.wholeImageClassLabel').text(rootAnnotationCode.get('code_name'));

                    GlobalEvent.trigger("annotation_set_has_changed");
                },
                error: function (model, xhr, options) {
                    GlobalEvent.trigger("annotation_set_has_changed");
                }
            });
        });

    },
    thumbnailSelected: function(selectedPosition) {
        //deprecated
        // thumbnail has been selected in the main UI. refresh UI for new loaded image
        // currentImageInView = selectedPosition;
        // this.render();
    },
    addNewBroadscaleAnnotation: function() {
        //make a new Broad Scale annotation with no annotation type
        var parent = this;
        var annotationSet = annotationSets.at(0);
        //var image = annotationSet.get("images")[currentImageInView];

        var broad_scale_annotation = new WholeImageAnnotation({ 'annotation_caab_code': '', 'image':'/api/dev/image/'+selectedImageId+'/', 'annotation_set':'/api/dev/annotation_set/'+annotationSet.get('id')+'/'});

        // add spinnner TBD
        broadScalePoints.create(broad_scale_annotation,{
            success:function() {
                parent.render();
                GlobalEvent.trigger("annotation_set_has_changed");
            }
        });
    },
    toggleAnnotationEditable: function(ev){
        //this.clearEditableStatus();  //permit no similataneous edits
        var parent = this;
        if($(ev.currentTarget).parent().hasClass('editable')){
            parent.clearEditableStatus();
            parent.disableAnnotationSelector();
        } else {
            parent.clearEditableStatus();
            var model_id = $(ev.target).data('model_id');
            $(ev.currentTarget).find('.editBroadScaleIndictor').css('display', 'block');
            $(ev.currentTarget).parent().addClass('editable');
            parent.enableAnnotationSelector();
        }
    },
    clearEditableStatus: function(){
        var editableAnnotations = $('.editable');
        $.each(editableAnnotations, function(index, element) {
            $(element).removeClass('editable');
            $(element).find('.editBroadScaleIndictor').css('display', 'none');
        });
    },
    showDeleteConfirmation: function(ev){
        var model_id = $(ev.target).data('model_id');
        $(ev.target).addClass('deleteStyle');
        this.$('#DeleteBroadScaleConfirm').css('display', 'block');
        this.$('#DeleteBroadScaleConfirm').data('model_id',model_id);
    },
    dismissConfirmation: function() {
        this.$('.actionConfirmAlert').css('display', 'none');
        var deletableAnnotations = $('.deleteStyle');
        $.each(deletableAnnotations, function(index, element) {
            $(element).removeClass('deleteStyle');
        });
    },
    deleteBroadScaleAnnotation: function(annotation_id){
        //delete specified annotation from server and update UI
        var parent = this;

        var deleteId = this.$('#DeleteBroadScaleConfirm').data('model_id');
        var objectsToRemove = broadScalePoints.get(this.$('#DeleteBroadScaleConfirm').data('model_id'));

        objectsToRemove.destroy({
            success: function(model, response, options) {
                parent.render();
                GlobalEvent.trigger("annotation_set_has_changed");
            },
            error: function (model, xhr, options) {
                console.log(xhr);
            }
        });
        //this.dismissConfirmation();
    },
    deleteAllBroadScaleAnnotations: function(){
        //remove all annotations from the current image
        this.$('#DeleteAllBroadScaleConfirm').css('display', 'block');
        this.$('.broadScaleRemoveButton').addClass('deleteStyle');

    },
    confirmDeleteAllBroadScaleAnnotation: function(){
        var parent = this;

        this.$('#DeleteAllBroadScaleConfirm').css('display', 'none');
        var model;
        
        var successCallback = _.after(broadScalePoints.length, function() {
            parent.render(); // render after all deletes are done (destorys are async)
        });

        for (var i = broadScalePoints.length - 1; i >= 0; i--){
            broadScalePoints.at(i).destroy({
                success: successCallback,
                error: function(model, response){
                    console.log('problem reseting Broad Scale Points',xhr);
                }
            });
        }

        GlobalEvent.trigger("annotation_set_has_changed");
        parent.render();
    },
    highlightInterfaceForBiota: function(){
        $('a[href=#biota_root_node]').trigger('activate-node');
    },
    highlightInterfaceForSubstrate: function(){
        $('a[href=#substrate_root_node]').trigger('activate-node');
    },
    highlightInterfaceForRelief: function(){
        $('a[href=#relief_root_node]').trigger('activate-node');
    },
    highlightInterfaceForBedform: function(){
        $('a[href=#bedforms_root_node]').trigger('activate-node');
    },
    clearAllWholeImageAnnotations: function(){
        //set all to '' (ie: no annotation)
        this.$('#ClearAllBroadScaleConfirm').css('display', 'block');
    },
    confirmClearAllBroadScaleAnnotation: function(){
        var parent = this;
        this.$('#ClearAllBroadScaleConfirm').css('display', 'none');

        var properties = { 'annotation_caab_code': '' };

        var successCallback = _.after(broadScalePoints.length, function() {
            GlobalEvent.trigger("annotation_set_has_changed");
            parent.render(); // render after all saves are done (saves are async)
        });

        broadScalePoints.each(function (whole_image_point) {
            whole_image_point.save(properties,{
                patch: true,
                headers: {"cache-control": "no-cache"},
                success: successCallback,
                error: function (model, xhr, options) {
                    console.log('problem reseting Broad Scale Points',xhr);
                }
            });
        });
    },
    toggleBroadScaleTools: function(ev){
        //ugh
        var model_id = $(ev.target).parent().data('model_id');

        var control = $('#ChooseAnnotationContainer').find("[data-model_id='"+model_id+"'] .broadScaleControlContainer");

        control.toggle();
    },
    percentCoverageSelected: function(ev) {
        var selected_percentage = $(ev.target).data('percentage');
        var model_id = $(ev.target).data('model_id');

        //set % in the model
        var properties = { 'coverage_percentage': selected_percentage};
        var theXHR  = broadScalePoints.get(model_id).save(properties, {
            patch: true,
            headers: {"cache-control": "no-cache"},
            success: function (model, xhr, options) {
                $('#ChooseAnnotationContainer').find("[data-model_id='"+model_id+"'] .broadScalePercentage").html(selected_percentage+" %");
            },
            error: function (model, xhr, options) {
                console.log('problem in percentCoverageSelected',xhr);
            }
        });
    },
    confirmSetImageUnscorable: function(){
        var parent = this;
        var model;
        
        var successCallback = _.after(broadScalePoints.length, function() {
            var unscorableCode = '00000001';

            var annotationSet = annotationSets.at(0);

            var broad_scale_annotation = new WholeImageAnnotation({ 'annotation_caab_code': unscorableCode, 'image':'/api/dev/image/'+selectedImageId+'/', 'annotation_set':'/api/dev/annotation_set/'+annotationSet.get('id')+'/'});

            // add spinnner TBD
            broadScalePoints.create(broad_scale_annotation,{
                success:function() {
                    parent.render();
                    GlobalEvent.trigger("annotation_set_has_changed");
                    //remove spinner TBD
                }
            });
            parent.render(); // render after all deletes are done (destorys are async)
        });

        for (var i = broadScalePoints.length - 1; i >= 0; i--){
            broadScalePoints.at(i).destroy({
                success: successCallback,
                error: function(model, response){
                    console.log('problem reseting Broad Scale Points',xhr);
                }
            });
        }

        //GlobalEvent.trigger("annotation_set_has_changed");
        parent.render();
    },
    showUnscorableConfirmation: function(){
        this.$('#SetImageUnscorable').css('display', 'block');
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