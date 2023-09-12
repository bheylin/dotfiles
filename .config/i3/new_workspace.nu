let max_workspace_index = i3-msg -t get_workspaces | from json | get num | math max
let new_workspace_index = $max_workspace_index + 1
i3-msg workspace $new_workspace_index
