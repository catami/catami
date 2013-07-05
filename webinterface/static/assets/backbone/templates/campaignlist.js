var Campaign = Backbone.Model.extend({
    urlRoot: "/api/dev/campaign/",
});

var Campaigns = Backbone.Tastypie.Collection.extend({
    urlRoot: "/api/dev/campaign/",
    model: Campaign
});

CampaignCollectionView = Backbone.View.extend({
    el: $('div'),
    meta: {},
    initialize: function (options) {
        this.meta = options['meta']; //assign specified metadata to local var
        this.render();
    },
    render: function () {
        var campaignTemplate = "";
        // Compile the template using underscore       
        campaigns.each(function (campaign) {
            //if type is not specified, list everything, else filter by type
            var campaignVariables = {
                "short_name": campaign.get("short_name"),
                "campaign_url": CampaignListUrl + campaign.get("id") + "/",
                "start_date": campaign.get("date_start"),
                "end_date": campaign.get("date_end"),
                "deployment_count": campaign.get("deployment_count"),
                "researchers": campaign.get("associated_research_grant"),
                "publications": campaign.get("associated_publications"),
                "grant": campaign.get("associated_research_grant"),
                "description": campaign.get("description"),
            };
            campaignTemplate += _.template($("#CampaignTemplate").html(), campaignVariables);
        });

        var campaignListVariables = { "campaigns": campaignTemplate };
        // Compile the template using underscore
        var campaignListTemplate = _.template($("#CampaignListTemplate").html(), campaignListVariables);
        // Load the compiled HTML into the Backbone "el"

        this.$el.html(campaignListTemplate);

        //Create pagination
        var options = catami_generatePaginationOptions(this.meta);
        $('#pagination').bootstrapPaginator(options);

        return this;
    }
});

var campaigns = new Campaigns();
loadPage();


function loadPage(offset) {
    var off = {}
    if (offset) off = offset;
    // Make a call to the server to populate the collection 
    campaigns.fetch({
        data: { offset: off },
        success: function (model, response, options) {
            var campaign_view = new CampaignCollectionView({
                el: $("#CampaignListContainer"),
                collection: campaigns,
                meta: campaigns.meta //read from initiaisation method's "option" variable
            });
        },
        error: function (model, response, options) {
            alert('fetch failed: ' + response.status);
        }
    });
}

