%{!?python2_sitelib: %global python2_sitelib %(python2 -c "from distutils.sysconfig import get_python_lib;print(get_python_lib())")}
Summary:        A next generation, high-performance debugger.
Name:           lldb
Version:        8.0.1
Release:        3%{?dist}
License:        NCSA
URL:            https://lldb.llvm.org
Source0:        https://github.com/llvm/llvm-project/releases/download/llvmorg-%{version}/%{name}-%{version}.src.tar.xz
Group:          Development/Tools
Vendor:         Microsoft Corporation
Distribution:   Mariner
BuildRequires:  cmake
BuildRequires:  llvm-devel = %{version}
BuildRequires:  clang-devel = %{version}
BuildRequires:  ncurses-devel
BuildRequires:  swig
BuildRequires:  zlib-devel
BuildRequires:  libxml2-devel
Requires:       llvm = %{version}
Requires:       clang = %{version}
Requires:       ncurses
Requires:       zlib
Requires:       libxml2

%description
LLDB is a next generation, high-performance debugger. It is built as a set of reusable components which highly leverage existing libraries in the larger LLVM Project, such as the Clang expression parser and LLVM disassembler.

%package devel
Summary:        Development headers for lldb
Requires:       %{name} = %{version}-%{release}

%description devel
The lldb-devel package contains libraries, header files and documentation
for developing applications that use lldb.

%package -n python-lldb
Summary:        Python module for lldb
Requires:       %{name} = %{version}-%{release}
BuildRequires:  python2-devel
Requires:       python-six

%description -n python-lldb
The package contains the LLDB Python module.

%prep
%setup -q -n %{name}-%{version}.src

%build
# Disable symbol generation
export CFLAGS="`echo " %{build_cflags} " | sed 's/ -g//'`"
export CXXFLAGS="`echo " %{build_cxxflags} " | sed 's/ -g//'`"

mkdir -p build
cd build
cmake -DCMAKE_INSTALL_PREFIX=/usr           \
      -DCMAKE_BUILD_TYPE=Release            \
      -DLLDB_PATH_TO_LLVM_BUILD=%{_prefix}  \
      -DLLDB_PATH_TO_CLANG_BUILD=%{_prefix} \
      -DLLVM_DIR=/usr/lib/cmake/llvm        \
      -DLLVM_BUILD_LLVM_DYLIB=ON ..         \
      -DLLDB_DISABLE_LIBEDIT:BOOL=ON

make %{?_smp_mflags}

%install
[ %{buildroot} != "/"] && rm -rf %{buildroot}/*
cd build
make DESTDIR=%{buildroot} install

#Remove bundled python-six files
rm -f %{buildroot}%{python2_sitelib}/six.*

%post   -p /sbin/ldconfig
%postun -p /sbin/ldconfig

#%check
#Commented out %check due to no test existence

%clean
rm -rf %{buildroot}/*

%files
%defattr(-,root,root)
%license LICENSE.TXT
%{_bindir}/*
%{_libdir}/liblldb.so.*
%{_libdir}/liblldbIntelFeatures.so.*

%files devel
%defattr(-,root,root)
%{_libdir}/liblldb.so
%{_libdir}/liblldbIntelFeatures.so
%{_libdir}/*.a
%{_includedir}/*

%files -n python-lldb
%defattr(-,root,root)
%{python2_sitelib}/*

%changelog
*   Fri Jun 12 2020 Henry Beberman <henry.beberman@microsoft.com> 8.0.1-3
-   Temporarily disable generation of debug symbols.
*   Sat May 09 2020 Nick Samson <nisamson@microsoft.com> - 8.0.1-2
-   Added %%license line automatically
*   Tue Mar 17 2020 Henry Beberman <henry.beberman@microsoft.com> 8.0.1-1
-   Update to 8.0.1. Source0 URL fixed. License verified.
*   Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 6.0.1-2
-   Initial CBL-Mariner import from Photon (license: Apache2).
*   Thu Aug 09 2018 Srivatsa S. Bhat <srivatsa@csail.mit.edu> 6.0.1-1
-   Update to version 6.0.1 to get it to build with gcc 7.3
-   Make python2_sitelib macro global to fix build error.
*   Mon Jul 10 2017 Chang Lee <changlee@vmware.com> 4.0.0-3
-   Commented out %check due to no test existence.
*   Wed Jul 5 2017 Divya Thaluru <dthaluru@vmware.com> 4.0.0-2
-   Added python-lldb package
*   Fri Apr 7 2017 Alexey Makhalov <amakhalov@vmware.com> 4.0.0-1
-   Version update
*   Wed Jan 11 2017 Xiaolin Li <xiaolinl@vmware.com>  3.9.1-1
-   Initial build.
