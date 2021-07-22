%{!?python3_sitelib: %define python3_sitelib %(python3 -c "from distutils.sysconfig import get_python_lib;print(get_python_lib())")}

%bcond_without check
%define pkgname repoze-lru
%define pypiname repoze.lru

Summary:        A tiny LRU cache implementation and decorator
Name:           python-%{pkgname}
Version:        0.7
Release:        2%{?dist}
License:        BSD
URL:            https://github.com/repoze/repoze.lru
Vendor:         Microsoft Corporation
Distribution:   Mariner
#Source0:       https://pypi.io/packages/source/r/%{pypiname}/%{pypiname}-%{version}.tar.gz
Source0:        %{pkgname}-%{version}.tar.gz

BuildArch:      noarch

%global _description %{expand:
A tiny LRU cache implementation and decorator.}

%description %_description

%package -n python3-%{pkgname}
Summary:        A tiny LRU cache implementation and decorator

BuildRequires:  python3-devel
BuildRequires:  python3-xml
BuildRequires:  python3-setuptools
Requires:       python3
%if %{with check}
BuildRequires:  python3-pip
%endif


%description -n python3-%{pkgname}  %_description

%prep
%setup -q -n %{pypiname}-%{version}

%build
python3 setup.py build

%install
python3 setup.py install --root=%{buildroot}

%if %{with check}
%check
pip3 install tox
LANG=en_US.UTF-8 tox -e py37
%endif

%files -n python3-%{pkgname}
%license LICENSE.txt
%doc README.rst
%{python3_sitelib}/*

%changelog
* Tue Jun 08 2021 Andrew Phelps <anphel@microsoft.com> 0.7-2
- Fix check tests
* Fri Aug 21 2020 Thomas Crain <thcrain@microsoft.com> 0.7-1
- Original version for CBL-Mariner
- License verified
