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



 
