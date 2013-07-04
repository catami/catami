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
        window.location.replace("/projects/create");
    }
});