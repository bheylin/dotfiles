let workspace_indices = i3-msg -t get_workspaces | from json | get num

for $i in $workspace_indices {
  i3-msg $"[workspace=($i)] move workspace to output eDP"
}

i3-msg 'focus output eDP'