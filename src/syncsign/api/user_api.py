# -*- coding: utf-8 -*-

from syncsign.api_helper import APIHelper
from syncsign.http.api_response import ApiResponse
from syncsign.api.base_api import BaseApi
from syncsign.http.auth.o_auth_2 import OAuth2


class UserApi(BaseApi):

    """A Controller to access Endpoints in the SyncSign API."""

    def __init__(self, config, call_back=None):
        super(UserApi, self).__init__(config, call_back)

    def info(self):
        """Does a GET request to /

        Returns `User` information for a given access token.
        If you don't know a `User` ID, you can use this endpoint to
        retrieve the User ID for an access token.

        Args:
            None

        Returns:
            ApiResponse: An object with the response value as well as other
                useful information such as status codes and headers. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        # Prepare query URL
        _url_path = '/'
        _query_builder = self.config.get_base_uri()
        _query_builder += _url_path
        _query_parameters = {
        }
        _query_builder = APIHelper.append_url_with_query_parameters(
            _query_builder,
            _query_parameters
        )
        _query_url = APIHelper.clean_url(_query_builder)

        # Prepare headers
        _headers = {
            'accept': 'application/json'
        }

        # Prepare and execute request
        _request = self.config.http_client.get(_query_url, headers=_headers)
        OAuth2.apply(self.config, _request)
        _response = self.execute_request(_request)

        decoded = APIHelper.json_deserialize(_response.text)
        if type(decoded) is dict:
            _errors = decoded.get('error')
        else:
            _errors = None
        _result = ApiResponse(_response, body=decoded, errors=_errors)
        return _result
