# Superbits Hit'n'Run for Home Assistant

A custom Home Assistant integration that reads a user's Superbits Hit'n'Run log and exposes two sensors. It is an unofficial community integration and is not affiliated with Superbits.

**Author and maintainer:** [@nissemayn](https://github.com/nissemayn)

## Features

- Total number of records returned by the HNR log.
- Number of active Hit'n'Runs. A record is active when Superbits returns `nohitnrun: false`.
- Active torrent names, IDs, and seed-time values in the Hit'n'Run sensor attributes.
- Configurable polling interval from 5 minutes to 24 hours (30 minutes by default).

## Dashboard card

![Superbits Hit'n'Run card in Home Assistant](docs/images/superbits-hnr-card.png)

The entity IDs include the configured Superbits user ID. For example, if your user ID is `12345`, they are:

- `sensor.superbits_hnr_12345_total_antal`
- `sensor.superbits_hnr_12345_hit_n_run`

## Installation with HACS

### Add the repository to HACS

1. In Home Assistant, open **HACS → Integrations**.
2. Open the menu in the top-right corner and choose **Custom repositories**.
3. Paste `https://github.com/nissemayn/superbits-hnr` as the repository URL.
4. Select **Integration** as the category and choose **Add**.
5. Search HACS for **Superbits Hit'n'Run**, open it, and choose **Download**.
6. Restart Home Assistant when prompted (or restart it from **Settings → System → Restart**).

### Configure the integration

1. Go to **Settings → Devices & services**.
2. Choose **Add integration** and search for **Superbits Hit'n'Run**.
3. Enter your Superbits user ID and authenticated session cookie, then submit.
4. The integration creates the total and active Hit'n'Run sensors. Add them to a dashboard like any other Home Assistant entities.

To update later, use **HACS → Integrations → Superbits Hit'n'Run → Update** when an update is available, then restart Home Assistant.

## Setup

Enter your Superbits user ID and a session cookie from an authenticated Superbits session. The integration checks the credentials when it is configured. To change the polling interval later, open the integration and select **Configure**. Leave the replacement-cookie field empty to keep the current cookie.

The integration makes HTTPS GET requests to Superbits' undocumented endpoint:

`https://superbits.org/api/v1/users/<user_id>/hnrlog`

The endpoint and response format can change without notice. The session cookie may expire; if so, sign in to Superbits again, obtain a fresh cookie, and replace it in the integration options.

## Privacy and security

- The cookie is stored in Home Assistant's config-entry storage and sent only to `superbits.org` over HTTPS.
- Treat the cookie like a password. Do not include it in logs, screenshots, issue reports, or support requests.
- The integration is read-only and only reads the Superbits Hit'n'Run log.

## Troubleshooting

- **Authentication error:** Sign in to Superbits again, obtain a fresh session cookie, and replace it in the integration options.
- **Connection error:** Check that Home Assistant can reach `superbits.org` and that the endpoint is responding.
- **Unexpected HNR count:** Check the `nohitnrun` values in Superbits' response. This integration counts `false` as an active HNR.

Please do not post cookies or other account credentials in GitHub issues.

## License and warranty

This project is licensed under **0BSD**. You may use, copy, modify, and distribute it for any purpose. It is provided **as-is**, without warranty. See [LICENSE](LICENSE) for the full license text.
