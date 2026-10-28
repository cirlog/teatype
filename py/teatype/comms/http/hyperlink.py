# Copyright (C) 2024-2026 Burak Günaydin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

_URL_ENCODE_MAP = {
    ' ': '+'
}

def decode(url:str) -> str:
    """
    Args:
        url (str): The url to be decoded.

    Returns:
        str: The decoded url.
    """
    decoded_url = url
    for char, replacement in _URL_ENCODE_MAP.items():
        decoded_url = decoded_url.replace(replacement, char)
    return decoded_url

def encode(url:str) -> str:
    """
    Args:
        url (str): The url to be encoded.

    Returns:
        str: The encoded url.
    """
    encoded_url = url
    for char, replacement in _URL_ENCODE_MAP.items():
        encoded_url = encoded_url.replace(char, replacement)
    return encoded_url

def join(*uris:str) -> str:
    """
    Join uris of a URL into a single URL string.

    Args:
        *uris (str): uris of the URL to be joined.

    Returns:
        str: The joined URL.
    """
    return '/'.join(uri.strip('/') for uri in uris if uri)

def url(*uris:str, encode_url:bool=True) -> str:
    """
    Join uris of a URL into a single URL string and optionally encode it.

    Args:
        *uris (str): uris of the URL to be joined.
        encode (bool): Whether to encode the resulting URL. Defaults to True.

    Returns:
        str: The joined (and optionally encoded) URL.
    """
    joined_url = join(*uris)
    if encode_url:
        joined_url = encode(joined_url)
    return joined_url