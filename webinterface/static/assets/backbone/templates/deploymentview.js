var Image = Backbone.Model.extend({
    urlRoot: "/api/dev/image/"
});

var Images = Backbone.Tastypie.Collection.extend({
    urlRoot: "/api/dev/image/",
    model: Image
});

var Deployment = Backbone.Model.extend({
    urlRoot: "/api/dev/deployment/"
});

DeploymentView = Backbone.View.extend({
    model : Deployment,
    el: $('div'),
    initialize: function () {
        this.render();
    },
    render: function () {
        var deploymentVariables = {
            "campaignlist_url": CampaignListUrl,
            "campaign_url": CampaignUrl,
            "campaign_name": deployment.get("campaign_name"),
            "deployment_name": deployment.get("short_name"),
            "start_time_stamp": deployment.get("start_time_stamp"),
            "end_time_stamp": deployment.get("end_time_stamp"),
            "mission_aim": deployment.get("mission_aim"),
            "contact_person": deployment.get("contact_person"),
            "license": deployment.get("license"),
            "descriptive_keywords": deployment.get("descriptive_keywords")
        };
        var deploymentViewTemplate = _.template($("#DeploymentViewTemplate").html(), deploymentVariables);
        // Load the compiled HTML into the Backbone "el"
        this.$el.html(deploymentViewTemplate);                              

        //instantiate openlayer map via Geoserver
        var deploymentId = deployment.get("id");
        var mapExtent = deployment.get("map_extent");

        //map is assigned to the given div
        var baseProjection = "EPSG:3857";
        var dataProjection = "EPSG:4326";
        var mapUtils = new MapUtils(baseProjection, dataProjection);
        map = new OpenLayers.Map("deployment-map", mapUtils.createMapOption());
        mapUtils.map = map; //assign map to mapUtils, so that we don't have to pass map object into function every time.       
        map.addLayer(mapUtils.createOSMLayer()); //create and add OpenStreetMaps baselayer to map

        //var loadingPanel = new OpenLayers.Control.LoadingPanel();
        //map.addControl(loadingPanel);
        //mapUtils.zoomToAustralia();

        //gsUrl, gslayerName, layerName, isBaseLayer
        var layer = mapUtils.createLayer(WMS_URL, LAYER_IMAGES, "deployment-image", false);
        map.addLayer(layer);

        //load layer and filter by deployment id
        filter_array = []
        filter_array.push(new OpenLayers.Filter.Comparison({
            type: OpenLayers.Filter.Comparison.EQUAL_TO,
            property: "deployment_id",
            value: deploymentId
        }));

        mapUtils.applyFilter(layer, filter_array);
        mapUtils.zoomToExtent(mapExtent);

        plotMeasurement("/api/dev/image/?format=json&deployment=" + deploymentId + "&output=flot&limit=10000", "#placeholder_01", "Depth (m)")
        plotMeasurement("/api/dev/measurements/?format=json&image__deployment=" + deploymentId + "&mtype=salinity&limit=10000&output=flot", "#placeholder_02", "Salinity (psu)")
        plotMeasurement("/api/dev/measurements/?format=json&image__deployment=" + deploymentId + "&mtype=temperature&limit=10000&output=flot", "#placeholder_03", "Temperature (cel)")
        loadPage();

        return this;
    }
});

DeploymentThumbanilView = Backbone.View.extend({
    el: $('div'),
    meta: {},
    initialize: function (options) {
        this.meta = options['meta']; //assign specified metadata to local var
        this.render();
    },
    render: function () {
        //get all the images to be rendered
        var imageTemplate = "";

        images.each(function (image) {
            var imageVariables = {
                "thumbnail_location": image.get('thumbnail_location'),
                "web_location": image.get('web_location')
            };
            imageTemplate += _.template($("#ImageTemplate").html(), imageVariables);
        });

        var thumbnailListVariables = { "images": imageTemplate };
        // Compile the template using underscore
        var thumbnailListTemplate = _.template($("#ThumbnailListTemplate").html(), thumbnailListVariables);
        // Load the compiled HTML into the Backbone "el"

        this.$el.html(thumbnailListTemplate);

        //Create pagination
        var options = thumbnailPaginationOptions(this.meta);
        $('#pagination').bootstrapPaginator(options);

        $(".group1").colorbox({rel:'group1', maxWidth:'95%', maxHeight:'95%'});
    }
});

var images = new Images();
var thumbnailView;

function loadPage(offset) {
    var off = {}
    if (offset) off = offset;
    // Make a call to the server to populate the collection
    images.fetch({
        data: { offset: off, deployment: catami_getIdFromUrl() },
        success: function (model, response, options) {
            thumbnailView = new DeploymentThumbanilView({
                el: $("#ThumbnailListContainer"),
                collection: images,
                meta: images.meta //read from initiaisation method's "option" variable
            });

        },
        error: function (model, response, options) {
            alert('fetch failed: ' + response.status);
        }
    });
}

function plotMeasurement(url, divId, axisLabel) {
    $.ajax({
        type: "GET",
        url: url,
        success: function (response, textStatus, jqXHR) {
            $.plot($(divId),
                    [{
                        data: response.data,
                        lines: { show: true, fill: false },
                        shadowSize: 0
                    }], {
                        yaxes: [
                            { axisLabel: axisLabel }
                        ], grid: { borderWidth: 0 }
                    }
            );
        }
    });
}

deployment = new Deployment({ id: catami_getIdFromUrl() });
deployment.fetch({
    success: function (model, response, options) {
        var deployment_view = new DeploymentView({
            el: $("#DeploymentViewContainer"),
            model : deployment
        });
    },
    error: function (model, response, options) {
        alert('fetch failed: ' + response.status);
    }
});



