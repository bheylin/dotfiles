# Call `cargo install` on all packages installed from crates.io
def cargo-pkg-upgrade-all [] {
  # compile list of packages that are installed from crates.io
  # locally installed packages should be installed from the local repo
  # a local package has a path
  # the installed packages are left aligned while the binaries are tabbed in
  # we're only interested in the installed packages, not the resulting binaries
  # the path column is null fo all packages install from crates.io
  let installed_from_crates_io = cargo install --list |
    lines |
    filter {|ln| $ln =~ '^\w' } |
    split column " " name version path |
    default '' path |
    where path == ''

  for $pkg in $installed_from_crates_io {
    cargo install --locked $pkg.name
  }
}
