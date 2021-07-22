%define openssl_cflags -DOPENSSL_NO_RIPEMD -DOPENSSL_NO_BF -DOPENSSL_NO_RC4 -DOPENSSL_NO_CAST -DOPENSSL_NO_DES

Summary:        libssh2 is a library implementing the SSH2 protocol.
Name:           libssh2
Version:        1.9.0
Release:        1%{?dist}
License:        BSD
URL:            https://www.libssh2.org/
Group:          System Environment/NetworkingLibraries
Vendor:         Microsoft Corporation
Distribution:   Mariner
Source0:        https://www.libssh2.org/download/libssh2-%{version}.tar.gz
%define sha1    libssh2=baf2d1fb338eee531ba9b6b121c64235e089e0f5
Patch0:         CVE-2019-17498.patch
BuildRequires:  openssl-devel
BuildRequires:  zlib-devel

Requires:       openssl
Requires:       zlib

%description
libssh2 is a client-side C library implementing the SSH2 protocol.

%package devel
Summary: Header files for libssh2
Group: System Environment/NetworkingLibraries
Requires: libssh2
%description devel
These are the header files of libssh2.

%prep
%setup -q
%patch0 -p1

%build
./configure --prefix=%{_prefix} \
    CFLAGS="%{openssl_cflags}" \
    CXXFLAGS="%{openssl_cflags}" \
    --bindir=%{_bindir} \
    --libdir=%{_libdir} \
    --mandir=%{_mandir} \
    --disable-static \
    --enable-shared
make

%install
make DESTDIR=%{buildroot} install
find %{buildroot} -name '*.la' -exec rm -f {} ';'

%files
%defattr(-,root,root)
%license COPYING
%{_libdir}/libssh2.so.*

%files devel
%defattr(-,root,root)
%{_includedir}/*
%{_libdir}/libssh2.so
%{_libdir}/pkgconfig/*
%{_mandir}/man3/*

%changelog
*   Wed May 13 2020 Paul Monson <paulmon@microsoft.com> 1.9.0-1
-   Update to version 1.9.0
*   Tue May 12 2020 Paul Monson <paulmon@microsoft.com> 1.8.0-4
-   Remove support for MD5, RIPEMD, BF, RC4, CAST, and DES
*   Sat May 09 2020 Nick Samson <nisamson@microsoft.com> - 1.8.0-4
-   Added %%license line automatically
*   Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 1.8.0-3
-   Initial CBL-Mariner import from Photon (license: Apache2).
*   Thu Mar 28 2019 Tapas Kundu <tkundu@vmware.com> 1.8.0-2
-   Fix for CVE-2019-3855
*   Wed Nov 30 2016 Xiaolin Li <xiaolinl@vmware.com> 1.8.0-1
-   Add libssh2 1.8.0 package.
