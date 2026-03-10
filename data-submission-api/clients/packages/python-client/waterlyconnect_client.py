from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Optional, Union
import json
import time
from urllib import request, error


class WaterlyConnectError(RuntimeError):
    pass


def _value_to_string(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _coerce_client_device(
    client_device: Union["ClientDeviceInfo", Mapping[str, Any]]
) -> "ClientDeviceInfo":
    if isinstance(client_device, ClientDeviceInfo):
        return client_device
    if isinstance(client_device, Mapping):
        return ClientDeviceInfo(**client_device)
    raise TypeError("client_device must be a ClientDeviceInfo or mapping")


def _coerce_tag_datum(tag: Union["TagDatum", Mapping[str, Any]]) -> "TagDatum":
    if isinstance(tag, TagDatum):
        return tag
    if isinstance(tag, Mapping):
        return TagDatum(**tag)
    raise TypeError("tags must be TagDatum instances or mappings")


def _normalize_proxy(proxy: Union[str, dict[str, str]]) -> dict[str, str]:
    if isinstance(proxy, str):
        return {"http": proxy, "https": proxy}
    return dict(proxy)


@dataclass
class ClientDeviceInfo:
    id: str
    type: str
    lan_ip: Optional[str] = None
    wan_ip: Optional[str] = None
    serial: Optional[str] = None
    uptime_millis: Optional[int] = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "id": self.id,
            "type": self.type,
        }

        if self.lan_ip is not None:
            data["lan_ip"] = self.lan_ip
        if self.wan_ip is not None:
            data["wan_ip"] = self.wan_ip
        if self.serial is not None:
            data["serial"] = self.serial
        if self.uptime_millis is not None:
            data["uptime_millis"] = self.uptime_millis

        return data


@dataclass
class TagDatum:
    name: str
    value: Any
    last_change_timestamp: int
    type: Optional[int] = None
    unit: Optional[str] = None

    def __post_init__(self) -> None:
        self.value = _value_to_string(self.value)
        self.last_change_timestamp = int(self.last_change_timestamp)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "name": self.name,
            "value": self.value,
            "last_change_timestamp": self.last_change_timestamp,
        }

        if self.type is not None:
            data["type"] = self.type
        if self.unit is not None:
            data["unit"] = self.unit

        return data


@dataclass
class WaterlyConnectApiClientConfig:
    url: str
    client_token: str
    client_device: Union[ClientDeviceInfo, dict[str, Any]]
    proxy: Optional[Union[str, dict[str, str]]] = None

    def __post_init__(self) -> None:
        self.client_device = _coerce_client_device(self.client_device)


class WaterlyConnectApiClient:
    def __init__(self, config: WaterlyConnectApiClientConfig) -> None:
        url = config.url
        client_token = config.client_token
        client_device = config.client_device

        if not url or not url.strip():
            raise ValueError("url is required")
        if not client_token or not client_token.strip():
            raise ValueError("client_token is required")
        if client_device is None:
            raise ValueError("client_device is required")

        if (
            not isinstance(client_device.id, str)
            or not client_device.id.strip()
            or not isinstance(client_device.type, str)
            or not client_device.type.strip()
        ):
            raise ValueError("client_device requires id and type")

        self.url = url
        self.client_token = client_token
        self.client_device = client_device
        self.proxy = config.proxy

        if self.proxy is None:
            self._opener = request.build_opener()
        else:
            proxy_map = _normalize_proxy(self.proxy)
            self._opener = request.build_opener(request.ProxyHandler(proxy_map))

    def submit_data(self, tags: list[Union[TagDatum, dict[str, Any]]]) -> None:
        if tags is None:
            raise ValueError("tags is required")

        tag_list = [_coerce_tag_datum(tag) for tag in tags]
        if not tag_list:
            raise ValueError("tags is required")

        submission = {
            "tags": [tag.to_dict() for tag in tag_list],
            "device": self.client_device.to_dict(),
            "timestamp": int(time.time()),
        }

        body = json.dumps(submission).encode("utf-8")

        req = request.Request(self.url, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("x-waterly-connect-token", self.client_token)
        req.add_header("x-waterly-request-type", "WaterlyConnect")

        try:
            with self._opener.open(req) as response:
                response.read()
        except error.HTTPError as exc:
            response_body = ""
            try:
                response_body = exc.read().decode("utf-8", errors="replace")
            except Exception:
                response_body = ""

            detail = f"HTTP {exc.code} {exc.reason}"
            if response_body:
                detail = f"{detail}: {response_body}"

            raise WaterlyConnectError(
                f"WaterlyConnect submission failed: {detail}"
            ) from exc
        except error.URLError as exc:
            raise WaterlyConnectError(
                f"WaterlyConnect submission failed: {exc.reason}"
            ) from exc


__all__ = [
    "ClientDeviceInfo",
    "TagDatum",
    "WaterlyConnectApiClient",
    "WaterlyConnectApiClientConfig",
    "WaterlyConnectError",
]
