if command -sq zoxide
    zoxide init fish | source
end

if command -sq starship
    starship init fish | source
end

if command -sq atuin
    set -gx ATUIN_NOBIND "true"
    atuin init fish | source
    bind \cr _atuin_search
end
