// worker javascript for synchronous file reading
// this worker reads files from a FILE list sequentially.  Read file data is sent
// back to the main thread for POST, or other action.
// 

var file_array = [];
var file_loaded_array = [];

function readFilesSyncronously(file_entry) {

	var reader = new FileReaderSync();

    postMessage({
        result: {filedata: reader.readAsArrayBuffer(file_entry.file), uri: file_entry.uri, filename: file_entry.file.name}
        //result: file_entry
    });
}

function addFileToList(file) {
	file_array.push(file);
	file_loaded_array.push(0);
}

function loadNextFile(){
	var i = 0;
	var found = 0;

	while (found === 0 && i < file_array.length) {
		if(file_loaded_array[i] === 0){
			file_loaded_array[i] = 1;
			readFilesSyncronously(file_array[i]);
			found = 1;
		}
		i = i + 1;
	}

	//this will end any further processing
	if (found === 0){
		postMessage({
			result: "Nothing found"
		});
	}
}

function onError(e) {
	postMessage('FileReadWorker Error: ' + e.toString()); // Forward the error to main app.
}

self.onmessage = function(e) {
	// message handler
	var data = e.data;
	if (e.data === 'loadfile'){
		loadNextFile();
	} else if (e.data === 'stop'){
		//Stop processing. placeholder in case we want to add any logic
	} else {
		//build file list
		addFileToList(data);
	}

};