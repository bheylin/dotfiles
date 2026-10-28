set fish_greeting ''
set SHELL (which fish)

set -gx BROWSER /usr/bin/librewolf
set -gx EDITOR ms
set -gx HELIX_RUNTIME ~/app_source/helix/runtime
set -gx TERMINAL ghostty

if command -sq rg
    set -gx FZF_DEFAULT_COMMAND 'rg --files --hidden'
    set -gx FZF_DEFAULT_OPTS '--multi --marker="*" --no-mouse --preview-window=wrap --border --height=90%'
end

fish_add_path -U ~/.cargo/bin
fish_add_path -m ~/.local/bin
fish_add_path -U ~/go/bin
fish_add_path -m /var/lib/flatpak/exports/bin

set -gx PGHOST /run/postgresql
set -gx PGPORT 5432
