Summary:    Library for netfilter related kernel/userspace communication
Name:       libnfnetlink
Version:    1.0.1
Release:        4%{?dist}
License:    GPLv2+
URL:        http://www.netfilter.org/projects/libnfnetlink/index.html
Group:      System Environment/Libraries
Vendor:         Microsoft Corporation
Distribution:   Mariner
Source0:    http://www.netfilter.org/projects/%{name}/files/%{name}-%{version}.tar.bz2
%define sha1 libnfnetlink=27ae2dfbd976e28cb7a417f9e946c901f512dd9a

BuildRequires:  kernel-headers

%description
libnfnetlink is the low-level library for netfilter related kernel/userspace communication. It provides a generic messaging infrastructure for in-kernel netfilter subsystems (such as nfnetlink_log, nfnetlink_queue, nfnetlink_conntrack) and their respective users and/or management tools in userspace.

%package        devel
Summary:        Development files for %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}
Requires:       kernel-headers

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%prep
%setup -q

%build
%configure --disable-static
make %{?_smp_mflags}

%install
%make_install
find %{buildroot} -type f -name '*.la' -exec rm -f {} ';'

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%license COPYING
%doc COPYING README
%{_libdir}/*.so.*

%files devel
%{_libdir}/pkgconfig/*.pc
%dir %{_includedir}/libnfnetlink
%{_includedir}/libnfnetlink/*.h
%{_libdir}/*.so

%changelog
* Sat May 09 2020 Nick Samson <nisamson@microsoft.com> - 1.0.1-4
- Added %%license line automatically

*   Thu Apr 30 2020 Emre Girgin <mrgirgin@microsoft.com> 1.0.1-3
-   Renaming linux-api-headers to kernel-headers
*   Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 1.0.1-2
-   Initial CBL-Mariner import from Photon (license: Apache2).
*   Wed Apr 05 2017 Anish Swaminathan <anishs@vmware.com> 1.0.1-1
-   Initial packaging
