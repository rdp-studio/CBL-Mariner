Summary:        advanced key-value store
Name:           redis
Version:        5.0.5
Release:        7%{?dist}
License:        BSD
URL:            https://redis.io/
Group:          Applications/Databases
Vendor:         Microsoft Corporation
Distribution:   Mariner
Source0:        https://download.redis.io/releases/%{name}-%{version}.tar.gz
Patch0:         redis-conf.patch
Patch1:         CVE-2020-14147.patch
Patch2:         disable_active_defrag_big_keys.patch
# CVE-2021-21309 affects 32-bit executables only. Mariner always builds with -m64 and does not support 32-bit architectures.
Patch3:         CVE-2021-21309.nopatch
Patch4:         CVE-2021-3470.patch

BuildRequires:  gcc
BuildRequires:  systemd
BuildRequires:  make
BuildRequires:  which
BuildRequires:  tcl
BuildRequires:  tcl-devel
Requires:       systemd
Requires(pre):  /usr/sbin/useradd /usr/sbin/groupadd

%description
Redis is an in-memory data structure store, used as database, cache and message broker.

%prep
%autosetup -p1

%build
make %{?_smp_mflags}

%install
install -vdm 755 %{buildroot}
make PREFIX=%{buildroot}/usr install
install -D -m 0640 %{name}.conf %{buildroot}%{_sysconfdir}/%{name}.conf
mkdir -p %{buildroot}/var/lib/redis
mkdir -p %{buildroot}/var/log
mkdir -p %{buildroot}/var/opt/%{name}/log
ln -sfv /var/opt/%{name}/log %{buildroot}/var/log/%{name}
mkdir -p %{buildroot}/usr/lib/systemd/system
cat << EOF >>  %{buildroot}/usr/lib/systemd/system/redis.service
[Unit]
Description=Redis in-memory key-value database
After=network.target

[Service]
ExecStart=/usr/bin/redis-server /etc/redis.conf --daemonize no
ExecStop=/usr/bin/redis-cli shutdown
User=redis
Group=redis

[Install]
WantedBy=multi-user.target
EOF

%check
make check

%pre
getent group %{name} &> /dev/null || \
groupadd -r %{name} &> /dev/null
getent passwd %{name} &> /dev/null || \
useradd -r -g %{name} -d %{_sharedstatedir}/%{name} -s /sbin/nologin \
-c 'Redis Database Server' %{name} &> /dev/null
exit 0

%post
/sbin/ldconfig
%systemd_post  redis.service

%postun
/sbin/ldconfig
%systemd_postun_with_restart redis.service


%files
%defattr(-,root,root)
%license COPYING
%dir %attr(0750, redis, redis) /var/lib/redis
%dir %attr(0750, redis, redis) /var/opt/%{name}/log
%attr(0750, redis, redis) %{_var}/log/%{name}
%{_bindir}/*
%{_libdir}/systemd/*
%config(noreplace) %attr(0640, %{name}, %{name}) %{_sysconfdir}/redis.conf

%changelog
* Fri Apr 09 2021 Suresh Babu Chalamalasetty <schalam@microsoft.com> 5.0.5-7
- Add patch for CVE-2021-3470
* Thu Mar 11 2021 Mateusz Malisz <mamalisz@microsoft.com> 5.0.5-6
- Add nopatch for CVE-2021-21309.
* Wed Mar 03 2021 Andrew Phelps <anphel@microsoft.com> 5.0.5-5
- Add patch to remove an unreliable test. License verified.
* Fri Oct 23 2020 Henry Li <lihl@microsoft.com> 5.0.5-4
- Add patch to resolve CVE-2020-14147
* Sat May 09 2020 Nick Samson <nisamson@microsoft.com> 5.0.5-3
- Added %%license line automatically
* Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 5.0.5-2
- Initial CBL-Mariner import from Photon (license: Apache2).
* Mon Jul 22 2019 Shreyas B. <shreyasb@vmware.com> 5.0.5-1
- Updated to version 5.0.5.
* Tue Sep 11 2018 Keerthana K <keerthanak@vmware.com> 4.0.11-1
- Updated to version 4.0.11.
* Thu Dec 28 2017 Divya Thaluru <dthaluru@vmware.com>  3.2.8-5
- Fixed the log file directory structure
* Mon Sep 18 2017 Alexey Makhalov <amakhalov@vmware.com> 3.2.8-4
- Remove shadow from requires and use explicit tools for post actions
* Wed May 31 2017 Siju Maliakkal <smaliakkal@vmware.com> 3.2.8-3
- Fix DB persistence,log file,grace-ful shutdown issues
* Tue May 16 2017 Siju Maliakkal <smaliakkal@vmware.com> 3.2.8-2
- Added systemd service unit
* Wed Apr 5 2017 Siju Maliakkal <smaliakkal@vmware.com> 3.2.8-1
- Updating to latest version
* Mon Oct 3 2016 Dheeraj Shetty <dheerajs@vmware.com> 3.2.4-1
- initial version
