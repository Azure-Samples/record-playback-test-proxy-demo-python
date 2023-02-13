# ------------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
# ------------------------------------------------------------

from azure.core.pipeline.transport import RequestsTransport
import os, json, sys
import requests, urllib3
from urllib3.exceptions import InsecureRequestWarning
from urllib.parse import urlparse

#=============================================================================
# This is an example integration with the Azure record/playback test proxy,
# which requires a custom implementation of the http pipeline transport used
# by the Azure SDK service clients.
# This implementation assumes the test-proxy is already running.
# Your test framework should start and stop the test-proxy process as needed.
#=============================================================================

class TestProxyTransport(RequestsTransport):
    def __init__(self, transport, host, port, recording_id, mode):
        # transport is used only to POST messages to the test proxy,
        # in order to start and stop the recording or playback process.
        self.transport = transport
        # host will point to 'localhost' since the test proxy is running locally.
        self.host = host
        # port will be set to 5001 since that is the port the test proxy automatically binds to.
        self.port = port
        # recordingId will contain a unique string provided by the test proxy
        # when a recording is first started.
        self.recording_id = recording_id
        # mode defines whether the proxy should operate in 'record' or 'playback' mode.
        self.mode = mode
    
    def redirect_to_test_proxy(self, request):
        request.headers.update({"x-recording-id": self.recording_id})
        request.headers.update({"x-recording-mode": self.mode})
        base_url = urlparse(request.url)
        request.headers.update({"x-recording-upstream-base-uri": "https://{}".format(base_url.netloc)})
        proxy_url = "https://{}:{}".format(self.host,self.port)
        request.url = base_url._replace(netloc=urlparse(proxy_url).netloc).geturl()

    # Derived from RequestsTransport, TestProxyTransport provides custom 
    # implementations of the methods defined in the base class
    # described above in the HTTP Transport section of this article. These
    # custom implementations allow us to intercept and reroute app traffic sent
    # between an app and Azure to the test proxy.
    def send(self, request, **kwargs):
        self.redirect_to_test_proxy(request)
        return self.transport.send(request)

# TestProxyVariables class encapsulates variables that store values
# related to the test proxy, such as connection host (localhost),
# connection port (5001), and mode (record/playback).
class TestProxyVariables():
    def __init__(self):
        self.host = None
        self.port = None
        self.mode = None
        self.recording_path = os.path.join(os.path.split(sys.argv[0])[0],'recordings',[f for f in os.listdir('recordings') if os.path.splitext(f)[1]=='.json'][0]).replace("\\", "/")
        
    # Maintain session for POST-ing to the test proxy to start and stop recording.
    # For your test client, you can either maintain the lack of certificate validation (the test-proxy
    # is making real HTTPS calls, so if your actual api call is having cert issues, those will still surface.
    def session(self):
        urllib3.disable_warnings(InsecureRequestWarning)
        rs = requests.session()
        rs.verify = False
        return rs

# Methods to start and stop a running test proxy processing traffic between your app and Azure.
class TestProxyMethods(TestProxyVariables):
    def __init__(self, rs):
        super().__init__()
        self.rs = rs

    # StartTextProxy() will initiate a record or playback session by POST-ing a request
    # to a running instance of the test proxy. The test proxy will return a recording ID
    # value in the response header, which we pull out and save as 'x-recording-id'.
    def start_test_proxy(self):
        start_url = "https://{}:{}/{}/start".format(self.host, self.port, self.mode)
        json_payload = {"x-recording-file": self.recording_path}
        data = json.dumps(json_payload).encode("utf-8")
        response = self.rs.post(start_url, data=data)
        self.recording_id = response.headers.get('x-recording-id')

    # StopTextProxy() instructs the test proxy to stop recording or stop playback,
    # depending on the mode it is running in. The instruction to stop is made by
    # POST-ing a request to a running instance of the test proxy. We pass in the recording
    # ID and a directive to save the recording (when recording is running).
    # **Note that if you skip this step your recording WILL NOT be saved.**
    def stop_test_proxy(self):
        stop_url = "https://{}:{}/{}/stop".format(self.host, self.port, self.mode)
        headers = {"x-recording-id": self.recording_id, "x-recording-save": 'True'}
        self.rs.post(stop_url, headers=headers)