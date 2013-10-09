var Deployment = Backbone.Model.extend({
    urlRoot: "/api/dev/deployment"
});

var Deployments = Backbone.Tastypie.Collection.extend({
    urlRoot: "/api/dev/deployment",
    model: Deployment
});


var ProjectImport = Backbone.Model.extend({
    urlRoot: "/api/dev/project/import_project/",
    validation: {
        name: {
            required: true,
            msg: 'Please provide a project name.'
        },
        description: {
            required: true,
            msg: 'Please provide a description for the project.'
        },
        deployment_id: {
            required: true,
            msg: 'Please select a deployment.'
        },
        image_sample_size_point: {
            required: true,
            msg: 'Please select an image sample size.',
            min: 1
        },
        image_sample_size_whole: {
            required: true,
            msg: 'Please select an image sample size.',
            min: 1
        },
        point_sampling_methodology: {
            required: true,
            msg: 'Please select a point sampling methodology.'
        },
        point_sample_size: {
            required: true,
            msg: 'Please select a point sample size.',
            min: 1
        }
    }
});

ProjectImportView = Backbone.View.extend({
    model: new ProjectImport(),
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
        deployments.fetch({ async: false, data: { limit: 1000 } });

        deployments.each(function (deployment) {
            var deploymentVariables = {
                "short_name": deployment.get("short_name"),
                "id": deployment.get("id")
            };

            deploymentTemplate += _.template($("#DeploymentTemplate").html(), deploymentVariables);
        });

        var projectVariables = {
            "deployments": deploymentTemplate
        };

        var projectTemplate = _.template($("#ProjectImportTemplate").html(), projectVariables);

        // Load the compiled HTML into the Backbone "el"
        this.$el.html(projectTemplate);
        $(".chosen-select").chosen();

        return this;
    },
    events: {
        'click #radio_point': 'pointAnnotationClicked',
        'click #radio_whole': 'wholeImageAnnotationClicked',
        "change #point_image_sampling_methodology": "pointImageSamplingSelected",
        "change #whole_image_sampling_methodology": "wholeImageSamplingSelected"
    },
    pointImageSamplingSelected: function (event) {
        var methodology = $("#point_image_sampling_methodology").val();

        //If ALL then hide the number list
        if (methodology == "3") {
            this.$('#point_number_of_images').hide();
        } else {
            this.$('#point_number_of_images').fadeIn();
        }
    },
    wholeImageSamplingSelected: function (event) {
        var methodology = $("#whole_image_sampling_methodology").val();

        //If ALL then hide the number list
        if (methodology == "3") {
            this.$('#whole_number_of_images').hide();
        } else {
            this.$('#whole_number_of_images').fadeIn();
        }
    },
    pointAnnotationClicked: function (event) {
        this.$('.wholeImage_annotation_annotation_div').hide();
        this.$('.point_annotation_div').fadeIn();
    },
    wholeImageAnnotationClicked: function (event) {
        this.$('.point_annotation_div').hide();
        this.$('.wholeImage_annotation_annotation_div').fadeIn();
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



var projectImport = new ProjectImport();
var projectImportView = new ProjectImportView({
    el: $("#ProjectImportContainer"),
    model: projectImport
});

