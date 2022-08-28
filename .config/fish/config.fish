if status is-interactive
    # Commands to run in interactive sessions can go here
    set PATH $PATH ~/.cargo/bin /home/brianh/.local/share/gem/ruby/3.0.0/bin

    set -gx TERMINAL "alacritty"
    set -gx EDITOR "hx"
    set -gx BROWSER /usr/bin/firefox

    alias ls="exa"
    alias ll="ls -l"
    alias z="zoxide"
    alias config='/usr/bin/git --git-dir=$HOME/.cfg/ --work-tree=$HOME'

    if command -sq zoxide
        zoxide init fish | source
    end
    
    set -gx FZF_DEFAULT_COMMAND 'fd --type f'
    set -gx FZF_DEFAULT_OPTS '--multi --marker="*" --no-mouse --preview-window=wrap --border --height=90%'
    
    starship init fish | source
end
