Summary:        cpio-2.13
Name:           cpio
Version:        2.13
Release:        2%{?dist}
License:        GPLv3+
URL:            https://www.gnu.org/software/cpio/
Group:          System Environment/System utilities
Vendor:         Microsoft Corporation
Distribution:   Mariner
Source0:        https://ftp.gnu.org/gnu/%{name}/%{name}-%{version}.tar.bz2

Conflicts:      toybox

%description
The cpio package contains tools for archiving.

%package lang
Summary: Additional language files for cpio
Group:   System Environment/System utilities
Requires: %{name} = %{version}-%{release}

%description lang
These are the additional language files of cpio

%prep
%setup -q

%build
sed -i -e '/gets is a/d' gnu/stdio.in.h
./configure \
    --prefix=%{_prefix} \
    --bindir=%{_bindir} \
    --enable-mt   \
    --with-rmt=/usr/libexec/rmt
make %{?_smp_mflags}
makeinfo --html            -o doc/html      doc/cpio.texi
makeinfo --html --no-split -o doc/cpio.html doc/cpio.texi
makeinfo --plaintext       -o doc/cpio.txt  doc/cpio.texi

%install
make DESTDIR=%{buildroot} install
install -v -m755 -d %{buildroot}/%{_docdir}/%{name}-%{version}/html
install -v -m644    doc/html/* %{buildroot}/%{_docdir}/%{name}-%{version}/html
install -v -m644    doc/cpio.{html,txt} %{buildroot}/%{_docdir}/%{name}-%{version}
rm -rf %{buildroot}%{_infodir}
%find_lang %{name}

%check
make %{?_smp_mflags} check

%files
%defattr(-,root,root)
%license COPYING
%{_bindir}/*
%{_mandir}/man1/*
%{_docdir}/%{name}-%{version}/*

%files lang -f %{name}.lang
%defattr(-,root,root)

%changelog
* Sat May 09 2020 Nick Samson <nisamson@microsoft.com> 2.13-2
- Added %%license line automatically
* Fri May 01 2020 Pawel Winogrodzki <pawelwi@microsoft.com> 2.13-1
- Bumping version up to 2.13 to fix CVE-2019-14866.
- Fixed "Source0" and "URL" tags.
- License verified.
* Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 2.12-5
- Initial CBL-Mariner import from Photon (license: Apache2).
* Mon Oct 02 2017 Alexey Makhalov <amakhalov@vmware.com> 2.12-4
- Added conflicts toybox
* Tue May 02 2017 Anish Swaminathan <anishs@vmware.com> 2.12-3
- Add lang package
* Tue May 24 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 2.12-2
- GA - Bump release of all rpms
* Thu Jan 14 2016 Xiaolin Li <xiaolinl@vmware.com> 2.12-1
- Updated to version 2.12
* Fri Aug 14 2015 Divya Thaluru <dthaluru@vmware.com> 2.11-2
- Adding security patch for CVE-2014-9112
* Tue Nov 04 2014 Divya Thaluru <dthaluru@vmware.com> 2.11-1
- Initial build. First version
