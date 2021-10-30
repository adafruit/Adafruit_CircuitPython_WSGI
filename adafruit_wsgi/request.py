# SPDX-FileCopyrightText: 2019 Matthew Costi for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`Request`
================================================================================


* Author(s): Matthew Costi
"""
import re

try:
    from typing import Dict
except ImportError:
    pass


class Request:
    """
    An incoming HTTP request.
    A higher level abstraction of the raw WSGI Environ dictionary.
    """

    def __init__(self, environ: Dict[str, str]) -> None:
        self._method = environ["REQUEST_METHOD"]
        self._path = environ["PATH_INFO"]
        self._query_params = self.__parse_query_params(environ.get("QUERY_STRING", ""))
        self._headers = self.__parse_headers(environ)
        self._body = environ["wsgi.input"]
        self._wsgi_environ = environ

    @property
    def method(self) -> str:
        """
        the HTTP Method Type of this request
        """
        return self._method

    @property
    def path(self) -> str:
        """
        the path this request was made to
        """
        return self._path

    @property
    def query_params(self) -> Dict[str, str]:
        """
        Request query parameters, represented as a dictionary of
        param name to param value
        """
        return self._query_params

    @property
    def headers(self) -> Dict[str, str]:
        """
        Request headers, represented as a dictionary of
        header name to header value
        """
        return self._headers

    @property
    def body(self):
        """
        The Request Body
        """
        return self._body

    @property
    def wsgi_environ(self) -> Dict[str, str]:
        """
        The raw WSGI Environment dictionary representation of the request
        """
        return self._wsgi_environ

    @staticmethod
    def __parse_query_params(query_string: str) -> Dict[str, str]:
        param_list = query_string.split("&")
        params = {}
        for param in param_list:
            key_val = param.split("=")
            if len(key_val) == 2:
                params[key_val[0]] = key_val[1]
        return params

    @staticmethod
    def __parse_headers(environ: Dict[str, str]) -> Dict[str, str]:
        headers = {}

        # Content Type and Content Length headers
        #  are stored in environ differently than other headers
        if "CONTENT_TYPE" in environ:
            headers["content-type"] = environ["CONTENT_TYPE"]
        if "CONTENT_LENGTH" in environ:
            headers["content-length"] = environ["CONTENT_LENGTH"]

        env_header_re = re.compile(r"HTTP_(.+)")
        for key, val in environ.items():
            header = env_header_re.match(key)
            if header:
                headers[header.group(1).replace("_", "-").lower()] = val
        return headers
