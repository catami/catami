/**
 *
 * Openlayers map for the explore page
 *
 * @param wmsUrl
 * @param wmsLayerName
 * @param divName
 * @constructor
 */
function ExploreMap(wmsUrl, wmsLayerName, divName) {
    this.BaseMap = BaseMap;
    this.BaseMap(wmsUrl, wmsLayerName, divName);
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

ExploreMap.prototype.updateMapForSelectedDeployments = function(deployment_ids) {
    var filter_array = [];

    for (var i = 0; i < deployment_ids.length; i++) {
        filter_array.push(new OpenLayers.Filter.Comparison({
            type: OpenLayers.Filter.Comparison.EQUAL_TO,
            property: "deployment_id",
            value: deployment_ids[i]
        }));
    }

    this.updateMapUsingFilter(filter_array);
}

