set -ex

PYTHON_FULL_VERSION=$1
PYTHON_PKG_NAME=$2
TOOLCACHE_ROOT="/Users/runner/hostedtoolcache"

MAJOR_VERSION=$(echo $PYTHON_FULL_VERSION | cut -d '.' -f 1)
MINOR_VERSION=$(echo $PYTHON_FULL_VERSION | cut -d '.' -f 2)

PYTHON_MAJOR=python$MAJOR_VERSION
PYTHON_MAJOR_DOT_MINOR=python$MAJOR_VERSION.$MINOR_VERSION
PYTHON_MAJOR_MINOR=python$MAJOR_VERSION$MINOR_VERSION

PYTHON_TOOLCACHE_PATH=$TOOLCACHE_ROOT/Python
PYTHON_TOOLCACHE_VERSION_PATH=$PYTHON_TOOLCACHE_PATH/$PYTHON_FULL_VERSION
PYTHON_TOOLCACHE_VERSION_ARCH_PATH=$PYTHON_TOOLCACHE_VERSION_PATH/x64
PYTHON_FRAMEWORK_PATH="/Library/Frameworks/Python.framework/Versions/${MAJOR_VERSION}.${MINOR_VERSION}"
PYTHON_APPLICATION_PATH="/Applications/Python ${MAJOR_VERSION}.${MINOR_VERSION}"
PYTHON_TOOLCACHE_VERSION_ARCH_PATH_COMPLETE="$PYTHON_TOOLCACHE_VERSION_ARCH_PATH/.complete"

if test -f "$PYTHON_TOOLCACHE_VERSION_ARCH_PATH_COMPLETE"; then
    echo "Already installed"
    exit 0
else
    rm -rf $PYTHON_TOOLCACHE_VERSION_ARCH_PATH
fi

mkdir -p $PYTHON_TOOLCACHE_VERSION_ARCH_PATH
cd $PYTHON_TOOLCACHE_VERSION_ARCH_PATH

cp /Users/ltuser/hyperexecute_mac_content/python/$PYTHON_PKG_NAME ./

echo "Install Python binaries from prebuilt package"
sudo installer -pkg $PYTHON_PKG_NAME -target /

echo "Create hostedtoolcach symlinks (Required for the backward compatibility)"
echo "Create Python $PYTHON_FULL_VERSION folder"
mkdir -p $PYTHON_TOOLCACHE_VERSION_ARCH_PATH
cd $PYTHON_TOOLCACHE_VERSION_ARCH_PATH

ln -s "${PYTHON_FRAMEWORK_PATH}/bin" bin
ln -s "${PYTHON_FRAMEWORK_PATH}/include" include
ln -s "${PYTHON_FRAMEWORK_PATH}/share" share
ln -s "${PYTHON_FRAMEWORK_PATH}/lib" lib

echo "Create additional symlinks (Required for the UsePythonVersion Azure Pipelines task and the setup-python GitHub Action)"
ln -s ./bin/$PYTHON_MAJOR_DOT_MINOR python

cd bin/

# This symlink already exists if Python version with the same major.minor version is installed, 
# since we do not remove the framework folder
if [ ! -f $PYTHON_MAJOR_MINOR ]; then
    ln -s $PYTHON_MAJOR_DOT_MINOR $PYTHON_MAJOR_MINOR
fi

if [ ! -f python ]; then
    ln -s $PYTHON_MAJOR_DOT_MINOR python
fi

chmod +x ../python $PYTHON_MAJOR $PYTHON_MAJOR_DOT_MINOR $PYTHON_MAJOR_MINOR python

echo "Upgrading pip..."
./python -m ensurepip
./python -m pip install --ignore-installed pip --disable-pip-version-check --no-warn-script-location

echo "Install OpenSSL certificates"
sh -e "${PYTHON_APPLICATION_PATH}/Install Certificates.command"

echo "Create complete file"
touch $PYTHON_TOOLCACHE_VERSION_ARCH_PATH_COMPLETE
