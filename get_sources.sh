#!/bin/bash
source sources.cfg
echo "Checking Linux $LINUX_VERSION release tarball"
if [[ ! -e SOURCES/$LINUX_RELEASE_FILE ]] ; then
    wget -P SOURCES/ $LINUX_RELEASE_BASE/$LINUX_RELEASE_FILE || exit 1
fi
if [[ ! -e SOURCES/$LINUX_RELEASE_FILE_SIG ]]; then
    wget -P SOURCES/ $LINUX_RELEASE_BASE/$LINUX_RELEASE_FILE_SIG || exit 1
fi
# Signature is on uncompressed image
echo "Uncompressing release file and checking signature"
xz -cd SOURCES/$LINUX_RELEASE_FILE | gpg2 --status-fd 1 --verify SOURCES/$LINUX_RELEASE_FILE_SIG - \
    | grep -q "GOODSIG ${LINUX_KEY}" || exit 1

echo "All sources present."
