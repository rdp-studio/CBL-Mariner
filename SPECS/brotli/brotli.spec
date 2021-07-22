%define python3_sitearch %(python3 -c "from distutils.sysconfig import get_python_lib; import sys; sys.stdout.write(get_python_lib(1))")
%define python3_version 3.7
%define python3_version_nodots 37
Summary:        Lossless compression algorithm
Name:           brotli
Version:        1.0.7
Release:        9%{?dist}
License:        MIT
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          Applications/File
URL:            https://github.com/google/brotli
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Patch0:         CVE-2020-8927.patch
BuildRequires:  cmake
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
%if %{with_check}
BuildRequires:  python3-xml
%endif

%description
Brotli is a generic-purpose lossless compression algorithm that compresses
data using a combination of a modern variant of the LZ77 algorithm, Huffman
coding and 2nd order context modeling, with a compression ratio comparable
to the best currently available general-purpose compression methods.
It is similar in speed with deflate but offers more dense compression.

%package -n python3-%{name}
%{?python_provide:%python_provide python3-%{name}}
Summary:        Lossless compression algorithm (python 3)

%description -n python3-%{name}
Brotli is a generic-purpose lossless compression algorithm that compresses
data using a combination of a modern variant of the LZ77 algorithm, Huffman
coding and 2nd order context modeling, with a compression ratio comparable
to the best currently available general-purpose compression methods.
It is similar in speed with deflate but offers more dense compression.
This package installs a Python 3 module.

%package devel
Summary:        Lossless compression algorithm (development files)
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Brotli is a generic-purpose lossless compression algorithm that compresses
data using a combination of a modern variant of the LZ77 algorithm, Huffman
coding and 2nd order context modeling, with a compression ratio comparable
to the best currently available general-purpose compression methods.
It is similar in speed with deflate but offers more dense compression.
This package installs the development files

%prep
%autosetup -p1

# fix permissions for -debuginfo
# rpmlint will complain if I create an extra %%files section for
# -debuginfo for this so we'll put it here instead
chmod 644 c/enc/*.[ch]
chmod 644 c/include/brotli/*.h
chmod 644 c/tools/brotli.c

%build
%if 0%{?rhel} == 7
. /opt/rh/devtoolset-7/enable
%endif
mkdir -p build
cd build
%cmake .. -DCMAKE_INSTALL_PREFIX="%{_prefix}" \
    -DCMAKE_INSTALL_LIBDIR="%{_libdir}"
%make_build
cd ..
python3 setup.py build

%install
%if 0%{?rhel} == 7
. /opt/rh/devtoolset-7/enable
%endif
cd build
%make_install

# I couldn't find the option to not build the static libraries
rm "%{buildroot}%{_libdir}/"*.a

cd ..
python3 setup.py install --skip-build --prefix=%{_prefix} --root=%{buildroot}
install -dm755 "%{buildroot}%{_mandir}/man3"
cd docs
for i in *.3;do
install -m644 "$i" "%{buildroot}%{_mandir}/man3/${i}brotli"
done

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%check
cd build
ctest -V
cd ..
python3 setup.py test

%files
%{_bindir}/brotli
%{_libdir}/libbrotlicommon.so.1*
%{_libdir}/libbrotlidec.so.1*
%{_libdir}/libbrotlienc.so.1*
%license LICENSE

# Note that there is no %%files section for the unversioned python module
# if we are building for several python runtimes
%files -n python3-%{name}
%{python3_sitearch}/brotli.py
%{python3_sitearch}/_brotli.cpython-%{python3_version_nodots}*.so
%{python3_sitearch}/__pycache__/brotli.cpython-%{python3_version_nodots}*.py*
%{python3_sitearch}/Brotli-%{version}-py%{python3_version}.egg-info
%license LICENSE

%files devel
%{_includedir}/brotli
%{_libdir}/libbrotlicommon.so
%{_libdir}/libbrotlidec.so
%{_libdir}/libbrotlienc.so
%{_libdir}/pkgconfig/libbrotlicommon.pc
%{_libdir}/pkgconfig/libbrotlidec.pc
%{_libdir}/pkgconfig/libbrotlienc.pc
%{_mandir}/man3/decode.h.3brotli*
%{_mandir}/man3/encode.h.3brotli*
%{_mandir}/man3/types.h.3brotli*

%changelog
* Fri Oct 30 2020 Thomas Crain <thcrain@microsoft.com> - 1.0.7-9
- Patch CVE-2020-8927
- Remove sha1 hash
- Lint to Mariner style

* Tue Oct 20 2020 Andrew Phelps <anphel@microsoft.com> 1.0.7-8
- Fix check test

* Mon Dec 9 2019 Emre Girgin <mrgirgin@microsoft.com>  1.0.7-7
- Initial CBL-Mariner import from Fedora 31 (license: MIT).

* Wed Jul 24 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.7-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Sat Apr 20 2019 Orion Poplawski <orion@nwra.com> - 1.0.7-5
- Build with devtoolset-7 on EPEL7 to fix aarch64 builds

* Thu Mar 28 2019 Carl George <carl@george.computer> - 1.0.7-4
- EPEL compatibility

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.7-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Sun Dec 09 2018 Miro Hrončok <mhroncok@redhat.com> - 1.0.7-2
- Remove last python2 bits

* Wed Nov 28 2018 Travis Kendrick pouar@pouar.net> - 1.0.7-1
- Update to 1.0.7

* Wed Nov 28 2018 Travis Kendrick pouar@pouar.net> - 1.0.5-2
- remove Python 2 support https://fedoraproject.org/wiki/Changes/Mass_Python_2_Package_Removal

* Fri Jul 13 2018 Travis Kendrick pouar@pouar.net> - 1.0.5-1
- update to 1.0.5

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Mon Jun 18 2018 Miro Hrončok <mhroncok@redhat.com> - 1.0.4-3
- Rebuilt for Python 3.7

* Wed Apr 18 2018 Travis Kendrick pouar@pouar.net> - 1.0.4-2
- update to 1.0.4

* Sat Mar 03 2018 Travis Kendrick <pouar@pouar.net> - 1.0.3-1
- update to 1.0.3

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sat Feb 03 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1.0.1-2
- Switch to %%ldconfig_scriptlets

* Fri Sep 22 2017 Travis Kendrick <pouar@pouar.net> - 1.0.1-1
- update to 1.0.1

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.6.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.6.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue May 23 2017 Travis Kendrick <pouar@pouar.net> - 0.6.0-4
- add man pages

* Sun May 14 2017 Travis Kendrick <pouar@pouar.net> - 0.6.0-3
- wrong directory for ctest
- LICENSE not needed in -devel
- fix "spurious-executable-perm"
- rpmbuild does the cleaning for us, so 'rm -rf %%{buildroot}' isn't needed

* Sat May 13 2017 Travis Kendrick <pouar@pouar.net> - 0.6.0-2
- include libraries and development files

* Sat May 06 2017 Travis Kendrick <pouar@pouar.net> - 0.6.0-1
- Initial build
