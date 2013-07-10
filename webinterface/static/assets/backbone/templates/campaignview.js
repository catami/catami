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
    meta: {},
    initialize: function (options) {
        this.meta = options['meta']; //assign specified metadata to local var
        this.render();
    },
    render: function () {
        var deploymentTemplate = populateDeploymentList();
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
        
        var map = new BaseMap(WMS_URL, WMS_DEPLOYMENTS, "deployment-map");//, mapExtent);
        //load layer and filter by deployment id
        
        filter_array = []
        filter_array.push(new OpenLayers.Filter.Comparison({
            type: OpenLayers.Filter.Comparison.EQUAL_TO,
            property: "campaign_id",
            value: campaigntId
        }));
        map.updateMapUsingFilter(filter_array);
        
        deploymentPicker = new OpenLayers.Control.WMSGetFeatureInfo({
            url: WMS_URL,
            title: 'identify features on click',
            //layers: [map.mapInstance.imagePointsLayer],
            queryVisible: true,
            eventListeners: {
                getfeatureinfo: function (event) {
                    //remove all existing popups first before generating one.
                    while (map.mapInstance.popups.length > 0) {
                        map.mapInstance.removePopup(map.mapInstance.popups[0]);
                    }
                    if (event.features.length > 0) {
                        map.mapInstance.addPopup(new OpenLayers.Popup.FramedCloud(
                            "deployment_popup", //id
                            map.mapInstance.getLonLatFromPixel(event.xy), //position on map
                            null, //size of content
                            generatePopupContent(event), //contentHtml
                            null, //flag for close box
                            true //function to call on closebox click
                        ));
                    }
                }
            }
        });
        deploymentPicker.infoFormat = 'application/vnd.ogc.gml';
        map.mapInstance.addControl(deploymentPicker);
        deploymentPicker.activate();

        //map.zoomToExtent();
        
        //Create pagination
        var options = catami_generatePaginationOptions(this.meta);
        $('#pagination').bootstrapPaginator(options);
                
        return this;
    }
});

var campaign_id = catami_getIdFromUrl();
campaign = new Campaign({ id: campaign_id });
deployments = new Deployments();
loadPage(); //get list deployments belonging to this campaign

campaign.fetch({
    success: function (model, response, options) {
        var campaign_view = new CampaignView({
            el: $("#CampaignViewContainer"),
            model: campaign,
            meta: deployments.meta //read from initiaisation method's "option" variable
        });
    },
    error: function (model, response, options) {
        alert('fetch failed: ' + response.status);
    }
});


function populateDeploymentList() {
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
                "deployment_url": DeploymentListUrl + deployment.get("id") /*+ "?type=" + type*/,
                "start_time": deployment.get("start_time_stamp"),
                "end_time": deployment.get("end_time_stamp"),
                "min_depth": deployment.get("min_depth"),
                "max_depth": deployment.get("max_depth")
            };
            deploymentTemplate += _.template($("#DeploymentTemplate").html(), deploymentVariables);
        }
    });
    return deploymentTemplate;
}

function loadPage(offset) {
    var off = {}
    if (offset) off = offset;
    deployments.fetch({
        //only fetch deployments belonging to this campaign
        data: {
            campaign: campaign_id,
            offset: off,
            limit: 5 //limit to 5 per list due to space constraint
        },
        success: function (model, response, options) {
            if (offset) {
                var deploymentListTemplate = populateDeploymentList();
                
                $("#deploymentlist").html(deploymentListTemplate);
            }
        },
        error: function (model, response, options) {
            alert('fetch failed: ' + response.status);
        }
    });
}


function generatePopupContent(e) {  
    var count = e.features.length;
    var content = "<div style=\"width:250px\"><b>Deployments (" + count + ") : </b> <br>";
    for (var i = 0; i < count; i++) {
        content += "&bull; <a href=\"" + DeploymentListUrl + e.features[i].attributes.id + "\">"
                    + e.features[i].attributes.short_name + "</a>" + (i < count ? "<br>" : "");
    }
    content += "</div>";
    return content;
}

