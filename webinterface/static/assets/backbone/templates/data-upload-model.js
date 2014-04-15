var LocalDeployment = Backbone.Model.extend({
    urlRoot: "/api/dev/deployment/"
});

var ImageMetadataUpload = Backbone.Model.extend({
    urlRoot: "/api/dev/image/upload/"
});

var ImageFileUpload = Backbone.Model.extend({
    urlRoot: "/api/dev/image_upload/"
});

// the fileReadWorker is a worker script home for FileReaderSync()
// it reads FILE objects to binary arrays and passes the arrays back to this
// model for POSTing to the CATAMI API
var fileReadWorker = new Worker('/static/assets/backbone/templates/fileReadWorker.js');

var DataUploader = Backbone.Model.extend({
    defaults: {
        username: '',
        apikey: '',
        file_list: [],
        version: '',
        type: '',
        description: '',
        operator: '',
        keywords: '',
        campaign: '',
        campaign_name: '',
        campaign_number: '',
        contact_person: '',
        descriptive_keywords: '',
        end_position: '',
        end_time_stamp: '',
        id: '',
        license: '',
        map_extent: '',
        max_depth: '',
        min_depth: '',
        mission_aim: '',
        reported_operator: '',
        resource_uri: '',
        short_name: '',
        start_position: '',
        start_time_stamp: '',
        transect_shape: '',
        reported_type: '',
        estimated_depth_uncertainty: '',
        imagedate_list: [],
        latitude_list: [],
        longitude_list: [],
        depth_list: [],
        filename_list: [],
        cameraname_list: [],
        cameraangle_list: [],
        temperature_list: [],
        salinity_list: [],
        pitch_list: [],
        roll_list: [],
        yaw_list: [],
        altitude_list: [],
        depth_uncertainty_list: [],
        images_uploaded_percent: 0
    },
    initialize: function(){
        console.log("init DataUploader");
    },
    upload: function() {
		// POST deployment, checking for various possible errors
        var parent = this;

        var new_deployment = new LocalDeployment();

        GlobalEvent.trigger("start_deployment_post");

        var properties = { 'type': parent.get('type'),
                            'start_position': parent.get('start_position'),
                            'end_position': parent.get('end_position'),
                            'transect_shape': parent.get('transect_shape'),
                            'start_time_stamp': parent.get('start_time_stamp'),
                            'end_time_stamp': parent.get('end_time_stamp'),
                            'short_name': parent.get('short_name'),
                            'mission_aim': parent.get('mission_aim'),
                            'min_depth': parent.get('min_depth'),
                            'max_depth': parent.get('max_depth'),
                            'campaign':parent.get('campaign'),
                            'descriptive_keywords': parent.get('descriptive_keywords'),
                            'license': parent.get('license')
                        };

        var theXHR = new_deployment.save(properties, {
            wait: true,
            patch: true,
            headers: {"cache-control": "no-cache"},
            success: function (model, xhr, options) {
                // it worked!
                GlobalEvent.trigger("deployment_post_success");
                parent.uploadImageryData(model.get('resource_uri'));

            },
            error: function (model, xhr, options) {
                //it didn't work
                GlobalEvent.trigger("deployment_post_failed");

                $.pnotify({
                    title: theXHR.response,
                    text: 'Failed to save deployment to the server',
                    type: 'error', // success | info | error
                    hide: true,
                    icon: false,
                    history: false,
                    sticker: false
                });
            }
        });
    },
    uploadImageryData: function(deployment_uri){
        var parent = this;
        var image_data_list = [];
        var angle_value = 0; //default angle is downward

        GlobalEvent.trigger("start_imagedata_upload");

        // build list

        // note: we've got 2 file lists here "file_list" and "filename_list"
        // "file_list" is all the files dropped on the page that are images
        // "filename_list" is that list, purged of images that don't have Lat Longs
        // so "filename_list" can be shorter than "file_List"

        for (var i = 0; i < this.get("filename_list").length; i++) {

            var local_angle = '';

            local_angle = parent.get('cameraangle_list')[i];

            if (local_angle.toLowerCase() === 'Downward'.toLowerCase()){
                angle_value = 0;
            } else if (local_angle.toLowerCase() === 'Upward'.toLowerCase()){
                angle_value = 1;
            } else if (local_angle.toLowerCase() === 'Slanting/Oblique'.toLowerCase()){
                angle_value = 2;
            } else if (local_angle.toLowerCase() === 'Horizontal/Seascape'.toLowerCase()){
                angle_value = 3;
            }

            image_data_list.push({
                deployment:deployment_uri,
                image_name: parent.get('filename_list')[i],
                date_time: parent.get('imagedate_list')[i],
                position: 'SRID=4326;POINT('+parent.get('longitude_list')[i]+' '+parent.get('latitude_list')[i]+')',
                depth: parent.get('depth_list')[i],
                depth_uncertainty: parent.get('depth_uncertainty_list')[i],
                temperature: parent.get('temperature_list')[i],
                temperature_unit: 'K',
                salinity: parent.get('salinity_list')[i],
                salinity_unit: '',
                pitch: parent.get('pitch_list')[i],
                pitch_unit: '',
                roll: parent.get('roll_list')[i],
                roll_unit: '',
                yaw: parent.get('yaw_list')[i],
                yaw_unit: '',
                altitude: parent.get('altitude_list')[i],
                altitude_unit: '',
                angle: angle_value,
                name: parent.get('cameraname_list')[i]
            });
        }

        var imageMetadataUploader = new ImageMetadataUpload();

        var image_properties = {objects: image_data_list};
        
        var theXHR = imageMetadataUploader.save(image_properties, {
            patch: true,
            headers: {"cache-control": "no-cache"},
            success: function (model, xhr, options) {
                // it worked!
                GlobalEvent.trigger("end_imagedata_upload_success");
                parent.uploadImageSetFromList(xhr, image_data_list);
            },
            error: function (model, xhr, options) {
                //it didn't work
                GlobalEvent.trigger("end_imagedata_upload_failed");

                $.pnotify({
                    title: theXHR.response,
                    text: 'imageMetadataUploader failed',
                    type: 'error', // success | info | error
                    hide: true,
                    icon: false,
                    history: false,
                    sticker: false
                });
            }
        });

    },
    uploadImageSetFromList: function(image_uri_list, image_data_list){
        // image_uri_list is generated from the images.csv list. It's the list of images we want to upload
        // and the URI we need to upload to.  file_list is the list of dropped File() objects it will
        // contain files we don't want to upload...there could be non-image drops, or images with no latlongs
        //
        // So first we need to get the objects in file_list that match up with those in image_uri_list and then 
        // we can read in the images and post the image data to the CATAMI Image POST endpoint

        // fileReadWorker is defined globally, just so you know. There should only be one this worker in
        // use.

        parent = this;
        var count = 0;

        var file_list = this.get("file_list");

        var filename_array = [];
        // console.log(file_list);

        for (var i = 0; i < file_list.length; i++){
            filename_array.push(file_list[i].name);
        }
        
        fileReadWorker.onmessage = function(e) {
            //message return handler for the fileReadWorker Worker function

            if(typeof e.data === 'string' || e.data instanceof String){
                // string messages might be special. Might not.
                if (e.data === "done"){
                    // don't send any more messages
                    GlobalEvent.trigger("end_images_upload");
                }

            } else if (count < image_uri_list.length) {
                // if the message is not a string, we assume it's the image data.  Be warned if you
                // start adding messages to the worker; all messages go through a single message handler!
                //
                // send a message back to the worker to load another image

                count = count + 1;

                parent.uploadImageFromBinaryBuffer(e.data);

                parent.set("images_uploaded_percent",count/file_list.length*100);
                GlobalEvent.trigger("image_uploaded");
                fileReadWorker.postMessage('loadfile');
            } else {
                fileReadWorker.postMessage('stop');

                GlobalEvent.trigger("end_images_upload");
            }
        };

        // this just populates the worker with the file list
        for (var j = 0; j < image_uri_list.length ;j++) {
            fileReadWorker.postMessage({file: file_list[jQuery.inArray(image_uri_list[j].image_name, filename_array)],uri: image_data_list[j].deployment});
        }

        // start the file reading loop
        fileReadWorker.postMessage('loadfile');

        // GlobalEvent.trigger("end_images_upload");
    },
    uploadImageFromBinaryBuffer: function(fileObject) {
        // upload actual image data to specified 
        // worker returned objects take the form of {filedata: *binary image data*, 
        //                                           uri: image URI to upload to,
        //                                           filename: image file name with file extension

        parent = this;
        imageFileUpload = new ImageFileUpload();
        
        var temp = fileObject.result.uri.split("/");
        var deploymentIndex = temp[temp.length-2];

        //var oBlob = new Blob([fileObject.result.filedata], {type : 'image/jpeg'}); // the blob

        // params = {
        //     deployment: deploymentIndex,
        //     img: fileObject.result.filename,
        //     username:"markg",
        //     api_key:"6dae22ba490685cf1f4681a8f0a421da155d6af6",
        //     filedata: oBlob
        // };


        var formData = new FormData();
        formData.append('deployment', deploymentIndex);
        formData.append('img', fileObject.result.filename);
        formData.append('username', parent.get('username'));
        formData.append('api_key', parent.get('apikey'));
        formData.append('filedata', new Blob([fileObject.result.filedata], {type : 'image/jpeg'}));
        

        var theXHR = imageFileUpload.save(null, {
            patch: true,
            data: formData,
            contentType: false,
            processData: false,
            wait: true,
            headers: {"cache-control": "no-cache"},
            success: function (model, xhr, options) {
                // it worked!
                console.log('file uploaded',fileObject.result.filename);
                delete formData.filedata;
            },
            error: function (model, xhr, options) {
                // it didn't work
                GlobalEvent.trigger("image_upload_failed");
                console.log('file NOT uploaded',fileObject.result.filename);
                delete formData.filedata;

                // $.pnotify({
                //     title: theXHR.response,
                //     text: 'imageMetadataUploader failed',
                //     type: 'error', // success | info | error
                //     hide: true,
                //     icon: false,
                //     history: false,
                //     sticker: false
                // });
            }
        });
    },
    parseRequiredFiles: function() {
        // read and parse description.txt and imagfes.csv

        for (var i = 0; i < this.get("file_list").length; i++) {
            if (this.get("file_list")[i].name === 'description.txt') {
                this.parseDescription(this.get("file_list")[i]);
            }
            if (this.get("file_list")[i].name === 'images.csv') {
                this.parseImageList(this.get("file_list")[i]);
            }
        }
    },
    parseDescription: function (file){
        // parse the description.txt
        var parent = this;

        var reader = new FileReader();
        reader.onload = (function(theFile){
            var fileName = theFile.name;
            return function(e){

                var text = reader.result;
                var lines  = text.split("\n");
                
                for(var i = 0; i < lines.length; i++){
                    var words = lines[i].split(":");
                    if (words[0].toUpperCase() === "version".toUpperCase()){
                        parent.set("version", words[1]);
                    }
                    if (words[0].toUpperCase() === "type".toUpperCase()){
                        parent.set("type", words[1]);
                    }
                    if (words[0].toUpperCase() === "description".toUpperCase()){
                        parent.set("description", words[1]);
                    }
                    if (words[0].toUpperCase() === "operator".toUpperCase()){
                        parent.set("operator", words[1]);
                    }
                    if (words[0].toUpperCase() === "keywords".toUpperCase()){
                        parent.set("keywords", words[1]);
                    }
                }


                GlobalEvent.trigger("deployment_description_parsed");
            };
        })(file);
        reader.readAsText(file);
    },
    parseImageList: function (file){
        // parse the images.csv 
        
        var parent = this;

        var reader = new FileReader();
        reader.onload = (function(theFile){
            var fileName = theFile.name;
            return function(e){

                var text = reader.result;
                var data = $.csv.toArrays(text);

                var imagedate_temp = [];
                var latitude_temp =[];
                var longitude_temp=[];
                var depth_temp=[];
                var filename_temp=[];
                var cameraname_temp=[];
                var cameraangle_temp=[];
                var temperature_temp=[];
                var salinity_temp=[];
                var pitch_temp=[];
                var roll_temp=[];
                var yaw_temp=[];
                var altitude_temp=[];
                var depth_uncertainty_temp = [];

                for (var i=2; i < data.length; i++){
                    var data_line = data[i];

                    //if the image has no lat/longs we ignore it for upload
                    if (data_line[1] !== "None" && data_line[2] !== "None"){

                        imagedate_temp.push(data_line[0]);
                        latitude_temp.push(Number(data_line[1]));
                        longitude_temp.push(Number(data_line[2]));
                        depth_temp.push(Number(data_line[3]));
                        filename_temp.push(data_line[4]);
                        cameraname_temp.push(data_line[5]);
                        cameraangle_temp.push(data_line[6]);
                        temperature_temp.push(data_line[7]);
                        salinity_temp.push(Number(data_line[8]));
                        pitch_temp.push(Number(data_line[9]));
                        roll_temp.push(Number(data_line[10]));
                        yaw_temp.push(Number(data_line[11]));
                        altitude_temp.push(Number(data_line[12]));
                        depth_uncertainty_temp.push(Number(data_line[13]));

                    }
                }

                var image_count = imagedate_temp.length;

                parent.set("imagedate_list",imagedate_temp);
                parent.set("latitude_list",latitude_temp);
                parent.set("longitude_list",longitude_temp);
                parent.set("depth_list",depth_temp);
                parent.set("filename_list",filename_temp);
                parent.set("cameraname_list",cameraname_temp);
                parent.set("cameraangle_list",cameraangle_temp);
                parent.set("temperature_list",temperature_temp);
                parent.set("salinity_list",salinity_temp);
                parent.set("pitch_list",pitch_temp);
                parent.set("roll_list",roll_temp);
                parent.set("yaw_list",yaw_temp);
                parent.set("altitude_list",altitude_temp);
                parent.set("depth_uncertainty_list",depth_uncertainty_temp);

                imagedate_temp = '';
                latitude_temp = '';
                longitude_temp = '';
                depth_temp = '';
                filename_temp = '';
                cameraname_temp = '';
                cameraangle_temp = '';
                temperature_temp = '';
                salinity_temp = '';
                pitch_temp = '';
                roll_temp = '';
                yaw_temp = '';
                altitude_temp = '';
                depth_uncertainty_temp = '';

                parent.set("start_position","SRID=4326;POINT(" + parent.get("longitude_list")[0].toString() + " " + parent.get("latitude_list")[0].toString() + ")");
                parent.set("end_position","SRID=4326;POINT(" + parent.get('longitude_list')[image_count - 1].toString() + " " + parent.get('latitude_list')[image_count - 1].toString() + ")");
                parent.set("start_time_stamp",parent.get("imagedate_list")[0]);
                parent.set("transect_shape","SRID=4326;POLYGON(("   + Math.min.apply(Math,parent.get("longitude_list")).toString() +" "+ Math.min.apply(Math,parent.get("latitude_list")).toString() + "," +
                                                                      Math.max.apply(Math,parent.get("longitude_list")).toString() +" "+ Math.min.apply(Math,parent.get("latitude_list")).toString() + "," +
                                                                      Math.max.apply(Math,parent.get("longitude_list")).toString() +" "+ Math.max.apply(Math,parent.get("latitude_list")).toString() + "," +
                                                                      Math.min.apply(Math,parent.get("longitude_list")).toString() +" "+ Math.max.apply(Math,parent.get("latitude_list")).toString() + "," +
                                                                      Math.min.apply(Math,parent.get("longitude_list")).toString() +" "+ Math.min.apply(Math,parent.get("latitude_list")).toString() + "))");
                parent.set("end_time_stamp",parent.get("imagedate_list")[image_count - 1]);

                parent.set("min_depth",Math.min.apply(Math,parent.get("depth_list")).toString());
                parent.set("max_depth",Math.max.apply(Math,parent.get("depth_list")).toString());

                GlobalEvent.trigger("image_list_parsed");
            };
        })(file);
        reader.readAsText(file);
    },
    descriptionFileMissing: function () {
        //description.txt apparently missing, make a blank one?

    },
    imagesListFileMissing: function () {
        //images.csv is missing. One day we might make one. Today we post an error.
    }

});