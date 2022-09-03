set fish_greeting ''
set SHELL (which fish)

set -gx TERMINAL "alacritty"
set -gx EDITOR "hx"
set -gx BROWSER /usr/bin/firefox

if command -sq rg
    set -gx FZF_DEFAULT_COMMAND 'rg --files --hidden'
    set -gx FZF_DEFAULT_OPTS '--multi --marker="*" --no-mouse --preview-window=wrap --border --height=90%'
end

fish_add_path -U ~/.cargo/bin 
fish_add_path -U /home/brianh/.local/share/gem/ruby/3.0.0/bin
