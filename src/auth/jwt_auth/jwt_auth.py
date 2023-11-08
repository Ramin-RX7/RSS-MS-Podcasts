from fastapi import Request,HTTPException

import jwt

from schemas import Result,JWTPayload
from services import RedisService
from .utils import (
    decode_jwt,
    _generate_access_token,
    _generate_payload,
    _generate_refresh_token,
    encode_payload,
)
from .exceptions import PermissionDenied




class JWTHandler:
    """
    This class is used to take place as JWT authentication handler.

    It will stands between user and server to authenticate users via their tokens.

    This class needs to take place between redis and JWT authentication package to \
     complete jwt token validation

    Usage:
    ------

    jwt_handler = JWTHandler()

    @app.get("/protected-url")
    async def protected_url(jwt:JWTPayload=Depends(jwt_handler)):
        ...
    """
    def __init__(self):
        self.jwt_auth = JWTAuth()
        self.auth_cache = RedisService()

    async def authenticate(self, request:Request) -> JWTPayload:
        """Main method of this class which is responsible to authenticate users with their access token

        Args:
        -----
        - request `(Request)`: _Http request of current request_

        Returns:
        --------
        `JWT_Scheme`: jwt scheme object built from payload
        """
        payload = await self.jwt_auth.authenticate(request.headers)
        id = payload.get("user_identifier")
        await self._validate_cache_data(
            id,
            payload.get("jti"),
            request.headers.get("user-agent")
        )
        return JWTPayload(payload)
    __call__ = authenticate

    async def _validate_cache_data(self, id, jti, user_agent):
        user_redis_jti = await self.auth_cache.get(f"{id}|{jti}")
        if user_redis_jti is None:
            raise PermissionDenied('Not Found in cache, login again.')
        if user_redis_jti != user_agent:
            raise PermissionDenied('Invalid refresh token, please login again.')



class JWTAuth:
    # BUG: payload structure is based on this class (instead of `JWTHandler` class)
    # BUG: header_prefix/header_name are based on this class(instead of `JWTHandler`)
    """JWT authentication class

    generates and validates access/refresh tokens of users.

    Usage:
    ------
    ```python
    jwt_auth = JWTAuth()

    jwt_auth.authenticate(request.headers)
    # Either raised error because of invalid access token or returns the payload
    """
    authentication_header_prefix = 'Token'
    authentication_header_name = 'Authorization'

    def __init__(self):
        self.auth_cache = RedisService()


    async def authenticate(self, headers):
        """Used for complete validation of access token (checking headers and token)

        Args:
        -----
        - headers `(dict)`: _dictionary of all http request headers_

        Returns:
        --------
        `dict[str,Any]`: _payload that is saved in access token_
        """
        access_token = self._get_access_token(headers)
        payload = self._validate_access_token(access_token)
        user = payload.get("user_identifier")
        jti = payload.get('jti')
        user_agent = self._get_user_agent(headers)
        return payload


    def generate_tokens(self, account_identifier:str) -> tuple[str,str,str]:
        """Used to generate tokens for user manually

        Normally it is called alone only when user logins with user identifier and password.

        Args:
        -----
        - account_identifier `(str)`: _identifier of the user_

        Returns:
        --------
        `tuple[str,str,str]`: returns tuple of jti, access token, refresh token
        """
        base_payload = _generate_payload(account_identifier)
        access_payload = _generate_access_token(base_payload)
        refresh_payload = _generate_refresh_token(base_payload)
        return (base_payload["jti"], encode_payload(access_payload), encode_payload(refresh_payload))


    def _get_user_agent(self, headers):
        """Get user agent from request headers

        Args:
        -----
        - headers `()`: headers retrieved from request

        Raises:
        -------
        PermissionDenied: raised when user-agent header is not provided in headers

        Returns:
        --------
        `str`: user agent header
        """
        user_agent = headers.get("user-agent")
        if user_agent is None:
            raise PermissionDenied('user-agent header is not provided')
        return user_agent

    def _get_access_token(self, headers):
        """Retrieves access token from authorization headers and validates the prefix

        Args:
        -----
        - headers `(dict)`: _request http headers_

        Raises:
        - PermissionDenied: when `self.authentication_header_name` is not given
        - PermissionDenied: when token prefix (self.authentication_header_prefix) is missing.

        Returns:
        --------
        `str`: access token
        """
        auth_header = headers.get(self.authentication_header_name)
        if not auth_header:
            raise PermissionDenied("No access token")
        full_token = auth_header.split(' ')
        if (len(full_token) != 2) or (full_token[0] != self.authentication_header_prefix):
            raise PermissionDenied('Token prefix missing')
        return full_token[1]

    def _validate_access_token(self, token):
        """Validates access token with decoding it

        Args:
        -----
        - token `(str)`: _token retrievd from http headers_

        Raises:
        - HTTPException (401): _When access token is expired_
        - HTTPException (403): _When invalid access token is given (can not be decoded)_

        Returns:
        --------
        `dict`: payload saved in the access token
        """
        try:
            return decode_jwt(token)
        except jwt.ExpiredSignatureError:
            raise HTTPException(401,'Access token expired') from None
        except jwt.DecodeError:
            raise HTTPException(403, "invalid access token")

    def _get_refresh_payload(self, token:str):
        """Retrieves decoded payload of refresh

        Args:
        -----
        - token `(str)`: _user given refresh token_

        Raises:
        - PermissionDenied: _When refresh token is expired_
        - HTTPException: _When refresh token is not decodeable_

        Returns:
        --------
        `dict`: payload of the token
        """
        try:
            return decode_jwt(token)
        except jwt.ExpiredSignatureError:
            raise PermissionDenied(
                'Expired refresh token, please login again.') from None
        except jwt.DecodeError:
            # raise
            raise HTTPException(403,"invalid refresh token")
