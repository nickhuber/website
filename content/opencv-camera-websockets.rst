Using Python, OpenCV and websockets for camera frames
======================================================

:date: 2019-09-10
:category: Blog
:slug: python-opencv-camera-websockets
:summary: A simple python script to read and communicate camera data

For starters, I'm using a Raspberry Pi 2 with the camera module V2. For the
operating system, I am using Fedora 30.

When using the base image from Fedora, from `Fedora ARM`_ you will need to make
sure the camera kernel module is loaded. Writing a file like 

.. code-block:: bash

    [nick@camerapi ~]$ cat /etc/modules-load.d/bcm2835-v4l2.conf bcm2835-v4l2

will ensure it is loaded at boot, and you can just do ``modprobe bcm2835-v4l2`` to
load it at runtime. If you don't want to run everything as root, just make sure
you add whatever user will be accessing the camera to the ``camera`` group with
something like ``usermod -a -G video username``. After a new login session that
user should be able to access the camera.

Getting frames from the camera itself is easy enough, 

.. code-block:: python

    import cv2 camera = cv2.VideoCapture(0) ret, frame = camera.read() #
    Optionally encode the frame into a more readable format ret, encoded =
    cv2.imencode(".jpg", frame)

There are many more options available to do things like setting the frame height
and width, but I would suggest reading the `OpenCV documentation`_ for that.

For simplicity's sake, I fetch frames in their own thread. This also frees up
the main thread for managing all the web requests. This is far from efficient
but works as a starting point.

.. code-block:: python

    # -*- coding: utf-8 -*-
    import threading
    import time

    import cv2


    class Camera:
        def __init__(self):
            self.thread = None
            self.current_frame  = None
            self.last_access = None
            self.is_running: bool = False
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                raise Exception("Could not open video device")
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        def __del__(self):
            self.camera.release()

        def start(self):
            if self.thread is None:
                self.thread = threading.Thread(target=self._capture)
                self.thread.start()

        def get_frame(self):
            self.last_access = time.time()
            return self.current_frame

        def stop(self):
            self.is_running = False
            self.thread.join()
            self.thread = None

        def _capture(self):
            self.is_running = True
            self.last_access = time.time()
            while self.is_running:
                time.sleep(0.1)
                ret, frame = self.camera.read()
                if ret:
                    ret, encoded = cv2.imencode(".jpg", frame)
                    if ret:
                        self.current_frame = encoded
                    else:
                        print("Failed to encode frame")
                else:
                    print("Failed to capture frame")
            print("Reading thread stopped")
            self.thread = None
            self.is_running = False


Since I wanted to be able to see the data my camera was capturing before going
any further into image processing, I setup a simple Flask webserver and served
the frames over a socket.io connection

.. code-block:: python

    #!/usr/bin/env python3 # -*- coding: utf-8 -*- import base64

    from flask import Flask, render_template, Response from flask_socketio
    import SocketIO, emit

    from camera import Camera

    app = Flask(__name__) socketio = SocketIO(app)

    camera = Camera()


    @app.route("/") def index():
        """Video streaming home page.""" return render_template("index.html")


    @socketio.on("request-frame", namespace="/camera-feed") def
    camera_frame_requested(message):
        frame = camera.get_frame() if frame is not None:
            emit("new-frame", {
                "base64": base64.b64encode(frame).decode("ascii")
            })


    if __name__ == "__main__":
        try:
            camera.start() socketio.run(app, host="0.0.0.0", port=8080)
        except KeyboardInterrupt:
            camera.stop()

With an associated simple HTML page

.. code-block:: html

    <!doctype html> <html> <head>
        <meta charset="utf-8"> <title>Camera Live Feed</title> <link
        rel="stylesheet" href="../static/bulma.min.css"/> <link rel="stylesheet"
        href="../static/style.css"/> <script
        src="../static/socketio.js"></script> <script
        src="../static/main.js"></script>
    </head> <body>
        <div class="container"> <div class="center">
            <h1>Camera Live Feed</h1> <img id="camera-frame" width="640"
            height="480">
        </div> </div>
    </body> </html>

And finally a bit of JavaScript to tie everything together. I wanted to use pure
websockets but it seems the flask-socketio library needs the socketio javascript
library to negotiate their use or something.

.. code-block:: javascript

    document.addEventListener("DOMContentLoaded", function(event) { 
        const socket =
        io.connect(`ws://${document.domain}:${location.port}/camera-feed`);
        socket.on('new-frame', message => {
            document.getElementById('camera-frame').setAttribute(
                'src', `data:image/jpeg;base64,${message.base64}`
            );
        }); window.setInterval(() => {
            socket.emit('request-frame', {});
        }, 100);

    });

I saw many other example using a streaming mjpeg format to accomplish the same
sort of effect without any JavaScript, but was having some issues with that and
wanted an excuse to use websocekts for something for a while.

See `My Github repository`_ for the full source code of my starting project.

.. _Fedora ARM: https://fedoraproject.org/wiki/Architectures/ARM/Raspberry_Pi
.. _OpenCV documentation: https://docs.opencv.org/master/
.. _My Github repository: https://github.com/nickhuber/opencv-flask-websockets
