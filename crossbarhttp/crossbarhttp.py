import json
import hmac
import hashlib
import base64
import datetime
from random import randint
from urllib.parse import urlencode

import requests
from requests_futures.sessions import FuturesSession

class ClientBaseException(Exception):
    """
    Catch all Exception for this class
    """
    pass


class ClientNoCalleeRegistered(ClientBaseException):
    """
    Exception thrown when no callee was registered
    """
    pass


class ClientBadUrl(ClientBaseException):
    """
    Exception thrown when the URL is invalid
    """
    pass


class ClientBadHost(ClientBaseException):
    """
    Exception thrown when the host name is invalid
    """
    pass

class ClientMissingParams(ClientBaseException):
    """
    Exception thrown when the request is missing params
    """
    pass

class ClientSignatureError(ClientBaseException):
    """
    Exception thrown when the signature check fails (if server has "key" and "secret" set)
    """
    pass

class ClientCallRuntimeError(ClientBaseException):
    """
    Exception thrown when a call generated an exception
    """
    pass


class Client(object):

    def __init__(self, url, key=None, secret=None, verbose=False, do_async=False, max_workers=8, session=None, response_hook=None, **kwargs):
        """
        Creates a client to connect to the HTTP bridge services
        :param url: The URL to connect to to access the Crossbar
        :param do_async: Run request in async mode
        :param key: The key for the API calls
        :param secret: The secret for the API calls
        :param verbose: True if you want debug messages printed
        :param kwargs: Extra kwargs passed to requests.request e.g proxies, auth, verify etc.
        :return: Nothing
        """
        assert url is not None

        self.url = url
        self.do_async = do_async
        self.key = key
        self.secret = secret
        self.verbose = verbose
        self.sequence = 1
        self.kwargs = kwargs
        if self.do_async is True:
            self.session = FuturesSession(max_workers=max_workers, session=session)
            self.session.hooks['response'] = response_hook

    def get_url(self, ext_url):
        url = self.url
        if ext_url not in self.url:
            url = '{}{}'.format(self.url, ext_url)
        return url

    def publish(self, topic, *args, **kwargs):
        """
        Publishes the request to the bridge service
        :param topic: The topic to publish to
        :param args: The arguments
        :param kwargs: The key/word arguments
        :return: The ID of the publish
        """
        assert topic is not None
        ext_url = kwargs.pop('transport_path', 'publish')
        response_hook = kwargs.pop('response_hook', None)
        params = {
            "topic": topic,
            "args": args,
            "kwargs": kwargs
        }
        response = self._make_api_call("POST", self.get_url(ext_url), json_params=params, response_hook=response_hook)
        if self.do_async is True:
            return response
        return response["id"]

    def call(self, procedure, *args, **kwargs):
        """
        Calls a procedure from the bridge service
        :param topic: The topic to publish to
        :param args: The arguments
        :param kwargs: The key/word arguments
        :return: The response from calling the procedure
        """
        assert procedure is not None
        ext_url = kwargs.pop('transport_path', 'call')
        response_hook = kwargs.pop('response_hook', None)
        params = {
            "procedure": procedure,
            "args": args,
            "kwargs": kwargs
        }

        response = self._make_api_call("POST", self.get_url(ext_url), json_params=params, response_hook=response_hook)
        if self.do_async is True:
            return response
        value = None
        if "args" in response and len(response["args"]) > 0:
            value = response["args"][0]

        if "error" in response:
            error = response["error"]
            if "wamp.error.no_such_procedure" in error:
                raise ClientNoCalleeRegistered(value)
            else:
                raise ClientCallRuntimeError(value)

        return value

    def _compute_signature(self, body):
        """
        Computes the signature.

        Described at:
        http://crossbar.io/docs/HTTP-Bridge-Services-Caller/

        Reference code is at:
        https://github.com/crossbario/crossbar/blob/master/crossbar/adapter/rest/common.py

        :return: (signature, none, timestamp)
        """

        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        nonce = randint(0, 2**53)

        # Compute signature: HMAC[SHA256]_{secret} (key | timestamp | seq | nonce | body) => signature
        hm = hmac.new(self.secret, None, hashlib.sha256)
        hm.update(self.key)
        hm.update(timestamp)
        hm.update(str(self.sequence))
        hm.update(str(nonce))
        hm.update(body)
        signature = base64.urlsafe_b64encode(hm.digest())

        return signature, nonce, timestamp

    def _make_api_call(self, method, url, json_params=None, response_hook=None):
        """
        Performs the REST API Call
        :param method: HTTP Method
        :param url:  The URL
        :param json_params: The parameters intended to be JSON serialized
        :return:
        """
        if self.verbose is True:
            print ("\ncrossbarhttp: Request: %s %s" % (method, url))

        if json_params is not None and self.verbose is True:
            print ("crossbarhttp: Params: " + json.dumps(json_params))

        if self.key is not None and self.secret is not None and json_params is not None:
            signature, nonce, timestamp = self._compute_signature(json.dumps(json_params))
            params = urlencode({
                "timestamp": timestamp,
                "seq": str(self.sequence),
                "nonce": nonce,
                "signature": signature,
                "key": self.key
            })
            if self.verbose is True:
                print ("crossbarhttp: Signature Params: " + params)
            url += "?" + params

        # TODO: I can't figure out what this is.  Guessing it is a number you increment on every call
        self.sequence += 1

        try:
            if self.do_async is True:
                return self.session.request(method, url=url, json=json_params, hooks={'response': response_hook}, **self.kwargs)
            response = requests.request(method, url=url, json=json_params, **self.kwargs)
            if response.status_code == 200:
                data = response.json()
                if self.verbose is True:
                    print("crossbarhttp: Response: " + str(data))
                return data
            elif response.status_code == 400:
                raise ClientMissingParams(str(response.text))
            elif response.status_code == 401:
                raise ClientSignatureError(str(response.text))
            else:
                raise ClientBadUrl(str(response.text))
        except requests.exceptions.RequestException as e:
            raise ClientBadHost(str(e))
