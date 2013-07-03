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