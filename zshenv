# tmux 3.8 can inherit a deleted server cwd even with new-window -c.
# Recover its recorded start directory before login/interactive setup runs.
if [[ "$PWD" != /* || ! -d "$PWD" ]]; then
  () {
    local start_dir
    if [[ -n "${TMUX_PANE:-}" ]] && (( $+commands[tmux] )); then
      start_dir=$(command tmux display-message -p -t "$TMUX_PANE" '#{pane_start_path}' 2>/dev/null)
    fi
    [[ -n "$start_dir" && -d "$start_dir" ]] || start_dir="$HOME"
    builtin cd -q -- "$start_dir" 2>/dev/null || builtin cd -q -- /
  }
fi

. "$HOME/.cargo/env"

# Disable T3 Code product analytics and relay diagnostics.
export T3CODE_TELEMETRY_ENABLED=false
