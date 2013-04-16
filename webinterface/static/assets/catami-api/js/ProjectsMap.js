/**
 *
 * Openlayers map for the projects page
 *
 * @param wmsUrl
 * @param wmsLayerName
 * @param divName
 * @constructor
 * @param extentUrl - this is the URL in which to query the extent of a collection
 */
function ProjectsMap(wmsUrl, wmsLayerName, divName, extentUrl) {
    this.BaseMap = BaseMap;
    this.BaseMap(wmsUrl, wmsLayerName, divName);
    this.extentUrl = extentUrl;
}

/**
 * Extend from the BaseMap
 * @type {BaseMap}
 */
ProjectsMap.prototype = new BaseMap;

/**
 *
 * Will take a collectionId and update the map
 *
 * @param collectionId
 */
ProjectsMap.prototype.updateMapForSelectedCollection = function(collectionId) {
    var filter_array = [];

    filter_array.push(new OpenLayers.Filter.Comparison({
        type: OpenLayers.Filter.Comparison.EQUAL_TO,
        property: "collection_id",
        value: collectionId
    }));

    this.updateMapUsingFilter(filter_array);
}

/**
 * Will update the bounds of a collection given it's id
 */
ProjectsMap.prototype.updateMapBoundsForCollection = function(collectionId) {
    var mapInstance = this.mapInstance;
    $.ajax({
        type: "POST",
        url: this.extentUrl,
        data: "collection_id="+collectionId,
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