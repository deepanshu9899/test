#! /bin/bash
set -e

PYTHON_FULL_VERSION=$1
PYTHON_PKG_NAME=$2
TOOLCACHE_ROOT="/Users/runner/hostedtoolcache"

MAJOR_VERSION=$(echo $PYTHON_FULL_VERSION | cut -d '.' -f 1)
MINOR_VERSION=$(echo $PYTHON_FULL_VERSION | cut -d '.' -f 2)

PYTHON_MAJOR=python$MAJOR_VERSION
PYTHON_MAJOR_DOT_MINOR=python$MAJOR_VERSION.$MINOR_VERSION
PYTHON_MAJORMINOR=python$MAJOR_VERSION$MINOR_VERSION

PYTHON_TOOLCACHE_PATH=$TOOLCACHE_ROOT/Python
PYTHON_TOOLCACHE_VERSION_PATH=$PYTHON_TOOLCACHE_PATH/$PYTHON_FULL_VERSION
PYTHON_TOOLCACHE_VERSION_ARCH_PATH=$PYTHON_TOOLCACHE_VERSION_PATH/x64
PYTHON_TOOLCACHE_VERSION_ARCH_PATH_COMPLETE="$PYTHON_TOOLCACHE_VERSION_ARCH_PATH/.complete"
CERT_COMMAND_PATH="/Users/ltuser/scripts/python/install_certificates_3.5_and_below.command"

if test -f "$PYTHON_TOOLCACHE_VERSION_ARCH_PATH_COMPLETE"; then
    echo "Already installed"
    exit 0
else
    rm -rf $PYTHON_TOOLCACHE_VERSION_ARCH_PATH
fi

mkdir -p $PYTHON_TOOLCACHE_VERSION_ARCH_PATH
cd $PYTHON_TOOLCACHE_VERSION_ARCH_PATH

cp /Users/ltuser/hyperexecute_mac_content/python/$PYTHON_PKG_NAME ./

echo "Extracting binaries"
tar -xvzf $PYTHON_TOOLCACHE_VERSION_ARCH_PATH/$PYTHON_PKG_NAME

rm -rf ./$PYTHON_PKG_NAME

echo "Create additional symlinks (Required for the UsePythonVersion Azure Pipelines task and the setup-python GitHub Action)"
ln -s ./bin/$PYTHON_MAJOR_DOT_MINOR python

cd bin/
ln -s $PYTHON_MAJOR_DOT_MINOR $PYTHON_MAJORMINOR
if [ ! -f python ]; then
    ln -s $PYTHON_MAJOR_DOT_MINOR python
fi

chmod +x ../python $PYTHON_MAJOR $PYTHON_MAJOR_DOT_MINOR $PYTHON_MAJORMINOR python

architecture=$(uname -m)
if [[ $architecture == "arm64" ]]; then
    echo "Installing certificates"
    /bin/bash /Users/ltuser/scripts/python/install_certificates_3.5_and_below.command $PYTHON_TOOLCACHE_VERSION_ARCH_PATH/bin/python
fi

echo "Upgrading PIP..."
#./python -m ensurepip 2>&1
./python -m pip install --ignore-installed pip 2>&1

echo "Create complete file"
touch $PYTHON_TOOLCACHE_VERSION_ARCH_PATH_COMPLETE
