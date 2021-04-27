# RTSPeep

Tool for enumerating (and optionally, screenshotting) anonymous access to RTSP streams.

Real time streaming protocol (RTSP) is a protocol used by security cameras to send video streams. Sometimes, you don't need credentials to view the streams.

```
usage: rtspeep.py [-h] --targets TARGETS [--uris URIS] [--screenshot] [--screenshot_outputdir SCREENSHOT_OUTPUTDIR]

RTSPeep: Test and optionally screenshot anonymous access to RTSP streams

optional arguments:
  -h, --help            show this help message and exit
  --targets TARGETS     targets (format is one target per line in a plaintext file)
  --uris URIS           Path to RTSP URIs to test
  --screenshot          use the --screenshot flag to capture a picture of the anonymously accessible RTSP streams
  --screenshot_outputdir SCREENSHOT_OUTPUTDIR
                        directory to save screenshots of RTSP streams
  --try_passwords       test commonly used default passwords against targets where streams are discovered

```

## Setup 

- For screenshot capability, install OpenCV by executing the command `sudo pip install opencv-python`

## Constraints

- all testing done on Ubuntu 20.04

## Related terms
RTSP, security cameras, surveillance cameras, ONVIF
