Summary:        A fast json library for C
Name:           libfastjson
Version:        0.99.8
Release:        4%{?dist}
License:        MIT
URL:            https://github.com/rsyslog/libfastjson
#Source0:       https://github.com/rsyslog/libfastjson/archive/v%{version}.tar.gz
Source0:        %{name}-%{version}.tar.gz
Group:          System Environment/Base
Vendor:         Microsoft Corporation
Distribution:   Mariner
BuildRequires:  libtool

%description
LIBFASTJSON is fast json library for C
It offers a small library with essential json handling functions, suffieciently good json support and very fast in processing.

%package	devel
Summary:	Development files for libfastjson
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}


%description	devel
This package contains libraries and header files for
developing applications that use libfastjson.

%prep
%setup -q
%build
sh autogen.sh
%configure --enable-shared --disable-static
make %{?_smp_mflags}

%install
make DESTDIR=%{buildroot} install
find %{buildroot} -name '*.la' -delete -print

%check
make check

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%license COPYING
%{_libdir}/libfastjson.so.*

%files devel
%{_includedir}/libfastjson
%{_libdir}/libfastjson.so
%{_libdir}/pkgconfig/libfastjson.pc


%changelog
* Sat May 09 2020 Nick Samson <nisamson@microsoft.com> - 0.99.8-4
- Added %%license line automatically

*       Tue Apr 21 2020 Eric Li <eli@microsoft.com> 0.99.8-3
-       Add #Source0: and delete sha1. Verified license. Fixed formatting.
*       Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 0.99.8-2
-       Initial CBL-Mariner import from Photon (license: Apache2).
*       Mon Sep 10 2018 Keerthana K <keerthanak@vmware.com> 0.99.8-1
-       Updated to version 0.99.8
*       Mon Apr 17 2017 Siju Maliakkal <smaliakkal@vmware.com>  0.99.4-1
-       Initial version
