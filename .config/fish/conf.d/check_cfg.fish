if test $(cfg status --short | wc -l) -ne 0
    echo "There are uncommited config changes tracked by the ~/.cfg repo"
    echo "Commit them using: cfg commit -m 'message'"
end
