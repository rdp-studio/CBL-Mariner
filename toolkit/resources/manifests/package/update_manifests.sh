#!/bin/bash

print_usage() {
    echo "Usage:"
    echo "update_manifests.sh x86_64|aarch64 ./toolchain_built_rpms_all.tar.gz"
    echo
    echo "Run this script to automatically update toolchain_*.txt and pkggen_core_*.txt based on the contents of toolchain_built_rpms_all.tar.gz"
    exit
}

TmpPkgGen=pkggen_core_temp.txt

if [ -z "$1" ] || [ -z "$2" ]; then
    print_usage
fi

if [[ "$1" == "x86_64" ]] || [[ "$1" == "aarch64" ]]; then
    ToolchainManifest=toolchain_"$1".txt
    PkggenManifest=pkggen_core_"$1".txt
else
    echo "Invalid architecture: '$1'"
    print_usage
fi

if [ -f "$2" ]; then
    TOOLCHAIN_ARCHIVE=$2
else
    echo "Bad toolchain parameter: '$2' does not exist"
    print_usage
fi

echo Updating files...

generate_toolchain () {
    # First generate toolchain_*.txt from TOOLCHAIN_ARCHIVE (toolchain_built_rpms_all.tar.gz)
    # This file is a sorted list of all toolchain packages in the tarball.
    tar -ztf "$TOOLCHAIN_ARCHIVE" | sed 's+built_rpms_all/++g' | sed '/^$/d' > "$ToolchainManifest"
    # Now sort the file in place
    sort -o "$ToolchainManifest" "$ToolchainManifest"
}

# Remove specific packages that are not needed in pkggen_core
remove_packages_for_pkggen_core () {
    sed -i '/alsa-lib-/d' $TmpPkgGen
    sed -i '/ca-certificates-[0-9]/d' $TmpPkgGen
    sed -i '/ca-certificates-legacy/d' $TmpPkgGen
    sed -i '/ca-certificates-microsoft/d' $TmpPkgGen
    sed -i '/cyrus-sasl/d' $TmpPkgGen
    sed -i '/libtasn1-d/d' $TmpPkgGen
    sed -i '/libffi-d/d' $TmpPkgGen
    sed -i '/p11-kit-d/d' $TmpPkgGen
    sed -i '/p11-kit-server/d' $TmpPkgGen
    sed -i '/^check/d' $TmpPkgGen
    sed -i '/cmake/d' $TmpPkgGen
    sed -i '/cracklib/d' $TmpPkgGen
    sed -i '/createrepo_c-devel/d' $TmpPkgGen
    sed -i '/docbook-xml/d' $TmpPkgGen
    sed -i '/docbook-xsl/d' $TmpPkgGen
    sed -i '/e2fsprogs-[0-9]/d' $TmpPkgGen
    sed -i '/e2fsprogs-devel/d' $TmpPkgGen
    sed -i '/e2fsprogs-lang/d' $TmpPkgGen
    sed -i '/openj/d' $TmpPkgGen
    sed -i '/freetype2/d' $TmpPkgGen
    sed -i '/finger-[[:alpha:]]/d' $TmpPkgGen
    sed -i '/gfortran/d' $TmpPkgGen
    sed -i '/glib-devel/d' $TmpPkgGen
    sed -i '/glib-schemas/d' $TmpPkgGen
    sed -i '/gmock/d' $TmpPkgGen
    sed -i '/gperf/d' $TmpPkgGen
    sed -i '/gpgme-[[:alpha:]]/d' $TmpPkgGen
    sed -i '/gtest/d' $TmpPkgGen
    sed -i '/kbd/d' $TmpPkgGen
    sed -i '/kmod/d' $TmpPkgGen
    sed -i '/krb5-[[:alpha:]]/d' $TmpPkgGen
    sed -i '/libarchive/d' $TmpPkgGen
    sed -i '/libcap-ng-[[:alpha:]]/d' $TmpPkgGen
    sed -i '/libgpg-error-[[:alpha:]]/d' $TmpPkgGen
    sed -i '/libgcrypt-[[:alpha:]]/d' $TmpPkgGen
    sed -i '/libsemanage-[[:alpha:]]/d' $TmpPkgGen
    sed -i '/libselinux-[[:alpha:]]/d' $TmpPkgGen
    sed -i '/libsepol-[[:alpha:]]/d' $TmpPkgGen
    sed -i '/libsolv-tools/d' $TmpPkgGen
    sed -i '/libxml2-python/d' $TmpPkgGen
    sed -i '/libxslt/d' $TmpPkgGen
    sed -i '/Linux-PAM/d' $TmpPkgGen
    sed -i '/lua-devel/d' $TmpPkgGen
    sed -ri '/mariner-repos-(extras|ui)/d' $TmpPkgGen
    sed -i '/npth-[[:alpha:]]/d' $TmpPkgGen
    sed -i '/pcre-devel/d' $TmpPkgGen
    sed -i '/perl-D/d' $TmpPkgGen
    sed -i '/perl-libintl/d' $TmpPkgGen
    sed -i '/perl-Object-Accessor/d' $TmpPkgGen
    sed -i '/perl-Test-Warnings/d' $TmpPkgGen
    sed -i '/perl-Text-Template/d' $TmpPkgGen
    sed -i '/python/d' $TmpPkgGen
    sed -i '/shadow/d' $TmpPkgGen
    sed -i '/tcp_wrappers-[[:alpha:]]/d' $TmpPkgGen
    sed -i '/unzip/d' $TmpPkgGen
    sed -i '/util-linux-lang/d' $TmpPkgGen
    sed -i '/wget/d' $TmpPkgGen
    sed -i '/which/d' $TmpPkgGen
    sed -i '/XML-Parser/d' $TmpPkgGen
    sed -i '/^zstd-doc/d' $TmpPkgGen
    sed -i '/^zip-/d' $TmpPkgGen
}

# create pkggen_core file in correct order
generate_pkggen_core () {
    # $1 = (pkggen_core_x86_64.txt or pkggen_core_aarch64.txt)
    {
        grep "^filesystem-" $TmpPkgGen
        grep "^kernel-headers-" $TmpPkgGen
        grep "^glibc-" $TmpPkgGen
        grep "^zlib-" $TmpPkgGen
        grep "^file-" $TmpPkgGen
        grep "^binutils-" $TmpPkgGen
        grep "^gmp-" $TmpPkgGen
        grep "^mpfr-" $TmpPkgGen
        grep "^libmpc-" $TmpPkgGen
        grep "^libgcc-" $TmpPkgGen
        grep "^libstdc++-" $TmpPkgGen
        grep "^libgomp-" $TmpPkgGen
        grep "^gcc-" $TmpPkgGen
        grep "^pkg-config-" $TmpPkgGen
        grep "^ncurses-" $TmpPkgGen
        grep "^readline-" $TmpPkgGen
        grep "^coreutils-" $TmpPkgGen
        grep "^bash-" $TmpPkgGen
        grep "^bzip2-" $TmpPkgGen
        grep "^sed-" $TmpPkgGen
        grep "^procps-ng-" $TmpPkgGen
        grep "^m4-" $TmpPkgGen
        grep "^grep-" $TmpPkgGen
        grep "^diffutils-" $TmpPkgGen
        grep "^gawk-" $TmpPkgGen
        grep "^findutils-" $TmpPkgGen
        grep "^gettext-" $TmpPkgGen
        grep "^gzip-" $TmpPkgGen
        grep "^make-" $TmpPkgGen
        grep "^mariner-release-" $TmpPkgGen
        grep "^patch-" $TmpPkgGen
        grep "^util-linux-" $TmpPkgGen
        grep "^tar-" $TmpPkgGen
        grep "^xz-" $TmpPkgGen
        grep "^zstd-" $TmpPkgGen
        grep "^libtool-" $TmpPkgGen
        grep "^flex-" $TmpPkgGen
        grep "^bison-" $TmpPkgGen
        grep "^popt-" $TmpPkgGen
        grep "^nspr-" $TmpPkgGen
        grep "^sqlite-" $TmpPkgGen
        grep "^nss-" $TmpPkgGen
        grep "^elfutils-" $TmpPkgGen
        grep "^expat-" $TmpPkgGen
        grep "^libpipeline-" $TmpPkgGen
        grep "^gdbm-" $TmpPkgGen
        grep "^perl-" $TmpPkgGen
        grep "^texinfo-" $TmpPkgGen
        grep "^autoconf-" $TmpPkgGen
        grep "^automake-" $TmpPkgGen
        grep "^openssl-" $TmpPkgGen
        grep "^libcap-" $TmpPkgGen
        grep "^libdb-" $TmpPkgGen
        grep "^rpm-" $TmpPkgGen
        grep "^cpio-" $TmpPkgGen
        grep "^e2fsprogs-" $TmpPkgGen
        grep "^libsolv-" $TmpPkgGen
        grep "^libssh2-" $TmpPkgGen
        grep "^curl-" $TmpPkgGen
        grep "^tdnf-" $TmpPkgGen
        grep "^createrepo_c-" $TmpPkgGen
        grep "^libxml2-" $TmpPkgGen
        grep "^glib-" $TmpPkgGen
        grep "^libltdl-" $TmpPkgGen
        grep "^pcre-" $TmpPkgGen
        grep "^krb5-" $TmpPkgGen
        grep "^lua-" $TmpPkgGen
        grep "^mariner-rpm-macros-" $TmpPkgGen
        grep "^mariner-check-" $TmpPkgGen
        grep "^libassuan-" $TmpPkgGen
        grep "^libgpg-error-" $TmpPkgGen
        grep "^libgcrypt-" $TmpPkgGen
        grep "^libksba-" $TmpPkgGen
        grep "^npth-" $TmpPkgGen
        grep "^pinentry-" $TmpPkgGen
        grep "^gnupg2-" $TmpPkgGen
        grep "^gpgme-" $TmpPkgGen
        grep "^mariner-repos-" $TmpPkgGen
        grep "^libffi-" $TmpPkgGen
        grep "^libtasn1-" $TmpPkgGen
        grep "^p11-kit-" $TmpPkgGen
        grep "^ca-certificates-shared-" $TmpPkgGen
        grep "^ca-certificates-tools-" $TmpPkgGen
        grep "^ca-certificates-base-" $TmpPkgGen
        grep "^cyrus-sasl-" $TmpPkgGen
        grep "^libselinux-" $TmpPkgGen

    } > "$1"
}

# Generate toolchain_*.txt based on the toolchain_built_rpms_all.tar.gz file contents
generate_toolchain

# Next, generate pkggen_core_*.txt
# Note that toolchain_*.txt is a superset of pkggen_core_*.txt
# Create a temp file that can be edited to remove the unnecessary files
cp "$ToolchainManifest" $TmpPkgGen

# Remove all *-debuginfo except openssl
R=$(grep openssl-debuginfo "$ToolchainManifest")
sed -i '/debuginfo/d' $TmpPkgGen
# Add the openssl-debuginfo file back
echo "$R" >> $TmpPkgGen

# Modify the temp file by removing other unneeded packages
remove_packages_for_pkggen_core

# Now create pkggen_core_*.txt file in correct order
# The packages are listed in the order they will be installed into the chroot
generate_pkggen_core "$PkggenManifest"

rm $TmpPkgGen
