# Crossbar HTTP

[![PyPi version](https://img.shields.io/pypi/v/crossbarhttprequests.svg)](https://pypi.python.org/pypi/crossbarhttprequests)
[![PyPi downloads](https://img.shields.io/pypi/dm/crossbarhttprequests.svg)](https://pypi.python.org/pypi/crossbarhttprequests)
[![Codecov](https://img.shields.io/codecov/c/github/thehq/python-crossbarhttp/master.svg)](https://codecov.io/github/thehq/python-crossbarhttp)
[![PyPi license](https://img.shields.io/pypi/l/crossbarhttprequests.svg)](https://pypi.python.org/pypi/crossbarhttprequests)

Module that provides methods for accessing Crossbar.io HTTP Bridge Services using python-requests

Fork of the original package by `Eric Chapman at The HQ`_, only supporting 
Python 3+ versions using python-requests module. Which means you can pass params like proxies, auth, certificate verify etc. to the Client.
Check python-requests for extra args you can use

## Revision History
  - v0.1.3:
    - Switched to python-requests module to support more params passing to the client
  - v0.1.2:
    - Added "ClientCallRuntimeError" exception for general errors
  - v0.1.1:
    - Added class defined Exceptions for specific events
    - Added key/secret handling
  - v0.1:
    - Initial version

## Installation

    pip install crossbarhttprequests

## Usage

### Call
To call a Crossbar HTTP bridge, do the following

    client = Client("https://127.0.0.1/call", verify=False) # Extra params goes to requests.request
    result = client.call("com.example.add", 2, 3, offset=10)
    
This will call the following method

    def onJoin(self, details):
        
        def add_something(x, y, offset=0):
            print "Add was called"
            return x+y+offset

        self.register(add_something, "com.example.add")
        
### Publish
To publish to a Crossbar HTTP bridge, do the following

    client = Client("http://127.0.0.1/publish", headers={'X-Custom-Headers': 'X-Value'}) # Extra params goes to requests.request
    result = client.publish("com.example.event", event="new event")
    
The receiving subscription would look like

    def onJoin(self, details):
        
        def subscribe_something(event=None, **kwargs):
            print "Publish was called with event %s" % event

        self.subscribe(subscribe_something, "com.example.event") 

### Key/Secret
For bridge services that have a key and secret defined, simply include the key and secret in the instantiation of the
client.

    client = Client("http://127.0.0.1/publish", key="key", secret="secret")

### Exceptions
The library will throw the following exceptions.  Note that all exceptions subclass from "ClientBaseException" so
you can just catch that if you don't want the granularity.

  - ClientBadUrl - The specified URL is not a HTTP bridge service
  - ClientBadHost - The specified host name is rejecting the connection
  - ClientMissingParams - The call was missing parameters
  - ClientSignatureError - The signature did not match
  - ClientNoCalleeRegistered - Callee was not registered on the router for the specified procedure
  - ClientCallRuntimeError - Procedure triggered an exception

## Contributing
To contribute, fork the repo and submit a pull request.

## Testing
The test can be run by using Docker Compose.  Connect to a docker host and type

    %> docker-compose build
    %> docker-compose up

The Docker Compose file creates a generic router with an example service connected to it and runs the tests.
    
The service "crossbarhttp_test_1" will return a 0 value if the tests were successful and non zero otherwise.  To get the
pass/fail results from a command line, do the following

    #!/usr/bin/env bash
    
    docker-compose build
    docker-compose up
    
    exit $(docker-compose ps -q | xargs docker inspect -f '{{ .Name }} exited with status {{ .State.ExitCode }}' | grep test_1 | cut -f5 -d ' ')

This is a little hacky (and hopefully Docker will fix it) but it will do the trick for now.

##License
MIT
