# Copied this spec file from inside of dracut-041.tar.xz and edited later.

%define dracutlibdir %{_lib}/dracut
%define _unitdir %{_lib}/systemd/system
Summary:        dracut to create initramfs
Name:           dracut
Version:        049
Release:        5%{?dist}
# The entire source code is GPLv2+
# except install/* which is LGPLv2+
License:        GPLv2+ AND LGPLv2+
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          System Environment/Base
URL:            https://dracut.wiki.kernel.org/
Source0:        http://www.kernel.org/pub/linux/utils/boot/dracut/dracut-%{version}.tar.xz
Source1:        https://www.gnu.org/licenses/lgpl-2.1.txt
Patch0:         disable-xattr.patch
Patch1:         fix-initrd-naming-for-mariner.patch
BuildRequires:  asciidoc
BuildRequires:  bash
BuildRequires:  git
BuildRequires:  kmod-devel
BuildRequires:  pkg-config
Requires:       /bin/grep
Requires:       /bin/sed
Requires:       bash >= 4
Requires:       coreutils
Requires:       cpio
Requires:       findutils
Requires:       kmod
Requires:       systemd
Requires:       util-linux

%description
dracut contains tools to create a bootable initramfs for 2.6 Linux kernels.
Unlike existing implementations, dracut does hard-code as little as possible
into the initramfs. dracut contains various modules which are driven by the
event-based udev. Having root on MD, DM, LVM2, LUKS is supported as well as
NFS, iSCSI, NBD, FCoE with the dracut-network package.

%package fips
Summary:        dracut modules to build a dracut initramfs with an integrity check
Requires:       %{name} = %{version}-%{release}
Requires:       libkcapi-hmaccalc
Requires:       nss

%description fips
This package requires everything which is needed to build an
initramfs with dracut, which does an integrity check.

%package tools
Summary:        dracut tools to build the local initramfs
Requires:       %{name} = %{version}-%{release}

%description tools
This package contains tools to assemble the local initrd and host configuration.

%prep
%setup -q
cp %{SOURCE1} .
%patch0 -p1
%patch1 -p1

%build
%configure --systemdsystemunitdir=%{_unitdir} --bashcompletiondir=$(pkg-config --variable=completionsdir bash-completion) \
           --libdir=%{_lib}   --disable-documentation

make %{?_smp_mflags}

%install
make %{?_smp_mflags} install \
     DESTDIR=%{buildroot} \
     libdir=%{_lib}

echo "DRACUT_VERSION=%{version}-%{release}" > %{buildroot}/%{dracutlibdir}/dracut-version.sh

rm -fr -- %{buildroot}/%{dracutlibdir}/modules.d/00bootchart

# we do not support dash in the initramfs
rm -fr -- %{buildroot}/%{dracutlibdir}/modules.d/00dash

# remove gentoo specific modules
rm -fr -- %{buildroot}/%{dracutlibdir}/modules.d/50gensplash

rm -fr -- %{buildroot}/%{dracutlibdir}/modules.d/96securityfs
rm -fr -- %{buildroot}/%{dracutlibdir}/modules.d/97masterkey
rm -fr -- %{buildroot}/%{dracutlibdir}/modules.d/98integrity

mkdir -p %{buildroot}/boot/dracut
mkdir -p %{buildroot}%{_sharedstatedir}/dracut/overlay
mkdir -p %{buildroot}%{_localstatedir}/log
mkdir -p %{buildroot}%{_localstatedir}/opt/dracut/log
touch %{buildroot}%{_localstatedir}/opt/dracut/log/dracut.log
ln -sfv %{_localstatedir}/opt/dracut/log/dracut.log %{buildroot}%{_localstatedir}/log/
mkdir -p %{buildroot}%{_sharedstatedir}/initramfs

rm -f %{buildroot}%{_mandir}/man?/*suse*

install -m 0644 dracut.conf.d/fips.conf.example %{buildroot}%{_sysconfdir}/dracut.conf.d/40-fips.conf
> %{buildroot}%{_sysconfdir}/system-fips

# create compat symlink
mkdir -p %{buildroot}%{_sbindir}
ln -sr %{buildroot}%{_bindir}/dracut %{buildroot}%{_sbindir}/dracut

%check
make %{?_smp_mflags} -k clean  check

%clean
rm -rf -- %{buildroot}


%files
%defattr(-,root,root,0755)
%{!?_licensedir:%global license %%doc}
%license COPYING lgpl-2.1.txt
%{_bindir}/dracut
%{_bindir}/mkinitrd
%{_bindir}/lsinitrd
# compat symlink
%{_sbindir}/dracut
%{_datadir}/bash-completion/completions/dracut
%{_datadir}/bash-completion/completions/lsinitrd
%dir %{dracutlibdir}
%dir %{dracutlibdir}/modules.d
%{dracutlibdir}/modules.d/*
%exclude %{_libdir}/kernel
%{_lib}/dracut/dracut-init.sh
%{_datadir}/pkgconfig/dracut.pc
%{dracutlibdir}/dracut-functions.sh
%{dracutlibdir}/dracut-functions
%{dracutlibdir}/dracut-version.sh
%{dracutlibdir}/dracut-logger.sh
%{dracutlibdir}/dracut-initramfs-restore
%{dracutlibdir}/dracut-install
%{dracutlibdir}/skipcpio
%config(noreplace) %{_sysconfdir}/dracut.conf
%dir %{_sysconfdir}/dracut.conf.d
%dir %{dracutlibdir}/dracut.conf.d
%dir %{_localstatedir}/opt/dracut/log
%attr(0644,root,root) %ghost %config(missingok,noreplace) %{_localstatedir}/opt/dracut/log/dracut.log
%{_localstatedir}/log/dracut.log
%dir %{_sharedstatedir}/initramfs
%{_unitdir}/dracut-shutdown.service
%{_unitdir}/sysinit.target.wants/dracut-shutdown.service
%{_unitdir}/dracut-cmdline.service
%{_unitdir}/dracut-initqueue.service
%{_unitdir}/dracut-mount.service
%{_unitdir}/dracut-pre-mount.service
%{_unitdir}/dracut-pre-pivot.service
%{_unitdir}/dracut-pre-trigger.service
%{_unitdir}/dracut-pre-udev.service
%{_unitdir}/initrd.target.wants/dracut-cmdline.service
%{_unitdir}/initrd.target.wants/dracut-initqueue.service
%{_unitdir}/initrd.target.wants/dracut-mount.service
%{_unitdir}/initrd.target.wants/dracut-pre-mount.service
%{_unitdir}/initrd.target.wants/dracut-pre-pivot.service
%{_unitdir}/initrd.target.wants/dracut-pre-trigger.service
%{_unitdir}/initrd.target.wants/dracut-pre-udev.service

%files fips
%defattr(-,root,root,0755)
%{dracutlibdir}/modules.d/01fips
%{_sysconfdir}/dracut.conf.d/40-fips.conf
%config(missingok) %{_sysconfdir}/system-fips

%files tools
%defattr(-,root,root,0755)

%{_bindir}/dracut-catimages
%dir /boot/dracut
%dir %{_sharedstatedir}/dracut
%dir %{_sharedstatedir}/dracut/overlay

%changelog
* Fri Feb 12 2021 Nicolas Ontiveros <niontive@microsoft.com> - 049-5
- Enable kernel crypto testing in dracut-fips

* Wed Feb 10 2021 Nicolas Ontiveros <niontive@microsoft.com> - 049-4
- Move 40-fips.conf to /etc/dracut.conf.d/

* Mon Feb 01 2021 Nicolas Ontiveros <niontive@microsoft.com> - 049-3
- Add dracut-fips package.
- Disable kernel crypto testing in dracut-fips.

*   Wed Apr 08 2020 Nicolas Ontiveros <niontive@microsoft.com> 049-2
-   Remove toybox from requires.

*   Thu Mar 26 2020 Nicolas Ontiveros <niontive@microsoft.com> 049-1
-   Update version to 49. License verified. 

*   Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 048-2
-   Initial CBL-Mariner import from Photon (license: Apache2).

*   Mon Oct 01 2018 Alexey Makhalov <amakhalov@vmware.com> 048-1
-   Version update

*   Thu Dec 28 2017 Divya Thaluru <dthaluru@vmware.com>  045-6
-   Fixed the log file directory structure

*   Mon Sep 18 2017 Alexey Makhalov <amakhalov@vmware.com> 045-5
-   Requires coreutils/util-linux/findutils or toybox,
    /bin/grep, /bin/sed

*   Fri Jun 23 2017 Xiaolin Li <xiaolinl@vmware.com> 045-4
-   Add kmod-devel to BuildRequires

*   Fri May 26 2017 Bo Gan <ganb@vmware.com> 045-3
-   Fix dependency

*   Thu Apr 27 2017 Bo Gan <ganb@vmware.com> 045-2
-   Disable xattr for cp

*   Wed Apr 12 2017 Chang Lee <changlee@vmware.com> 045-1
-   Updated to 045

*   Wed Jan 25 2017 Harish Udaiya Kumar <hudaiyakumr@vmware.com> 044-6
-   Added the patch for bash 4.4 support.

*   Wed Nov 23 2016 Anish Swaminathan <anishs@vmware.com>  044-5
-   Add systemd initrd root device target to list of modules

*   Fri Oct 07 2016 ChangLee <changlee@vmware.com> 044-4
-   Modified %check

*   Tue May 24 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 044-3
-   GA - Bump release of all rpms

*   Thu Apr 25 2016 Gengsheng Liu <gengshengl@vmware.com> 044-2
-   Fix incorrect systemd directory.

*   Thu Feb 25 2016 Kumar Kaushik <kaushikk@vmware.com> 044-1
-   Updating Version.
