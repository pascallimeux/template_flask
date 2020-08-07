
const videoConstraints = {
    width: { min: 1024, ideal: 1280, max: 1920 }//,
    //height: { min: 776, ideal: 720, max: 1080 }
};
const constraints = {
    audio: true,
    video: videoConstraints,
};
const picture  = document.getElementById('picture');
const context = picture.getContext('2d');

var recordButton, stopButton, recorder, liveStream, recordingLabel


window.onload = function () {
    recordButton = document.getElementById('record');
    stopButton   = document.getElementById('stop');
    snapButton   = document.getElementById('snap');
    liveVideo    = document.getElementById('live');

    navigator.mediaDevices.getUserMedia(constraints)
        .then(function (stream) {
            liveStream = stream;
            liveVideo.srcObject = stream;
            liveVideo.play();
            recordButton.disabled = false;
            recordButton.addEventListener('click', startRecording);
            stopButton.addEventListener('click', stopRecording);
            snapButton.addEventListener('click', snapPicture);
        });
    };

function startRecording() {
    recorder = new MediaRecorder(liveStream,  {
        type: 'video/mp4'
    });
    recorder.addEventListener('dataavailable', onRecordingReady);
    recordButton.disabled = true;
    stopButton.disabled = false;
    recorder.start();
}

function stopRecording() {
    recordButton.disabled = false;
    stopButton.disabled = true;
    recorder.stop();
}

function snapPicture() {
    context.drawImage(liveVideo, 0, 0, picture.width, picture.height);
    var ImageData = picture.toDataURL('Image/jpeg', 1);
    var blob = base64DateUrlToBlob(ImageData, 'image/jpeg');
    socket.emit("image-save", blob);
}


function base64DateUrlToBlob(base64DataUrl, type) {
    var bytes = window.atob(base64DataUrl.split(',')[1]);
    var ab = new ArrayBuffer(bytes.length);
    var ia = new Uint8Array(ab);
    for (var i = 0; i < bytes.length; i++) {
        ia[i] = bytes.charCodeAt(i);
    }
    return new Blob([ab], { type: type });
}
            
function onRecordingReady(e) {
    var video = document.getElementById('recording');
    var blob = e.data
    video.src = URL.createObjectURL(blob);
    socket.emit("video-save", blob);
    //video.play();
}    