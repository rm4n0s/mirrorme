# mirrorme

This project is a desktop application to be able to look at your scalp (or other body parts) from your laptop using your mobile phone's camera or vice versa. <br/>
The desktop application will create a web server so any device with a browser and a camera can visit it and create a WebRTC connection between them. <br/>
However, this application is created to learn more about python, webrtc and tkinter, for that reason, it is missing features, and works only on linux. <br/>

## Install
Clone the repo and install dependencies
```bash
git clone https://github.com/rm4n0s/mirrorme
cd mirrorme
poetry install
```

## Run

Run the application
```bash
poetry run mirrorme
```

On the initialization select the network interface of your LAN for the connection between your laptop and mobile phone.<br/>
![](https://github.com/rm4n0s/mirrorme/blob/main/images/initialization.png)

After pressing start, you will see a link and QR Code.<br/>
![](https://github.com/rm4n0s/mirrorme/blob/main/images/qr_code.png)

Look at the QR code from your mobile's camera to redirect to the browser and visit the link.<br/>
![](https://github.com/rm4n0s/mirrorme/blob/main/images/scan_qrcode_from_mobile.png)

From the browser you will see a security alert because the SSL is created and self-signed from the desktop application. <br/>
Press "visit the page" or "accept the risk and continue" <br/>
![](https://github.com/rm4n0s/mirrorme/blob/main/images/pass_security_alert.png)

When openning the web page, you will see a button "start" that will open your cameras to your screens from both laptop and mobile phone. <br/>
![](https://github.com/rm4n0s/mirrorme/blob/main/images/press_start.png)

After pressing "start" you will see your mobile's camera on the desktop application and your laptop's camera on the browser <br/>

To close the connection exit the application by pressing "Quit" button on the desktop application. <br/>
