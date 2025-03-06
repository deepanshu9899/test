#! /bin/bash

cd ~/Downloads
curl -L https://github.com/Homebrew/brew/tarball/master | tar xz --
mv Homebrew-brew-c5cbe64 homebrew
sudo mv homebrew /usr/local/homebrew

export PATH=$HOME/bin:/usr/local/bin:$PATH

alias axbrew='arch -x86_64 /usr/local/homebrew/bin/brew'
axbrew install gettext
sudo mkdir -p /usr/local/opt
sudo ln -s /usr/local/homebrew/Cellar/gettext/0.21.1 /usr/local/opt/gettext

axbrew install openssl@1.1
sudo ln -s /usr/local/homebrew/Cellar/openssl@1.1/1.1.1u/ /usr/local/opt/openssl@1.1

# "out ->%!(EXTRA string=Extracting binaries
# Create additional symlinks (Required for the UsePythonVersion Azure Pipelines task and the setup-python GitHub Action)
# Upgrading PIP...
# dyld[1504]: Library not loaded: '/usr/local/opt/gettext/lib/libintl.8.dylib'
#   Referenced from: '/Users/runner/hostedtoolcache/Python/3.5.10/x64/bin/python3.5'
#   Reason: tried: '/usr/local/opt/gettext/lib/libintl.8.dylib' (no such file), '/usr/local/lib/libintl.8.dylib' (no such file), '/usr/lib/libintl.8.dylib' (no such file)
# )"
# /bin/bash /Users/ltuser/scripts/python/install_certificates_3.5_and_below.command /Users/runner/hostedtoolcache/Python/3.5.10/x64/bin/python
