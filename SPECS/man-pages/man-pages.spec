Summary:        Man pages
Name:           man-pages
Version:        4.16
Release:        4%{?dist}
License:        GPLv2+ and GPLv2 and BSD and Latex2e and Verbatim and GPL+ and BSD with advertising and MIT and LDPL and Public Domain
URL:            https://www.kernel.org/doc/man-pages
Group:          System Environment/Base
Vendor:         Microsoft Corporation
Distribution:   Mariner
Source0:        https://mirrors.edge.kernel.org/pub/linux/docs/%{name}/Archive/%{name}-%{version}.tar.gz
BuildArch:      noarch

%description
The Man-pages package contains over 1,900 man pages.

%prep
%setup -q
%build

%install
make DESTDIR=%{buildroot} install
#	The following man pages conflict with other packages
rm -vf %{buildroot}%{_mandir}/man3/getspnam.3
rm -vf %{buildroot}%{_mandir}/man5/passwd.5

%files

%defattr(-,root,root)
%license man3/copysign.3
%{_mandir}/man1/*
%{_mandir}/man2/*
%{_mandir}/man3/*
%{_mandir}/man4/*
%{_mandir}/man5/*
%{_mandir}/man6/*
%{_mandir}/man7/*
%{_mandir}/man8/*

%changelog
* Sat May 09 2020 Nick Samson <nisamson@microsoft.com> - 4.16-4
- Added %%license line automatically and updated licenses.

*   Wed Apr 15 2020 Nick Samson <nisamson@microsoft.com> 4.16-3
-   Updated Source0, URL; license verified.
*   Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 4.16-2
-   Initial CBL-Mariner import from Photon (license: Apache2).
*   Thu Sep 06 2018 Srivatsa S. Bhat <srivatsa@csail.mit.edu> 4.16-1
-   Update to version 4.16
*   Fri Mar 31 2017 Michelle Wang <michellew@vmware.com> 4.10-1
-   Update pacakge version
*   Tue May 24 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 4.04-2
-   GA - Bump release of all rpms
*   Thu Feb 25 2016 Anish Swaminathan <anishs@vmware.com>  4.04-1
-   Upgrade to 4.04
*   Wed Nov 5 2014 Divya Thaluru <dthaluru@vmware.com> 3.59-1
-   Initial build. First version
