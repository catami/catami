//need so the ajax queries can make it outside the projects domain and contact geoserver
OpenLayers.ProxyHost = "/proxy/?url=";


/** 
 * Generic Helper functions for OpenLayers API.
 */
function MapUtils(baseProjection, dataProjection) {
    this.baseProjection = baseProjection;
    this.dataProjection = dataProjection;
}

MapUtils.prototype.baseProjection;
MapUtils.prototype.dataProjection;
MapUtils.prototype.map;

/**
 * Creates mao option which is specified during map creation
 *
 * @param baseProjection - Base layer's projection (usually the first layer added to Map object)
 * @param dataProjection - Projection of other layers, used for reprojections and other operations.
 */
MapUtils.prototype.createMapOption = function () {
    var world = new OpenLayers.Bounds(-180, -90, 180, 90).transform(
                    this.dataProjection, this.baseProjection);

    //map setting based on projections
    var options = {
        projection: this.baseProjection,
        //displayProjection: dataProjection,
        units: "m",
        maxExtent: world,
        maxResolution: 156543.0399,
        numZoomLevels: 25
    };
    return options;
}

/**
 * Creates OpenLayers Layer object
 *
 * @param gsUrl - Geoserver endpoint
 * @param gslayerName - GeoServer layer name
 * @param layerName - Name of OpenLayers Layer, used to retrieve layer object via OpenLayers API
 * @param isBaseLayer - flag specifying if layer is baselayer
 */
MapUtils.prototype.createLayer = function (gsUrl, gslayerName, layerName, isBaseLayer) {
    var myWMS = OpenLayers.Class(OpenLayers.Layer.WMS, {

        getURL: function (bounds) {
            var url = OpenLayers.Layer.WMS.prototype.getURL.call(this, bounds);
            if (OpenLayers.ProxyHost && OpenLayers.String.startsWith(url, "http")) {
                url = OpenLayers.ProxyHost + encodeURIComponent(url);
            }
            return url;
        }
    });

    var filter_1_1 = new OpenLayers.Format.Filter({ version: "1.1.0" });
    var filter = new OpenLayers.Filter.Logical({
        type: OpenLayers.Filter.Logical.OR,
        filters: []
    });
    var xml = new OpenLayers.Format.XML();

    var layer = new myWMS(layerName, gsUrl,
                    { 
                        layers: gslayerName, transparent: "true", 
                        format: "image/png", 
                        filter: xml.write(filter_1_1.write(filter)) 
                    },
                    { 
                        isBaseLayer: isBaseLayer, minZoomLevel: 1, 
                        maxZoomLevel: 25, numZoomLevels: 25 
                    });
    return layer;
}

/**
 * Called to zoom into Australia
 */
MapUtils.prototype.zoomToAustralia = function () { 

    var bounds = new OpenLayers.Bounds();
    bounds.extend(new OpenLayers.LonLat(110, -10).transform(new OpenLayers.Projection("EPSG:4326"), this.map.getProjectionObject()));
    bounds.extend(new OpenLayers.LonLat(170, -46).transform(new OpenLayers.Projection("EPSG:4326"), this.map.getProjectionObject()));

    this.map.zoomToExtent(bounds);
};


/**
* Zoom to extent
*/
MapUtils.prototype.zoomToExtent = function (extent) {
    var boundsArr = extent.replace("(", "").replace(")", "").split(",");
    
    var bounds = new OpenLayers.Bounds();
    bounds.extend(new OpenLayers.LonLat(boundsArr[0], boundsArr[1]));
    bounds.extend(new OpenLayers.LonLat(boundsArr[2], boundsArr[3]));
    var fromProj = new OpenLayers.Projection(this.dataProjection); //e.g. "EPSG:4326"
    var toProj = new OpenLayers.Projection(this.baseProjection); //e.g.  "EPSG:3857"
    this.map.zoomToExtent(bounds.transform(fromProj, toProj));
};

/**
 * Given a layer and filter array, this function will query the layer and update the map
 * with the result.  
 *
 * @param map
 * @param layer
 * @param filterArray
 */

MapUtils.prototype.applyFilter = function (layer, filterArray) {
     var filter_1_1 = new OpenLayers.Format.Filter({ version: "1.1.0" });
     var xml = new OpenLayers.Format.XML();
     var filter_logic = new OpenLayers.Filter.Logical({
         type: OpenLayers.Filter.Logical.AND,
            filters: filterArray
     });
     var new_filter = xml.write(filter_1_1.write(filter_logic));    
    
     layer.params['FILTER'] = new_filter;
     layer.redraw();

};


/**
 * Removes all non base-layers from the map
 * @param map
 */
MapUtils.prototype.clearMap = function () {
    for (var layer in this.map.layers) {
        if (!layer.isBaseLayer) this.map.removeLayer(layer);
    }
};

//Helper to create Open Steet Base layer
MapUtils.prototype.createOSMLayer = function () {
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
    return osm;
};

MapUtils.prototype.createClusterLayer = function (url) {
    // Define three colors that will be used to style the cluster features
    // depending on the number of features they contain.
    var colors = {
        low: "rgb(181, 226, 140)",
        middle: "rgb(241, 211, 87)",
        high: "rgb(253, 156, 115)"
    };

    // Define three rules to style the cluster features.
    var lowRule = new OpenLayers.Rule({
        filter: new OpenLayers.Filter.Comparison({
            type: OpenLayers.Filter.Comparison.LESS_THAN,
            property: "count",
            value: 15
        }),
        symbolizer: {
            fillColor: colors.low,
            fillOpacity: 0.9,
            strokeColor: colors.low,
            strokeOpacity: 0.5,
            strokeWidth: 12,
            pointRadius: 10,
            label: "${count}",
            labelOutlineWidth: 1,
            fontColor: "#ffffff",
            fontOpacity: 0.8,
            fontSize: "12px"
        }
    });
    var middleRule = new OpenLayers.Rule({
        filter: new OpenLayers.Filter.Comparison({
            type: OpenLayers.Filter.Comparison.BETWEEN,
            property: "count",
            lowerBoundary: 15,
            upperBoundary: 50
        }),
        symbolizer: {
            fillColor: colors.middle,
            fillOpacity: 0.9,
            strokeColor: colors.middle,
            strokeOpacity: 0.5,
            strokeWidth: 12,
            pointRadius: 15,
            label: "${count}",
            labelOutlineWidth: 1,
            fontColor: "#ffffff",
            fontOpacity: 0.8,
            fontSize: "12px"
        }
    });
    var highRule = new OpenLayers.Rule({
        filter: new OpenLayers.Filter.Comparison({
            type: OpenLayers.Filter.Comparison.GREATER_THAN,
            property: "count",
            value: 50
        }),
        symbolizer: {
            fillColor: colors.high,
            fillOpacity: 0.9,
            strokeColor: colors.high,
            strokeOpacity: 0.5,
            strokeWidth: 12,
            pointRadius: 20,
            label: "${count}",
            labelOutlineWidth: 1,
            fontColor: "#ffffff",
            fontOpacity: 0.8,
            fontSize: "12px"
        }
    });

    // Create a Style that uses the three previous rules
    var style = new OpenLayers.Style(null, {
        rules: [lowRule, middleRule, highRule]
    });

    var vector = new OpenLayers.Layer.Vector("Features", {
        protocol: new OpenLayers.Protocol.HTTP({
            url: url,
            format: new OpenLayers.Format.GeoJSON()
        }),
        renderers: ['Canvas', 'SVG'],
        strategies: [
            new OpenLayers.Strategy.Fixed(),
            new OpenLayers.Strategy.AnimatedCluster({
                distance: 5,
                animationMethod: OpenLayers.Easing.Expo.easeOut,
                animationDuration: 10
            })
        ],
        styleMap: new OpenLayers.StyleMap(style)
    });
    return vector;
};