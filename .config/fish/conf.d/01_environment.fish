set fish_greeting ''
set SHELL (which fish)

set -gx BROWSER /var/lib/flatpak/exports/bin/engineer.atlas.Nyxt
set -gx EDITOR hx
set -gx TERMINAL rxvt

if command -sq rg
    set -gx FZF_DEFAULT_COMMAND 'rg --files --hidden'
    set -gx FZF_DEFAULT_OPTS '--multi --marker="*" --no-mouse --preview-window=wrap --border --height=90%'
end

fish_add_path -U ~/.cargo/bin
fish_add_path -m ~/.local/bin
fish_add_path -m /var/lib/flatpak/exports/bin

set -gx PGHOST /run/postgresql
set -gx PGPORT 5432
