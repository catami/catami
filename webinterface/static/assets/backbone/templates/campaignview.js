var Deployment = Backbone.Model.extend({
    urlRoot: "/api/dev/generic_deployment/",
});

var Deployments = Backbone.Tastypie.Collection.extend({
    urlRoot: "/api/dev/generic_deployment/",
    model: Deployment
});

var Campaign = Backbone.Model.extend({
    urlRoot: "/api/dev/campaign/",
});

CampaignView = Backbone.View.extend({
    model: Campaign,
    el: $('div'),
    initialize: function (options) {
        this.render();
    },
    render: function () {
        var deploymentTemplate = "";
        // Compile the template using underscore       
        var deploymentType = catami_getURLParameter("type");

        deployments.each(function (deployment) {
            var type = deployment.get("type").toUpperCase();
            //if type is not specified, list everything, else filter by type
            if (deploymentType == "null" || deploymentType.toUpperCase() == type) {
                var deploymentVariables = {
                    "type": type,
                    "type_url": "?type=" + type,
                    "short_name": deployment.get("short_name"),
                    "deployment_url": DeploymentListUrl + deployment.get("id") + "?type=" + type,
                    "start_time": deployment.get("start_time_stamp"),
                    "end_time": deployment.get("end_time_stamp"),
                    "min_depth": deployment.get("min_depth"),
                    "max_depth": deployment.get("max_depth")
                };
                deploymentTemplate += _.template($("#DeploymentTemplate").html(), deploymentVariables);
            }
        });      
        var deploymentListVariables = {
            "deployments": deploymentTemplate,
            "campaign_name": campaign.get("short_name")
        };
        var deploymentListTemplate = _.template($("#DeploymentListTemplate").html(), deploymentListVariables);
        var campaignVariables = {
            //breadcrumb
            "campaignlist_url": CampaignListUrl,
            "campaign_url": CampaignListUrl + campaign.get("id") + "/",
            "campaign_name": campaign.get("short_name"),
            //campaign details            
            "start_date": campaign.get("date_start"),
            "end_date": campaign.get("date_end"),
            "researchers": campaign.get("associated_research_grant"),
            "publications": campaign.get("associated_publications"),
            "grant": campaign.get("associated_research_grant"),
            "description": campaign.get("description"),
            "deploymentlist": deploymentListTemplate
        };
        var campaignViewTemplate = _.template($("#CampaignViewTemplate").html(), campaignVariables);
        // Load the compiled HTML into the Backbone "el"
        this.$el.html(campaignViewTemplate);

        //instantiate openlayer map via Geoserver
        var campaigntId = campaign.get("id");
        //var mapExtent = campaign.get("map_extent");
        /*
        var map = new BaseMap(WMS_URL, WMS_DEPLOYMENTS, "deployment-map");//, mapExtent);
        //load layer and filter by deployment id
        
        filter_array = []
        filter_array.push(new OpenLayers.Filter.Comparison({
            type: OpenLayers.Filter.Comparison.EQUAL_TO,
            property: "campaign_id",
            value: campaigntId
        }));
        map.updateMapUsingFilter(filter_array);
        */
        //map.zoomToExtent();
        
                
        return this;
    }
});

var campaign_id = catami_getIdFromUrl();
campaign = new Campaign({ id: campaign_id });
deployments = new Deployments();
deployments.fetch({
    //only fetch deployments belonging to this campaign
    data: { campaign: campaign_id },
    success: function (model, response, options) {
        campaign.fetch({
            success: function (model, response, options) {
                var campaign_view = new CampaignView({
                    el: $("#CampaignViewContainer"),
                    model: campaign
                });
            },
            error: function (model, response, options) {
                alert('fetch failed: ' + response.status);
            }
        });
    },
    error: function (model, response, options) {
        alert('fetch failed: ' + response.status);
    }
});

