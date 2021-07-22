%{!?python3_sitelib: %define python3_sitelib %(python3 -c "from distutils.sysconfig import get_python_lib;print(get_python_lib())")}

%bcond_without check
%define pkgname remoto

Summary:        A very simplistic remote-command-executor
Name:           python-%{pkgname}
Version:        1.2.0
Release:        2%{?dist}
License:        MIT
URL:            https://github.com/alfredodeza/remoto
Vendor:         Microsoft Corporation
Distribution:   Mariner
Source0:        https://pypi.io/packages/source/r/%{pkgname}/%{pkgname}-%{version}.tar.gz

BuildArch:      noarch

%global _description %{expand:
A very simplistic remote-command-executor using connections to hosts (ssh, local, containers, and several others are supported) and Python in the remote end.

All the heavy lifting is done by execnet, while this minimal API provides the bare minimum to handle easy logging and connections from the remote end.

remoto is a bit opinionated as it was conceived to replace helpers and remote utilities for ceph-deploy, a tool to run remote commands to configure and setup the distributed file system Ceph. ceph-medic uses remoto as well to inspect Ceph clusters.}

%description %_description

%package -n python3-%{pkgname}
Summary:        A very simplistic remote-command-executor

BuildRequires:  python3-devel
BuildRequires:  python3-xml
BuildRequires:  python3-setuptools
Requires:       python3
Requires:       python3-execnet
%if %{with check}
BuildRequires:  python3-pip
%endif


%description -n python3-%{pkgname}  %_description

%prep
%setup -q -n %{pkgname}-%{version}

%build
python3 setup.py build

%install
python3 setup.py install --root=%{buildroot}

%if %{with check}
%check
pip3 install tox==3.4.0
tox
%endif

%files -n python3-%{pkgname}
%license LICENSE
%doc README.rst
%{python3_sitelib}/*

%changelog
* Wed Jun 23 2021 Neha Agarwal <nehaagarwal@microsoft.com> 1.2.0-2
- Pass check section

* Fri Aug 21 2020 Thomas Crain <thcrain@microsoft.com> 1.2.0-1
- Original version for CBL-Mariner
- License verified
