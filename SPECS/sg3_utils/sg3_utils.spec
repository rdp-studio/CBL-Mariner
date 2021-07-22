Summary:        Tools and Utilities for interaction with SCSI devices.
Name:           sg3_utils
Version:        1.44
Release:        2%{?dist}
License:        BSD
URL:            http://sg.danny.cz/sg/sg3_utils.html
Source0:        https://github.com/hreinecke/sg3_utils/archive/%{name}-%{version}.tar.gz
#Source0:        https://github.com/hreinecke/sg3_utils/archive/v%{version}.tar.gz
Group:          System/Tools.
Vendor:         Microsoft Corporation
Distribution:   Mariner
Provides:       sg_utils.

%description
Linux tools and utilities to send commands to SCSI devices.

%package -n libsg3_utils-devel
Summary:        Devel pacjage for sg3_utils.
Group:          Development/Library.

%description -n libsg3_utils-devel
Package containing static library object for development.

%prep
%setup -q

%build
#make some fixes required by glibc-2.28:
sed -i '/unistd/a #include <sys/sysmacros.h>' src/sg_dd.c src/sg_map26.c src/sg_xcopy.c

%configure

%install
make DESTDIR=%{buildroot} install %{?_smp_mflags}
install -m 755 scripts/scsi_logging_level %{buildroot}/%{_bindir}
install -m 755 scripts/rescan-scsi-bus.sh %{buildroot}/%{_bindir}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root)
%license COPYING
%{_bindir}/*
%{_mandir}/*
%{_libdir}/libsgutils2.so.*

%files -n libsg3_utils-devel
%defattr(-,root,root)
%{_libdir}/libsgutils2.a
%{_libdir}/libsgutils2.la
%{_libdir}/libsgutils2.so
%{_includedir}/scsi/*

%changelog
* Sat May 09 2020 Nick Samson <nisamson@microsoft.com> - 1.44-2
- Added %%license line automatically

*   Wed Mar 18 2020 Henry Beberman <henry.beberman@microsoft.com> 1.44-1
-   Update to 1.44. Removed ctr patch (fixed upstream). Fix URL. Fix Source0 URL. License verified.
*   Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 1.43-3
-   Initial CBL-Mariner import from Photon (license: Apache2).
*   Mon Sep 10 2018 Alexey Makhalov <amakhalov@vmware.com> 1.43-2
-   Fix compilation issue against glibc-2.28
*   Tue Oct 03 2017 Vinay Kulkarni <kulkarniv@vmware.com> 1.43-1
-   Update to v1.43
*   Tue May 24 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 1.42-2
-   GA - Bump release of all rpms
*   Thu Apr 14 2016 Kumar Kaushik <kaushikk@vmware.com> 1.42-1
-   Initial build. First version
