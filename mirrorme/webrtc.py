import asyncio
import json
import platform
from typing import Set
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.media import MediaPlayer, MediaRelay, MediaRecorder
from aiortc.rtcrtpsender import RTCRtpSender
from .globals import photo_queue
import cv2
import av
from PIL import Image as ImagePIL, ImageTk


relay = None
webcam = None
pcs: Set[RTCPeerConnection] = set()


def create_local_tracks():
    global relay, webcam
    options = {"framerate": "30", "video_size": "640x480"}
    if relay is None:
        if platform.system() == "Darwin":
            webcam = MediaPlayer("default:none", format="avfoundation", options=options)
        elif platform.system() == "Windows":
            webcam = MediaPlayer(
                "video=Integrated Camera", format="dshow", options=options
            )
        else:
            webcam = MediaPlayer("/dev/video0", format="v4l2", options=options)
        relay = MediaRelay()

    if webcam is None:
        raise Exception("webcam is empty")

    return None, relay.subscribe(webcam.video)


def force_codec(pc, sender, forced_codec):
    kind = forced_codec.split("/")[0]
    codecs = RTCRtpSender.getCapabilities(kind).codecs
    transceiver = next(t for t in pc.getTransceivers() if t.sender == sender)
    transceiver.setCodecPreferences(
        [codec for codec in codecs if codec.mimeType == forced_codec]
    )


async def track_from_browser(track):
    global photo_queue
    while True:
        pic = await track.recv()
        img = pic.to_ndarray(format="bgr24")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)

        image_frame = ImagePIL.fromarray(img)
        photo_image = ImageTk.PhotoImage(image=image_frame)
        photo_queue.put(photo_image)


async def offer_handler(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print("Connection state is %s" % pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    @pc.on("track")
    async def on_track(track):
        print(f"kind {track.kind}")
        if track.kind == "video":
            if relay is not None:
                print("relay is ok")
                task = asyncio.ensure_future(track_from_browser(relay.subscribe(track)))
                # while True:
                #     pic = await relay.subscribe(track).recv()
                #     if isinstance(pic, av.VideoFrame) and photo_queue is not None:
                #         print(pic)

                # photo_queue.put(photo_image)

                # browser_stream = track
                # browser_stream_started = True

        @track.on("ended")
        async def on_ended():
            print(f"kind {track.kind} ended")

    # open media source
    audio, video = create_local_tracks()

    if audio:
        audio_sender = pc.addTrack(audio)
        force_codec(pc, audio_sender, "audio/opus")

    if video:
        video_sender = pc.addTrack(video)
        force_codec(pc, video_sender, "video/H264")

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
