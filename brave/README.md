# Brave

A portable snapshot of Grant's Default profile: browser appearance, tabs,
new-tab toggles, language, password-saving toggles and other selected settings,
plus third-party extension names, IDs and Chrome Web Store links.
Brave itself is already included in `../install_casks.sh`.

From the dotfiles root:

```sh
# Refresh tracked settings and extension inventory from this Mac.
python3 brave/manage.py export

# Print links; open each in Brave and install the extensions you want.
python3 brave/manage.py extensions

# On another Mac, launch Brave once to create the profile, then quit it fully.
python3 brave/manage.py restore
```

All commands accept `--profile /path/to/profile` for another profile or OS.
Restore merges the selected settings into existing Preferences, preserves other
keys and creates a dated backup beside that file. Restore is intentionally
separate from `install.sh`. It does not install extensions automatically.

Excluded: passwords, cookies, history, bookmarks, open tabs, account/sync data,
wallets, site permissions, search-provider URLs, machine-specific paths and
extension storage. No live profile files are symlinked into git. Built-in
extensions and leftover extension records without manifests are omitted.
Extension options, blocklists and Yomichan dictionaries need their own exports;
the extension inventory does not preserve those. Refresh after changing settings
(quit Brave first for its latest saved state). Some protected or version-specific
preferences may require reapplying through Brave's Settings UI after restore.
