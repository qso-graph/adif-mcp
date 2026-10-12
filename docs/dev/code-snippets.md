# Code Snippets & Helpers

Code snippets handy for rendering commonly used items quickly. While this is a subjective topic on how one sets up their environment, these we have found helpful.
For Linux and Mac users, add them to your `.bashrc`, `.bash_profile` or create `.bash_functions` and `.bash_aliases` and source them how you wish. For Windows users,
we'll get the PowerShell commands done when time allows.

## 1. Print available providers
```bash
uv run python -c "from adif_mcp.resources import list_providers; print(list_providers())"

# Load ADIF meta version
uv run python -c "from adif_mcp.resources import get_adif_meta; print(get_adif_meta()['spec_version'])"
```

---

## 2. Simple Quick Actoin Functions
```bash
# List what personas you have configured
persona-list() {
  uv run adif-mcp persona list --verbose
}

# Add a contest persona with dates
persona-add-contest() {
  uv run adif-mcp persona add \
    --name "ContestW7A" \
    --callsign W7A \
    --start 2025-03-01 \
    --end   2025-03-03
}

```

---

## 2. Recreate Your Persona Mappings

This example is for my own callsign history. I have one callsign change that was merged into my primary eQSL and LoTW logbooks. You can add as many as needed.

**Important Overlap Note** - when changing call signs, either via vanity call, or license upgrades, stop the old call one day short of the new call start date. That avoids any
potential collisions with dates when making queries. Also note, this applies to your Primary Lincese callsign, but could also apply to club calls.

**Important Security Note** - There are no credentials leaked here. Export your password as ENV variables for the current session. The function will pick them up for entry.
You should never ( as a standard security practice, *never* write down or save passwords in files ; use exported ENV variables as they are ephemeral )


**Real Example** - The Example below is how I re-create my personans. KI7MT is my primary callsign. KE1HA was my previous call. Both call signs are
merged in LoTW and eQSL for award purposes.The personas I used are for the major logging platforms: `MyEQSL`, `MyLOTW`, `MyQRZ`. The associated
usernames and passwords are stored in macOS Keychain with `set-credentials`. For things like contests, or special events, use an event handle, for example:
`CQ-WW-CW-2025-W7X` or whatever makes sense as the identifier.

```bash
#
# Each of these expects you to have exported the relevant secrets to environment variables beforehand
#
#   export EQSL_USER=... EQSL_PASS=...
#   export LOTW_USER=... LOTW_PASS=...
#   export QRZ_USER=...  QRZ_KEY=...
#
function reset-personas () {
  set -euo pipefail

# Clear all the existing adif-mcp personas and secrets
uv run adif-mcp persona remove-all --yes || true

# Add KI7MT personas starting 2009-12-22
uv run adif-mcp persona add --name MyEQSL    --callsign KI7MT --start 2009-12-22
uv run adif-mcp persona add --name MyLOTW    --callsign KI7MT --start 2009-12-22
uv run adif-mcp persona add --name MyQRZ     --callsign KI7MT --start 2009-12-22

# add login credentials and save to macOS Keychain for safe keeping
# WinCred for Windows
# systemd-secrets or vault for linux
uv run adif-mcp persona set-credential --persona MyEQSL    --provider eqsl    --username "${EQSL_USER}"    --password "${EQSL_PASS}"
uv run adif-mcp persona set-credential --persona MyLOTW    --provider lotw    --username "${LOTW_USER}"    --password "${LOTW_PASS}"
uv run adif-mcp persona set-credential --persona MyQRZ     --provider qrz     --username "${QRZ_USER}"     --password "${QRZ_KEY}"

# Add my previous call sign as a persona, using my Primay account ( KI7MT ) for login
# Again, KE1HA is merged in LoTW and eQSL. If yours is not, add the appropriate user and password for those accounts.
uv run adif-mcp persona add --name KE1HA --callsign KE1HA --start 2001-04-16 --end 2009-12-21
uv run adif-mcp persona set-credential --persona KE1HA --provider eqsl     --username "${EQSL_USER}"    --password "${EQSL_PASS}"
uv run adif-mcp persona set-credential --persona KE1HA --provider lotw     --username "${LOTW_USER}"    --password "${LOTW_PASS}"
uv run adif-mcp persona set-credential --persona KE1HA --provider qrz      --username "${QRZ_USER}"     --password "${QRZ_KEY}"

# Print out my list of personans in verbose mode
uv run adif-mcp persona list --verbose
}
```
