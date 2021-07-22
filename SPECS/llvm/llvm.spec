Summary:        A collection of modular and reusable compiler and toolchain technologies.
Name:           llvm
Version:        8.0.1
Release:        5%{?dist}
License:        NCSA
URL:            https://llvm.org/
Source0:        https://github.com/llvm/llvm-project/releases/download/llvmorg-%{version}/%{name}-%{version}.src.tar.xz
Group:          Development/Tools
Vendor:         Microsoft Corporation
Distribution:   Mariner

BuildRequires:  cmake
BuildRequires:  libxml2-devel
BuildRequires:  libffi-devel
BuildRequires:  python2
BuildRequires:  ninja-build

%if %{with_check}
BuildRequires:  python-xml
%endif

Requires:       libxml2

%description
The LLVM Project is a collection of modular and reusable compiler and toolchain technologies. Despite its name, LLVM has little to do with traditional virtual machines, though it does provide helpful libraries that can be used to build them. The name "LLVM" itself is not an acronym; it is the full name of the project.

%package devel
Summary:        Development headers for llvm
Requires:       %{name} = %{version}-%{release}

%description devel
The llvm-devel package contains libraries, header files and documentation
for developing applications that use llvm.

%prep
%setup -q -n %{name}-%{version}.src

%build
# Disable symbol generation
export CFLAGS="`echo " %{build_cflags} " | sed 's/ -g//'`"
export CXXFLAGS="`echo " %{build_cxxflags} " | sed 's/ -g//'`"

mkdir -p build
cd build
cmake -G Ninja                              \
      -DCMAKE_INSTALL_PREFIX=/usr           \
      -DLLVM_ENABLE_FFI=ON                  \
      -DCMAKE_BUILD_TYPE=Release            \
      -DLLVM_PARALLEL_LINK_JOBS=1           \
      -DLLVM_BUILD_LLVM_DYLIB=ON            \
      -DLLVM_INCLUDE_TESTS=ON               \
      -DLLVM_BUILD_TESTS=ON                 \
      -DLLVM_TARGETS_TO_BUILD="host;AMDGPU;BPF" \
      -DLLVM_INCLUDE_GO_TESTS=No            \
      -DLLVM_ENABLE_RTTI=ON                 \
      -Wno-dev ..

%ninja_build LLVM
%ninja_build

%install
%ninja_install -C build

%post   -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%check
# disable security hardening for tests
rm -f $(dirname $(gcc -print-libgcc-file-name))/../specs
cd build
ninja check-all

%clean
rm -rf %{buildroot}/*

%files
%defattr(-,root,root)
%license LICENSE.TXT
%{_bindir}/*
%{_libdir}/*.so
%{_libdir}/*.so.*
%dir %{_datadir}/opt-viewer
%{_datadir}/opt-viewer/opt-diff.py
%{_datadir}/opt-viewer/opt-stats.py
%{_datadir}/opt-viewer/opt-viewer.py
%{_datadir}/opt-viewer/optpmap.py
%{_datadir}/opt-viewer/optrecord.py
%{_datadir}/opt-viewer/style.css


%files devel
%{_libdir}/*.a
%{_libdir}/cmake/*
%{_includedir}/*

%changelog
*   Wed Feb 03 2021 Henry Beberman <henry.beberman@microsoft.com> - 8.0.1-5
-   Enable RTTI (runtime type information) so other packages can depend on it.
*   Thu Dec 17 2020 Andrew Phelps <anphel@microsoft.com> - 8.0.1-4
-   Enable tests in build and run test with ninja.
*   Fri Jun 12 2020 Henry Beberman <henry.beberman@microsoft.com> - 8.0.1-3
-   Switch to ninja-build to use LLVM_PARALLEL_LINK_JOBS=1 to reduce
-   fatal OOM errors during linking phase.
-   Temporarily disable generation of debug symbols.
*   Sat May 09 2020 Nick Samson <nisamson@microsoft.com> - 8.0.1-2
-   Added %%license line automatically
*   Tue Mar 17 2020 Henry Beberman <henry.beberman@microsoft.com> 8.0.1-1
-   Update to 8.0.1. URL Fixed. Source0 URL Fixed. License verified.
*   Fri Sep 27 2019 Andrew Phelps <anphel@microsoft.com> 6.0.1-5
-   Enable BPF target which is required for BCC spec
*   Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 6.0.1-4
-   Initial CBL-Mariner import from Photon (license: Apache2).
*   Wed Jun 26 2019 Keerthana K <keerthanak@vmware.com> 6.0.1-3
-   Enable target BPF
*   Tue Jan 08 2019 Alexey Makhalov <amakhalov@vmware.com> 6.0.1-2
-   Added BuildRequires python2
*   Thu Aug 09 2018 Srivatsa S. Bhat <srivatsa@csail.mit.edu> 6.0.1-1
-   Update to version 6.0.1 to get it to build with gcc 7.3
*   Thu Aug 10 2017 Alexey Makhalov <amakhalov@vmware.com> 4.0.0-3
-   Make check fix
*   Fri Apr 14 2017 Alexey Makhalov <amakhalov@vmware.com> 4.0.0-2
-   BuildRequires libffi-devel
*   Fri Apr 7 2017 Alexey Makhalov <amakhalov@vmware.com> 4.0.0-1
-   Version update
*   Wed Jan 11 2017 Xiaolin Li <xiaolinl@vmware.com>  3.9.1-1
-   Initial build.
