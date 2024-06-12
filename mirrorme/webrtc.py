import asyncio
import json
from typing import Set
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.media import MediaPlayer, MediaRelay, MediaRecorder
from aiortc.rtcrtpsender import RTCRtpSender
from .globals import photo_queue
import cv2
from PIL import Image as ImagePIL, ImageTk


class WebRTC:
    relay = None
    webcam = None

    def __init__(self, video_dev: str):
        self.video_dev = video_dev
        self.pcs: Set[RTCPeerConnection] = set()

    def create_local_tracks(self):
        options = {"framerate": "30", "video_size": "640x480"}
        self.webcam = MediaPlayer(self.video_dev, format="v4l2", options=options)
        self.relay = MediaRelay()
        return self.relay.subscribe(self.webcam.video)

    def force_codec(self, pc, sender, forced_codec):
        kind = forced_codec.split("/")[0]
        codecs = RTCRtpSender.getCapabilities(kind).codecs
        transceiver = next(t for t in pc.getTransceivers() if t.sender == sender)
        transceiver.setCodecPreferences(
            [codec for codec in codecs if codec.mimeType == forced_codec]
        )

    async def track_from_browser(self, track):
        global photo_queue
        while True:
            pic = await track.recv()
            img = pic.to_ndarray(format="bgr24")
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)

            image_frame = ImagePIL.fromarray(img)
            photo_image = ImageTk.PhotoImage(image=image_frame)
            photo_queue.put(photo_image)

    async def offer_handler(self, request):
        params = await request.json()
        offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
        pc = RTCPeerConnection()
        self.pcs.add(pc)

        @pc.on("connectionstatechange")
        async def on_connectionstatechange():
            print("Connection state is %s" % pc.connectionState)
            if pc.connectionState == "failed":
                await pc.close()
                self.pcs.discard(pc)

        @pc.on("track")
        async def on_track(track):
            print(f"kind {track.kind}")
            if track.kind == "video":
                if self.relay is not None:
                    print("relay is ok")
                    task = asyncio.ensure_future(
                        self.track_from_browser(self.relay.subscribe(track))
                    )

            @track.on("ended")
            async def on_ended():
                print(f"kind {track.kind} ended")

        # open media source
        video = self.create_local_tracks()

        if video:
            video_sender = pc.addTrack(video)
            self.force_codec(pc, video_sender, "video/H264")

        await pc.setRemoteDescription(offer)
        answer = await pc.createAnswer()
        if answer is None:
            raise Exception("answer is empty")

        await pc.setLocalDescription(answer)

        return web.Response(
            content_type="application/json",
            text=json.dumps(
                {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
            ),
        )
