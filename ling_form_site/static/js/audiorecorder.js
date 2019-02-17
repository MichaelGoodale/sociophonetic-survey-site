let is_recording = false;
let is_uploading = false;
let survey_name = "";

window.onload = () => {
	survey_name = document.getElementById("survey_name").getAttribute('data-survey_name');
};

let mediaRecorder = {};
navigator.mediaDevices.getUserMedia({audio: true, video: false})
    .then(stream => {
	    mediaRecorder = new MediaRecorder(stream);
	    mediaRecorder.mimeType = 'audio/wav'
    });

function upload_file(file, file_id) {
	is_uploading = true;
	const xhr = new XMLHttpRequest();
	const formData = new FormData();
	formData.append("recording", file);
	xhr.open("POST", `http://localhost:5000/upload_audio/${survey_name}/${file_id}`);
	xhr.onload = () => is_uploading = false;
	xhr.send(formData);
}

function record_audio(recording) {
	if (is_recording) {
		return false;
	}

	if (!(mediaRecorder instanceof MediaRecorder)){
		is_recording = false;
		alert("Please enable media recorder and refresh the page");
		return false;
	}

	is_recording = true;

	let button = document.getElementById(`${recording}-button`);
	button.value = "Finish recording";
	button.style.background = "red";
	let chunks = [];
	mediaRecorder.start();
	

	button.addEventListener("click", () => {
		mediaRecorder.stop();
		button.style.background = "";
		button.value = "Record";
		button.onclick = () => {
			record_audio(recording);
		}
	});

	mediaRecorder.addEventListener("stop", () => {
		console.log(`recording:${recording} stopped`);
		const buffer = new Blob(chunks, { "type" : "audio/wav" });
		upload_file(buffer, recording);
		let recorded = document.getElementById(`${recording}-finished`);
		recorded.style.display = "";
		is_recording = false;
	});

	mediaRecorder.addEventListener("dataavailable", e => {
		chunks.push(e.data);
	});
}
