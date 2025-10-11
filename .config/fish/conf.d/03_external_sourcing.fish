if command -sq zoxide
    zoxide init fish --no-cmd | source

    abbr --erase z &>/dev/null
    alias g=__zoxide_z
    alias z=__zoxide_z

    abbr --erase zi &>/dev/null
    alias gi=__zoxide_zi
    alias zi=__zoxide_zi
end

if command -sq starship
    starship init fish | source
end

if command -sq atuin
    set -gx ATUIN_NOBIND true
    atuin init fish | source
    bind \cr _atuin_search
end
