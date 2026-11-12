"""Local vault MCP adapter; credentials stay in Secret Service."""
from __future__ import annotations

import asyncio
import json
import os
import re
import stat
from pathlib import Path
from typing import Literal

import secretstorage
from mcp.server.fastmcp import FastMCP

ROOT = Path(__file__).resolve().parent
OP = str(Path.home() / ".local/bin/op")
ATTRIBUTES = {"application": "codex-1password-mcp", "credential": "agents-service-account"}
server = FastMCP("1Password Vault", instructions=(
    "Local vault adapter to the official 1Password CLI. Authentication uses the "
    "VPS login keyring, independently of the Mac. Metadata reads redact field "
    "values. Use run_with_secrets to authenticate a local process without "
    "returning credentials to the model. write_item supports authorized create "
    "and edit operations in the Agents vault and returns metadata only. "
    "Only perform user-authorized operations."
), log_level="ERROR")


def token() -> str:
    # MCP clients may start stdio servers with a minimal environment.
    bus_path = Path(f"/run/user/{os.getuid()}/bus")
    if "DBUS_SESSION_BUS_ADDRESS" not in os.environ and bus_path.exists():
        os.environ["DBUS_SESSION_BUS_ADDRESS"] = f"unix:path={bus_path}"
    bus = secretstorage.dbus_init()
    collection = secretstorage.Collection(bus, "/org/freedesktop/secrets/collection/login")
    if collection.is_locked():
        raise RuntimeError("The VPS login keyring is locked.")
    items = list(collection.search_items(ATTRIBUTES))
    if len(items) != 1:
        raise RuntimeError("The VPS service-account credential is not configured uniquely.")
    return items[0].get_secret().decode().strip()


async def op(arguments: list[str], input_data: bytes | None = None) -> bytes:
    environment = {k: v for k, v in os.environ.items() if not k.startswith("OP_")}
    environment["OP_SERVICE_ACCOUNT_TOKEN"] = await asyncio.to_thread(token)
    environment["OP_BIOMETRIC_UNLOCK_ENABLED"] = "false"
    process = await asyncio.create_subprocess_exec(
        OP, "--config", str(ROOT / "cli"), "--format=json", *arguments,
        stdin=asyncio.subprocess.PIPE if input_data is not None else asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL, env=environment,
    )
    try:
        output, _ = await asyncio.wait_for(process.communicate(input_data), timeout=45)
    except (TimeoutError, asyncio.CancelledError):
        if process.returncode is None:
            process.kill()
        await process.wait()
        raise RuntimeError("1Password request timed out; credential output withheld.") from None
    if process.returncode:
        raise RuntimeError("1Password authentication or vault operation failed; credential output withheld.")
    return output


def conceal(value):
    if isinstance(value, list):
        return [conceal(item) for item in value]
    if isinstance(value, dict):
        return {k: "[redacted]" if k.lower() in {
            "value", "password", "secret", "token", "credential", "totp", "content", "notesplain"
        } else conceal(v) for k, v in value.items()}
    return value


@server.tool(annotations={"readOnlyHint": True})
async def authenticate() -> dict:
    """Verify the locally stored service account. Returns no credential values."""
    result = json.loads(await op(["whoami"]))
    return {"authenticated": True, "type": result.get("user_type", result.get("type")),
            "state": result.get("state"), "source": "VPS login keyring"}


@server.tool(annotations={"readOnlyHint": True})
async def op_command(arguments: list[str], reveal_secrets: bool = False) -> dict:
    """Read vault/item metadata through the existing adapter API; all fields are redacted."""
    if reveal_secrets:
        raise ValueError("Secret values cannot be returned. Use run_with_secrets for authentication.")
    if not arguments or any(not isinstance(a, str) or "\x00" in a for a in arguments):
        raise ValueError("Invalid arguments.")
    head = arguments[:2]
    if arguments != ["whoami"] and head not in [["vault", "list"], ["item", "list"], ["item", "get"]]:
        raise ValueError("Only whoami, vault list, item list and item get are supported.")
    allowed_flags = {"--vault", "--categories", "--tags", "--include-archive"}
    if any(a.startswith("-") and a.split("=", 1)[0] not in allowed_flags for a in arguments):
        raise ValueError("Unsupported flag; file output, templates and field extraction are disabled.")
    return {"success": True, "result": conceal(json.loads(await op(arguments)))}


AGENTS_VAULT = "5hrlo6hj5vy7dys6gqzq3ubz7u"


def private_file(path: str) -> bytes:
    """Read a small owner-only regular file without following a final symlink."""
    if not Path(path).is_absolute():
        raise ValueError("Use an absolute private file path.")
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise ValueError("The input must be an owner-only regular file owned by this user.")
        data = stream.read(1024 * 1024 + 1)
    if len(data) > 1024 * 1024:
        raise ValueError("Private input is too large.")
    return data


def has_key_material(item) -> bool:
    if isinstance(item, list):
        return any(has_key_material(value) for value in item)
    if isinstance(item, dict):
        return any(
            (key.lower() in {"fido2credentials", "passkeys", "sshkey"} and bool(value))
            or (key == "type" and isinstance(value, str) and value.upper() in {"PASSKEY", "SSHKEY"})
            or has_key_material(value)
            for key, value in item.items()
        )
    return False


@server.tool(annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False})
async def write_item(
    action: Literal["create", "edit"],
    title: str | None = None,
    item_id: str | None = None,
    category: str = "Login",
    username: str | None = None,
    url: str | None = None,
    generate_password: bool = False,
    password_file: str | None = None,
    template_file: str | None = None,
) -> dict:
    """Create or edit an authorized item in the Agents vault. Returns metadata only.

    For a new login, supply title, username, url and generate_password=true.
    Existing secrets must come from an owner-only password_file or JSON
    template_file, never literal tool arguments. Inputs travel to op via stdin;
    no secret values are returned or logged. This does not change any website
    password. Inspect existing item metadata and obtain task authorization
    before editing. Deletion, vault administration and sharing are unsupported.
    """
    if action not in {"create", "edit"}:
        raise ValueError("Only create and edit are supported.")
    if action == "create" and (not title or item_id):
        raise ValueError("Creation requires a title and no existing item ID.")
    if action == "edit" and (not item_id or not re.fullmatch(r"[a-z2-7]{26}", item_id)):
        raise ValueError("Editing requires an exact item ID.")
    if sum([generate_password, password_file is not None, template_file is not None]) > 1:
        raise ValueError("Choose generated password, password file, or JSON template.")
    payload = None
    if template_file:
        try:
            payload = json.loads(private_file(template_file))
        except (ValueError, UnicodeError):
            raise ValueError("The private template must contain one valid JSON object.") from None
        if not isinstance(payload, dict):
            raise ValueError("The private template must contain one valid JSON object.")
        if payload.get("vault", {}).get("id", AGENTS_VAULT) != AGENTS_VAULT:
            raise ValueError("Writes are restricted to the Agents vault.")
        if action == "edit" and payload.get("id", item_id) != item_id:
            raise ValueError("The template item ID must match the requested item.")
    if password_file:
        # Read a single password; strip only the conventional terminal newline.
        try:
            password = private_file(password_file).decode().removesuffix("\n").removesuffix("\r")
        except UnicodeError:
            raise ValueError("The password input must be UTF-8.") from None
        if not password or "\x00" in password or "\n" in password or "\r" in password:
            raise ValueError("The password input must contain one nonempty line.")
        if action == "edit":
            payload = json.loads(await op(["item", "get", item_id, "--vault", AGENTS_VAULT]))
            if has_key_material(payload):
                raise ValueError("Template updates of passkey or SSH key items are unsupported.")
        else:
            payload = json.loads(await op(["item", "template", "get", category]))
        fields = payload.setdefault("fields", [])
        field = next((field for field in fields if field.get("id") == "password"), None)
        if field is None:
            field = {"id": "password", "type": "CONCEALED", "purpose": "PASSWORD", "label": "password"}
            fields.append(field)
        field["value"] = password
    if action == "edit" and template_file:
        current = json.loads(await op(["item", "get", item_id, "--vault", AGENTS_VAULT]))
        if has_key_material(current):
            raise ValueError("Template updates of passkey or SSH key items are unsupported.")
    arguments = ["item", action]
    if action == "edit":
        arguments.append(item_id)
    elif payload is not None:
        arguments.append("-")
    arguments += ["--vault", AGENTS_VAULT]
    if action == "create" and payload is None:
        arguments += ["--category", category]
    elif action == "create" and not payload.get("category"):
        payload["category"] = json.loads(await op(["item", "template", "get", category]))["category"]
    for flag, value in [("--title", title), ("--url", url)]:
        if value is not None:
            arguments += [flag, value]
    if generate_password:
        arguments += ["--generate-password=letters,digits,symbols,32"]
    if username is not None:
        arguments.append("username=" + username)
    result = json.loads(await op(arguments, json.dumps(payload).encode() if payload is not None else None))
    return {"success": True, "action": action, "item": {
        "id": result["id"], "title": result.get("title"),
        "category": result.get("category"), "vault_id": result.get("vault", {}).get("id"),
        "password_reference": f"op://{AGENTS_VAULT}/{result['id']}/password",
    }}


@server.tool()
async def run_with_secrets(command: list[str], secrets: dict[str, str], cwd: str) -> dict:
    """Run an authorized local check with op:// references injected into environment variables.

    No secret values or child output are returned. The child can save reviewed,
    credential-free screenshots or structured results. Never submit business forms
    or modify site data during a read-only check. The service-account token itself
    is not inherited by the child.
    """
    if not command or not Path(command[0]).is_absolute() or not Path(cwd).is_absolute():
        raise ValueError("Use absolute executable and working-directory paths.")
    if not secrets or any(not re.fullmatch(r"[A-Z_][A-Z0-9_]*", key) or key.startswith("OP_")
                          or not ref.startswith("op://") or "\n" in ref
                          for key, ref in secrets.items()):
        raise ValueError("Use named environment variables and op:// secret references.")
    environment = {k: v for k, v in os.environ.items() if not k.startswith("OP_")}
    for name, reference in secrets.items():
        environment[name] = (await op(["read", reference])).decode().rstrip("\n")
    process = await asyncio.create_subprocess_exec(
        *command, cwd=cwd, env=environment,
        stdin=asyncio.subprocess.DEVNULL, stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    try:
        code = await asyncio.wait_for(process.wait(), timeout=300)
    except (TimeoutError, asyncio.CancelledError):
        if process.returncode is None:
            process.kill()
        await process.wait()
        raise RuntimeError("The authenticated process timed out; all output withheld.") from None
    return {"exit_code": code, "output": "withheld to protect credentials"}


if __name__ == "__main__":
    server.run(transport="stdio")
