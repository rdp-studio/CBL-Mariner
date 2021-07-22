Summary:        The lm_sensors package provides user-space support for the hardware monitoring drivers in the Linux kernel.
Name:           lm-sensors
Version:        3.5.0
Release:        6%{?dist}
License:        GPLv2
URL:            https://github.com/lm-sensors/lm-sensors
Group:          System Drivers
Vendor:         Microsoft Corporation
Distribution:   Mariner
#Source0:       https://github.com/lm-sensors/lm-sensors/archive/V3-5-0.tar.gz
Source0:        %{name}-%{version}.tar.gz
BuildRequires:  gcc
BuildRequires:  bison
BuildRequires:  flex
BuildRequires:  make
BuildRequires:  bison
BuildRequires:  glibc-devel
BuildRequires:  libgcc-devel
BuildRequires:  which
Requires:       perl

# The kernel optimized for Hyper-V doesn't have the "CONFIG_I2C_CHARDEV" configuration enabled,
# which is required by this package.
Conflicts: kernel-hyperv

%description
The lm_sensors package provides user-space support for the hardware monitoring drivers in the Linux kernel.
This is useful for monitoring the temperature of the CPU and adjusting the performance of some hardware (such as cooling fans).

%package   devel
Summary:   lm-sensors devel
Group:     Development/Libraries
Requires:  lm-sensors = %{version}-%{release}

%description devel
lm-sensors devel

%package   doc
Summary:   lm-sensors docs
Group:     Development/Libraries
Requires:  lm-sensors = %{version}-%{release}

%description doc
Documentation for lm-sensors.

%prep
%setup -q -n %{name}-3-5-0

%build

make all %{?_smp_mflags}

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/usr/lib
mkdir -p %{buildroot}/usr/share
make PREFIX=%{buildroot}/usr        \
     BUILD_STATIC_LIB=0 \
     MANDIR=%{buildroot}/usr/share/man install &&

install -v -m755 -d %{buildroot}/usr/share/doc/%{name}-%{version} &&
cp -rv              README INSTALL doc/* \
                    %{buildroot}/usr/share/doc/%{name}-%{version}
%check

%post
/sbin/modprobe i2c-dev

%postun
/sbin/modprobe -r i2c-dev

%clean
rm -rf %{buildroot}/*

%files
%defattr(-,root,root)
%license COPYING
%{_bindir}/*
%{_libdir}/libsensors.so.5
%{_libdir}/libsensors.so.5.0.0
%{_sbindir}/*

%files devel
%defattr(-,root,root)
%{_includedir}/*
%{_libdir}/libsensors.so

%files doc
%defattr(-,root,root)
%{_docdir}/*
%{_mandir}/*

%changelog
*   Thu Jun 18 2020 Pawel Winogrodzki <pawelwi@microsoft.com> 3.5.0-6
-   Removing runtime dependency on a specific kernel package.
*   Sat May 09 2020 Nick Samson <nisamson@microsoft.com> 3.5.0-5
-   Added %%license line automatically
*   Tue Apr 28 2020 Emre Girgin <mrgirgin@microsoft.com> 3.5.0-4
-   Renaming linux to kernel
*   Tue Apr 07 2020 Joe Schmitt <joschmit@microsoft.com> 3.5.0-3
-   Update Source0 with valid URL.
-   Remove sha1 macro.
-   Fix changelog styling
-   License verified.
*   Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 3.5.0-2
-   Initial CBL-Mariner import from Photon (license: Apache2).
*   Thu Jun 20 2019 Tapas Kundu <tkundu@vmware.com> 3.5.0-1
-   Initial packaging with Photon OS.
