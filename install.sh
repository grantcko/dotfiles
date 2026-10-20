#!/bin/zsh

# Resolve files relative to this script, even when launched from another directory.
DOTFILES_DIR="${0:A:h}"
cd "$DOTFILES_DIR" || exit 1

# Back up existing regular files without overwriting earlier backups.
backup() {
  target=$1
  if [ -e "$target" ]; then
    if [ ! -L "$target" ]; then
      mv "$target" "$target.backup.$(date +%Y%m%d%H%M%S).$$"
      echo "-----> Moved your old $target config file to a timestamped backup"
    fi
  fi
}

symlink() {
  file=$1
  link=$2
  if [ ! -e "$link" ] && [ ! -L "$link" ]; then
    echo "-----> Symlinking your new $link"
    ln -s "$file" "$link"
  fi
}

# For all files `$name` in the present folder except `*.sh`, `README.md`, `settings.json`,
# and `config`, backup the target file located at `~/.$name` and symlink `$name` to `~/.$name`
for name in aliases gitconfig irbrc rspec zprofile zshrc; do
  if [ ! -d "$name" ]; then
    target="$HOME/.$name"
    backup "$target"
    symlink "$DOTFILES_DIR/$name" "$target"
  fi
done

# Install each optional plugin independently.
ZSH_PLUGINS_DIR="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins"
mkdir -p "$ZSH_PLUGINS_DIR"
for plugin in zsh-autosuggestions zsh-syntax-highlighting; do
  if [ ! -d "$ZSH_PLUGINS_DIR/$plugin" ]; then
    git clone "https://github.com/zsh-users/$plugin" "$ZSH_PLUGINS_DIR/$plugin" || exit 1
  fi
done

# Symlink VS Code settings and keybindings to the present `settings.json` and `keybindings.json` files
# If it's a macOS
if [[ `uname` =~ "Darwin" ]]; then
  CODE_PATH=~/Library/Application\ Support/Code/User
# Else, it's a Linux
else
  CODE_PATH=~/.config/Code/User
  # If this folder doesn't exist, it's a WSL
  if [ ! -e "$CODE_PATH" ]; then
    CODE_PATH=~/.vscode-server/data/Machine
  fi
fi

mkdir -p "$CODE_PATH"
for name in settings.json keybindings.json; do
  target="$CODE_PATH/$name"
  backup "$target"
  symlink "$DOTFILES_DIR/$name" "$target"
done

# Symlink SSH config file to the present `config` file for macOS and add SSH passphrase to the keychain
if [[ `uname` =~ "Darwin" ]]; then
  mkdir -p "$HOME/.ssh"
  target=~/.ssh/config
  backup "$target"
  symlink "$DOTFILES_DIR/config" "$target"
  if [ -f "$HOME/.ssh/id_ed25519" ]; then
    ssh-add --apple-use-keychain "$HOME/.ssh/id_ed25519"
  fi
fi

# Ghostty: keep settings and custom themes in this checkout.
if [[ "$(uname)" == "Darwin" ]]; then
  GHOSTTY_DIR="$HOME/Library/Application Support/com.mitchellh.ghostty"
else
  GHOSTTY_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/ghostty"
fi
mkdir -p "$GHOSTTY_DIR/themes"
for name in config.ghostty themes/iTerm-light themes/iTerm-dark; do
  target="$GHOSTTY_DIR/$name"
  backup "$target"
  symlink "$DOTFILES_DIR/ghostty/$name" "$target"
done

# Claude Code: symlink statusline script; copy settings template if no settings exist yet
mkdir -p "$HOME/.claude"
symlink "$DOTFILES_DIR/claude/statusline-command.sh" "$HOME/.claude/statusline-command.sh"
chmod +x "$HOME/.claude/statusline-command.sh"
if [ ! -f "$HOME/.claude/settings.json" ]; then
  echo "-----> Copying Claude Code settings template to ~/.claude/settings.json"
  cp "$DOTFILES_DIR/claude/settings.json" "$HOME/.claude/settings.json"
fi

# Refresh the current terminal with the newly installed configuration
exec zsh

echo "👌 Carry on with git setup!"
