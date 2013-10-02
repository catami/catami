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


var ProjectCreate = Backbone.Model.extend({
    urlRoot: "/api/dev/project/create_project/",
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

ProjectCreateView = Backbone.View.extend({
    model: new ProjectCreate(),
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
        deployments.fetch({async:false, data:{limit: 1000}});

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

        var projectTemplate = _.template($("#ProjectCreateTemplate").html(), projectVariables);

        // Load the compiled HTML into the Backbone "el"
        this.$el.html(projectTemplate);
        $(".chosen-select").chosen();
        
        return this;
    },
    events: {
        'click #radio_point': 'pointAnnotationClicked',
        'click #radio_whole': 'wholeImageAnnotationClicked',
        "click #create_button": "doCreate",
        "change #point_image_sampling_methodology": "pointImageSamplingSelected",
        "change #whole_image_sampling_methodology": "wholeImageSamplingSelected"
    },
    pointImageSamplingSelected: function(event) {
        var methodology = $("#point_image_sampling_methodology").val();

        //If ALL then hide the number list
        if(methodology == "3") {
            this.$('#point_number_of_images').hide();
        } else {
            this.$('#point_number_of_images').fadeIn();
        }
    },
    wholeImageSamplingSelected: function(event) {
        var methodology = $("#whole_image_sampling_methodology").val();

        //If ALL then hide the number list
        if(methodology == "3") {
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
    doCreate: function (event) {
        var data = $('form').serializeObject();
        //$(this).hasClass('disabled') // for disabled states
        //$(this).hasClass('active') // for active states
        //$(this).is(':disabled') // for disabled buttons only       
        if ($("#radio_point").hasClass('active')) { //if point annotation set 
            data["image_sample_size"] = $("#image_sample_size_point").val();
            data["annotation_set_type"] = 0; //refer to /projects/models.py/ class AnnotationSet / ANNOTATATION_TYPE_CHOICES  
            data["image_sampling_methodology"] = $("#point_image_sampling_methodology").val();
        }
        else { //else whole image annotation set
            data["image_sample_size"] = $("#image_sample_size_whole").val();
            data["annotation_set_type"] = 1; //refer to /projects/models.py/ class AnnotationSet / ANNOTATATION_TYPE_CHOICES  
            data["image_sampling_methodology"] = $("#whole_image_sampling_methodology").val();      
        }
        //remove fields that aren't required
        //delete data['image_sample_size_whole']; this field is used in validation, don't remove
        //delete data['image_sample_size_point']; this field is used in validation, don't remove
        delete data['whole_image_sampling_methodology'];
        delete data['point_image_sampling_methodology'];

        this.model.set(data);
        var isValid = this.model.isValid(true);

        if (isValid) {
            //show a loading symbol
            buttonLoading("create_button");

            //save away
            var theXHR = this.model.save({},{
                success: function (model, xhr, options) {
                    //get the id of the project from teh reponse headers
                    var projectResourceURI  = theXHR.getResponseHeader('Location');
                    var splitURI = projectResourceURI.split("/");
                    var projectId = splitURI[splitURI.length-2];

                    //redirect to the page for the project
                    window.location.replace("/projects/" + projectId);
                },
                error: function (model, xhr, options) {

                    buttonReset("create_button");

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
            });
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



var projectCreate = new ProjectCreate();
var projectConfigureView = new ProjectCreateView({
    el: $("#ProjectCreateContainer"),
    model: projectCreate
});

