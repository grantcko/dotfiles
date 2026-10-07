#!/usr/bin/env python3
"""Export portable Brave preferences; restore only explicitly selected keys."""
import argparse
import datetime
import json
import pathlib
import re
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
DEFAULT = pathlib.Path.home() / 'Library/Application Support/BraveSoftware/Brave-Browser/Default'
# Explicit paths exclude profile identity, history, sites, sessions and secrets.
PATHS = '''
bookmark_bar.show_on_all_tabs bookmark_bar.show_tab_groups
browser.allow_javascript_apple_events browser.show_forward_button browser.show_fullscreen_toolbar
download.open_pdf_in_system_reader intl.selected_languages
enable_do_not_track credentials_enable_service credentials_enable_autosignin
alternate_error_pages.enabled autofill.credit_card_enabled autofill.profile_enabled
spellcheck.dictionaries spellcheck.use_spelling_service
vertical_tabs.collapsed_state vertical_tabs.uncollapsed_width
webkit.webprefs.default_font_size webkit.webprefs.default_fixed_font_size
webkit.webprefs.minimum_font_size webkit.webprefs.force_dark_mode_enabled
brave.always_show_bookmark_bar_on_ntp brave.ask_widevine_install
brave.autocomplete_enabled brave.autofill_private_windows
brave.enable_media_router_on_restart brave.enable_window_closing_confirm
brave.location_bar_is_wide brave.mru_cycling_enabled
brave.show_bookmarks_button brave.show_fullscreen_reminder brave.show_side_panel_button
brave.top_site_suggestions_enabled brave.web_view_rounded_corners
'''.split()
# These sections contain display/behavior toggles. Only scalar booleans/numbers
# are exported; strings, URLs, identifiers and arbitrary subtrees are excluded.
TOGGLE_SECTIONS = ['brave.new_tab_page', 'brave.tabs', 'brave.sidebar',
                   'brave.shields', 'brave.speedreader', 'brave.omnibox',
                   'brave.commander', 'brave.web_discovery']


def read(path):
    return json.loads(path.read_text())


def get(data, path):
    for part in path.split('.'):
        if not isinstance(data, dict) or part not in data:
            return None
        data = data[part]
    return data


def put(data, path, value):
    parts = path.split('.')
    for part in parts[:-1]:
        data = data.setdefault(part, {})
    data[parts[-1]] = value


def snapshot(profile):
    prefs = read(profile / 'Preferences')
    selected = {p: get(prefs, p) for p in PATHS if get(prefs, p) is not None}
    for section in TOGGLE_SECTIONS:
        for key, value in (get(prefs, section) or {}).items():
            if isinstance(value, (bool, int, float)) and not any(word in key for word in ('count', 'last_used', 'shown', 'migration')):
                selected[f'{section}.{key}'] = value
    (HERE / 'settings.json').write_text(json.dumps(selected, indent=2, sort_keys=True) + '\n')
    secure = profile / 'Secure Preferences'
    extensions = read(secure).get('extensions', {}).get('settings', {}) if secure.exists() else {}
    extensions.update(prefs.get('extensions', {}).get('settings', {}))
    result = []
    for identifier, entry in sorted(extensions.items()):
        manifest = entry.get('manifest', {})
        if entry.get('location') != 1 or not manifest or not re.fullmatch('[a-p]{32}', identifier):
            continue
        name = manifest.get('name', identifier)
        if name.startswith('__MSG_'):
            name = identifier
        result.append({'id': identifier, 'name': name,
                       'url': f'https://chromewebstore.google.com/detail/{identifier}'})
    (HERE / 'extensions.json').write_text(json.dumps(result, indent=2) + '\n')
    print(f'Exported {len(selected)} preferences and {len(result)} extensions.')


def restore(profile):
    processes = subprocess.run(['pgrep', '-f', '/Brave Browser.app/Contents/'], capture_output=True)
    if processes.returncode == 0:
        raise SystemExit('Quit Brave completely before restoring preferences.')
    target = profile / 'Preferences'
    data = read(target)  # Initialize the profile in Brave first.
    selected = read(HERE / 'settings.json')
    for path, value in selected.items():
        if path not in PATHS and not any(path.startswith(s + '.') and path.count('.') == s.count('.') + 1
                                         and isinstance(value, (bool, int, float)) for s in TOGGLE_SECTIONS):
            raise SystemExit(f'Unapproved preference: {path}')
        put(data, path, value)
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backup = target.with_name(f'Preferences.backup-{stamp}')
    backup.write_bytes(target.read_bytes())
    backup.chmod(0o600)
    temporary = target.with_name(f'Preferences.dotfiles-{stamp}')
    temporary.write_text(json.dumps(data))
    temporary.chmod(target.stat().st_mode & 0o777)
    temporary.replace(target)
    print(f'Restored {len(selected)} preferences. Backup: {backup}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['export', 'restore', 'extensions'])
    parser.add_argument('--profile', type=pathlib.Path, default=DEFAULT)
    args = parser.parse_args()
    if args.action == 'export':
        snapshot(args.profile)
    elif args.action == 'restore':
        restore(args.profile)
    else:
        for entry in read(HERE / 'extensions.json'):
            print(f"{entry['name']}: {entry['url']}")


if __name__ == '__main__':
    main()
