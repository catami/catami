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

var Deployment = Backbone.Tastypie.Model.extend({
    urlRoot: "/api/dev/generic_deployment"
});

var Deployments = Backbone.Tastypie.Collection.extend({
    urlRoot: "/api/dev/generic_deployment",
    model: Deployment
});

var Image = Backbone.Tastypie.Model.extend({
    urlRoot: "/api/dev/generic_image"
});

var Images = Backbone.Tastypie.Collection.extend({
    urlRoot: "/api/dev/generic_image",
    model: Image
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

        //ge tall the images to be rendered
        var imageTemplate = "";
        //var images = project.get("objects")[0].generic_images;
        var images = project.get("generic_images");

        for(var i=0; i < images.length; i++) {
            var imageVariables = {
                "thumbnail_location": images[i].thumbnail_location
            };
            imageTemplate += _.template($("#ImageTemplate").html(), imageVariables);
        }

        //render the items to the main template
        var projectVariables = {
            "name": project.get("name"),
            "description": project.get("description"),
            "map_extent": project.get("map_extent"),
            "images": imageTemplate
        };

        // Compile the template using underscore
        var projectTemplate = _.template($("#ProjectDashboardTemplate").html(), projectVariables);

        // Load the compiled HTML into the Backbone "el"
        this.$el.html(projectTemplate);

        return this;
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

ProjectConfigureView = Backbone.View.extend({
    model: new Project(),
    el: $('div'),
    initialize: function () {
        this.render();
    },
    render: function () {
        Backbone.Validation.bind(this);
        this.model.on('validated:valid', this.valid, this);
        this.model.on('validated:invalid', this.invalid, this);

        //get all the deployments to be rendered
        var deploymentTemplate = "";

        var deployments = new Deployments();
        deployments.fetch({async:false});

        deployments.each(function (deployment) {
            var deploymentVariables = {
                "short_name": deployment.get("short_name"),
                "id": deployment.get("id")
            };

            deploymentTemplate += _.template($("#DeploymentTemplate").html(), deploymentVariables);
        });

        var projectVariables = {
            "name": project.get("name"),
            "description": project.get("description"),
            "id": project.get("id"),
            "deployments": deploymentTemplate
        };

        var projectTemplate = _.template($("#ProjectConfigureTemplate").html(), projectVariables);

        // Load the compiled HTML into the Backbone "el"
        this.$el.html(projectTemplate);

        return this;
    },
    events: {
        "click #save_button": "doSave"
    },
    doSave: function (event) {
        var configureView = this;
        var data = $('form').serializeObject();
        this.model.set(data);
        var isValid = this.model.isValid(true);
        if (isValid) {
            //assign the id of the project we are looking at
            this.model.set({id: project.get("id")});

            //get the images for the deployment we want and assign them
            var apiImages = new Images({deployment: data.deployment});
            apiImages.fetch({async:false, data: { limit : 10000 }});

            var daImages = [];
            apiImages.each(function (image) {
                daImages.push(image.get('resource_uri'));
            });

            this.model.set({generic_images: daImages});

            //save away
            var theXHR = this.model.save(null, {
                success: function (model, xhr, options) {
                    //now create an annotation set for the project
                    //var projectResourceURI  = theXHR.getResponseHeader('Location');
                    configureView.doCreateAnnotationSet(model.get("resource_uri"),  model.get("id"), data);

                    //refresh page back to this project
                    //window.location.replace("/projects/" + model.get("id"));
                },
                error: function (model, xhr, options) {
                    this.$('.alert').hide();
                    /* XXX
                       Backbone save() implementation triggers  error callback even when 201 (Created) and 202 (Accepted) status code is returned
                       http://documentcloud.github.io/backbone/#Model-save
                       Save() accepts success and error callbacks in the options hash,
                       which are passed (model, response, options) and (model, xhr, options) as arguments, respectively.
                       If a server-side validation fails, return a non-200 HTTP response code, along with an error response in text or JSON.

                    */
                    if (xhr.status == "201" || xhr.status == "202") {
                        this.$('.alert').hide();
                        this.$('.form1').hide();
                        this.$('.alert-success').fadeIn();
                    }
                    else {
                        $('#error_message1').text("Campaign creation failed!");
                        $('#error_message2').text("Error status: " + xhr.status + " (" + jQuery.parseJSON(xhr.responseText).error_message + ")");
                        this.$('.alert-error').fadeIn();
                    }
                }
            })
        }
    },
    doCreateAnnotationSet: function(projectResourceURI, projectId, formData) {
        var newAnnotationSet = new AnnotationSet({
            project: projectResourceURI,
            name: '',
            description: '',
            annotation_methodology: formData.point_sampling_methodology,
            image_sampling_methodology: formData.image_sampling_methodology,
            image_sample_size: formData.image_sample_size,
            point_sample_size: formData.point_sample_size
        });

        var theXHR = newAnnotationSet.save({}, {
            success: function (model, xhr, options) {
                //redirect to the page for the annotation
                window.location.replace("/projects/" + projectId );
            },
            error: function (model, xhr, options) {
                /* XXX
                   Backbone save() implementation triggers  error callback even when 201 (Created) and 202 (Accepted) status code is returned
                   http://documentcloud.github.io/backbone/#Model-save
                   Save() accepts success and error callbacks in the options hash,
                   which are passed (model, response, options) and (model, xhr, options) as arguments, respectively.
                   If a server-side validation fails, return a non-200 HTTP response code, along with an error response in text or JSON.

                */
                if (xhr.status == "201" || xhr.status == "202") {
                    //redirect to the page for the annotation
                    window.location.replace("/projects/" + project.get("id") + "/annotate");
                }
                else {
                    $('#error_message1').text("Project creation failed!");
                    $('#error_message2').text("Error status: " + xhr.status + " (" + jQuery.parseJSON(xhr.responseText).error_message + ")");
                    this.$('.alert-error').fadeIn();
                }
            }
        });
    },
    valid: function (view, attr) {
    },
    invalid: function (view, attr, error) {
        $('#error_message1').text("Form incomplete!");
        $('#error_message2').text("The following fields are required:");
        this.$('.alert').hide();
        this.$('.alert-error').fadeIn();
    }
});

 
