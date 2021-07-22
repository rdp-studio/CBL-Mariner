Summary:        Libraries for terminal handling of character screens
Name:           ncurses
Version:        6.2
Release:        4%{?dist}
License:        MIT
URL:            https://invisible-island.net/ncurses/
Group:          Applications/System
Vendor:         Microsoft Corporation
Distribution:   Mariner
Source0:        ftp://ftp.invisible-island.net/%{name}/%{name}-%{version}.tar.gz

Requires:       ncurses-libs = %{version}-%{release}

%description
The Ncurses package contains libraries for terminal-independent
handling of character screens.

%package libs
Summary: Ncurses Libraries
Group: System Environment/Libraries
Provides:       libncurses.so.6()(64bit)

%description libs
This package contains ncurses libraries

%package compat
Summary: Ncurses compatibility libraries
Group: System Environment/Libraries
Provides: libncurses.so.5()(64bit)

%description compat
This package contains the ABI version 5 of the ncurses libraries for
compatibility.

%package        devel
Summary:        Header and development files for ncurses
Requires:       %{name} = %{version}-%{release}
Provides:       pkgconfig(ncurses)
%description    devel
It contains the libraries and header files to create applications

%package        term
Summary:        terminfo files for ncurses
Requires:       %{name} = %{version}-%{release}
%description    term
It contains all terminfo files

%prep
%setup -q -n %{name}-%{version}

%build
common_options="\
    --enable-colorfgbg \
    --enable-hard-tabs \
    --enable-overwrite \
    --enable-pc-files \
    --enable-xmc-glitch \
    --disable-stripping \
    --disable-wattr-macros \
    --with-cxx-shared \
    --with-ospeed=unsigned \
    --with-pkg-config-libdir=%{_libdir}/pkgconfig \
    --with-shared \
    --with-terminfo-dirs=%{_sysconfdir}/terminfo:%{_datadir}/terminfo \
    --with-termlib=tinfo \
    --with-ticlib=tic \
    --with-xterm-kbs=DEL \
    --without-ada"
abi5_options="--with-chtype=long"

for abi in 5 6; do
    for char in narrowc widec; do
        mkdir $char$abi
        pushd $char$abi
        ln -s ../configure .

        [ $abi = 6 -a $char = widec ] && progs=yes || progs=no

        %configure $(
            echo $common_options --with-abi-version=$abi
            [ $abi = 5 ] && echo $abi5_options
            [ $char = widec ] && echo --enable-widec
            [ $progs = yes ] || echo --without-progs
        )

        make %{?_smp_mflags} libs
        [ $progs = yes ] && make %{?_smp_mflags} -C progs

        popd
    done
done

%install
make -C narrowc5 DESTDIR=$RPM_BUILD_ROOT install.libs
rm ${RPM_BUILD_ROOT}%{_libdir}/lib{tic,tinfo}.so.5*
make -C widec5 DESTDIR=$RPM_BUILD_ROOT install.libs
make -C narrowc6 DESTDIR=$RPM_BUILD_ROOT install.libs
rm ${RPM_BUILD_ROOT}%{_libdir}/lib{tic,tinfo}.so.6*
make -C widec6 DESTDIR=$RPM_BUILD_ROOT install.{libs,progs,data,includes,man}

chmod 755 ${RPM_BUILD_ROOT}%{_libdir}/lib*.so.*.*
chmod 644 ${RPM_BUILD_ROOT}%{_libdir}/lib*.a

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/terminfo

baseterms=

# prepare -base and -term file lists
for termname in \
    ansi dumb linux vt100 vt100-nav vt102 vt220 vt52 \
    Eterm\* aterm bterm cons25 cygwin eterm\* gnome gnome-256color hurd jfbterm \
    konsole konsole-256color mach\* mlterm mrxvt nsterm putty{,-256color} pcansi \
    rxvt{,-\*} screen{,-\*color,.[^mlp]\*,.linux,.mlterm\*,.putty{,-256color},.mrxvt} \
    st{,-\*color} sun teraterm teraterm2.3 tmux{,-\*} vte vte-256color vwmterm \
    wsvt25\* xfce xterm xterm-\*
do
    for i in $RPM_BUILD_ROOT%{_datadir}/terminfo/?/$termname; do
        for t in $(find $RPM_BUILD_ROOT%{_datadir}/terminfo -samefile $i); do
            baseterms="$baseterms $(basename $t)"
        done
    done
done 2> /dev/null
for t in $baseterms; do
    echo "%dir %{_datadir}/terminfo/${t::1}"
    echo %{_datadir}/terminfo/${t::1}/$t
done 2> /dev/null | sort -u > terms.base
find $RPM_BUILD_ROOT%{_datadir}/terminfo \! -type d | \
    sed "s|^$RPM_BUILD_ROOT||" | while read t
do
    echo "%dir $(dirname $t)"
    echo $t
done 2> /dev/null | sort -u | comm -2 -3 - terms.base > terms.term

# can't replace directory with symlink (rpm bug), symlink all headers
mkdir $RPM_BUILD_ROOT%{_includedir}/ncurses{,w}
for l in $RPM_BUILD_ROOT%{_includedir}/*.h; do
    ln -s ../$(basename $l) $RPM_BUILD_ROOT%{_includedir}/ncurses
    ln -s ../$(basename $l) $RPM_BUILD_ROOT%{_includedir}/ncursesw
done

# don't require -ltinfo when linking with --no-add-needed
for l in $RPM_BUILD_ROOT%{_libdir}/libncurses{,w}.so; do
    soname=$(basename $(readlink $l))
    rm -f $l
    echo "INPUT($soname -ltinfo)" > $l
done

rm -f $RPM_BUILD_ROOT%{_libdir}/libcurses{,w}.so
echo "INPUT(-lncurses)" > $RPM_BUILD_ROOT%{_libdir}/libcurses.so
echo "INPUT(-lncursesw)" > $RPM_BUILD_ROOT%{_libdir}/libcursesw.so

echo "INPUT(-ltinfo)" > $RPM_BUILD_ROOT%{_libdir}/libtermcap.so

rm -f $RPM_BUILD_ROOT%{_bindir}/ncurses*5-config
rm -f $RPM_BUILD_ROOT%{_libdir}/terminfo
rm -f $RPM_BUILD_ROOT%{_libdir}/pkgconfig/*_g.pc

xz NEWS

%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%post compat -p /sbin/ldconfig
%postun compat -p /sbin/ldconfig

%post devel -p /sbin/ldconfig
%postun devel -p /sbin/ldconfig

%files
%defattr(-,root,root)
%license COPYING
%doc ANNOUNCE AUTHORS NEWS.xz README TO-DO
%{_bindir}/[cirt]*
%{_mandir}/man1/[cirt]*
%{_mandir}/man5/*
%{_mandir}/man7/*

%files libs -f terms.base
%{!?_licensedir:%global license %%doc}
%doc README
%license COPYING
%{_datadir}/terminfo/l/linux
%dir %{_sysconfdir}/terminfo
%{_datadir}/tabset
%dir %{_datadir}/terminfo
%{_libdir}/lib*.so.6*

%files compat
%{_libdir}/lib*.so.5*

%files devel
%doc doc/html/hackguide.html
%doc doc/html/ncurses-intro.html
%doc c++/README*
%doc misc/ncurses.supp
%{_bindir}/ncurses*-config
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*.pc
%dir %{_includedir}/ncurses
%dir %{_includedir}/ncursesw
%{_includedir}/ncurses/*.h
%{_includedir}/ncursesw/*.h
%{_includedir}/*.h
%{_mandir}/man1/ncurses*-config*
%{_mandir}/man3/*
%{_libdir}/lib*.a

%files term -f terms.term

%changelog
*   Thu Aug 06 2020 Mateusz Malisz <mamalisz@microsoft.com> 6.2-4
-   Sync build process with Fedora 32.
-   Add libtinfo
*   Sat May 09 2020 Nick Samson <nisamson@microsoft.com> 6.2-3
-   Added %%license line automatically
*   Mon Apr 27 2020 Emre Girgin <mrgirgin@microsoft.com> 6.2-2
-   Rename ncurses-terminfo to ncurses-term.
*   Thu Apr 23 2020 Andrew Phelps <anphel@microsoft.com> 6.2-1
-   Update to version 6.2. Verified license.
*   Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 6.1-2
-   Initial CBL-Mariner import from Photon (license: Apache2).
*   Wed Sep 12 2018 Him Kalyan Bordoloi <bordoloih@vmware.com> 6.1-1
-   Update to version 6.1.
*   Tue Jul 17 2018 Tapas Kundu <tkundu@vmware.com> 6.0-14
-   Fix for CVE-2018-10754
*   Wed Dec 06 2017 Xiaolin Li <xiaolinl@vmware.com> 6.0-13
-   version bump to 20171007, fix CVE-2017-16879
*   Tue Oct 10 2017 Bo Gan <ganb@vmware.com> 6.0-12
-   version bump to 20171007
-   Fix for CVE-2017-11112, CVE-2017-11113 and CVE-2017-13728
*   Fri Sep 15 2017 Xiaolin Li <xiaolinl@vmware.com> 6.0-11
-   ncurses-devel provides pkgconfig(ncurses)
*   Thu Aug 10 2017 Bo Gan <ganb@vmware.com> 6.0-10
-   Move ncursesw6-config to devel
*   Thu Jul 06 2017 Dheeraj Shetty <dheerajs@vmware.com> 6.0-9
-   Fix for CVE-2017-10684 and CVE-2017-10685
*   Mon Jun 05 2017 Bo Gan <ganb@vmware.com> 6.0-8
-   Fix bash dependency
*   Sun Jun 04 2017 Bo Gan <ganb@vmware.com> 6.0-7
-   Fix symlink
*   Wed Mar 29 2017 Alexey Makhalov <amakhalov@vmware.com> 6.0-6
-   --with-chtype=long --with-mmask-t=long to avoid type clashes (1838226)
*   Wed Nov 23 2016 Alexey Makhalov <amakhalov@vmware.com> 6.0-5
-   Add -terminfo subpackage. Main package carries only 'linux' terminfo
*   Wed Nov 16 2016 Alexey Makhalov <amakhalov@vmware.com> 6.0-4
-   Move doc and man3 to the devel package
*   Fri Oct 07 2016 ChangLee <changlee@vmware.com> 6.0-3
-   Modified %check
*   Tue May 24 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 6.0-2
-   GA - Bump release of all rpms
*   Wed Apr 27 2016 Xiaolin Li <xiaolinl@vmware.com> 6.0-1
-   Update to version 6.0.
*   Wed Nov 18 2015 Mahmoud Bassiouny <mbassiouny@vmware.com> 5.9-4
-   Package provides libncurses.so.5()(64bit)
*   Tue Nov 10 2015 Mahmoud Bassiouny <mbassiouny@vmware.com> 5.9-3
-   Add libncurses.so.5, and minor fix in the devel package
*   Mon May 18 2015 Touseef Liaqat <tliaqat@vmware.com> 5.9-2
-   Update according to UsrMove.
*   Wed Nov 5 2014 Divya Thaluru <dthaluru@vmware.com> 5.9-1
-   Initial build. First version
