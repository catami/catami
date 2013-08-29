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

ProjectView = Backbone.View.extend({
    model: Project,
    el: $('div'),
    initialize: function () {
        this.render();
    },
    render: function () {

        var permissions = project.get("permissions");

        var edit_content = $.inArray("change_project", permissions) > -1 ? "<a id=\"configure_project_button\" class=\"btn\" href=\"#\">Configure Project</a>" : "";
        var delete_content = $.inArray("delete_project", permissions) > -1 ? "<a id=\"delete_project_button\" class=\"btn btn-danger\" href=\"#delete_modal\" data-toggle=\"modal\">Delete Project</a>" : "";

        //render the items to the main template
        var projectVariables = {
            "name": project.get("name"),
            "description": project.get("description"),
            "map_extent": project.get("map_extent"),
            "edit_content": edit_content,
            "delete_content": delete_content
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

        //get total images
        annotationSetImages.fetch({
            data: { limit: 1, offset: 0},
            success: function (model, response, options) {
                //total images set
                $('#total_images').html(annotationSetImages.meta.total_count);
                $('#image_sampling_method').html(imageSampling);

                //get points total and calculate completeness
                if (annotationSetType == annotationSetTypes[0]){
                    points.fetch({ //assuming annotation sets have been fetched and succeeded
                        data: { limit: 100000, annotation_set: annotationSets.at(0).get('id') },
                        success: function (model, response, options) {

                            //points per image set
                            var totalPoints = points.meta.total_count;
                            var totalImages = annotationSetImages.meta.total_count;
                            $('#annotation_type_label').html('Fine Scale Annotation')
                            $('#points_per_image').html(totalPoints/totalImages);
                            $('#point_sampling_method').html(pointSampling);

                            console.log("total points " + totalPoints);

                            var pointsAnnotatedCounter = 0;
                            //loop through the points calculate completeness
                            points.each(function (point) {
                                if(point.get('annotation_caab_code') != "")
                                    pointsAnnotatedCounter++;
                            });

                            $('#percentage_complete').html(Math.floor((pointsAnnotatedCounter/totalPoints)*100) + "%");

                        },
                        error: function (model, response, options) {
                            $('#points_per_image').html("?");
                            $('#percentage_complete').html("?");

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
                }
                if (annotationSetType == annotationSetTypes[1]){
                    whole_image_points.fetch({ //assuming annotation sets have been fetched and succeeded
                        data: { limit: 100000, annotation_set: annotationSets.at(0).get('id') },
                        success: function (model, response, options) {

                            //points per image set
                            var totalPoints = whole_image_points.meta.total_count;
                            var totalImages = annotationSetImages.meta.total_count;
                            $('#annotation_type_label').html('Broad Scale Annotation')
                            $('#points_per_image').html(totalPoints/totalImages);
                            $('#point_sampling_method').html('whole image');

                            console.log("total points " + totalPoints);

                            var pointsAnnotatedCounter = 0;
                            //loop through the points calculate completeness
                            whole_image_points.each(function (whole_image_point) {
                                if(whole_image_point.get('annotation_caab_code') !== ""){
                                    pointsAnnotatedCounter++;
                                }
                            });
                            console.log('pointsAnnotatedCounter '+pointsAnnotatedCounter)
                            $('#percentage_complete').html(Math.floor((pointsAnnotatedCounter/totalPoints)*100) + "%");

                        },
                        error: function (model, response, options) {
                            $('#points_per_image').html("?");
                            $('#percentage_complete').html("?");

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
                }

            },
            error: function (model, response, options) {
                $('#total_images').html("?");
                $('#points_per_image').html("?");
                $('#percentage_complete').html("?");

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
        "click #delete_project_modal_button": "doDeleteProject"
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
var images;
var annotationSets = new AnnotationSets();
var points = new PointAnnotations();
var whole_image_points = new WholeImageAnnotations();

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

                    projectView.renderProjectStats();
                } else {
                    $.pnotify({
                        title: 'Failed to load annotation set details. Try refreshing the page.',
                        text: '',
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
                    title: 'Failed to load annotation set details. Try refreshing the page.',
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


 
