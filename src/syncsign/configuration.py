# -*- coding: utf-8 -*-

from copy import deepcopy
from syncsign.api_helper import APIHelper
from syncsign.http.requests_client import RequestsClient


class Configuration(object):
    """A class used for configuring the SDK by a user.
    """

    @property
    def http_client(self):
        return self._http_client

    @property
    def timeout(self):
        return self._timeout

    @property
    def max_retries(self):
        return self._max_retries

    @property
    def backoff_factor(self):
        return self._backoff_factor

    @property
    def environment(self):
        return self._environment

    @property
    def custom_url(self):
        return self._custom_url

    @property
    def api_version(self):
        return self._api_version

    @property
    def api_key(self):
        return self._api_key

    @property
    def access_token(self):
        return self._access_token

    @property
    def additional_headers(self):
        return deepcopy(self._additional_headers)

    def __init__(self, timeout=60, max_retries=3, backoff_factor=0,
                 environment='production',
                 custom_url='https://api.sync-sign.com',
                 api_version="v2",
                 api_key='',
                 access_token='',
                 additional_headers={}):
        # The value to use for connection timeout
        self._timeout = timeout

        # The number of times to retry an endpoint call if it fails
        self._max_retries = max_retries

        # A backoff factor to apply between attempts after the second try.
        # urllib3 will sleep for:
        # `{backoff factor} * (2 ** ({number of total retries} - 1))`
        self._backoff_factor = backoff_factor

        # Current API environment
        self._environment = environment

        # Sets the base URL requests are made to. Defaults to `https://api.sync-sign.com`
        self._custom_url = custom_url

        # SyncSign Connect API versions
        self._api_version = api_version

        if access_token:
            # The OAuth 2.0 Access Token to use for API requests.
            self._access_token = access_token
            self._api_key = ''
        else:
            # Use simple API KEY instead
            self._api_key = api_key
            self._access_token = ''

        # Additional headers to add to each API request
        self._additional_headers = deepcopy(additional_headers)

        # The Http Client to use for making requests.
        self._http_client = self.create_http_client()

    def create_http_client(self):
        return RequestsClient(timeout=self.timeout,
                              max_retries=self.max_retries,
                              backoff_factor=self.backoff_factor)

    # All the environments the SDK can run in
    environments = {
        'production': {
            'default': 'https://api.sync-sign.com',
            'simple': 'https://api.sync-sign.com/{api_version}/key/{api_key}'
        },
        'sandbox': {
            'default': 'https://api.sync-sign.com',
            'simple': 'https://api.sync-sign.com/{api_version}/key/{api_key}'
        },
        'custom': {
            'default': '{custom_url}',
            'simple': '{custom_url}/{api_version}/key/{api_key}'
        }
    }

    def get_base_uri(self):
        """Generates the appropriate base URI for the environment and the
        server.

        Args:
            server (Configuration.Server): The server enum for which the base
            URI is required.

        Returns:
            String: The base URI.

        """
        parameters = {
            "custom_url": {'value': self.custom_url, 'encode': False},
        }

        if self.access_token:
            server = 'default'
        else:
            server = 'simple'
            parameters['api_version'] = {'value': self.api_version, 'encode': False}
            parameters['api_key'] = {'value': self.api_key, 'encode': False}
        return APIHelper.append_url_with_template_parameters(
            self.environments[self.environment][server], parameters
        )
