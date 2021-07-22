Summary:        Modern C++ library for realtime consumption of LTTNG events
Name:           lttng-consume
Version:        0.2
Release:        3%{?dist}
License:        MIT
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          System Environment
URL:            https://github.com/microsoft/lttng-consume
#Source0:       https://github.com/microsoft/%{name}/archive/v%{version}.tar.gz
Source0:        lttng-consume-%{version}.tar.gz
BuildRequires:  catch-devel
BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  jsonbuilder-devel
BuildRequires:  libbabeltrace2-devel
# 'lttng' tool needed for tests to run
BuildRequires:  lttng-tools
BuildRequires:  lttng-ust-devel
BuildRequires:  tracelogging-devel

%description
The lttng-consume project produces JsonBuilder structures from a realtime
LTTNG session.

%package        devel
Summary:        Development files for lttng-consume
Group:          System Environment/Libraries
Requires:       lttng-consume = %{version}-%{release}

%description    devel
This package contains the headers and symlinks for applications and libraries to
use lttng-consume.

%prep
%setup -q

%build
mkdir build && cd build
%cmake ..
%make_build

%install
%make_install -C build

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(-,root,root)
%doc README.md
%license LICENSE
%{_libdir}/liblttng-consume.so.*

%files devel
%defattr(-,root,root)
%{_libdir}/liblttng-consume.so
%{_libdir}/cmake/lttng-consume
%{_includedir}/lttng-consume

%changelog
* Wed Oct 07 2020 Thomas Crain <thcrain@microsoft.com> - 0.2-3
- Add #Source0 URL
- Verified License field and %%license macro

* Tue Apr 07 2020 Daniel McIlvaney <damcilva@microsoft.com> - 0.2-2
- Require lttng-ust packages.

* Wed Feb 12 2020 Nick Bopp <nichbop@microsoft.com> - 0.2-1
- Original version for CBL-Mariner.
