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

`install_casks.sh` installs:

- Brave Browser
- Google Drive
- Surfshark
- DeepL
- Ghostty
- VLC
- Anki
- Telegram
- Zoom
- GrandPerspective

Saved iTerm and VS Code settings remain available separately.

notes:
- save logs and other data from resolve and other applications

## Brave settings and extensions

See [brave/README.md](brave/README.md) for the portable settings snapshot,
extension install links, and export/restore commands.

## iTerm appearance

See [iterm/README.md](iterm/README.md) for portable profile appearance and how to
refresh it. The live iTerm preferences and Finder metadata remain local and are
not tracked.

## Syncing changes

Shell, Git, SSH, VS Code, shared agent instructions and the Claude statusline use
symlinks into this checkout after installation. Commit and push changes here to
save them on GitHub.
Brave and iTerm use explicit portable exports; refresh those separately using
their linked instructions. Private app state stays local.

## Shared agent instructions

`~/.agents/AGENTS.md` is the canonical shared path for global instructions.
Its Git-backed storage is `agents/AGENTS.md` in this checkout:

```text
~/.agents/AGENTS.md -> dotfiles/agents/AGENTS.md
~/.codex/AGENTS.md  -> ~/.agents/AGENTS.md
~/.claude/CLAUDE.md imports @~/.agents/AGENTS.md
```

`install.sh` installs the two symlinks, backing up existing files or obsolete
links. Claude's existing import stays in its own instructions file; on another
machine, add `@~/.agents/AGENTS.md` there while keeping any Claude-specific rules.
Edit `~/.agents/AGENTS.md`, then commit and push here. The links all reach the
same file, so changes are immediately shared. `~/.agents/agents/` is a separate
directory for agent definitions, currently empty; it is not the global rules file.
No copy or sync job is needed. Project instructions stay in each project's
`AGENTS.md`. Reusable workflows stay in the enabled Notion skills. Credentials,
local settings, logs and session data are not included.

## Ghostty

`ghostty/` saves the current font, keybindings and light/dark iTerm-derived
colors. `install_casks.sh` includes Ghostty; `install.sh` links its config and
themes (backing up existing regular files). Custom themes use portable names.

## tmux

`tmux.conf` links to `~/.tmux.conf`. New-tab and split shortcuts inherit the
current pane's directory, falling back to home when unavailable. `zshenv` recovers
tmux's requested start directory if tmux 3.8 launches a shell in a deleted working
directory, before Homebrew, mise or prompt setup runs. Existing sessions stay open.
The shell's last-working-directory plugin is disabled inside tmux so it cannot
replace an explicitly selected home directory with an unrelated cached project.

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
