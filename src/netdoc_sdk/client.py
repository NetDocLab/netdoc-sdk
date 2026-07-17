"""Asynchronous and synchronous HTTP clients for the NetDoc API."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import TYPE_CHECKING, Any

import httpx

from netdoc_sdk._client_base import _NetDocClientBase
from netdoc_sdk.exceptions import ConnectionError

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping


logger = logging.getLogger('netdoc_sdk')


class NetDocClient(_NetDocClientBase):
    """Asynchronous client for the NetDoc API.

    Intended for use in asyncio environments such as async collectors, FastAPI
    applications, and other non-blocking services. Endpoint methods inherited
    from ``_NetDocClientBase`` must be awaited by the caller.
    """

    _client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = self._make_client()
        return self._client

    def _make_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.base_url,
            cookies=self.cookies,
            headers=self._build_headers(),
            timeout=self.timeout,
            transport=self.transport,
            verify=self.verify,
            **self.client_kwargs,
        )

    async def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> NetDocClient:
        self._client = self._make_client()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    @classmethod
    async def from_credentials(
        cls,
        base_url: str,
        username: str,
        password: str,
        **kwargs: Any,
    ) -> NetDocClient:
        """Authenticate with username/password and return a token-authenticated client."""
        async with cls(base_url=base_url, **kwargs) as bootstrap:
            token = await bootstrap.tokens_add(username=username, password=password)  # type: ignore[misc] # tokens_add is shared between sync and async clients
        return cls(base_url=base_url, token=token.token, **kwargs)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        content: bytes | str | None = None,
        expected_status: int | Iterable[int] | None = None,
        headers: Mapping[str, str] | None = None,
        json: Any | None = None,
        params: Mapping[str, Any] | None = None,
        response_model: Any = None,
    ) -> Any:
        request_headers = self._request_headers(method, headers)
        expected = self._expected_set(expected_status)
        response: httpx.Response | None = None

        for attempt in range(self.max_retries + 1):
            try:
                response = await self.client.request(
                    method=method,
                    url=self._api_path(path),
                    content=content,
                    headers=request_headers,
                    json=json,
                    params=self._clean_params(params),
                )
            except (httpx.ConnectError, httpx.NetworkError) as exc:
                raise ConnectionError(f'Failed to connect: {exc}') from exc
            except httpx.TimeoutException as exc:
                raise ConnectionError(f'Request timed out: {exc}') from exc

            if self._is_ok(response.status_code, expected):
                break

            if response.status_code == 429 and attempt < self.max_retries:
                wait = self._parse_retry_after(response.headers.get('Retry-After'))
                logger.warning(
                    'Rate limited (attempt %d/%d), retrying in %.1fs',
                    attempt + 1,
                    self.max_retries,
                    wait,
                )
                await asyncio.sleep(wait)
                continue

            self._raise_for_error(response)

        if response:
            return self._parse_response(response, response_model, expected)

        raise ValueError('Should not be here - guaranteed by range(max_retries + 1) >= 1')


class NetDocSyncClient(_NetDocClientBase):
    """Synchronous client for the NetDoc API.

    Intended for use in thread-based collectors, scripts, and other contexts
    where an asyncio event loop is not available or desirable. Endpoint methods
    inherited from ``_NetDocClientBase`` return values directly and do not
    require ``await``.
    """

    _client: httpx.Client | None = None

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = self._make_client()
        return self._client

    def _make_client(self) -> httpx.Client:
        return httpx.Client(
            base_url=self.base_url,
            cookies=self.cookies,
            headers=self._build_headers(),
            timeout=self.timeout,
            transport=self.transport,
            verify=self.verify,
            **self.client_kwargs,
        )

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> NetDocSyncClient:
        self._client = self._make_client()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    @classmethod
    def from_credentials(
        cls,
        base_url: str,
        username: str,
        password: str,
        **kwargs: Any,
    ) -> NetDocSyncClient:
        """Authenticate with username/password and return a token-authenticated client."""
        with cls(base_url=base_url, **kwargs) as bootstrap:
            token = bootstrap.tokens_add(username=username, password=password)
        return cls(base_url=base_url, token=token.token, **kwargs)

    def _request(
        self,
        method: str,
        path: str,
        *,
        content: bytes | str | None = None,
        expected_status: int | Iterable[int] | None = None,
        headers: Mapping[str, str] | None = None,
        json: Any | None = None,
        params: Mapping[str, Any] | None = None,
        response_model: Any = None,
    ) -> Any:
        request_headers = self._request_headers(method, headers)
        expected = self._expected_set(expected_status)
        response: httpx.Response | None = None

        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.request(
                    method=method,
                    url=self._api_path(path),
                    content=content,
                    headers=request_headers,
                    json=json,
                    params=self._clean_params(params),
                )
            except (httpx.ConnectError, httpx.NetworkError) as exc:
                raise ConnectionError(f'Failed to connect: {exc}') from exc
            except httpx.TimeoutException as exc:
                raise ConnectionError(f'Request timed out: {exc}') from exc

            if self._is_ok(response.status_code, expected):
                break

            if response.status_code == 429 and attempt < self.max_retries:
                wait = self._parse_retry_after(response.headers.get('Retry-After'))
                logger.warning(
                    'Rate limited (attempt %d/%d), retrying in %.1fs',
                    attempt + 1,
                    self.max_retries,
                    wait,
                )
                time.sleep(wait)
                continue

            self._raise_for_error(response)

        if response:
            return self._parse_response(response, response_model, expected)

        raise ValueError('Should not be here - guaranteed by range(max_retries + 1) >= 1')
