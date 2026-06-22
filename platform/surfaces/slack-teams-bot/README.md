# Governova — Chat Notifier (Slack / Teams)

**Status:** Alpha — working (v0.1)
**Surface:** governance verdicts to a chat webhook

Posts the consolidated **Governova Guardian** verdict (Score · this-PR enforcement ·
coverage) to a chat channel via an incoming webhook — Slack, Microsoft Teams, or any
endpoint that accepts a `{"text": ...}` body.

Same discipline as the semantic tier: **provider-agnostic** (the webhook URL comes from
the environment) and **inactive without configuration** — a clean no-op, so nothing
depends on it being set up.

## Use it

```bash
export GOVERNOVA_WEBHOOK_URL="https://hooks.slack.com/services/…"
governova notify --base origin/main
```

With no `GOVERNOVA_WEBHOOK_URL`, the command prints `notifier inactive` and exits 0.
The monthly governance workflow includes a notify step that is a no-op unless the
`GOVERNOVA_WEBHOOK_URL` repository secret is set.

## Implementation

`governova_notify` (`scripts/governova_notify/`): env-driven config, a stdlib `urllib`
transport (injectable for tests), and a payload built from the Guardian verdict. No SDK,
no hosted service.
