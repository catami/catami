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
                "researchers": campaign.get("associated_researchers"),
                "publications": campaign.get("associated_publications"),
                "grant": campaign.get("associated_research_grant"),
                "description": campaign.get("description")
            };
            campaignTemplate += _.template($("#CampaignTemplate").html(), campaignVariables);
        });

        var campaignListVariables = { "campaigns": campaignTemplate };
        // Compile the template using underscore
        var campaignListTemplate = _.template($("#CampaignListTemplate").html(), campaignListVariables);
        // Load the compiled HTML into the Backbone "el"

        this.$el.html(campaignListTemplate);

        //map is assigned to the given div        
        var baseProjection = "EPSG:3857";
        var dataProjection = "EPSG:4326";
        var mapUtils = new MapUtils(baseProjection, dataProjection);        
        map = new OpenLayers.Map("campaign-map", mapUtils.createMapOption());
        mapUtils.map = map; //assign map to mapUtils, so that we don't have to pass map object into function every time.            
        map.addLayer(mapUtils.createOSMLayer()); //create and add OpenStreetMaps baselayer to map

        var loadingPanel = new OpenLayers.Control.LoadingPanel();
        map.addControl(loadingPanel);
        mapUtils.zoomToAustralia();

        //gsUrl, gslayerName, layerName, isBaseLayer
        var layer = mapUtils.createLayer(WMS_URL, LAYER_CAMPAIGNS, "campaign-list", false);
        map.addLayer(layer);
        mapUtils.applyFilter(layer, []);
        
        campaignPicker = new OpenLayers.Control.GetFeature({
            protocol: OpenLayers.Protocol.WFS.fromWMSLayer(layer),
            box: false,
            clickTolerance: 10,
            title: 'identify features on click',
            queryVisible: true
        });
        campaignPicker.infoFormat = 'application/vnd.ogc.gml';
        campaignPicker.events.register("featureselected", this, function (e) {
            while (map.popups.length > 0) {
                map.removePopup(map.popups[0]);
            }
            map.addPopup(new OpenLayers.Popup.FramedCloud(
                                        "campaign_popup", //id
                                        e.feature.geometry.getBounds().getCenterLonLat(), //position on map
                                        null, //size of content
                                        generatePopupContent(e), //contentHtml
                                        null, //flag for close box
                                        true //function to call on closebox click
                                    ));
        });
        map.addControl(campaignPicker);        
        campaignPicker.activate();

        //Create pagination
        var options = catami_generatePaginationOptions(this.meta);
        $('#pagination').bootstrapPaginator(options);

        //shrink the table text
        $('td').truncate({
            length: 20,
            minTrail: 10,
            moreText: '',
            lessText: ''
        });

        return this;
    }
});

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

function generatePopupContent(e) {   
    var content = "<div style=\"width:250px\"><b>Campaign: </b> <br>";
    content += "<a href=\"" + CampaignListUrl + e.feature.attributes.campaign_id + "\">"
                + e.feature.attributes.short_name + "</a>";
    content += "</div>";
    return content;
}

var campaigns = new Campaigns();
loadPage();