Name:           oniguruma
Version:        6.9.5
Release:        2%{?dist}
License:        BSD
Summary:        Regular expressions library
Group:          System Environment/Libraries
Vendor:         Microsoft Corporation
Distribution:   Mariner
URL:            https://github.com/kkos/oniguruma/
Source0:        https://github.com/kkos/oniguruma/releases/download/v%{version}/onig-%{version}.tar.gz
# https://github.com/kkos/oniguruma/commit/cbe9f8bd9cfc6c3c87a60fbae58fa1a85db59df0.patch
Patch0:         CVE-2020-26159.patch

%description
Oniguruma is a regular expressions library.
The characteristics of this library is that different character encoding
for every regular expression object can be specified.
(supported APIs: GNU regex, POSIX and Oniguruma native)

%package devel
Summary:        Library providing headers and libraries to libonig
Group:          Development/Libraries
Requires:       oniguruma = %{version}-%{release}

%description devel
Development files for libonig

%prep
%autosetup -n onig-%{version} -p1


%build
%configure                     \
        --prefix=%{_prefix}    \
        --disable-silent-rules \
        --disable-static       \
        --with-rubydir=%{_bindir}
make

%install
make install \
        DESTDIR=%{buildroot}  \
        INSTALL="install -c -p"
find %{buildroot}/%{_libdir} -name '*.la' -delete

%check
make  check
%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%{_libdir}/libonig.so.*

%files devel
%defattr(-,root,root,-)
%doc    AUTHORS
%license        COPYING
%doc    README
%doc    index.html
%lang(ja)       %doc    README_japanese
%lang(ja)       %doc    index_ja.html
%{_bindir}/onig-config
%{_libdir}/libonig.so
%{_includedir}/onig*.h
%{_libdir}/pkgconfig/%{name}.pc

%changelog
* Thu Oct 15 2020 Emre Girgin <mrgirgin@microsoft.com> 6.9.5-2
- Fix CVE-2020-26159. 
* Tue May 19 2020 Andrew Phelps <anphel@microsoft.com> 6.9.5-1
- Upgrade to 6.9.5.
* Wed Apr 22 2020 Emre Girgin <mrgirgin@microsoft.com> 6.9.0-4
- Fix CVE-2019-19012.
* Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 6.9.0-3
- Initial CBL-Mariner import from Photon (license: Apache2).
* Mon Jul 15 2019 Dweep Advani <dadvani@vmware.com> 6.9.0-2
- Fixed CVE-2019-13224
* Mon Sep 10 2018 Him Kalyan Bordoloi <bordoloih@vmware.com> 6.9.0-1
- Upgrade to 6.9.0
- Created devel package
* Tue Aug 22 2017 Chang Lee <changlee@vmware.com> 6.5.0-1
- Initial version
