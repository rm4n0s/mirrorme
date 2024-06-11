const constraints = (window.constraints = {
  audio: false,
  video: true,
});

async function initMobileCamera() {
  navigator.mediaDevices.getUserMedia(constraints).then(
    function (stream) {
      const video = document.getElementById("mobile-video");
      video.srcObject = stream;
      stream.getTracks().forEach(function (track) {
        pc.addTrack(track, stream);
      });
      return negotiate();
    },
    function (err) {
      alert("Could not acquire media: " + err);
    }
  );
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

  initMobileCamera();

  document.getElementById("start").style.display = "none";
  document.getElementById("stop").style.display = "inline-block";
}

function stop() {
  document.getElementById("stop").style.display = "none";
  setTimeout(() => {
    pc.close();
  }, 500);
}
