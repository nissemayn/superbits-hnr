"""Small async client for Superbits' undocumented HNR endpoint."""

from __future__ import annotations

from typing import Any

from aiohttp import ClientError, ClientResponseError, ClientSession, ClientTimeout

from .const import API_BASE_URL, DEFAULT_TIMEOUT


class SuperbitsApiError(Exception):
    """Base exception for Superbits API errors."""


class SuperbitsAuthError(SuperbitsApiError):
    """The supplied cookie was rejected."""


class SuperbitsRateLimitError(SuperbitsApiError):
    """Superbits rate-limited the request."""


class SuperbitsConnectionError(SuperbitsApiError):
    """Superbits could not be reached or returned an unexpected response."""


def _is_active_hnr(value: Any) -> bool:
    """Superbits marks a current HNR when nohitnrun is false."""
    if value is False or value == 0:
        return True
    if isinstance(value, str) and value.strip().casefold() in {"false", "0"}:
        return True
    return False


def _normalise_records(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, list):
        raise SuperbitsConnectionError("Superbits returned an unexpected HNR response.")

    records: list[dict[str, Any]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        torrent = item.get("torrent")
        if not isinstance(torrent, dict):
            torrent = {}
        records.append(
            {
                "torrent_id": torrent.get("id"),
                "name": torrent.get("name") or f"Torrent {torrent.get('id', item.get('id', 'unknown'))}",
                "seedtime": item.get("seedtime"),
                "nohitnrun": item.get("nohitnrun"),
                "is_hitrun": _is_active_hnr(item.get("nohitnrun")),
                "uploaded": item.get("uploaded"),
                "downloaded": item.get("downloaded"),
            }
        )

    active = [record for record in records if record["is_hitrun"]]
    return {
        "total": len(payload),
        "hitrun": len(active),
        "records": records,
        "active_hnr": active,
    }


async def async_get_hnr_data(
    session: ClientSession,
    user_id: int,
    cookie: str,
) -> dict[str, Any]:
    """Fetch and normalize the user's current Superbits HNR log."""
    url = API_BASE_URL.format(user_id=user_id)
    headers = {
        "Cookie": cookie,
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "da-DK,da;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://superbits.org/",
    }

    try:
        async with session.get(
            url,
            headers=headers,
            timeout=ClientTimeout(total=DEFAULT_TIMEOUT.total_seconds()),
        ) as response:
            if response.status in (401, 403):
                raise SuperbitsAuthError("Superbits rejected the cookie or request.")
            if response.status == 429:
                raise SuperbitsRateLimitError("Superbits rate-limited the request.")
            response.raise_for_status()
            try:
                payload = await response.json(content_type=None)
            except (ValueError, ClientError) as err:
                raise SuperbitsConnectionError("Superbits returned invalid JSON.") from err
    except SuperbitsApiError:
        raise
    except ClientResponseError as err:
        raise SuperbitsConnectionError(
            "Superbits returned an HTTP error."
        ) from err
    except (ClientError, TimeoutError) as err:
        raise SuperbitsConnectionError("Could not connect to Superbits.") from err

    return _normalise_records(payload)
