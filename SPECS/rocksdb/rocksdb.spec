%define _build_id_links none

Name:           rocksdb
Summary:        A library that provides an embeddable, persistent key-value store for fast storage.
Version:        6.7.3
Release:        2%{?dist}
License:        GPLv2+ and ASL 2.0 and BSD
Vendor:         Microsoft Corporation
Distribution:   Mariner
URL:            https://rocksdb.org
#Source0:       https://github.com/facebook/%{name}/archive/v%{version}.tar.gz
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  build-essential
BuildRequires:  gflags-devel

%description
RocksDB is developed and maintained by Facebook Database Engineering Team. It is built on
earlier work on LevelDB by Sanjay Ghemawat (sanjay@google.com) and Jeff Dean (jeff@google.com)

This code is a library that forms the core building block for a fast key-value server, 
especially suited for storing data on flash drives. It has a Log-Structured-Merge-Database
(LSM) design with flexible tradeoffs between Write-Amplification-Factor (WAF), 
Read-Amplification-Factor (RAF) and Space-Amplification-Factor (SAF). It has multi-threaded
compactions, making it especially suitable for storing multiple terabytes of data in a single
database.

%package devel
Summary:        Development files for %{name}
Requires:       %{name} = %{version}

%description devel
Development files for %{name}

%prep
%setup -q

%build
mkdir build
cd build
%cmake -DPORTABLE=1 ..
make %{?_smp_mflags}

%install
cd build
make install DESTDIR=%{buildroot}

%files
%license COPYING
%license LICENSE.Apache
%license LICENSE.leveldb
%doc README.md
%{_libdir}/*.so.*

%files devel
%{_includedir}/rocksdb
%{_libdir}/{*.so,*.a}
%{_libdir}/cmake/rocksdb
/usr/src/debug/*

%changelog
*   Thu Oct 08 2020 Pawel Winogrodzki <pawelwi@microsoft.com> 6.7.3-2
-   Fixed 'Source0' URL.
-   License verified.
*   Mon Mar 30 2020 Jonathan Chiu <jochi@microsoft.com> 6.7.3-1
-   Original version for CBL-Mariner.
