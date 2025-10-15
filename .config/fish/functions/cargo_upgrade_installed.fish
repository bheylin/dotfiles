function cargo_upgrade_installed
    for line in (cargo install --list | rg '^\w+')
        set -l fields (string split ' ' $line)
        set -l pkg_name $fields[1]
        set -l path $fields[3]

        if test -z $path
            cargo install --locked $pkg_name
        end
    end
end
