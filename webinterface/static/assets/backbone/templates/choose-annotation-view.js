ChooseAnnotationView = Backbone.View.extend({
    model: AnnotationCodeList,
    el: $('div'),
    initialize: function () {

        GlobalEvent.on("annotation_chosen", this.annotationChosen, this);
        GlobalEvent.on("point_is_selected", this.initializeSelection, this);
        GlobalEvent.on("new_parent_node", this.new_parent_node, this);
        GlobalEvent.on("OpenToBiotaTree", this.openTreeToBiota, this);
        GlobalEvent.on("OpenToSubstrateTree", this.openTreeToSubstrate, this);
        GlobalEvent.on("OpenToReliefTree", this.openTreeToRelief, this);
        GlobalEvent.on("OpenToBedformTree", this.openTreeToBedform, this);

        //this.render();
    },
    render: function() {
        // Compile the template using underscore
        var chooseAnnotationTemplate = _.template($("#ChooseAnnotationTemplate").html(), {});

        list_html = buildList(nested_annotation_list, false);

        // Load the compiled HTML into the Backbone "el"
        this.$el.html(chooseAnnotationTemplate);
        $('#annotation-chooser').append(list_html);
        this.clearSelection();

        $('#annotation-chooser ul').accordion();

        //make the first item expanded
        //this.initTreeToTopItem();

        return this;
    },
    events: {
        'mouseenter': 'mouse_entered',
        'mouseleave': 'mouse_exited',
        'click #assign_annotation_button': 'annotationFinalised',
        'click #annotation-chooser a': 'annotationChosen'
    },
    mouse_entered: function() {
        // selected annotations remain editable until mouse exit
    },
    mouse_exited: function() {
        // selected annotations rare now set with the current annotation code
        //GlobalEvent.trigger("annotation_to_be_set", this.current_annotation);
    },
    initializeSelection: function() {
        this.$('#assign_annotation_button').css('visibility', 'hidden');
        this.$('#current_annotation_label').text('Select Annotation...');
    },
    clearSelection: function(){
        this.$('#assign_annotation_button').css('visibility', 'hidden');
        this.$('#current_annotation_label').text('Annotation Selector');
    },
    annotationChosen: function(e){
        e.preventDefault();
        var annotation_code_id = $(e.currentTarget).data("id");
        GlobalEvent.trigger("annotation_to_be_set", annotation_code_id);
    },
    annotationFinalised: function(){
        //make it so
        /*
        this.$('#assign_annotation_button').css('visibility', 'hidden');
        GlobalEvent.trigger("annotation_to_be_set", this.current_annotation);*/
    },
    new_parent_node: function(new_parent_id){
        this.current_annotation = new_parent_id;
        var caab_object = annotationCodeList.get(new_parent_id);

        if (new_parent_id === '1'){
            this.$('#assign_annotation_button').css('visibility', 'hidden');
            this.$('#current_annotation_label').text(caab_object.get('code_name'));
        } else {
            this.annotationChosen(new_parent_id);
        }
    },
    initTreeToTopItem: function(){
        //make the first item expanded
        // $('ul.accordion > li').addClass('active', 'true');
        // $('ul.accordion > li > ul').css('display', 'block');
    }
});
ChooseAnnotationView.current_annotation = null;