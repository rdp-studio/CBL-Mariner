Summary:        Ruby
Name:           ruby
Version:        2.6.7
Release:        1%{?dist}
License:        (Ruby OR BSD) AND Public Domain AND MIT AND CC0 AND zlib AND UCD
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          System Environment/Security
URL:            https://www.ruby-lang.org/en/
Source0:        https://cache.ruby-lang.org/pub/ruby/2.6/%{name}-%{version}.tar.xz
BuildRequires:  openssl-devel
BuildRequires:  readline
BuildRequires:  readline-devel
BuildRequires:  tzdata
Requires:       gmp
Requires:       openssl
%if %{with_check}
BuildRequires:  shadow-utils
BuildRequires:  sudo
%endif

%description
The Ruby package contains the Ruby development environment.
This is useful for object-oriented scripting.

%prep
%autosetup -p1

%build
%configure \
        --enable-shared \
        --with-compress-debug-sections=no \
        --docdir=%{_docdir}/%{name}-%{version}
make %{?_smp_mflags} COPY="cp -p"

%install
[ %{buildroot} != "/"] && rm -rf %{buildroot}/*
make DESTDIR=%{buildroot} install

%check
chmod g+w . -R
useradd test -G root -m
# Only run stable tests
sudo -u test make test TESTS="-v"

%post   -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(-,root,root)
%license COPYING
%{_bindir}/*
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/*.so.2.6*
%{_libdir}/pkgconfig/*.pc
%{_libdir}/ruby/*
%{_datadir}/ri/*
%{_docdir}/%{name}-%{version}
%{_mandir}/man1/*
%{_mandir}/man5/*

%changelog
* Mon May 03 2021 Pawel Winogrodzki <pawelwi@microsoft.com> - 2.6.7-1
- Updating to version 2.6.7 to fix CVE-2021-28965.
- Updated the "%%files" section to display shared lib's version.
- License verified.

* Thu Jan 14 2021 Andrew Phelps <anphel@microsoft.com> - 2.6.6-4
- Run "make test" instead of "make check" to avoid unstable tests.

* Wed Nov 18 2020 Pawel Winogrodzki <pawelwi@microsoft.com> - 2.6.6-3
- Adding 'BuildRequires' on 'shadow-utils' and 'sudo' to run the package tests.

* Thu Oct 22 2020 Thomas Crain <thcrain@microsoft.com> - 2.6.6-2
- Patch CVE-2020-25613

* Thu Oct 15 2020 Emre Girgin <mrgirgin@microsoft.com> - 2.6.6-1
- Upgrade to 2.6.6 to resolve CVEs.

* Sat May 09 2020 Nick Samson <nisamson@microsoft.com> - 2.6.3-3
- Added %%license line automatically

* Wed May 06 2020 Pawel Winogrodzki <pawelwi@microsoft.com> - 2.6.3-2
- Removing *Requires for "ca-certificates".

* Fri Mar 13 2020 Paul Monson <paulmon@microsoft.com> - 2.6.3-1
- Update to version 2.6.3. License verified.

* Mon Feb 3 2020 Andrew Phelps <anphel@microsoft.com> - 2.5.3-3
- Disable compressing debug sections

* Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> - 2.5.3-2
- Initial CBL-Mariner import from Photon (license: Apache2).

* Tue Jan 01 2019 Sujay G <gsujay@vmware.com> - 2.5.3-1
- Update to version 2.5.3, to fix CVE-2018-16395 & CVE-2018-16396

* Tue Sep 11 2018 srinidhira0 <srinidhir@vmware.com> - 2.5.1-1
- Update to version 2.5.1

* Fri Jan 12 2018 Xiaolin Li <xiaolinl@vmware.com> - 2.4.3-2
- Fix CVE-2017-17790

* Wed Jan 03 2018 Xiaolin Li <xiaolinl@vmware.com> - 2.4.3-1
- Update to version 2.4.3, fix CVE-2017-17405

* Fri Sep 29 2017 Xiaolin Li <xiaolinl@vmware.com> - 2.4.2-1
- Update to version 2.4.2

* Fri Sep 15 2017 Xiaolin Li <xiaolinl@vmware.com> - 2.4.1-5
- [security] CVE-2017-14064

* Tue Sep 05 2017 Chang Lee <changlee@vmware.com> - 2.4.1-4
- Built with copy preserve mode and fixed %check

* Mon Jul 24 2017 Priyesh Padmavilasom <ppadmavilasom@vmware.com> - 2.4.1-3
- [security] CVE-2017-9228

* Tue Jun 13 2017 Priyesh Padmavilasom <ppadmavilasom@vmware.com> - 2.4.1-2
- [security] CVE-2017-9224,CVE-2017-9225
- [security] CVE-2017-9227,CVE-2017-9229

* Thu Apr 13 2017 Siju Maliakkal <smaliakkal@vmware.com> - 2.4.1-1
- Update to latest 2.4.1

* Wed Jan 18 2017 Anish Swaminathan <anishs@vmware.com> - 2.4.0-1
- Update to 2.4.0 - Fixes CVE-2016-2339

* Mon Oct 10 2016 ChangLee <changlee@vmware.com> - 2.3.0-4
- Modified %check

* Tue May 24 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> - 2.3.0-3
- GA - Bump release of all rpms

* Wed Mar 09 2016 Divya Thaluru <dthaluru@vmware.com> - 2.3.0-2
- Adding readline support

* Wed Jan 20 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> - 2.3.0-1
- Updated to 2.3.0-1

* Tue Apr 28 2015 Fabio Rapposelli <fabio@vmware.com> - 2.2.1-2
- Added SSL support

* Mon Apr 6 2015 Mahmoud Bassiouny <mbassiouny@vmware.com> - 2.2.1-1
- Version upgrade to 2.2.1

* Fri Oct 10 2014 Divya Thaluru <dthaluru@vmware.com> - 2.1.3-1
- Initial build.  First version
