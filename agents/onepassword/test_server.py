import asyncio
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

spec = importlib.util.spec_from_file_location("adapter", Path(__file__).with_name("server.py"))
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)
ITEM = "a" * 26
SECRET = "test-only-secret-do-not-return"


class WriteTests(unittest.IsolatedAsyncioTestCase):
    async def test_generated_password_has_no_literal_secret_and_returns_only_metadata(self):
        response = {"id": ITEM, "vault": {"id": adapter.AGENTS_VAULT}, "fields": [{"value": SECRET}]}
        with patch.object(adapter, "op", AsyncMock(return_value=json.dumps(response).encode())) as op:
            result = await adapter.write_item("create", title="Test", username="test@example.invalid", generate_password=True)
        self.assertNotIn(SECRET, json.dumps(result))
        self.assertIn("--generate-password=letters,digits,symbols,32", op.call_args.args[0])
        self.assertEqual(result["item"]["vault_id"], adapter.AGENTS_VAULT)

    async def test_private_password_uses_stdin_and_preserves_existing_fields(self):
        original = {"id": ITEM, "fields": [{"id": "username", "value": "keep"}, {"id": "password", "value": "old"}]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "password"
            path.write_text(SECRET + "\n")
            path.chmod(0o600)
            with patch.object(adapter, "op", AsyncMock(side_effect=[json.dumps(original).encode(), json.dumps({"id": ITEM}).encode()])) as op:
                result = await adapter.write_item("edit", item_id=ITEM, password_file=str(path))
        arguments, stdin = op.call_args.args
        self.assertNotIn(SECRET, json.dumps(arguments))
        self.assertNotIn(SECRET, json.dumps(result))
        fields = json.loads(stdin)["fields"]
        self.assertEqual(fields[0]["value"], "keep")
        self.assertEqual(fields[1]["value"], SECRET)

    async def test_private_password_create_does_not_conflict_with_category_flag(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "password"
            path.write_text(SECRET)
            path.chmod(0o600)
            template = {"category": "LOGIN", "fields": []}
            with patch.object(adapter, "op", AsyncMock(side_effect=[json.dumps(template).encode(), json.dumps({"id": ITEM}).encode()])) as op:
                await adapter.write_item("create", title="Test", password_file=str(path))
        arguments, stdin = op.call_args.args
        self.assertNotIn("--category", arguments)
        self.assertEqual(arguments[2], "-")
        self.assertEqual(json.loads(stdin)["category"], "LOGIN")
        self.assertNotIn(SECRET, json.dumps(arguments))

    async def test_refuses_ambiguous_edits_and_multiple_password_sources(self):
        with patch.object(adapter, "op", AsyncMock()) as op:
            for kwargs in [dict(action="edit", item_id="A name"), dict(action="create", title="Test", generate_password=True, password_file="/tmp/nope"), dict(action="delete")]:
                with self.assertRaises(ValueError):
                    await adapter.write_item(**kwargs)
            op.assert_not_called()

    async def test_rejects_cross_vault_templates(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "template"
            path.write_text(json.dumps({"vault": {"id": "other"}}))
            path.chmod(0o600)
            with patch.object(adapter, "op", AsyncMock()) as op:
                with self.assertRaises(ValueError):
                    await adapter.write_item("create", title="Test", template_file=str(path))
                op.assert_not_called()

    async def test_refuses_template_password_edit_on_passkey_item(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "password"
            path.write_text(SECRET)
            path.chmod(0o600)
            original = {"fields": [{"id": "passkey", "type": "PASSKEY"}]}
            with patch.object(adapter, "op", AsyncMock(return_value=json.dumps(original).encode())) as op:
                with self.assertRaises(ValueError):
                    await adapter.write_item("edit", item_id=ITEM, password_file=str(path))
                self.assertEqual(op.await_count, 1)

    async def test_detects_fido2_credentials_in_existing_item(self):
        self.assertTrue(adapter.has_key_material({"fido2Credentials": [{"credentialId": "test"}]}))
        self.assertFalse(adapter.has_key_material({"fields": [], "fido2Credentials": []}))

    async def test_metadata_read_still_rejects_mutations_and_reveal(self):
        for arguments, reveal in [(["item", "delete", ITEM], False), (["item", "get", ITEM], True)]:
            with self.assertRaises(ValueError):
                await adapter.op_command(arguments, reveal)


class FileTests(unittest.TestCase):
    def test_rejects_readable_by_others_and_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "password"
            path.write_text(SECRET)
            path.chmod(0o644)
            with self.assertRaises(ValueError):
                adapter.private_file(str(path))
            path.chmod(0o600)
            link = Path(directory) / "link"
            link.symlink_to(path)
            with self.assertRaises(OSError):
                adapter.private_file(str(link))


if __name__ == "__main__":
    unittest.main()
