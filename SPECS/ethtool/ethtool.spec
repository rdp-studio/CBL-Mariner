Summary:	Standard Linux utility for controlling network drivers and hardware
Name:		ethtool
Version:    5.0
Release:    2%{?dist}
License:	GPLv2
URL:		https://www.kernel.org/pub/software/network/ethtool/
Group:		Productivity/Networking/Diagnostic
Vendor:         Microsoft Corporation
Distribution:   Mariner
Source0:	https://www.kernel.org/pub/software/network/%{name}/%{name}-%{version}.tar.xz

%description
ethtool is the standard Linux utility for controlling network drivers and hardware,
particularly for wired Ethernet devices

%prep
%setup -q

%build
autoreconf -fi
%configure --sbindir=/sbin
make %{?_smp_mflags}

%install
make install DESTDIR=%{buildroot}

%check
make %{?_smp_mflags} check

%clean
rm -rf %{buildroot}/*

%files
%doc AUTHORS COPYING NEWS README ChangeLog
%defattr(-,root,root)
%license LICENSE
/sbin/*
%{_mandir}

%changelog
* Sat May 09 2020 Nick Samson <nisamson@microsoft.com> - 5.0-2
- Added %%license line automatically

*   Mon Mar 16 2020 Henry Beberman <henry.beberman@microsoft.com> 5.0-1
-   Update to 5.0. License verified.
*   Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 4.18-2
-   Initial CBL-Mariner import from Photon (license: Apache2).
* Mon Oct 01 2018 Alexey Makhalov <amakhalov@vmware.com> 4.18-1
- Version update
* Mon Apr 03 2017 Chang Lee <changlee@vmware.com> 4.8-1
- Upgraded to version 4.8
* Tue May 24 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 4.2-3
- GA - Bump release of all rpms
* Wed Jan 20 2016 Anish Swaminathan <anishs@vmware.com> 4.2-2
- Change file packaging.
* Mon Nov 30 2015 Harish Udaiya Kumar <hudaiyakumar@vmware.com> 4.2-1
- Initial build. First version
