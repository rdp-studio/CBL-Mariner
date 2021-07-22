Summary:        Time zone data
Name:           tzdata
Version:        2021a
Release:        1%{?dist}
URL:            https://www.iana.org/time-zones
License:        Public Domain
Group:          Applications/System
Vendor:         Microsoft Corporation
Distribution:   Mariner
Source0:        https://data.iana.org/time-zones/releases/%{name}%{version}.tar.gz

BuildArch:      noarch

%description
Sources for time zone and daylight saving time data
%define blddir      %{name}-%{version}

%prep
rm -rf %{blddir}
install -vdm 755 %{blddir}
cd %{blddir}
tar xf %{SOURCE0} --no-same-owner
%build
%install
cd %{blddir}
ZONEINFO=%{buildroot}%{_datarootdir}/zoneinfo
install -vdm 755 $ZONEINFO/{posix,right}
for tz in etcetera southamerica northamerica europe africa antarctica  \
    asia australasia backward; do
    zic -L /dev/null    -d $ZONEINFO        -y "sh yearistype.sh" ${tz}
    zic -L /dev/null    -d $ZONEINFO/posix  -y "sh yearistype.sh" ${tz}
    zic -L leapseconds  -d $ZONEINFO/right  -y "sh yearistype.sh" ${tz}
done
cp -v zone.tab iso3166.tab zone1970.tab $ZONEINFO
zic -d $ZONEINFO -p America/New_York
install -vdm 755 %{buildroot}%{_sysconfdir}
ln -svf %{_datarootdir}/zoneinfo/UTC %{buildroot}%{_sysconfdir}/localtime

%files
%defattr(-,root,root)
%license %{blddir}/LICENSE
%config(noreplace) %{_sysconfdir}/localtime
%{_datadir}/*

%changelog
* Mon Apr 05 2021 CBL-Mariner Service Account <cblmargh@microsoft.com> - 2021a-1
- Update to version  "2021a".
- Removed 'pacificnew' and 'systemv' from parsed zone info, since they have been removed from the sources.

* Sat May 09 2020 Nick Samson <nisamson@microsoft.com> - 2019c-3
- Added %%license line automatically

*   Tue Apr 07 2020 Paul Monson <paulmon@microsoft.com> 2019c-2
-   Fix Source0.
*   Wed Mar 18 2020 Henry Beberman <henry.beberman@microsoft.com> 2019c-1
-   Update to 2019c. License verified.
*   Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 2019a-2
-   Initial CBL-Mariner import from Photon (license: Apache2).
*   Wed May 22 2019 Gerrit Photon <photon-checkins@vmware.com> 2019a-1
-   Automatic Version Bump
*   Thu Sep 06 2018 Anish Swaminathan <anishs@vmware.com> 2017b-3
-   Add zone1970.tab to zoneinfo
*   Mon May 01 2017 Bo Gan <ganb@vmware.com> 2017b-2
-   Remove (pre/post)trans, config file as noreplace.
*   Wed Apr 05 2017 Xiaolin Li <xiaolinl@vmware.com> 2017b-1
-   Updated to version 2017b.
*   Wed Dec 14 2016 Anish Swaminathan <anishs@vmware.com> 2016h-2
-   Preserve /etc/localtime symlink over upgrade
*   Thu Oct 27 2016 Anish Swaminathan <anishs@vmware.com> 2016h-1
-   Upgrade to 2016h
*   Tue May 24 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 2016a-2
-   GA - Bump release of all rpms
*   Tue Feb 23 2016 Harish Udaiya Kumar <hudaiyakumar@vmware.com> 2016a-1
-   Upgraded to version 2016a
*   Wed Nov 5 2014 Divya Thaluru <dthaluru@vmware.com> 2013i-1
-   Initial build. First version
