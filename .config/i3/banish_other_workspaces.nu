let unfocused_workspace_indices = i3-msg -t get_workspaces | from json | where not focused

for $i in $unfocused_workspace_indices {
  i3-msg $"[workspace=($i)] move workspace to output next"
}
