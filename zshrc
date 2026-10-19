ZSH=$HOME/.oh-my-zsh

# You can change the theme with another one from https://github.com/robbyrussell/oh-my-zsh/wiki/themes
ZSH_THEME="robbyrussell"

# Useful oh-my-zsh plugins
plugins=(git gitfast last-working-dir common-aliases history-substring-search)

# Add syntax highlighting only if installed
[ -d "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting" ] && plugins+=(zsh-syntax-highlighting)

# (macOS-only) Prevent Homebrew from reporting - https://github.com/Homebrew/brew/blob/master/docs/Analytics.md
export HOMEBREW_NO_ANALYTICS=1

# Disable warning about insecure completion-dependent directories
ZSH_DISABLE_COMPFIX=true

# Actually load Oh-My-Zsh
source "${ZSH}/oh-my-zsh.sh"
unalias rm # No interactive rm by default (brought by plugins/common-aliases)
unalias lt # we need `lt` for https://github.com/localtunnel/localtunnel

# Linux-specific Gemini path
if [[ "$(uname)" == "Linux" ]]; then
    export PATH="$HOME/.npm-global/bin:$PATH"
fi

# Load rbenv if installed
export PATH="${HOME}/.rbenv/bin:${PATH}"
type -a rbenv > /dev/null && eval "$(rbenv init -)"

# Shared aliases are maintained separately from toolchain setup.
[[ -f "$HOME/.aliases" ]] && source "$HOME/.aliases"


# Load direnv only if it exists
if command -v direnv >/dev/null; then
  eval "$(direnv hook zsh)"
fi


# Kill processes using a TCP port: k 3004
k() {
  local pids
  pids=$(lsof -ti :"$1")
  [ -n "$pids" ] && kill $pids
}
export PATH="$HOME/.vit/venv/bin:$PATH"
alias vps="$HOME/bin/vps"
alias zvps="$HOME/bin/zvps"

# >>> grok installer >>>
export PATH="$HOME/.grok/bin:$PATH"
# <<< grok installer <<<

# >>> Hermes fuzzy editor helpers >>>
export PATH="$HOME/.local/bin:$PATH"
if command -v fzf >/dev/null 2>&1; then
  export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
  export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
  export FZF_ALT_C_COMMAND='fd --type d --hidden --follow --exclude .git'
  export FZF_DEFAULT_OPTS='--height=80% --layout=reverse --border --info=inline --preview-window=right:60%:wrap'

  # Load fzf keybindings only in a real terminal. Non-TTY shells can error on zle.
  if [ -t 0 ] && [ -t 1 ]; then
    if [ -n "${ZSH_VERSION:-}" ]; then
      source <(fzf --zsh) 2>/dev/null || true
    elif [ -n "${BASH_VERSION:-}" ]; then
      eval "$(fzf --bash)" 2>/dev/null || true
    fi
  fi

  cdf() {
    local dir
    dir=$(fd --type d --hidden --follow --exclude .git . "${1:-.}" | fzf --prompt='cd> ' --preview='command ls -la {} 2>/dev/null') && cd "$dir"
  }

  alias tf='telescope files'
  alias tg='telescope grep'
fi
# <<< Hermes fuzzy editor helpers <<<

# Keep mise last: it must run after every PATH modification so its managed
# Ruby and Rails toolchain wins over Apple Ruby and rbenv shims.
if command -v mise >/dev/null 2>&1; then
  eval "$(mise activate zsh)"
fi
