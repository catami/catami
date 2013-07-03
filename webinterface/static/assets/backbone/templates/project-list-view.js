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

/*
 * Note we are using the light project resource in here for performance reasons
 *
 */
var Projects = Backbone.Tastypie.Collection.extend({
    urlRoot: "/api/dev/project_lite/",
    model: Project
});

ProjectCollectionView = Backbone.View.extend({
    el: $('div'),
    initialize: function () {
        this.render();
    },
    render: function () {

        //render each of the items to the template
        var projectTemplate = "";
        projects.each(function (project) {
            var projectVariables = {
                "name": project.get("name"),
                "owner": project.get("owner").username,
                "id": project.get("id")
            };
            projectTemplate += _.template($("#ProjectTemplate").html(), projectVariables);
        });

        //render the items to the main list template
        var projectListVariables = { "projects": projectTemplate };

        // Compile the template using underscore
        var projectListTemplate = _.template($("#ProjectListTemplate").html(), projectListVariables);

        // Load the compiled HTML into the Backbone "el"
        this.$el.html(projectListTemplate);

        return this;
    },
    events: {
        "click #create_button": "doCreate"
    },
    doCreate: function (event) {
        var projectView = this;

        var newProject = new Project({
          name: "Untitled",
          description: "",
          generic_images: []
        });

        var theXHR = newProject.save({}, {
                success: function (model, xhr, options) {

                    //get the id of the project from teh reponse headers
                    var projectResourceURI  = theXHR.getResponseHeader('Location');
                    var splitURI = projectResourceURI.split("/");
                    var projectId = splitURI[splitURI.length-2];

                    //redirect to the page for the project
                    window.location.replace("/projects/" + projectId + "/configure");
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
                        //get the id of the project from teh reponse headers
                        var projectResourceURI  = theXHR.getResponseHeader('Location');
                        var splitURI = projectResourceURI.split("/");
                        var projectId = splitURI[splitURI.length-2];

                        //redirect to the page for the project
                        window.location.replace("/projects/" + projectId + "/configure");
                    }
                    else {
                        $('#error_message1').text("Project creation failed!");
                        $('#error_message2').text("Error status: " + xhr.status + " (" + jQuery.parseJSON(xhr.responseText).error_message + ")");
                        this.$('.alert-error').fadeIn();
                    }
                }
            });
    }
});