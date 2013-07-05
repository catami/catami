var Deployment = Backbone.Model.extend({
    urlRoot: "/api/dev/generic_deployment/",
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
            "deployment_name": deployment.get("short_name")            
        };
        var deploymentViewTemplate = _.template($("#DeploymentViewTemplate").html(), deploymentVariables);
        // Load the compiled HTML into the Backbone "el"
        this.$el.html(deploymentViewTemplate);                              

        //instantiate openlayer map via Geoserver
        var deploymentId = deployment.get("id");
        var mapExtent = deployment.get("map_extent");
        var map = new BaseMap(WMS_URL, WMS_LAYER_NAME, "deployment-map", mapExtent);
        //load layer and filter by deployment id
        filter_array = []
        filter_array.push(new OpenLayers.Filter.Comparison({
            type: OpenLayers.Filter.Comparison.EQUAL_TO,
            property: "deployment_id",
            value: deploymentId
        }));
        map.updateMapUsingFilter(filter_array);
        map.zoomToExtent();

        plotMeasurement("/api/dev/generic_image/?format=json&deployment=" + deploymentId + "&output=flot&limit=10000", "#placeholder_01", "Depth (m)")
        plotMeasurement("/api/dev/measurements/?format=json&image__deployment=" + deploymentId + "&mtype=salinity&limit=10000&output=flot", "#placeholder_02", "Salinity (psu)")
        plotMeasurement("/api/dev/measurements/?format=json&image__deployment=" + deploymentId + "&mtype=temperature&limit=10000&output=flot", "#placeholder_03", "Temperature (cel)")
           
        return this;
    }
});

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