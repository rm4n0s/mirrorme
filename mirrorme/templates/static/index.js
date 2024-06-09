const constraints = (window.constraints = {
  audio: false,
  video: true,
});

async function initMobileCamera(e) {
  try {
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    const video = document.getElementById('mobile-video');
    const videoTracks = stream.getVideoTracks();
    console.log('Got stream with constraints:', constraints);
    console.log(`Using video device: ${videoTracks[0].label}`);
    window.stream = stream; // make variable available to browser console
    video.srcObject = stream;
    e.target.disabled = true;
  } catch (e) {
    console.log(e);
  }
}
var pc = null;

function negotiate() {
  pc.addTransceiver("video", { direction: "recvonly" });
  return pc
    .createOffer()
    .then((offer) => {
      return pc.setLocalDescription(offer);
    })
    .then(() => {
      // wait for ICE gathering to complete
      return new Promise((resolve) => {
        if (pc.iceGatheringState === "complete") {
          resolve();
        } else {
          const checkState = () => {
            if (pc.iceGatheringState === "complete") {
              pc.removeEventListener("icegatheringstatechange", checkState);
              resolve();
            }
          };
          pc.addEventListener("icegatheringstatechange", checkState);
        }
      });
    })
    .then(() => {
      var offer = pc.localDescription;
      return fetch("/offer", {
        body: JSON.stringify({
          sdp: offer.sdp,
          type: offer.type,
        }),
        headers: {
          "Content-Type": "application/json",
        },
        method: "POST",
      });
    })
    .then((response) => {
      return response.json();
    })
    .then((answer) => {
      return pc.setRemoteDescription(answer);
    })
    .catch((e) => {
      alert(e);
    });
}

function start() {
  var config = {
    sdpSemantics: "unified-plan",
  };

  config.iceServers = [{ urls: ["stun:stun.l.google.com:19302"] }];

  pc = new RTCPeerConnection(config);

  // connect video
  pc.addEventListener("track", (evt) => {
    if (evt.track.kind == "video") {
      document.getElementById("desktop-video").srcObject = evt.streams[0];
    }
  });

  initMobileCamera()

  document.getElementById("start").style.display = "none";
  negotiate();
  document.getElementById("stop").style.display = "inline-block";
}

function stop() {
  document.getElementById("stop").style.display = "none";

  // close peer connection
  setTimeout(() => {
    pc.close();
  }, 500);
}
