is_recording = false;
function record_audio(recording) {
	if (is_recording) {
		return false;
	}
	is_recording = true;

	let stop_button = document.getElementById(`stop-${recording}`);
	let chunks = [];

	var handleSuccess = function(stream) {
		let mediaRecorder = new MediaRecorder(stream);
		mediaRecorder.start();
		console.log(`recording:${recording} started`);
		stop_button.onclick = function () {
			mediaRecorder.stop()
		}
		mediaRecorder.onstop = function(e) {
			console.log(`recording:${recording} stopped`);
			console.log(recording);
			console.log(chunks);
			is_recording = false;
		}
		mediaRecorder.ondataavailable = function (e) {
			chunks.push(e.data);
		}
	}

	navigator.mediaDevices.getUserMedia({audio: true, video: false})
	    .then(handleSuccess);
}


