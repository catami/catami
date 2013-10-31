// data placeholders used in the computation process
var computeData = {
    p: undefined,
    canvas: [],
    cID: undefined,
    detachedImageArray: []
};

// data placeholders for the image display
var displayData = {
    canvas: null,
    dimensions: [0, 0],
    imageDimensions: [0, 0],

    clear: function () {
        displayData.canvas.clearRect(0, 0, displayData.dimensions[0], displayData.dimensions[1]);
    }
};

/**
 * Class definition
 * @constructor
 */
function ImageSegmentation() {}

/**
 * Performs the segmentation of an image, given the image element Id
 * @param imageElementId - the html element which containts the image
 * @param numberOfCentroids - the number of centroids to build our segments from
 */
ImageSegmentation.prototype.segmentImage = function(imageElementId, numberOfCentroids) {

    //create a hidden canvas from the image
    var img = $(imageElementId)[0];
    $("#RightPane").append("<canvas style='z-index:2000;position:absolute;visibility:hidden;' width="+600+" height="+600+" id=\"canvas\"></canvas>");
    displayData.canvas = $("#canvas")[0].getContext('2d');

    //scale the image down for speed max width 600px
    var width = 600;
    var height = Math.round(img.height * (600.0 / img.width));

    displayData.imageDimensions = [width, height];
    displayData.canvas.drawImage(img, 0, 0, width, height);
    computeData.p = displayData.canvas.getImageData(0, 0, displayData.imageDimensions[0], displayData.imageDimensions[1]);
    computeData.cID = displayData.canvas.createImageData(displayData.imageDimensions[0], displayData.imageDimensions[1]);

    var kM = {

        // ----------------- space/color distance metrics --------------------------
        d0: function (p1, p2) {
            var a = p2[0] - p1[0], b = p2[1] - p1[1],
                c = p2[2] - p1[2], d = p2[3] - p1[3], e = p2[4] - p1[4];
            return (c * c + d * d + e * e);												// only color!
        },
        d1: function (p1, p2) {
            var a = p2[0] - p1[0], b = p2[1] - p1[1],
                c = p2[2] - p1[2], d = p2[3] - p1[3], e = p2[4] - p1[4];
            return ((a * a + b * b) * 0.1) + ((c * c + d * d + e * e) * 0.9);
        },
        d2: function (p1, p2) {
            var a = p2[0] - p1[0], b = p2[1] - p1[1],
                c = p2[2] - p1[2], d = p2[3] - p1[3], e = p2[4] - p1[4];
            return ((a * a + b * b) * 0.4) + ((c * c + d * d + e * e) * 0.6);
        },
        d3: function (p1, p2) {
            var a = p2[0] - p1[0], b = p2[1] - p1[1],
                c = p2[2] - p1[2], d = p2[3] - p1[3], e = p2[4] - p1[4];
            return ((a * a + b * b) * 0.8) + ((c * c + d * d + e * e) * 0.2);
        },
        d4: function (p1, p2) {
            var a = p2[0] - p1[0], b = p2[1] - p1[1],
                c = p2[2] - p1[2], d = p2[3] - p1[3], e = p2[4] - p1[4];
            return a * a + b * b;														// only 2-space
        },

        makeCentroids: function (n) {													// make starting centroids
            computeData.p = displayData.canvas.getImageData(0, 0, displayData.imageDimensions[0], displayData.imageDimensions[1]);
            var r = Math.random;
            while (n--) {
                var cx = (r() * computeData.p.width) >> 0, cy = (r() * computeData.p.height) >> 0;
                var i = 4 * (cy * computeData.p.width + cx);
                var cRGB = [    cx, cy,
                    computeData.p.data[i],
                    computeData.p.data[i + 1],
                    computeData.p.data[i + 2]];
                computeData.canvas.push(cRGB);
            }
        },

        assignToCentroids: function (dist) {
            displayData.clear();
            //displayData.canvas.fillText("Processing...", displayData.dimensions[0] >> 1, displayData.dimensions[1] >> 1);
            var i = computeData.canvas.length;
            var newCentroids = [];
            while (i--) newCentroids.push([0, 0, 0, 0, 0, 0]);
            delete i;

            var n = computeData.p.width * computeData.p.height;
            while (n--) {
                var mind = Number.POSITIVE_INFINITY,
                    minc = -1,
                    m = computeData.canvas.length;
                var px = n % computeData.p.width;					// data pixel (x,y)
                var py = (n - px) / computeData.p.width;
                var n4 = n * 4;

                while (m--) {
                    var cx = computeData.canvas[m][0];
                    var cy = computeData.canvas[m][1];
                    var im = [px, py,
                        computeData.p.data[n4], computeData.p.data[n4 + 1], computeData.p.data[n4 + 2]];
                    var cn = [cx, cy,
                        computeData.canvas[m][2], computeData.canvas[m][3], computeData.canvas[m][4]];
                    var d = dist(im, cn);
                    if (mind > d) {
                        mind = d;
                        minc = m;
                    }
                }

                newCentroids[minc][0] += px;
                newCentroids[minc][1] += py;
                newCentroids[minc][2] += computeData.p.data[n4];
                newCentroids[minc][3] += computeData.p.data[n4 + 1];
                newCentroids[minc][4] += computeData.p.data[n4 + 2];
                newCentroids[minc][5]++;

                computeData.cID.data[n4] = computeData.canvas[minc][2];
                computeData.cID.data[n4 + 1] = computeData.canvas[minc][3];
                computeData.cID.data[n4 + 2] = computeData.canvas[minc][4];
                computeData.cID.data[n4 + 3] = 255;

            }
            m = computeData.canvas.length;
            while (m--) {
                if (newCentroids[m][5] != 0) {
                    computeData.canvas[m][0] = newCentroids[m][0] / newCentroids[m][5];
                    computeData.canvas[m][1] = newCentroids[m][1] / newCentroids[m][5];

                    computeData.canvas[m][2] = newCentroids[m][2] / newCentroids[m][5];
                    computeData.canvas[m][3] = newCentroids[m][3] / newCentroids[m][5];
                    computeData.canvas[m][4] = newCentroids[m][4] / newCentroids[m][5];
                }
            }
            displayData.clear();
            displayData.canvas.putImageData(computeData.cID, 0, 0);

            //placeholder for the image contents - for faster pixel access
            computeData.detachedImageArray = displayData.canvas.getImageData(0, 0, computeData.p.width, computeData.p.height).data;
        }
    };

    kM.makeCentroids(numberOfCentroids);
    kM.assignToCentroids(kM.d0);
}


/**
 * For a given xy location in the image, return the colour
 *
 * @param x value in percentage
 * @param y value in percentage
 */
ImageSegmentation.prototype.getPointColour = function(x, y) {

    //TODO: just check the segmentation has been done

    //translate the xy percentage points into a pixel location based on the image size
    var width = computeData.p.width;
    var height = computeData.p.height;

    var xPixel = Math.round(x * width);
    var yPixel = Math.round(y * height);

    //return the colour pixel
    //var colour = displayData.canvas.getImageData(xPixel, yPixel, 1, 1).data;
    //colour = rgbToHex(colour[0], colour[1], colour[2]);

    //get the image data
    var imageData = computeData.detachedImageArray;

    //locate the index of the pixel we want to find the colour for
    var index = (xPixel + yPixel * width) * 4;

    //the colour is made of RGBA values [R,G,B,A]
    var colour = [imageData[index+0], imageData[index+1], imageData[index+2], imageData[index+3]];

    //send the colour back
    return colour;
}
