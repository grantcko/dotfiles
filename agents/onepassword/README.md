# VPS 1Password MCP adapter

This adapter uses the official 1Password CLI and a service-account token from
the VPS login keyring. It supports redacted metadata reads, secret injection
into authorized local processes, and item creation/editing in the Agents vault.
It never returns secret values. Vault administration, sharing and deletion
are not exposed.

The installed runtime lives in `~/.local/share/onepassword-agents/`. Its existing
virtual environment provides `mcp` and `secretstorage`; `~/.local/bin/op` is the
CLI. Keep the keyring, CLI configuration and virtual environment outside Git.
The Agents vault ID and keyring lookup attributes in `server.py` identify the
existing deployment; they are references, not credentials.

Copy the Python sources to that runtime directory when upgrading. New MCP
connections expose `write_item`. Existing sessions can call the upgraded MCP
without restarting unrelated agents:

```sh
~/.local/share/onepassword-agents/.venv/bin/python \
  ~/.local/share/onepassword-agents/client.py write_item \
  --arguments '{"action":"create","title":"Example login","username":"user@example.invalid","url":"https://example.invalid","generate_password":true}'
```

Only nonsecret values and private file paths belong in tool arguments or command
text. For an existing password, pass an owner-only `password_file` path. For other
item fields, use an owner-only JSON `template_file`; content is sent through stdin.
Edits require the exact item ID. JSON/password-file edits refuse existing items
containing passkeys or SSH key material. `generate_password` changes the stored
password only; it does not change a website's password. Use task authorization
and inspect existing metadata before writing to avoid duplicates or unwanted
credential rotation. Handle any temporary secret file through its private input
lifecycle and remove it after use; do not commit or log it.

The write result includes item metadata and an `op://` password reference. Use
`run_with_secrets` for secret injection into authorized processes. If a write
times out, inspect matching item metadata before retrying because it may have
completed. Run the adapter tests with the existing virtual environment:

```sh
~/.local/share/onepassword-agents/.venv/bin/python -m unittest discover \
  -s agents/onepassword -p test_server.py -v
```

CLI reference: [Create items](https://www.1password.dev/cli/item-create),
[service account support](https://www.1password.dev/service-accounts/use-with-1password-cli).
