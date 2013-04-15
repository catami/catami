//need so the ajax queries can make it outside the projects domain and contact geoserver
OpenLayers.ProxyHost = "/proxy/?url=";

/**
 * Used for WMS mapping purposes. Takes a WMSUrl and WMS Layer name and configures a map.
 *
 * @param wmsUrl - The URL of the Web Map Service, we are using geoserver
 * @param wmsLayerName - The name of the WMS Layer
 * @param divName - This is the name of the <div> in which the map is bound to in the page
 * @constructor
 */

function BaseMap(wmsUrl, wmsLayerName, divName) {
    //Map view code to get moved out later.
    //prep some data we need to use to display the points
    this.wmsUrl = wmsUrl;
    this.wmsLayerName = wmsLayerName;

    /* Filter based on the deployment id */

    this.filter_1_1 = new OpenLayers.Format.Filter({version: "1.1.0"});
    this.filter = new OpenLayers.Filter.Logical({
        type: OpenLayers.Filter.Logical.OR,
        filters: []
    });

    /* Setting up the projection details here, so that 4326 projected data can be displayed on top of
     * base layers that use the google projection */
    this.xml = new OpenLayers.Format.XML();
    this.geographic = new OpenLayers.Projection("EPSG:4326");
    this.mercator = new OpenLayers.Projection("EPSG:900913");
    this.world = new OpenLayers.Bounds(-180, -89, 180, 89).transform(
        this.geographic, this.mercator
    );

    //map setting based on projections
    var options = {
        projection: this.mercator,
        //displayProjection: geographic,
        units: "m",
        maxExtent: this.world,
        maxResolution: 156543.0399,
        numZoomLevels: 25
    };

    //map is assigned to the given div
    this.mapInstance = new OpenLayers.Map(divName, options);

    /*set up the open street map base layers, need to set some extra resolution information here so that
     we can zoom beyond OSM's maximum zoom level of 18*/
    var osm = new OpenLayers.Layer.OSM(null, null, {
        resolutions: [156543.03390625, 78271.516953125, 39135.7584765625,
            19567.87923828125, 9783.939619140625, 4891.9698095703125,
            2445.9849047851562, 1222.9924523925781, 611.4962261962891,
            305.74811309814453, 152.87405654907226, 76.43702827453613,
            38.218514137268066, 19.109257068634033, 9.554628534317017,
            4.777314267158508, 2.388657133579254, 1.194328566789627,
            0.5971642833948135, 0.25, 0.1, 0.05],
        serverResolutions: [156543.03390625, 78271.516953125, 39135.7584765625,
            19567.87923828125, 9783.939619140625,
            4891.9698095703125, 2445.9849047851562,
            1222.9924523925781, 611.4962261962891,
            305.74811309814453, 152.87405654907226,
            76.43702827453613, 38.218514137268066,
            19.109257068634033, 9.554628534317017,
            4.777314267158508, 2.388657133579254,
            1.194328566789627, 0.5971642833948135],
        transitionEffect: 'resize',
        isBaseLayer: true,
        minZoomLevel: 1,
        maxZoomLevel: 25,
        numZoomLevels: 25,
        sphericalMercator: true
    });
    this.mapInstance.addLayer(osm);

    //this is the layer for our points to be displayed with
    var imagePointsLayer = new OpenLayers.Layer.WMS("Images",
        this.wmsUrl,
        {layers: this.wmsLayerName, transparent: "true", format: "image/png", filter: this.xml.write(this.filter_1_1.write(this.filter))},
        {isBaseLayer: false, minZoomLevel: 1, maxZoomLevel: 25, numZoomLevels: 25}
    );
    this.mapInstance.addLayer(imagePointsLayer);

    //$('.btn-create-collection').attr('disabled', 'disabled');
    //currentSelectedDeployments = [];
    //return deploymentMap;

    var popupMapInstance = this.mapInstance;
    //popup window configuration that queries more information about a point that is clicked on
    var info = new OpenLayers.Control.WMSGetFeatureInfo({
        url: this.wmsUrl,
        title: 'Identify features by clicking',
        queryVisible: true,
        eventListeners: {
            getfeatureinfo: function (event) {
                if (event.text.search('ServiceExceptionReport') > 0) {
                    event.text = '<p>I have encountered an error looking for Catami image data,<br>please contact <a href="mailto:catami@ivec.org?subject=Catami%20Error%20Report&body=Error%20Text%0A%0A' + encodeURIComponent(event.text) + '%0A%0APlease%20enter%20any%20other%20revelant%20information."><br>Catami Support</a></p>';
                };

                //ugly hack:  if there are no img tags there are no thumbnails, so the popup would be empty.
                if (event.text.search('img') != -1) {
                    var popup = new OpenLayers.Popup.FramedCloud(
                        "Details",
                        popupMapInstance.getLonLatFromPixel(event.xy),
                        null,
                        event.text,
                        null,
                        true,
                        null
                    );
                    popupMapInstance.addPopup(popup, true);
                };
            }
        }
    });
    this.mapInstance.addControl(info);
    info.activate();

    this.zoomToInitialExtent();
}

/**
 * Called to zoom into Australia
 */
BaseMap.prototype.zoomToInitialExtent = function() {
    //TODO: work out a better way to do this. This bounds code has a bad smell.
    var boundsArr = "(108, -10, 157, -46)".replace("(", "").replace(")", "").split(",");
    var bounds = new OpenLayers.Bounds();
    bounds.extend(new OpenLayers.LonLat(boundsArr[0], boundsArr[1]));
    bounds.extend(new OpenLayers.LonLat(boundsArr[2], boundsArr[3]));
    this.mapInstance.zoomToExtent(bounds.transform(this.geographic, this.mercator));
};

/**
 * Given a filter array, this function will query the WMS and update the map
 * with the result.
 *
 * @param filterArray
 */
BaseMap.prototype.updateMapUsingFilter = function(filterArray) {
    console.log("Applying map filter");

    // the images layer may have been removed by a clear call, so re make it
    if(this.mapInstance.getLayersByName("Images")[0] == null) {
        //this is the layer for our points to be displayed with
        var imagePointsLayer = new OpenLayers.Layer.WMS("Images",
            this.wmsUrl,
            {layers: this.wmsLayerName, transparent: "true", format: "image/png", filter: this.xml.write(this.filter_1_1.write(this.filter))},
            {isBaseLayer: false, minZoomLevel: 1, maxZoomLevel: 25, numZoomLevels: 25}
        );
        this.mapInstance.addLayer(imagePointsLayer);
    }

    var filter_logic = new OpenLayers.Filter.Logical({
        type: OpenLayers.Filter.Logical.AND,
        filters: filterArray
    });
    var xml = new OpenLayers.Format.XML();
    var new_filter = xml.write(this.filter_1_1.write(filter_logic));

    var layer = this.mapInstance.getLayersByName("Images")[0];
    layer.params['FILTER'] = new_filter;
    layer.redraw();
};


/**
 * Removes all layers from the map
 */
BaseMap.prototype.clearMap = function() {
    if(this.mapInstance.getLayersByName("Images")[0] != null)
        this.mapInstance.removeLayer(this.mapInstance.getLayersByName("Images")[0]);
}



