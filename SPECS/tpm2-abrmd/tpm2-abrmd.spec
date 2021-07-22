Summary:    TPM2 Access Broker & Resource Management Daemon implementing the TCG spec
Name:       tpm2-abrmd
Version:    2.3.3
Release:    1%{?dist}
License:    BSD 2-Clause
URL:        https://github.com/tpm2-software/tpm2-abrmd/releases/
Source0:    https://github.com/tpm2-software/tpm2-abrmd/releases/download/%{version}/%{name}-%{version}.tar.gz
Group:      System Environment/Security
Vendor:         Microsoft Corporation
Distribution:   Mariner

BuildRequires:  which dbus-devel glib-devel tpm2-tss-devel
Requires:   dbus glib tpm2-tss
%description
TPM2 Access Broker & Resource Management Daemon implementing the TCG spec

%package devel
Summary:    The libraries and header files needed for TSS2 ABRMD development.
Requires:   %{name} = %{version}-%{release}
%description devel
The libraries and header files needed for TSS2 ABRMD development.

%prep
%setup -q
%build
%configure \
    --disable-static \
    --with-systemdsystemunitdir=/usr/lib/systemd/system \
    --with-dbuspolicydir=/etc/dbus-1/system.d

make %{?_smp_mflags}

%install
make DESTDIR=%{buildroot} install

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(-,root,root)
%license LICENSE
%{_sysconfdir}/dbus-1/system.d/tpm2-abrmd.conf
%{_sbindir}/tpm2-abrmd
%{_libdir}/libtss2-tcti-tabrmd.so.0.0.0
%{_libdir}/systemd/system/tpm2-abrmd.service
%{_libdir}/systemd/system-preset/tpm2-abrmd.preset
%{_datadir}/dbus-1/*
%{_mandir}/man8

%files devel
%defattr(-,root,root)
%{_includedir}/tss2/*
%{_libdir}/pkgconfig/*
%{_libdir}/libtss2-tcti-tabrmd.la
%{_libdir}/libtss2-tcti-tabrmd.so
%{_libdir}/libtss2-tcti-tabrmd.so.0
%{_mandir}/man3
%{_mandir}/man7

%changelog
*   Sun Sep 27 2020 Daniel McIlvaney <damcilva@microsoft.com> 2.3.3-1
-   Update to 2.3.3 to solve incompatibility with tpm2-tss 2.4.0
*   Sat May 09 2020 Nick Samson <nisamson@microsoft.com> 2.1.1-2
-   Added %%license line automatically
*   Wed Mar 18 2020 Henry Beberman <henry.beberman@microsoft.com> 2.1.1-1
-   Update to 2.1.1. Fix URL. Fix Source0 URL. License verified.
*   Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 2.1.0-2
-   Initial CBL-Mariner import from Photon (license: Apache2).
*   Thu Feb 21 2019 Alexey Makhalov <amakhalov@vmware.com> 2.1.0-1
-   Initial build. First version
