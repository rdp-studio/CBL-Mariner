Summary:        List Open Files
Name:           lsof
Version:        4.93.2
Release:        3%{?dist}
License:        BSD
URL:            https://github.com/lsof-org/lsof
Group:          System Environment/Tools
Vendor:         Microsoft Corporation
Distribution:   Mariner
#Source0:       https://github.com/lsof-org/%{name}/archive/%{version}.tar.gz
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  libtirpc-devel

Requires:   libtirpc

%description
Contains programs for generating Makefiles for use with Autoconf.

%prep
%setup -q

%build
./Configure -n linux
make CFGL="-L./lib -ltirpc" %{?_smp_mflags}

%install
mkdir -p %{buildroot}%{_sbindir}
install -v -m 0755 lsof %{buildroot}%{_sbindir}
mkdir -p %{buildroot}%{_mandir}/man8
install -v -m 0644 Lsof.8 %{buildroot}%{_mandir}/man8/lsof.8

%files
%defattr(-,root,root)
%license 00README
%{_sbindir}/*
%{_mandir}/man8/*

%changelog
*   Wed Jul 01 2020 Henry Beberman <henry.beberman@microsoft.com> - 4.93.2-3
-   Fix license to point to 00README which contains the license. Removes false dependency on /bin/ksh
*   Sat May 09 2020 Nick Samson <nisamson@microsoft.com> - 4.93.2-2
-   Added %%license line automatically
*   Mon Apr 27 2020 Pawel Winogrodzki <pawelwi@microsoft.com> 4.93.2-1
-   Bumping up the version to 4.93.2.
-   Fixed 'Source0' tag.
-   License verified.
*   Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 4.91-2
-   Initial CBL-Mariner import from Photon (license: Apache2).
*   Wed Sep 05 2018 Srivatsa S. Bhat <srivatsa@csail.mit.edu> 4.91-1
-   Update to version 4.91
*   Tue May 24 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 4.89-2
-   GA - Bump release of all rpms
*   Thu Jul 23 2015 Divya Thaluru <dthaluru@vmware.com> 4.89-1
-   Initial build.
