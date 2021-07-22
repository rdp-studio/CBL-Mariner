Summary:        Compressed file format
Name:           zchunk
Version:        1.1.5
Release:        2%{?dist}
License:        BSD 2-Clause AND MIT
URL:            https://github.com/zchunk/zchunk
Group:          Applications/System
Vendor:         Microsoft Corporation
Distribution:   Mariner
#Source0:        https://github.com/zchunk/zchunk/archive/%{version}.tar.gz
Source0:        https://github.com/zchunk/zchunk/archive/%{name}-%{version}.tar.gz

BuildRequires:  meson
BuildRequires:  curl-devel
BuildRequires:  openssl-devel
Requires:       %{name}-libs = %{version}-%{release}

%description
zchunk is a compressed file format that splits the file into independent
chunks.  This allows you to only download the differences when downloading a
new version of the file, and also makes zchunk files efficient over rsync.
zchunk files are protected with strong checksums to verify that the file you
downloaded is in fact the file you wanted.

%package libs
Summary:        Zchunk library
Group:          System/Libraries

%description libs
zchunk is a compressed file format that splits the file into independent
chunks.  This allows you to only download the differences when downloading a
new version of the file, and also makes zchunk files efficient over rsync.
zchunk files are protected with strong checksums to verify that the file you
downloaded is in fact the file you wanted.

This package contains the zchunk library, libzck.

%package devel
Summary:        Headers for building against zchunk
Group:          Development/Libraries/C and C++
Requires:       %{name}-libs = %{version}-%{release}

%description devel
zchunk is a compressed file format that splits the file into independent
chunks.  This allows you to only download the differences when downloading a
new version of the file, and also makes zchunk files efficient over rsync.
zchunk files are protected with strong checksums to verify that the file you
downloaded is in fact the file you wanted.

This package contains the headers necessary for building against the zchunk
library, libzck.

%prep
%setup -q
# Remove bundled sha libraries
rm -rf src/lib/hash/sha*

%build
mkdir build &&
cd build &&
meson --prefix=%{_prefix} -Dwith-openssl=enabled .. &&
ninja

%check
cd build
ninja test

%install
cd build
DESTDIR=%{buildroot}/ ninja install

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%license LICENSE
%doc README.md contrib
%doc LICENSE
%doc zchunk_format.txt
%{_bindir}/zck*
%{_bindir}/unzck

%files libs
%{_libdir}/libzck.so.*

%files devel
%{_libdir}/libzck.so
%{_libdir}/pkgconfig/zck.pc
%{_includedir}/zck.h

%changelog
*   Sat May 09 2020 Nick Samson <nisamson@microsoft.com> 1.1.5-2
-   Added %%license line automatically
*   Fri Mar 13 2020 Paul Monson <paulmon@microsoft.com> 1.1.5-1
-   Update to version 1.1.5
*   Wed Sep 25 2019 Saravanan Somasundaram <sarsoma@microsoft.com> 1.1.1-2
-   Initial CBL-Mariner import from Photon (license: Apache2).
*   Wed May 15 2019 Ankit Jain <ankitja@vmware.com> 1.1.1-1
-   Initial build. First version