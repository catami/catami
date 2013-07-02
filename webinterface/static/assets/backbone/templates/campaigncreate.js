var Campaign = Backbone.Tastypie.Model.extend({
    urlRoot: "/api/dev/campaign/",
    validation: {
        short_name: {
            required: true,
            msg: 'Please provide a campaign name'
        },
        description: {
            required: true,
            msg: 'Please provide a description for the campaign'
        },
        associated_researchers: {
            required: true,
            msg: 'Please specify associated researcher(s) for this campaign'
        },
        associated_publications: {
            required: true,
            msg: 'Please specify associated publication(s) for this campaign'
        },
        associated_research_grant: {
            required: true,
            msg: 'Please specify associated research grant(s) for this campaign'
        },
        date_start: {
            required: true,
            msg: 'Please specify a start date for campaign'
        },
        date_end: {
            required: true,
            msg: 'Please specify a end date for campaign'
        },
        contact_person: {
            required: true,
            msg: 'Please provide a contact'
        },        
    }
});

CreateCampaignView = Backbone.View.extend({
    model: new Campaign(),
    el: $('div'),
    initialize: function () {
        this.render();        
    },
    render: function () {
        var variables = {};
        // Compile the template using underscore
        var template = _.template($("#createcampaign_template").html(), variables);
        // Load the compiled HTML into the Backbone "el"
        Backbone.Validation.bind(this);
        this.model.on('validated:valid', this.valid, this);
        this.model.on('validated:invalid', this.invalid, this);
        this.$el.html(template);
    },
    events: {
        "click #create_button": "doCreate",
        "click #create_another_button" : "createNew",
        "click #done_button" : "goBack",
        "click #hide_button" : "doHide"
    },
    createNew: function (event) {
        window.location = '/staging/campaign/create';
    },
    goBack: function (event) {
        window.location = '/data/campaigns';
    },
    doHide: function (event) {
        this.$('.alert').hide();
        this.$('.alert-success').fadeIn();
        this.$('.form1').hide();
    },
    doCreate: function (event) {
        var data = $('form').catami_serializeObject();       
        this.model.set(data);       
        var isValid = this.model.isValid(true);
        if (isValid) {
            this.model.save(null, {
                success: function (model, xhr, options) {
                    this.$('.alert').hide();
                    this.$('.form1').hide();
                    this.$('.alert-success').fadeIn();
                },
                error: function (model, xhr, options) {
                    alert('xhr: ' + xhr.toSource());
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
    valid: function (view, attr) {     
    },

    invalid: function (view, attr, error) {
        $('#error_message1').text("Form incomplete!");
        $('#error_message2').text("The following fields are required:");
        this.$('.alert').hide();
        this.$('.alert-error').fadeIn();
    }

});

var createcampaign_view = new CreateCampaignView({ el: $("#createcampaign_container") });