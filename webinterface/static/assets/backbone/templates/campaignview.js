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
        var campaignId = campaign.get("id");
        //var mapExtent = campaign.get("map_extent");
                
        //map is assigned to the given div        
        var baseProjection= "EPSG:3857";
        var dataProjection = "EPSG:4326";
        var mapUtils = new MapUtils(baseProjection, dataProjection);        
        map = new OpenLayers.Map("deployment-map", mapUtils.createMapOption());
        mapUtils.map = map; //assign map to mapUtils, so that we don't have to pass map object into function every time.        
        map.addLayer(mapUtils.createOSMLayer()); //create and add OpenStreetMaps baselayer to map

        var loadingPanel = new OpenLayers.Control.LoadingPanel();        
        map.addControl(loadingPanel);
        mapUtils.zoomToAustralia();

        var url = WFS_URL + "?service=WFS&version=1.1.0" +
                  "&request=GetFeature&typeName=" + LAYER_DEPLOYMENTS + "&srsName=epsg:3857" +
                  "&outputFormat=json&CQL_FILTER=campaign_id=" + campaignId;
       
        var clusterLayer = mapUtils.createClusterLayer(url);
        map.addLayer(clusterLayer);

        var selectCtrl = new OpenLayers.Control.SelectFeature(clusterLayer, {
            clickout: true,
            eventListeners: {
                featurehighlighted: clusterSelected
            }
        });
        map.addControl(selectCtrl);        
        selectCtrl.activate();
      
        //Create pagination
        var options = catami_generatePaginationOptions(this.meta);
        $('#pagination').bootstrapPaginator(options);
                
        return this;
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

function clusterSelected(event) {
    var f = event.feature;
    var count = f.cluster.length;
    var content = "<div style=\"width:250px\"><b>Deployments (" + count + ") : </b> <br>";    
    if (count > 0) {
        for (var i = 0; i < count; i++) {
            content += "&bull; <a href=\"" + DeploymentListUrl + f.cluster[i].attributes.id + "\">"
                        + f.cluster[i].attributes.short_name + "</a>" + (i < count ? "<br>" : "");
        }
        content += "</div>";
        while (map.popups.length > 0) {
            map.removePopup(map.popups[0]);
        }
        map.addPopup(new OpenLayers.Popup.FramedCloud(
            "deployment_popup", //id
            f.geometry.getBounds().getCenterLonLat(), //position on map
            null, //size of content
            content, //contentHtml
            null, //flag for close box
            true //function to call on closebox click
        ));
    }    
}

var map;
var campaign_id = catami_getIdFromUrl();
campaign = new Campaign({ id: campaign_id });
deployments = new Deployments();

campaign.fetch({
    success: function (model, response, options) {
        var campaign_view = new CampaignView({
            el: $("#CampaignViewContainer"),
            model: campaign,
            meta: deployments.meta //read from initiaisation method's "option" variable
        });
        loadPage(); //get list deployments belonging to this campaign
    },
    error: function (model, response, options) {
        alert('fetch failed: ' + response.status);
    }
});