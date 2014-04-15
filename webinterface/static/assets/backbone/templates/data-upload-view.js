//the data-upload-view will create deployments
var Deployment = Backbone.Model.extend({
    urlRoot: "/api/dev/deployment"
});

var GlobalEvent = _.extend({}, Backbone.Events);

// data-upload-model handles the file list and xhr2 business
var dataUploader = new DataUploader();

var UploadOrchestratorView = Backbone.View.extend({
    el: $('div'),
    events: {
    },
    onLoadError: function(model,response,options) {
        if(response.status == 401) {
            // $("#load-error-message").html("You do not have permission to upload data.");
        }
        else {
            // $("#load-error-message").html("An error occurred trying to load this project. Try refreshing the page.");
        }

        // $("#load-error-div").show();
    },
    initialize: function () {
        GlobalEvent.on("clear_everything", this.updateInterfaceForClear, this);
        GlobalEvent.on("files_were_dropped", this.updateInterfaceForDrop, this);
        GlobalEvent.on("deployment_description_parsed", this.updateDeploymentInfo, this);
        GlobalEvent.on("image_list_parsed", this.updateDeploymentInfo, this);

        //load the subviews
        this.dataErrorView = new DataErrorView({});
        this.dataUploadView = new DataUploadView({});
        this.deploymentInfoView = new DeploymentInfoView({});
        this.uploadControlView = new UploadControlView({});
        this.authenticationView = new AuthenticationView({});

        //render the views
        this.render();
    },
    render: function () {
        //required here to define editable fields for inline editing.
        $.fn.editable.defaults.mode = 'inline';

        // render subviews
        this.assign(this.dataErrorView,'#data_error_container');
        this.assign(this.dataUploadView,'#data_upload_container');
        this.assign(this.deploymentInfoView, '#deployment_info_container');
        this.assign(this.uploadControlView, '#upload_control_container');
        this.assign(this.authenticationView, '#authent_info_container');

        $('#deployment_info_container').hide();
        $('#upload_control_container').hide();
    },
    assign : function (view,selector) {
        //makes this view hierachy work like bananas
        view.setElement($(selector)).render();
    },
    updateInterfaceForDrop: function() {
        // this.deploymentInfoView.render();
        // $('#deployment_info_container').show();
    },
    updateDeploymentInfo: function() {
        $('#deployment_info_container').show();
        $("#no-drop-alert").hide();
        this.deploymentInfoView.updateDeploymentInfo();
    },
    updateInterfaceForClear: function() {
        // clear the file list, update the UI
        dataUploader.set({file_list:[]});
        this.dataUploadView.updateFileListInView(dataUploader.get("file_list"));
        $('#deployment_info_container').hide();
        $('#upload_control_container').hide();
    }

});

// Error view for reporting success or failure of import/file checking etc
var DataErrorView = Backbone.View.extend({
    // model: new Campaign(),
    el: $('div'),
    initialize: function () {
        GlobalEvent.on("image_list_missing", this.showImagesListError, this);
        GlobalEvent.on("description_missing", this.showDescriptionFileError, this);
        GlobalEvent.on("all_import_passed", this.allImportPassed, this);
        GlobalEvent.on("all_upload_passed", this.allUploadPassed, this);
    },
    events: {
    },
    render: function () {
        var variables = {};
        // Compile the template using underscore
        var dataErrorTemplate = _.template($("#error_report_template").html(),variables);
        this.$el.html(dataErrorTemplate);
        this.hideAll();

        return this.el;
    },
    hideAll: function () {
        $('#no_images_list_file').hide();
        $('#no_deployment_file').hide();
        $('#all_import_worked').hide();
        $('#all_upload_worked').hide();
    },
    showImagesListError: function() {
        $('#no_images_list_file').show();
    },
    showDescriptionFileError: function () {
        $('#no_deployment_file').show();
    },
    allImportPassed: function () {
        this.hideAll();
        $('#all_import_worked').hide();
    },
    allUploadPassed: function() {
        this.hideAll();
        $('#all_upload_worked').hide();
    }
});

// this view handles the file drop and drop events
var DataUploadView = Backbone.View.extend({
    // model: new Campaign(),
    el: $('div'),
    initialize: function () {
    },
    events: {
        "change #fileselect": "fileSelectHandler",
        "dragover #filedrag":  "fileDragHover",
        "dragleave #filedrag": "fileDragHover",
        "drop #filedrag": "fileSelectHandler",
    },
    render: function () {
        var variables = {};
        // Compile the template using underscore
        var dataUploadTemplate = _.template($("#data_upload_template").html(),variables);

        this.$el.html(dataUploadTemplate);
        $("#dragged-files-view").hide();
        return this.el;
    },
    fileSelectHandler: function (event){
        var parent = this;

        //show dropped or selected file list in main UI
        // jQuery.event.props.push('dataTranfer');

        this.fileDragHover(event);
        
        // fetch FileList object
        // note: dataTranfer is not in the jQuery event,have to poll the originalEvent contained within.

        var dt = event.originalEvent.dataTransfer;
        //var files = event.target.files || event.originalEvent.dataTransfer.files;

        dataUploader.set({file_list:event.originalEvent.dataTransfer.files});
        this.updateFileListInView(dataUploader.get("file_list"));
        dataUploader.parseRequiredFiles();

    },
    updateFileListInView: function(selectedFileList){
        //update UI elements for dropped files
        if (selectedFileList.length > 0){
            $('#upload_control_container').show();
            $("#draghere-cartoon").hide();
            $("#dragged-files-view").show();
        } else {
            $('#upload_control_container').hide();
            $("#draghere-cartoon").show();
            $("#dragged-files-view").hide();
        }

        // process all File objects,parsing for file info.
        for (var i = 0; i < selectedFileList.length; i++) {

            var item = selectedFileList[i]; //.webkitGetAsEntry();
            // console.log(item);
            // this.parseFile(f);
            if (item.isDirectory){
                // probahly never works.
                this.parseDir(item);
            } else {
                this.parseFile(item);
            }
        }
        GlobalEvent.trigger("files_were_dropped");

    },
    parseFile: function (file){
        //parse file for useful contents
        $("#dragged-files-view table").append("<tr>"+"<td>"+file.name+"</td>"+"<td>"+file.size+"</td>"+"<td>"+file.type+"</td>"+"</tr>");
    },
    parseDir: function(event){
        //directory parsing code,in the unlikely event thate we have access to DirectoryReader()
        var parent = this;

        // this probably means dir dropping is webkit only (chrome/safari)
        var entry = event.dataTransfer.items[0].webkitGetAsEntry();
        var entries = [];

        // console.log(entry);

        // Call the reader.readEntries() until no more results are returned.
        var readEntries = function() {
            dirReader.readEntries (function(results) {
                if (!results.length) {
                    listResults(entries.sort());
                } else {
                    entries = entries.concat(toArray(results));
                }
            },parent.errorHandler);
          };
    },
    errorHandler: function (error) {
        console.log(error);
    },
    fileDragHover: function (event){
        //drag or hover event
        event.stopPropagation();
        event.preventDefault();
        event.target.className = (event.type == "dragover" ? "hover" : "");
    }
});

var DeploymentInfoView = Backbone.View.extend({
    // the DeploymentInfoView shows the deployment info for the currently set of files to be
    // uploaded.  If the deployment already exists on the server all the current metadata is
    // displayed

    // model: new Deployment(),
    el: $('div'),
    initialize: function () {
    },
    events: {
    },
    render: function () {
        var variables = {
            'version': '',
            'type': '',
            'description': '',
            'operator': '',
            'keywords': '',
            'campaign': '',
            'campaign_name': '',
            'campaign_number': '',
            'contact_person': '',
            'descriptive_keywords': '',
            'end_position': '',
            'end_time_stamp': '',
            'id': '',
            'license': '',
            'map_extent': '',
            'max_depth': '',
            'min_depth': '',
            'mission_aim': '',
            'reported_operator': '',
            'resource_uri': '',
            'short_name': '',
            'start_position': '',
            'start_time_stamp': '',
            'transect_shape': '',
            'reported_type': '',
            'estimated_depth_uncertainty': ''
        };
        // Compile the template using underscore

        var deploymentTemplate = _.template($("#deployment_info_template").html(),variables);

        this.$el.html(deploymentTemplate);
        this.initDeploymentInfo();
        $('#deployment_model_well').hide();
        return this.el;
    },
    updateDeploymentInfo: function() {
        // update fields and remove x-editable 'empty' style so that the fields will look normal
        // we're assuming that all of these fields have had 'editable' run on them in the initDeploymentInfo

        var parent = this;
        if (dataUploader.get("description").trim() !== ""){
            $('#description_text').text(dataUploader.get("description"));
            $('#description_text').removeClass('editable-empty');
        }
        
        if (dataUploader.get("operator").trim() !== ""){
            $('#operator_text').text(dataUploader.get("operator"));
            $('#operator_text').removeClass('editable-empty');
        }

        if(dataUploader.get("contact_person").trim() !== ""){
           $('#contact_text').text(dataUploader.get("contact_person"));
            $('#contact_text').removeClass('editable-empty');
        }

        if (dataUploader.get("keywords").trim() !== ""){
            $('#keywords_text').text(dataUploader.get("keywords"));
            $('#keywords_text').removeClass('editable-empty');
        }

        if (dataUploader.get("short_name").trim() !== ""){
            $('#shortname_text').text(dataUploader.get("short_name"));
            $('#shortname_text').removeClass('editable-empty');
        }

        if(dataUploader.get("start_position").trim() !== ""){
            $('#start_position_text').text(dataUploader.get("start_position"));
            $('#start_position_text').removeClass('editable-empty');
        }

        if (dataUploader.get("end_position").trim() !== ""){
            $('#end_position_text').text(dataUploader.get("end_position"));
            $('#end_position_text').removeClass('editable-empty');
        }
        if(dataUploader.get("min_depth") !== ""){
            $('#min_depth_text').text(dataUploader.get("min_depth"));
            $('#min_depth_text').removeClass('editable-empty');
        }

        if(dataUploader.get("max_depth") !== ""){
            $('#max_depth_text').text(dataUploader.get("max_depth"));
            $('#max_depth_text').removeClass('editable-empty');
        }

        if(dataUploader.get("transect_shape").trim() !== ""){
            $('#bounding_polygon_text').text(dataUploader.get("transect_shape"));
            $('#bounding_polygon_text').removeClass('editable-empty');
        }


        if(dataUploader.get("campaign_number").trim() !== ""){
            $('#campaign_text').text(dataUploader.get("campaign_number"));
            $('#campaign_text').removeClass('editable-empty');
        }
        //update warnings and errors
        parent.checkDeploymentDataEntry();
    },
    initDeploymentInfo: function() {
        var parent = this;

        // get, from the model or the user, what we need for the deployment data model. 
        // uses x-editable (http://vitalets.github.io/x-editable)
        // Note:
        //      For each text entry box we explicitly set 'editable-empty' and run checkDeploymentDataEntry()
        //      this allows the error box to stay up to date with user changes.  Normally the class 'editable-empty'
        //      gets set *after* the success function and x-editable function is done.

        // Select boxes come with a default selection, so a blank selection should not happen.
        // the success function and checks are just there for consistency and ass covering.

        var versionArray = [{value: 0, text: 'Select data format version'},
                            {value: 1, text: '1.0'}];
        $('#version_text').editable({   type: 'select',
                                        value: 1,
                                        defaultValue: 1,
                                        autotext: 'always',
                                        unsavedclass: null,
                                        source: versionArray,
                                        success: function(response, newValue){
                                            if(newValue.trim()===''){
                                                $('#version_text').addClass('editable-empty');
                                            } else {
                                                $('#version_text').removeClass('editable-empty');
                                                dataUploader.set("version", versionArray[newValue].text);
                                            }
                                            parent.checkDeploymentDataEntry();
                                        }
                                    });


        var typeArray = [{value: 0, text: 'Select data deployment type'},
                        {value: 1, text: 'TI'},
                        {value: 2, text: 'AUV'},
                        {value: 3, text: 'DOV'},
                        {value: 4, text: 'BRUV'}];
        $('#type_text').editable({  type: 'select',
                                    value: 1,
                                    defaultValue: 0,
                                    unsavedclass: null,
                                    source: typeArray,
                                    success: function(response, newValue){
                                        if(newValue.trim()===''){
                                            $('#type_text').addClass('editable-empty');
                                        } else {
                                            $('#type_text').removeClass('editable-empty');
                                            dataUploader.set("type", typeArray[newValue].text);
                                        }
                                        parent.checkDeploymentDataEntry();
                                    }
                                });
        $('#description_text').editable({type: 'text',
                                        emptytext: 'Click to enter description ...',
                                        value: dataUploader.get("description"),
                                        // unsavedclass: null,
                                        success: function(response, newValue){
                                            if(newValue.trim()===''){
                                                $('#description_text').addClass('editable-empty');
                                            } else {
                                                $('#description_text').removeClass('editable-empty');
                                                dataUploader.set("description", newValue);
                                            }
                                            parent.checkDeploymentDataEntry();
                                        }

                                    });
        
        $('#operator_text').editable({  type: 'text',
                                        value: dataUploader.get("operator"),
                                        emptytext: 'Click to enter operator name...',
                                        unsavedclass: null,
                                        success: function(response, newValue){
                                            if(newValue.trim()===''){
                                                $('#operator_text').addClass('editable-empty');
                                            } else {
                                                $('#operator_text').removeClass('editable-empty');
                                                dataUploader.set("operator ", newValue);
                                            }
                                            parent.checkDeploymentDataEntry();
                                        }
                                    });
        
        $('#contact_text').editable({   type: 'text',
                                        emptytext: 'enter contact person name/email...',
                                        value: dataUploader.get("contact_person"),
                                        unsavedclass: null,
                                        success: function(response, newValue){
                                            if(newValue.trim()===''){
                                                $('#contact_text').addClass('editable-empty');
                                            } else {
                                                $('#contact_text').removeClass('editable-empty');
                                                dataUploader.set("contact_person", newValue);
                                            }
                                            parent.checkDeploymentDataEntry();
                                      }
                                    });

        var licenseArray = [{value: 0, text: 'CC-BY'}];
        $('#license_text').editable({   type: 'select',
                                        value: 0,
                                        source: licenseArray,
                                        unsavedclass: null,
                                        success: function(response, newValue){
                                            if(newValue.trim()===''){
                                                $('#license_text').addClass('editable-empty');
                                            } else {
                                                $('#license_text').removeClass('editable-empty');
                                                dataUploader.set("license", licenseArray[newValue].text);
                                            }
                                        }     
                                    });

        console.log('campaogn number -', dataUploader.get("campaign_number"),'-');
        $('#campaign_text').editable({type: 'text',
                                        emptytext: ' [campaign number] ',
                                        value: dataUploader.get("campaign_number"),
                                        unsavedclass: null,
                                        success: function(response, newValue){
                                            if(newValue.trim()===''){
                                                $('#campaign_text').addClass('editable-empty');
                                            } else {
                                                $('#campaign_text').removeClass('editable-empty');
                                                dataUploader.set("campaign_number", newValue);
                                                dataUploader.set("campaign", "/api/dev/campaign/"+newValue+"/");
                                            }
                                            parent.checkDeploymentDataEntry();
                                      }
                                    });

        $('#keywords_text').editable({  type: 'text',
                                        emptytext: 'Click to enter useful keywords (comma or space delimited)...',
                                        value: dataUploader.get("keywords"),
                                        unsavedclass: null,
                                        success: function(response, newValue){
                                            if(newValue.trim()===''){
                                                $('#keywords_text').addClass('editable-empty');
                                            } else {
                                                $('#keywords_text').removeClass('editable-empty');
                                            }
                                            parent.checkDeploymentDataEntry();
                                            dataUploader.set("keywords", newValue);
                                      }
                                    });
        $('#shortname_text').editable({type: 'text',
                                       emptytext: 'Click to enter deployment title...',
                                       value: dataUploader.get("short_name"),
                                       unsavedclass: null,
                                       success: function(response, newValue){
                                            if(newValue.trim()===''){
                                                $('#shortname_text').addClass('editable-empty');
                                            } else {
                                                $('#shortname_text').removeClass('editable-empty');
                                                dataUploader.set("short_name", newValue);
                                            }
                                            parent.checkDeploymentDataEntry();
                                       }
                            });
        $('#start_position_text').editable({type: 'text',
                                            emptytext: 'Click to enter start lat long (ie: -22.195 113.8853)',
                                            value: dataUploader.get("start_position"),
                                            success: function(response, newValue){
                                                if(newValue.trim()===''){
                                                    $('#start_position_text').addClass('editable-empty');
                                                } else {
                                                    $('#start_position_text').removeClass('editable-empty');
                                                }
                                                parent.checkDeploymentDataEntry();
                                                dataUploader.set("start_position", newValue);
                                            }
                                        });
        $('#end_position_text').editable({  type: 'text',
                                            emptytext: 'Click to enter end lat long (ie: -22.195 13.8853)',
                                            value: dataUploader.get("end_position"),
                                            unsavedclass: null,
                                            success: function(response, newValue){
                                                if(newValue.trim()===''){
                                                    $('#end_position_text').addClass('editable-empty');
                                                } else {
                                                    $('#end_position_text').removeClass('editable-empty');
                                                }
                                                parent.checkDeploymentDataEntry();
                                                dataUploader.set("end_position", newValue);
                                            }
                                        });
        
        $('#min_depth_text').editable({ type: 'text',
                                        emptytext: 'Click to enter minimum depth (m)...',
                                        value: dataUploader.get("min_depth"),
                                        unsavedclass: null,
                                        success: function(response, newValue){
                                            if(newValue.trim()===''){
                                                $('#min_depth_text').addClass('editable-empty');
                                            } else {
                                                $('#min_depth_text').removeClass('editable-empty');
                                                dataUploader.set("min_depth", newValue);
                                            }
                                            parent.checkDeploymentDataEntry();
                                        }
                                    });
        
        $('#max_depth_text').editable({ type: 'text',
                                        emptytext: 'Click to enter maximum depth (m)...',
                                        value: dataUploader.get("max_depth"),
                                        unsavedclass: null,
                                        success: function(response, newValue){
                                            if(newValue.trim()===''){
                                                $('#max_depth_text').addClass('editable-empty');
                                            } else {
                                                $('#max_depth_text').removeClass('editable-empty');
                                                dataUploader.set("max_depth", newValue);
                                            }
                                            parent.checkDeploymentDataEntry();
                                        }
                                    });
        
        $('#bounding_polygon_text').editable({  type: 'text',
                                                emptytext: 'Click to enter bounding polygon ...',
                                                value: dataUploader.get("transect_shape"),
                                                unsavedclass: null,
                                                success: function(response, newValue){
                                                    if(newValue.trim()===''){
                                                        $('#bounding_polygon_text').addClass('editable-empty');
                                                    } else {
                                                        $('#bounding_polygon_text').removeClass('editable-empty');
                                                    }
                                                    parent.checkDeploymentDataEntry();
                                                    dataUploader.set("transect_shape", newValue);
                                                }
                                            });
        this.updateDeploymentInfo();
        this.checkDeploymentDataEntry();
    },
    checkDeploymentDataEntry: function() {
        // check each bit of data needed to POST the deployment, showing a useful message if missing.
        
        // default is success with error views hidden.
        // if missing data is found the success view is hidden and error view is shown

        // if the entry exists, it is updated in the model with the contents

        $("#deployment_data_complete").show();
        $("#deployment_data_incomplete").hide();
        $("#deployment_data_optional_incomplete").hide();
        $("#no-valid-data-alert").hide();

        $("#deployment_missing_info > li").remove();
        $("#deployment_missing_optional_info > li").remove();

        if($('#shortname_text').hasClass("editable-empty")) {
            $("#deployment_missing_info").append("<li> The deployment name is missing</li>");
            $("#deployment_data_incomplete").show();
            $("#no-valid-data-alert").show();
            $("#deployment_data_complete").hide();
        }

        if($('#version_text').hasClass("editable-empty")) {
            $("#deployment_missing_info").append("<li>Version is missing</li>");
            $("#deployment_data_incomplete").show();
            $("#no-valid-data-alert").show();
            $("#deployment_data_complete").hide();
        }

        if($('#type_text').hasClass("editable-empty")) {
            $("#deployment_missing_info").append("<li>Deployment type is missing, select a type.</li>");
            $("#deployment_data_incomplete").show();
            $("#no-valid-data-alert").show();
            $("#deployment_data_complete").hide();
        }

        if($('#campaign_text').hasClass("editable-empty")) {
            $("#deployment_missing_info").append("<li>Campaign selection is missing, enter a campaign</li>");
            $("#deployment_data_incomplete").show();
            $("#no-valid-data-alert").show();
            $("#deployment_data_complete").hide();
        }

        if($('#description_text').hasClass("editable-empty")) {
            $("#deployment_missing_info").append("<li>Deployment description is missing</li>");
            $("#deployment_data_incomplete").show();
            $("#no-valid-data-alert").show();
            $("#deployment_data_complete").hide();
        }
        
        if($('#operator_text').hasClass("editable-empty")) {
            $("#deployment_missing_optional_info").append("<li>Operator name is missing</li>");
            $("#deployment_data_optional_incomplete").show();
        }

        if($('#contact_text').hasClass("editable-empty")) {
            $("#deployment_missing_optional_info").append("<li>Contact person name is missing</li>");
            $("#deployment_data_optional_incomplete").show();
        }
        
        if($('#keywords_text').hasClass("editable-empty")) {
            $("#deployment_missing_optional_info").append("<li>Deployment keywords are missing</li>");
            $("#deployment_data_optional_incomplete").show();
        }

        if($('#license_text').hasClass("editable-empty")) {
            $("#deployment_missing_info").append("<li>Deployment description is missing</li>");
            $("#deployment_data_incomplete").show();
            $("#no-valid-data-alert").show();
            $("#deployment_data_complete").hide();
        }

        if($('#start_position_text').hasClass("editable-empty")) {
            $("#deployment_missing_info").append("<li>The start position is missing, Check your images.csv file.</li>");
            $("#deployment_data_incomplete").show();
            $("#deployment_data_complete").hide();
        }
        if($('#end_position_text').hasClass("editable-empty")) {
            $("#deployment_missing_info").append("<li>The end position is missing, Check your images.csv file.</li>");
            $("#deployment_data_incomplete").show();
            $("#no-valid-data-alert").show();
            $("#deployment_data_complete").hide();
        }
        if($('#bounding_polygon_text').hasClass("editable-empty")) {
            $("#deployment_missing_info").append("<li>The bounding box is missing, Check your images.csv file.</li>");
            $("#deployment_data_incomplete").show();
            $("#no-valid-data-alert").show();
            $("#deployment_data_complete").hide();
        }
        if($('#min_depth_text').hasClass("editable-empty")) {
            $("#deployment_missing_info").append("<li>The depth minimum is missing, Check your images.csv file, or enter an estimate</li>");
            $("#deployment_data_incomplete").show();
            $("#no-valid-data-alert").show();
            $("#deployment_data_complete").hide();
        }
        if($('#max_depth_text').hasClass("editable-empty")) {
            $("#deployment_missing_info").append("<li>The depth maximum is missing, Check your images.csv file, or enter an estimate</li>");
            $("#deployment_data_incomplete").show();
            $("#no-valid-data-alert").show();
            $("#deployment_data_complete").hide();
        }

    }
});
var AuthenticationView = Backbone.View.extend({
    el: $('div'),
    initialize: function () {},
    events: {},
    render: function() {
        // Compile the template using underscore
        var variables = {
            'apikey': '',
            'username': ''
        };

        var authentTemplate = _.template($("#account_info_template").html(),variables);

        this.$el.html(authentTemplate);
        this.initEditableFields();

        return this.el;
    },
    initEditableFields: function() {
        $('#apikey_text').editable({  type: 'text',
                                        emptytext: 'Click to enter user API Key',
                                        value: dataUploader.get("apikey"),
                                        unsavedclass: null,
                                        success: function(response, newValue){
                                            if(newValue.trim()===''){
                                                $('#apikey_text').addClass('editable-empty');
                                            } else {
                                                $('#apikey_text').removeClass('editable-empty');
                                            }
                                            dataUploader.set("apikey", newValue);
                                      }
                                    });
        $('#username_text').editable({  type: 'text',
                                emptytext: 'Click to enter username',
                                value: dataUploader.get("username"),
                                unsavedclass: null,
                                success: function(response, newValue){
                                    if(newValue.trim()===''){
                                        $('#username_text').addClass('editable-empty');
                                    } else {
                                        $('#username_text').removeClass('editable-empty');
                                    }
                                    dataUploader.set("username", newValue);
                              }
                            });
    }
});
var UploadControlView = Backbone.View.extend({
    el: $('div'),
    initialize: function () {
        GlobalEvent.on("image_uploaded", this.updateImageProgressView, this);
        GlobalEvent.on("start_imagedata_upload", this.startImageDataUpload, this);
        GlobalEvent.on("end_imagedata_upload_success", this.imageDataUploadSuccess, this);
        GlobalEvent.on("end_imagedata_upload_failed", this.imageDataUploadFailed, this);
        GlobalEvent.on("start_deployment_post", this.startDeploymentPost, this);
        GlobalEvent.on("deployment_post_success", this.deploymentPostSuccess, this);
        GlobalEvent.on("deployment_post_failed", this.deploymentPostFailed, this);
        GlobalEvent.on("end_images_upload", this.deploymentCompleteSuccess, this);
    },
    events: {
        "click #start-upload-button": "startUploadProcess",
        "click #cancel-clear-button": "clearEverything",
    },
    render: function () {
        // Compile the template using underscore
        var variables = {};

        var actionTemplate = _.template($("#action_control_template").html(),variables);

        this.$el.html(actionTemplate);

        $("#upload_success_status").hide();

        return this.el;
    },
    startDeploymentPost: function() {
        //an entry has been POSTed to the deployment API
        $("#button_zone").hide();
        $("#deployment_post_status #activity-icon").addClass("icon-spin");
    },
    deploymentPostSuccess: function() {
        // the deployment API post worked
        $("#deployment_post_status #activity-icon").removeClass("icon-spin");
        $("#deployment_post_status").addClass("action-box-success");
    },
    deploymentPostFailed: function() {
        // the deployment API post failed
        $("#deployment_post_status #activity-icon").removeClass("icon-spin");
        $("#deployment_post_status").addClass("action-box-failed");
    },
    startImageDataUpload: function() {
        $("#image_metadata_status #activity-icon").addClass("icon-spin");
    },
    imageDataUploadSuccess: function() {
        $("#image_metadata_status #activity-icon").removeClass("icon-spin");
        $("#image_metadata_status").addClass("action-box-success");
    },
    imageDataUploadFailed: function() {
        $("#image_metadata_status #activity-icon").removeClass("icon-spin");
        $("#image_metadata_status").addClass("action-box-failed");
    },
    startUploadProcess: function() {
        dataUploader.upload();
    },
    clearEverything: function() {
        // clear all UI, start the upload process from scratch
        selectedFileList = [];
        GlobalEvent.trigger("clear_everything");
    },
    updateImageProgressView: function() {
        $("#image_upload_bar").css("width",dataUploader.get("images_uploaded_percent")+"%");
    },
    deploymentCompleteSuccess: function () {
        $("#upload_success_status").show();
    }
});
