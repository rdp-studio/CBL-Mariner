Summary:        Netlink Protocol Library Suite
Name:           libnl3
Version:        3.4.0
Release:        6%{?dist}
License:        LGPLv2+
Group:          System Environment/Libraries
URL:            https://www.infradead.org/~tgr/libnl/
# It seems like the website no longer has the latest version of the source; this seems to be the correct source.
# Note that a branch tag made it into the name using underscores in the semver. This will have to be updated with versions.
Source0:        https://github.com/thom311/libnl/releases/download/%{name}_4_0/libnl-%{version}.tar.gz
Vendor:         Microsoft Corporation
Distribution:   Mariner
BuildRequires:  glib-devel
BuildRequires:  dbus-devel
Requires:       glib
Requires:       dbus

%description
The libnl suite is a collection of libraries providing APIs to netlink protocol based Linux kernel interfaces.
Netlink is a IPC mechanism primarly between the kernel and user space processes. It was designed to be a more flexible successor to ioctl to provide mainly networking related kernel configuration and monitoring interfaces.

%package devel
Summary:	Libraries and headers for the libnl
Requires:	libnl3
Provides:   pkgconfig(libnl-3.0)
Provides:   pkgconfig(libnl-cli-3.0)
Provides:   pkgconfig(libnl-genl-3.0)
Provides:   pkgconfig(libnl-idiag-3.0)
Provides:   pkgconfig(libnl-nf-3.0)
Provides:   pkgconfig(libnl-route-3.0)
Provides:   pkgconfig(libnl-xfrm-3.0)

%description devel
Headers and static libraries for the libnl

%prep
%setup -q -n libnl-%{version}
%build
%configure
make %{?_smp_mflags}

%install
make DESTDIR=%{buildroot} install

%check
make %{?_smp_mflags} check

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(-,root,root)
%license COPYING
%{_sysconfdir}/*
%{_bindir}/*
%{_libdir}/*.so.*
%{_mandir}/man8/*

%files devel
%defattr(-,root,root)
%{_includedir}/*
%{_libdir}/libnl/*
%{_libdir}/*.so
%{_libdir}/*.la
%{_libdir}/*.a
%{_libdir}/pkgconfig/libnl-3.0.pc
%{_libdir}/pkgconfig/libnl-cli-3.0.pc
%{_libdir}/pkgconfig/libnl-genl-3.0.pc
%{_libdir}/pkgconfig/libnl-idiag-3.0.pc
%{_libdir}/pkgconfig/libnl-nf-3.0.pc
%{_libdir}/pkgconfig/libnl-route-3.0.pc
%{_libdir}/pkgconfig/libnl-xfrm-3.0.pc

%changelog
* Fri Aug 28 2020 Thomas Crain <thcrain@microsoft.com> - 3.4.0-6
- Add pkg-config provides to devel package
- License verified
* Sat May 09 2020 Nick Samson <nisamson@microsoft.com> - 3.4.0-5
- Added %%license line automatically
* Thu Apr 30 2020 Nicolas Ontiveros <niontive@microsoft.com> - 3.4.0-4
- Rename from libnl to libnl3.
* Tue Apr 14 2020 Nick Samson <nisamson@microsoft.com> - 3.4.0-3
- Updated Source0, URL. License verified.
* Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> - 3.4.0-2
- Initial CBL-Mariner import from Photon (license: Apache2).
* Wed Sep 19 2018 Bo Gan <ganb@vmware.com> - 3.4.0-1
- Updated to version 3.4.0
* Tue Apr 11 2017 Harish Udaiya Kumar <hudaiyakumar@vmware.com> - 3.2.29-1
- Updated to version 3.2.29.
* Tue May 24 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> - 3.2.27-2
- GA - Bump release of all rpms
* Fri Jan 15 2016 Xiaolin Li <xiaolinl@vmware.com> - 3.2.27-1
- Updated to version 3.2.27
* Tue Sep 22 2015 Harish Udaiya Kumar <hudaiyakumar@vmware.com> - 3.2.25-2
- Updated build-requires after creating devel package for dbus.
* Tue Jun 23 2015 Divya Thaluru <dthaluru@vmware.com> - 3.2.25-1
- Initial build.
