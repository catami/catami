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
    urlRoot: "/api/dev/generic_deployment"
});

var Deployments = Backbone.Tastypie.Collection.extend({
    urlRoot: "/api/dev/generic_deployment",
    model: Deployment
});

var Image = Backbone.Model.extend({
    urlRoot: "/api/dev/generic_image"
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

        //render the items to the main template
        var projectVariables = {
            "name": project.get("name"),
            "description": project.get("description"),
            "map_extent": project.get("map_extent")
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
        var pointSamplingMethods = ["random", "stratified"];
        var imageSampling = imageSamplingMethods[annotationSets.at(0).get('image_sampling_methodology')];
        var pointSampling = pointSamplingMethods[annotationSets.at(0).get('annotation_methodology')];

        var annotationSetImages = new Images({"url": "/api/dev/generic_annotation_set/" + annotationSets.at(0).get('id') + "/images/"});

        //get total images
        annotationSetImages.fetch({
            data: { limit: 1, offset: 0},
            success: function (model, response, options) {
                //total images set
                $('#total_images').html(annotationSetImages.meta.total_count);
                $('#image_sampling_method').html(imageSampling);

                //get points total and calculate completeness
                points.fetch({ //assuming annotation sets have been fetched and succeeded
                    data: { limit: 100000, generic_annotation_set: annotationSets.at(0).get('id') },
                    success: function (model, response, options) {

                        //points per image set
                        var totalPoints = points.meta.total_count;
                        var totalImages = annotationSetImages.meta.total_count;
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
                    }
                });

            },
            error: function (model, response, options) {
                $('#total_images').html("?");
                $('#points_per_image').html("?");
                $('#percentage_complete').html("?");
            }

        });



    },
    events: {
        "click #configure_project_button": "doConfigure",
        "click #start_annotating_button": "doStartAnnotating"
    },
    doConfigure: function (event) {
        //redirect to configuration page
        window.location.replace("/projects/" + project.get("id") + "/configure");
    },
    doStartAnnotating: function(event) {
        window.location.replace("/projects/" + project.get("id") + "/annotate");
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
            alert('fetch failed: ' + response.status);
        }
    });
}



 