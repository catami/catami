/**
 *
 * Openlayers map for the explore page
 *
 * @param wmsUrl
 * @param wmsLayerName
 * @param divName
 * @constructor
 */
function ExploreMap(wmsUrl, wmsLayerName, divName, extentUrl) {
    this.BaseMap = BaseMap;
    this.BaseMap(wmsUrl, wmsLayerName, divName);
    this.extentUrl = extentUrl;
}

ExploreMap.prototype = new BaseMap;

/**
 *
 * Used for constructing the filter in which to run on the WMS
 *
 * @param minDepth
 * @param maxDepth
 * @param minAltitude
 * @param maxAltitude
 * @param minTemperature
 * @param maxTemperature
 * @param minSalinity
 * @param maxSalinity
 * @returns {Array}
 */
ExploreMap.prototype.createExploreFilterArray = function(minDepth,
                                                      maxDepth,
                                                      minAltitude,
                                                      maxAltitude,
                                                      minTemperature,
                                                      maxTemperature,
                                                      minSalinity,
                                                      maxSalinity,
                                                      deploymentIds) {

    var filter = [
        new OpenLayers.Filter.Comparison({
            type: OpenLayers.Filter.Comparison.BETWEEN,
            property: "depth",
            lowerBoundary: minDepth,
            upperBoundary: maxDepth
        }),
        new OpenLayers.Filter.Comparison({
            type: OpenLayers.Filter.Comparison.BETWEEN,
            property: "altitude",
            lowerBoundary: minAltitude,
            upperBoundary: maxAltitude
        }),
        new OpenLayers.Filter.Comparison({
            type: OpenLayers.Filter.Comparison.BETWEEN,
            property: "temperature",
            lowerBoundary: minTemperature,
            upperBoundary: maxTemperature
        }),
        new OpenLayers.Filter.Comparison({
            type: OpenLayers.Filter.Comparison.BETWEEN,
            property: "salinity",
            lowerBoundary: minSalinity,
            upperBoundary: maxSalinity
        })
    ];

    var deploymentIdFilter = [];
    for (var i = 0; i < deploymentIds.length; i++) {
        deploymentIdFilter.push(new OpenLayers.Filter.Comparison({
            type: OpenLayers.Filter.Comparison.EQUAL_TO,
            property: "deployment_id",
            value: deploymentIds[i]
        }));
    }

    deploymentIdFilter = new OpenLayers.Filter.Logical({
        type: OpenLayers.Filter.Logical.OR,
        filters: deploymentIdFilter
    });

    filter.push(deploymentIdFilter);

    return filter;
}

ExploreMap.prototype.updateMapBoundsForDeployments = function(deploymentIds) {
    var mapInstance = this.mapInstance;
    $.ajax({
        type: "POST",
        url: this.extentUrl,
        data: "deployment_ids=" + currentSelectedDeployments,
        success: function (response, textStatus, jqXHR) {
            var boundsArr = response.extent.replace("(", "").replace(")", "").split(",");
            var bounds = new OpenLayers.Bounds();
            bounds.extend(new OpenLayers.LonLat(boundsArr[0], boundsArr[1]));
            bounds.extend(new OpenLayers.LonLat(boundsArr[2], boundsArr[3]));
            var geographic = new OpenLayers.Projection("EPSG:4326");
            var mercator = new OpenLayers.Projection("EPSG:900913");
            mapInstance.zoomToExtent(bounds.transform(geographic, mercator));
        }
    });
}


