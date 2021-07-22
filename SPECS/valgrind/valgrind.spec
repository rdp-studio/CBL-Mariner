%global security_hardening none
Summary:        Memory Management Debugger.
Name:           valgrind
Version:        3.15.0
Release:        3%{?dist}
License:        GPLv2+
URL:            https://valgrind.org
Group:          Development/Debuggers
Source0:        https://sourceware.org/pub/%{name}/%{name}-%{version}.tar.bz2

Vendor:         Microsoft Corporation
Distribution:   Mariner
BuildRequires:  pkg-config

%description
Valgrind is a GPL'd system for debugging and profiling Linux programs. With
Valgrind's tool suite you can automatically detect many memory management and
threading bugs, avoiding hours of frustrating bug-hunting, making your programs
more stable. You can also perform detailed profiling to help speed up your
programs.

%prep
%setup -q -n %{name}-%{version}

%build
CFLAGS="`echo " %{build_cflags} " | sed 's/-fstack-protector-strong//'`"
export CFLAGS
./configure --prefix=%{_prefix}
make

%install
make DESTDIR=%{buildroot} install

%check
make %{?_smp_mflags} -k check

%files
%defattr(-,root,root)
%license COPYING
%{_bindir}/*
%{_includedir}/valgrind
%{_libdir}/valgrind
%{_libdir}/pkgconfig/*
%{_mandir}/*/*
%{_datadir}/doc/valgrind/*
%{_libexecdir}/valgrind/*

%changelog
*   Mon Jun 01 2020 Henry Beberman <henry.beberman@microsoft.com> - 3.15.0-3
-   Fix compilation by disabling -fstack-protector-strong
*   Sat May 09 2020 Nick Samson <nisamson@microsoft.com> - 3.15.0-2
-   Added %%license line automaticall
*   Wed Mar 18 2020 Henry Beberman <henry.beberman@microsoft.com> 3.15.0-1
-   Update to 3.15.0. Fix Source0 URL. Removed patch fixed upstream. License verified.
*   Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 3.13.0-2
-   Initial CBL-Mariner import from Photon (license: Apache2).
*   Wed Sep 12 2018 Anish Swaminathan <anishs@vmware.com> 3.13.0-1
-   Update to version 3.13.0
*   Tue Sep 19 2017 Bo Gan <ganb@vmware.com> 3.12.0-2
-   Fix make check issue
*   Wed Apr 05 2017 Xiaolin Li <xiaolinl@vmware.com> 3.12.0-1
-   Updated to version 3.12.0.
*   Fri Aug 05 2016 Kumar Kaushik <kaushikk@vmware.com> 3.11.0-1
-   Initial Build.
