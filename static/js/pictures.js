var video = document.getElementById('video');
var canvas = document.getElementById('canvas');

function start_webcam()
{
    if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia)
    {
        navigator.mediaDevices.getUserMedia({ video: true }).then(function(stream)
        {
            video.srcObject = stream;
        });
    }
}

function stop_webcam()
{
    var track = video.srcObject.getTracks()[0];
    track.stop();
}

function snap()
{
    var con = document.getElementsByTagName("canvas");
    var context = document.getElementById("canvas").getContext('2d');
    var uploa = document.getElementById('upload');
    context.drawImage(video, 0, 0, 640, 480);
    context.drawImage(uploa, 0, 0, 640, 480);
    var fin = con[2].toDataURL();
    document.getElementById('hidden_data').value = fin;
}

document.getElementById('file').onchange = function(e) 
{
    var img = new Image();
    img.onload = draw;
    img.onerror = failed;
    img.src = URL.createObjectURL(this.files[0]);
    stop_webcam;
};

function draw()
{
    var canvas = document.getElementById('upload');
    var ctx = canvas.getContext('2d');
    ctx.drawImage(this, 0,0,640,480);
}

function failed()
{
    console.error("The provided file couldn't be loaded as an Image media");
}


