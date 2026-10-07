# Portable iTerm appearance

`profiles.json` contains the names, fonts, colors and selected appearance toggles
of the Default and tmux profiles. It excludes commands, key mappings, environment
variables, paths, session/window arrangements, host/user records, AI settings and
API-server settings. Generated profile IDs differ from the live profiles.

Refresh the snapshot from the dotfiles root:

```sh
python3 iterm/export.py
```

Review the diff before committing, including profile names. This command only
reads the live preferences and writes the portable snapshot.

On another Mac, copy `profiles.json` into
`~/Library/Application Support/iTerm2/DynamicProfiles/`. iTerm loads the profiles
with `(portable)` appended to their names. Unspecified attributes inherit from
that Mac's default profile; this is an appearance snapshot, not a full settings
restore. See the [iTerm dynamic-profile documentation](https://iterm2.com/documentation-dynamic-profiles.html).

The current Mac still uses the repository root as its custom-preferences folder.
Its raw `com.googlecode.iterm2.plist` stays on disk and is ignored by Git. Do not
force-add it: it contains private session state. Existing Git history is unchanged.
