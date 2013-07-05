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
    url: function() {
        var origUrl = Backbone.Model.prototype.url.call(this);
        return origUrl + (origUrl.charAt(origUrl.length - 1) == '/' ? '' : '/');
    },
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

        var projectVariables = {
            "name": project.get("name"),
            "description": project.get("description"),
            "id": project.get("id")
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

            //need to specify the properties to patch
            var properties = { 'name': data.name, 'description': data.description };

            //show a loading symbol
            buttonLoading("save_button");

            //save away
            var theXHR = this.model.save(properties, {
                patch: true,
                success: function (model, xhr, options) {
                    //refresh page back to this project
                    window.location.replace("/projects/" + model.get("id"));
                },
                error: function (model, xhr, options) {
                    buttonReset("save_button");

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
                        $('#error_message1').text("Project creation failed!");
                        $('#error_message2').text("Error message: " + jQuery.parseJSON(theXHR.responseText).error_message );
                        this.$('.alert-error').fadeIn();
                    }
                }
            })
        }
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