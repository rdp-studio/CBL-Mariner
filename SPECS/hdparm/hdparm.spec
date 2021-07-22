Summary:	command line utility to set and view hardware parameters
Name:		hdparm
Version:	9.56
Release:        4%{?dist}
License:	BSD
URL:		http://sourceforge.net/projects/%{name}/
Source0:	http://downloads.sourceforge.net/hdparm/%{name}-%{version}.tar.gz
%define sha1 hdparm=9e143065115229c4f929530157627dc92e5f6deb
Group:		Applications/System
Vendor:         Microsoft Corporation
Distribution:   Mariner

%description
The Hdparm package contains a utility that is useful for controlling ATA/IDE
controllers and hard drives both to increase performance and sometimes to increase stability.

%prep
%setup -q
%build
make %{?_smp_mflags} CFLAGS="%{build_cflags}" LDFLAGS="%{build_ldflags}" STRIP="/bin/true"
%install
make DESTDIR=%{buildroot} binprefix=%{_prefix} install

#%check
#Commented out %check due to no test existence

%files
%defattr(-,root,root)
%license LICENSE.TXT
%{_sbindir}/hdparm
%{_mandir}/man8/hdparm.8*
%changelog
* Sun May 31 2020 Henry Beberman <henry.beberman@microsoft.com> - 9.56-4
- Update make to explicitly consume cflags and ldflags.
* Sat May 09 2020 Nick Samson <nisamson@microsoft.com> - 9.56-3
- Added %%license line automatically

*   Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 9.56-2
-   Initial CBL-Mariner import from Photon (license: Apache2).
* Mon Sep 10 2018 Alexey Makhalov <amakhalov@vmware.com> 9.56-1
- Version update to fix compilation issue againts glibc-2.28
* Wed Jul 05 2017 Chang Lee <changlee@vmware.com> 9.51-3
- Removed %check  due to no test existence.
* Tue Apr 25 2017 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 9.51-2
- Ensure non empty debuginfo
* Wed Jan 25 2017 Dheeraj Shetty <dheerajs@vmware.com> 9.51-1
- Initial build. First version
