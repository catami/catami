//a mixin helper function to serialize forms
$.fn.serializeObject = function()
{
   var o = {};
   var a = this.serializeArray();
   $.each(a, function() {
       if (o[this.name]) {
           if (!o[this.name].push) {
               o[this.name] = [o[this.name]];
           }
           o[this.name].push(this.value || '');
       } else {
           o[this.name] = this.value || '';
       }
   });
   return o;
};

var Deployment = Backbone.Model.extend({
    urlRoot: "/api/dev/deployment"
});

var Deployments = Backbone.Tastypie.Collection.extend({
    urlRoot: "/api/dev/deployment",
    model: Deployment
});

var Image = Backbone.Model.extend({
    urlRoot: "/api/dev/image"
});

var Images = Backbone.Tastypie.Collection.extend({
    model: Image,
    url: function(){
        return this.instanceUrl;
    },
    initialize: function(props){
        this.instanceUrl = props.url;
    }
});

var Project = Backbone.Model.extend({
    urlRoot: "/api/dev/project/",
    validation: {
        name: {
            required: true,
            msg: 'Please provide a project name.'
        },
        description: {
            required: true,
            msg: 'Please provide a description for the project.'
        }
    }
});

var Projects = Backbone.Tastypie.Collection.extend({
    urlRoot: "/api/dev/project/",
    model: Project
});

var ProjectPermissions = Backbone.Model.extend({
    url: function(){
        return this.instanceUrl;
    },
    initialize: function(props){
        this.instanceUrl = props.url;
    }
});

function getPercentageCompleteURL(annotationSetId) {
    return "/api/dev/annotation_set/" + annotationSetId + "/get_percentage_complete/";
}



ProjectView = Backbone.View.extend({
    model: Project,
    el: $('div'),
    initialize: function () {
        this.render();
    },
    render: function () {

        var owner = project.get("owner").username;
        var permissions = project.get("permissions");

        var edit_content = $.inArray("change_project", permissions) > -1 ? "<a id=\"configure_project_button\" class=\"btn\" href=\"#\">Configure Project</a>" : "";
        var delete_content = $.inArray("delete_project", permissions) > -1 ? "<a id=\"delete_project_button\" class=\"btn btn-danger\" href=\"#delete_modal\" data-toggle=\"modal\">Delete Project</a>" : "";
        var share_content = (owner == currentUsername) ? "<a id=\"share_project_button\" class=\"btn btn-info\">Share Project</a>" : "";

        //render the items to the main template
        var projectVariables = {
            "name": project.get("name"),
            "description": project.get("description"),
            "map_extent": project.get("map_extent"),
            "edit_content": edit_content,
            "delete_content": delete_content,
            "share_content": share_content
        };

        // Compile the template using underscore
        var projectTemplate = _.template($("#ProjectDashboardTemplate").html(), projectVariables);

        // Load the compiled HTML into the Backbone "el"
        this.$el.html(projectTemplate);

        return this;
    },
    renderProjectStats: function() {

        //get sampling methods
        var imageSamplingMethods = ["random", "stratified", "spatial"];
        var pointSamplingMethods = ["random point", "stratified point"];
        var annotationSetTypes = ["fine scale","broad scale"]

        var imageSampling = imageSamplingMethods[annotationSets.at(0).get('image_sampling_methodology')];
        var pointSampling = pointSamplingMethods[annotationSets.at(0).get('point_sampling_methodology')];
        var annotationSetType = annotationSetTypes[annotationSets.at(0).get('annotation_set_type')];

        var annotationSetImages = new Images({"url": "/api/dev/annotation_set/" + annotationSets.at(0).get('id') + "/images/"});

        $.get(
                getPercentageCompleteURL(annotationSets.at(0).get('id'))
        ).done(
            function(data) {
                $('#percentage_complete').html(data.percentage_complete + "%");
            }
        ).fail(
            function() {
                $('#percentage_complete').html("-%");
            }
        );

        //get total images
        annotationSetImages.fetch({
            data: { limit: 1, offset: 0},
            success: function (model, response, options) {
                //total images set
                $('#total_images').html(annotationSetImages.meta.total_count);
                $('#image_sampling_method').html(imageSampling);

                //get points total and calculate completeness
                if (annotationSetType == annotationSetTypes[0]){
                    $('#annotation_type_label').html('Fine Scale Annotation')
                    $('#points_per_image').html(annotationSets.at(0).get('points_per_image'));
                    $('#point_sampling_method').html(pointSampling);
                }
                else if (annotationSetType == annotationSetTypes[1]){
                    $('#annotation_type_label').html('Broad Scale Annotation')
                    $('#points_per_image').html(annotationSets.at(0).get('whole_image_annotations_per_image'));
                    $('#point_sampling_method').html('whole image');
                }

            },
            error: function (model, response, options) {
                $('#total_images').html("?");

                $.pnotify({
                    title: 'Failed to load the project stats. Try refreshing the page.',
                    text: response.status,
                    type: 'error', // success | info | error
                    hide: true,
                    icon: false,
                    history: false,
                    sticker: false
                });
            }

        });
    },
    events: {
        "click #configure_project_button": "doConfigure",
        "click #export_project_button": "doExport",
        "click #start_annotating_button": "doStartAnnotating",
        "click #delete_project_modal_button": "doDeleteProject",
        "click #share_project_button": "doShareProject"
    },
    doConfigure: function (event) {
        //redirect to configuration page
        window.location.replace("/projects/" + project.get("id") + "/configure");
    },
    doExport: function (event) {
        window.location.replace("/api/dev/project/" + project.get("id") + "/csv");
    },
    doStartAnnotating: function(event) {
        window.location.replace("/projects/" + project.get("id") + "/annotate");
    },
    doDeleteProject: function(event) {
        project.destroy({
            success: function() {
                //redirect away from this project
                window.location.replace("/projects/");
            },
            error: function() {
                $.pnotify({
                    title: 'Error',
                    text: "Failed to delete this project.",
                    type: 'error', // success | info | error
                    hide: true,
                    icon: false,
                    history: false,
                    sticker: false
                });
            }
        });
    },
    doShareProject: function(event) {

        projectPermissions.fetch({
            success: function (model, response, options) {
                //load the project
                if(projectPermissionsView == null)
                    projectPermissionsView = new ProjectPermissionsView({
                        el: $("#ProjectPermissionsContainer"),
                        model: projectPermissions
                    });

                projectPermissionsView.render();
                $("#share_modal").modal('show');
            },
            error: function (model, response, options) {
                $.pnotify({
                    title: 'Failed to load project details. Try refreshing the page.',
                    text: response.status,
                    type: 'error', // success | info | error
                    hide: true,
                    icon: false,
                    history: false,
                    sticker: false
                });
            }
        });

    }
});



ProjectPermissionsView = Backbone.View.extend({
    typeaheadUsers: [],
    model: ProjectPermissions,
    el: $('div'),
    initialize: function () {
        this.render();
    },
    render: function () {

        //get tall the images to be rendered
        var permissionTemplate = "";

        // get the permissions
        var project_permissions = projectPermissions.get("project_permissions");

        // get the permissions of each of the users
        for (var i=0; i<project_permissions.length; i++) {

            var view_selected = "";
            var edit_selected = "";

            // select the appropriate permissions
            $.inArray("change_project", project_permissions[i].permissions) > -1 ? edit_selected = "selected" : view_selected = "selected";

            var userPermissionsVariables = {
                "display_name": project_permissions[i].display_name,
                "username": project_permissions[i].username,
                "view_selected": view_selected,
                "edit_selected": edit_selected
            };

            permissionTemplate += _.template($("#UserProjectPermissionsTemplate").html(), userPermissionsVariables);
        }

        // publicly visible?
        var public_selected = "";
        var private_selected = "";

        (projectPermissions.get("is_public") == true) ? public_selected = "selected" : private_selected = "selected";

        // render the permissions public/private
        var projectPermissionsVariables = {
            "project_permissions": permissionTemplate,
            "private_selected": private_selected,
            "public_selected": public_selected
        };

        // Compile the template using underscore
        var projectPermissionsTemplate = _.template($("#ProjectPermissionsTemplate").html(), projectPermissionsVariables);

        // Load the compiled HTML into the Backbone "el"
        this.$el.html(projectPermissionsTemplate);

        //$(projectPermissionsTemplate).appendTo('#ProjectPermissionsContainer');

        //for the user lookup add permissions
        this.renderTypeahead();

        return this;
    },
    renderTypeahead: function() {
        var parent = this;

        // this is for the typeahead lookup
        $('.typeahead').typeahead({
            name: 'users',
            remote: {
                // this API call excludes the logged in user
                url: '/api/dev/users/?format=json&first_name__icontains=%QUERY&first_name__iregex=^((?!'+currentUsername+').)*$&limit=10',
                filter: function(parsedResponse) {
                    parent.typeaheadUsers = [];
                    for(i = 0; i < parsedResponse.objects.length; i++) {
                        parent.typeaheadUsers.push({
                             "display_name": parsedResponse.objects[i].first_name + " " + parsedResponse.objects[i].last_name,
                             "value": parsedResponse.objects[i].username
                        });
                    }
                    return parent.typeaheadUsers;
                }
            }
        });
    },
    events: {
        "change select": "selectChanged",
        "click .remove-button": "removePermission",
        "click #permissions-save": "doSave",
        "click #add-permission": "addPermission"
    },
    selectChanged: function(event) {
        //update the relative permission
        var project_permissions = projectPermissions.get('project_permissions');

        //username which has been updated
        var username = $(event.target).attr("id");
        var newPermission = $(event.target).val();

        //update public/private status
        if(username == "is_public")
            if(newPermission == "public") {
                projectPermissions.set("is_public", true);
            }
            else {
                projectPermissions.set("is_public", false);
            }

        //update permissions for users
        for(var i=0; i<project_permissions.length; i++) {
            if(project_permissions[i].username == username)
                if(newPermission == "change_project") {
                    project_permissions[i].permissions = ['change_project', 'view_project'];
                } else {
                    project_permissions[i].permissions = ['view_project'];
                }
        }

    },
    removePermission: function(event) {
        var username = $(event.target).attr("id");

        //remove the relative permission
        var project_permissions = projectPermissions.get('project_permissions');

        // remove from model
        for(var i=0; i<project_permissions.length; i++) {
            if(project_permissions[i].username == username)
                project_permissions.splice(i, 1);
        }

        //remove from user interface
        $("#"+username+"-row").remove();
    },
    addPermission: function(event) {
        $("#user-typeahead-error-div").hide();

        //the username entered
        var username = $("#user-typeahead").val();
        var display_name = username;

        //username validation bool
        var usernameValid = false;

        // check that this user actually exists
        for (var i=0; i < this.typeaheadUsers.length; i++) {
            if(username = this.typeaheadUsers[i].value) {
                usernameValid = true;
                display_name = this.typeaheadUsers[i].display_name;
                break;
            }
        };

        // permission already set bool
        var permissionAlreadySet = false;

        // check that the user does not already have a permission set
        var project_permissions = projectPermissions.get('project_permissions');
        for(var i=0; i<project_permissions.length; i++) {
            if(project_permissions[i].username == username) {
                permissionAlreadySet = true;
                break;
            }
        }

        if(!usernameValid) {
            $("#user-typeahead-error-message").html("User '" + username + "' does not exist.");
            $("#user-typeahead-error-div").show();
        }
        else if (!permissionAlreadySet){
            // add the user to the list with default permission
            var userPermissionsVariables = {
                "display_name": display_name,
                "username": username,
                "view_selected": "selected",
                "edit_selected": ""
            };

            var permissionTemplate = _.template($("#UserProjectPermissionsTemplate").html(), userPermissionsVariables);
            $("#permission_table_body").append(permissionTemplate);

            //also have to add to the model
            var project_permissions = projectPermissions.get('project_permissions');
            var newPermission = {};
            newPermission.username = username;
            newPermission.display_name = display_name;
            newPermission.permissions = ['view_project'];
            project_permissions.push(newPermission);
        }

    },
    doSave: function() {
        //save away
        var theXHR = projectPermissions.save(null, {
            success: function (model, xhr, options) {
                // no need to do anything
            },
            error: function (model, xhr, options) {
                // notify the users something went wrong
                $.pnotify({
                    title: 'Error',
                    text: "Failed to save permissions",
                    type: 'error', // success | info | error
                    hide: true,
                    icon: false,
                    history: false,
                    sticker: false
                });
            }
        })
    }
});

ThumbanilView = Backbone.View.extend({
    el: $('div'),
    meta: {},
    initialize: function (options) {
        this.meta = options['meta']; //assign specified metadata to local var
        this.render();
    },
    render: function () {
        //ge tall the images to be rendered
        var imageTemplate = "";

        images.each(function (image) {
            var imageVariables = {
                "thumbnail_location": image.get('thumbnail_location')
            };
            imageTemplate += _.template($("#ThumbnailTemplate").html(), imageVariables);
        });

        var thumbnailListVariables = { "images": imageTemplate };
        // Compile the template using underscore
        var thumbnailListTemplate = _.template($("#ThumbnailListTemplate").html(), thumbnailListVariables);
        // Load the compiled HTML into the Backbone "el"

        this.$el.html(thumbnailListTemplate);

        //Create pagination
        var options = thumbnailPaginationOptions(this.meta);
        $('#pagination').bootstrapPaginator(options);

        return this;
    }
});


function loadPage(offset) {
    var off = {}
    if (offset) off = offset;
    // Make a call to the server to populate the collection
    images.fetch({
        data: { limit: 12, offset: off },
        success: function (model, response, options) {
            var thumbnailView = new ThumbanilView({
                el: $("#ThumbnailListContainer"),
                collection: images,
                meta: images.meta //read from initiaisation method's "option" variable
            });
        },
        error: function (model, response, options) {
            $.pnotify({
                title: 'Failed to load the desired images. Try refreshing the page.',
                text: response.status,
                type: 'error', // success | info | error
                hide: true,
                icon: false,
                history: false,
                sticker: false
            });
        }
    });
}

var project = new Project({ id: projectId });
var projectPermissions = new ProjectPermissions({ "url": "/api/dev/project/" + projectId + "/share_project/" });
var images;
var annotationSets = new AnnotationSets();
var points = new PointAnnotations();
var whole_image_points = new WholeImageAnnotations();
var projectPermissionsView;

project.fetch({

    success: function (model, response, options) {
        console.log(project);

        mapExtent = project.get("map_extent");

        annotationSets.fetch({
            data: { project: projectId },
            success: function (model, response, options) {

                //check not an empty list
                if (annotationSets.length > 0) {
                    var annotationSetId = annotationSets.at(0).get('id');

                    //load the image thumbnails
                    images = new Images({ "url": "/api/dev/annotation_set/" + annotationSetId + "/images/" });
                    loadPage();

                    //create the map
                    var map = new NewProjectsMap(WMS_URL, LAYER_PROJECTS, 'map', mapExtent);
                    map.updateMapForSelectedProject(projectId);
                    //map.updateMapForSelectedAnnotationSet(annotationSetId);
                    map.addAnnotationSetLayer(annotationSetId, WMS_URL, LAYER_ANNOTATIONSET);
                    map.zoomToExtent();

                    //load the project
                    var projectView = new ProjectView({
                        el: $("#ProjectDashboardContainer"),
                        model: project
                    });

                    $('#Legend').css('visibility', 'visible');
                    projectView.renderProjectStats();
                } else {
                    $.pnotify({
                        title: 'Error',
                        text: 'Failed to load annotation set details. Try refreshing the page.',
                        type: 'error', // success | info | error
                        hide: true,
                        icon: false,
                        history: false,
                        sticker: false
                    });
                }
            },
            error: function (model, response, options) {
                $.pnotify({
                    title: response.status,
                    text: 'Failed to load annotation set details. Try refreshing the page.',
                    type: 'error', // success | info | error
                    hide: true,
                    icon: false,
                    history: false,
                    sticker: false
                });
            }
        });
    },
    error: function (model, response, options) {

        if(response.status == 401) {
            $("#load-error-message").html("You do not have permission to view this project.");
        }
        else {
            $("#load-error-message").html("An error occurred trying to load this project. Try refreshing the page.");
        }

        $("#load-error-div").show();
    }
});




 
