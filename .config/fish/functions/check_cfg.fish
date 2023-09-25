if test $(cfg status --short | wc -l) -ne 0
    echo "There are uncommitted config changes tracked by the ~/.cfg repo"
    echo "Commit them using: cfg commit -am 'message'"
    echo
end

if test $(cfg log @{u}.. | wc -l) -ne 0
    echo "There are unpushed config changes tracked by the ~/.cfg repo"
    echo "Push them using: cfg push"
    echo 
end
