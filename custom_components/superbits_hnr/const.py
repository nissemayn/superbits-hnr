"""Constants for the Superbits Hit'n'Run integration."""

from datetime import timedelta

DOMAIN = "superbits_hnr"
PLATFORMS = ["sensor"]

CONF_USER_ID = "user_id"
CONF_COOKIE = "cookie"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = 30
MIN_SCAN_INTERVAL = 5
MAX_SCAN_INTERVAL = 1440

API_BASE_URL = "https://superbits.org/api/v1/users/{user_id}/hnrlog"
DEFAULT_TIMEOUT = timedelta(seconds=25)
