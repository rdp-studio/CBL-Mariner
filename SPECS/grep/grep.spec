Summary:        Programs for searching through files
Name:           grep
Version:        3.1
Release:        5%{?dist}
License:        GPLv3+
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          Applications/File
URL:            https://www.gnu.org/software/grep
Source0:        http://ftp.gnu.org/gnu/grep/%{name}-%{version}.tar.xz
Patch0:         grep-3.31-man-fix-gs.patch
Patch1:         grep-3.31-help-align.patch
Patch2:         grep-3.1-glibc-2.28-fix.patch
BuildRequires:  pcre-devel
Requires:       pcre
Conflicts:      toybox

%description
The Grep package contains programs for searching through files.

%package lang
Summary:        Additional language files for grep
Group:          System Environment/Base
Requires:       %{name} = %{version}-%{release}

%description lang
These are the additional language files of grep

%prep
%setup -q
%patch0 -p1 -b .man-fix-gs
%patch1 -p1 -b .help-align
%patch2 -p1 -b .glibc-2.28-fix
# Skip pcre-jitstack test, which is known to fail when libpcre is built without jit
sed -i 's/require_pcre_/require_pcre_\nskip_ "test known to fail when libpcre is built without jit"/g' tests/pcre-jitstack

%build
./configure \
    --prefix=%{_prefix} \
    --bindir=/bin \
    --without-included-regex \
    --disable-silent-rules
make %{?_smp_mflags}

%install
make DESTDIR=%{buildroot} install
rm -rf %{buildroot}%{_infodir}
%find_lang %{name}

%check
make %{?_smp_mflags} check

%files
%defattr(-,root,root)
%license COPYING
/bin/*
%{_mandir}/*/*

%files lang -f %{name}.lang
%defattr(-,root,root)

%changelog
* Tue Jun 15 2021 Andrew Phelps <anphel@microsoft.com> 3.1-5
- Support perl regular expressions ("grep -P")
- Fix test issues
- Add Fedora patch files for help text and manpage.
* Tue Jan 05 2021 Andrew Phelps <anphel@microsoft.com> 3.1-4
- Fix test issue by configuring "--with-included-regex". Remove sha1.
* Sat May 09 2020 Nick Samson <nisamson@microsoft.com> 3.1-3
- Added %%license line automatically
* Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 3.1-2
- Initial CBL-Mariner import from Photon (license: Apache2).
* Wed Sep 12 2018 Anish Swaminathan <anishs@vmware.com> 3.1-1
- Update to version 3.1
* Mon Oct 02 2017 Alexey Makhalov <amakhalov@vmware.com> 3.0-4
- Added conflicts toybox
* Wed Aug 23 2017 Rongrong Qiu <rqiu@vmware.com> 3.0-3
- Disable grep -P for make check bug 1900287
* Tue May 02 2017 Anish Swaminathan <anishs@vmware.com> 3.0-2
- Add lang package.
* Fri Mar 24 2017 Dheeraj Shetty <dheerajs@vmware.com> 3.0-1
- Upgrading grep to 3.0 version
* Thu Oct 06 2016 ChangLee <changlee@vmware.com> 2.21-3
- Modified %check
* Tue May 24 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 2.21-2
- GA - Bump release of all rpms
* Mon Apr 6 2015 Mahmoud Bassiouny <mbassiouny@vmware.com> 2.21-1
- Upgrading grep to 2.21 version, and adding
* Wed Nov 5 2014 Divya Thaluru <dthaluru@vmware.com> 2.16-1
- Initial build. First version
