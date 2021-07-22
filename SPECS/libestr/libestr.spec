Summary:        String handling essentials library
Name:           libestr
Version:        0.1.10
Release:        5%{?dist}
License:        LGPLv2+
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          System Environment/Base
URL:            https://libestr.adiscon.com/
Source0:        http://%{name}.adiscon.com/files/download/%{name}-%{version}.tar.gz
BuildRequires:  gcc

%description
This package compiles the string handling essentials library
used by the Rsyslog daemon.

%package devel
Summary:        Development libraries for string handling
Requires:       libestr

%description devel
The package contains libraries and header files for
developing applications that use libestr.

%prep
%setup -q

%build
%configure
make %{?_smp_mflags}

%install
make DESTDIR=%{buildroot} install
find %{buildroot} -type f -name "*.la" -delete -print

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(-,root,root)
%license COPYING
%{_libdir}/*.so.*
%{_libdir}/*.a

%files devel
%defattr(-,root,root)
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc

%changelog
* Mon Oct 12 2020 Thomas Crain <thcrain@microsoft.com> - 0.1.10-5
- Remove %%sha1 line
- Lint to Mariner style
- Remove *.la files
- License verified.

* Sat May 09 2020 Nick Samson <nisamson@microsoft.com> - 0.1.10-4
- Added %%license line automatically

* Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> - 0.1.10-3
- Initial CBL-Mariner import from Photon (license: Apache2).

* Tue May 24 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> - 0.1.10-2
- GA - Bump release of all rpms

* Wed Jun 17 2015 Divya Thaluru <dthaluru@vmware.com> - 0.1.10-1
- Initial build. First version
