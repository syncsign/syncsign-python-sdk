# -*- coding: utf-8 -*-

from syncsign.decorators import lazy_property
from syncsign.configuration import Configuration
from syncsign.api.user_api import UserApi
from syncsign.api.display_render_api import DisplayRenderApi
from syncsign.api.devices_api import DevicesApi
from syncsign.api.nodes_api import NodesApi


class Client(object):

    @staticmethod
    def sdk_version():
        return '0.1.0'

    @staticmethod
    def api_version():
        return 'v2'

    @lazy_property
    def display_render(self):
        return DisplayRenderApi(self.config)

    @lazy_property
    def devices(self):
        return DevicesApi(self.config)

    @lazy_property
    def nodes(self):
        return NodesApi(self.config)

    @lazy_property
    def user(self):
        return UserApi(self.config)

    def __init__(self, timeout=60, max_retries=3, backoff_factor=0,
                 environment='production',
                 custom_url='https://api.sync-sign.com',
                 api_version='v2',
                 api_key='',
                 access_token='',
                 additional_headers={}, config=None):
        if config is None:
            self.config = Configuration(timeout=timeout,
                                        max_retries=max_retries,
                                        backoff_factor=backoff_factor,
                                        environment=environment,
                                        custom_url=custom_url,
                                        api_version=api_version,
                                        api_key=api_key,
                                        access_token=access_token,
                                        additional_headers=additional_headers)
        else:
            self.config = config
