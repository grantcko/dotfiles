## Grant's Dotfiles

This is a fork from Le Wagon's dotfiles. [Here is their whole computer setup](github.com/lewagon/setup). Default to those instructions. Covers 99% of what I use. I've added a bit.

## Requirements
Mac

## Setting up the terminal:
1. Run:
```
zsh install.sh
```

2. Open terminal preferences. Navigate to profiles and import the file ending in `.terminal`. Set set terminal to open up using it and set as default.

## Toolset

- [oh-my-zsh](http://ohmyz.sh/)
- [Visual Studio Code](https://code.visualstudio.com/)
- [git](https://git-scm.com/)

## Native Mac apps
- FBReader
- Brave Browser
- Biglybt
- Google Drive
- surfshark
- visual studio code
- davinci resolve
- adobe lightroom
- adobe photoshop
- deepl
- libreoffice
- surfshark
- app cleaner

notes:
- save logs and other data from resolve and other applications

## Brave settings and extensions

See [brave/README.md](brave/README.md) for the portable settings snapshot,
extension install links, and export/restore commands.

## iTerm appearance

See [iterm/README.md](iterm/README.md) for portable profile appearance and how to
refresh it. The live iTerm preferences and Finder metadata remain local and are
not tracked.

## Current machine setup

- Shell startup uses mise last so its managed tools take precedence, with rbenv
  and direnv integration retained. Shared aliases load from `~/.aliases`.
- `vps-sync` is available only when `~/code/scripts/vps-sync.sh` exists.
- SSH connection reuse and agent forwarding for `openclaw-nbg1` reflect the
  existing configuration. Agent forwarding is enabled only for that host.
- Git's Cursor credential-helper entries require the installed helper at the
  recorded path. They contain no credentials. No default pull reconciliation
  policy is set here; choose an explicit pull strategy when needed.
- The Claude bootstrap template leaves bypass-mode warning acceptance to the
  user. Existing `~/.claude/settings.json` is not overwritten by installation.
