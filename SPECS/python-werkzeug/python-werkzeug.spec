%{!?python2_sitelib: %define python2_sitelib %(python2 -c "from distutils.sysconfig import get_python_lib;print(get_python_lib())")}
%{!?python3_sitelib: %define python3_sitelib %(python3 -c "from distutils.sysconfig import get_python_lib;print(get_python_lib())")}

Summary:        The Swiss Army knife of Python web development
Name:           python-werkzeug
Version:        0.14.1
Release:        6%{?dist}
License:        BSD
Group:          Development/Languages/Python
Vendor:         Microsoft Corporation
Distribution:   Mariner
Url:            https://pypi.python.org/pypi/Werkzeug
Source0:        https://files.pythonhosted.org/packages/9f/08/a3bb1c045ec602dc680906fc0261c267bed6b3bb4609430aff92c3888ec8/Werkzeug-%{version}.tar.gz

BuildRequires:  python2
BuildRequires:  python2-libs
BuildRequires:  python2-devel
BuildRequires:  python-setuptools
BuildRequires:  python-incremental
BuildRequires:  python3-devel
BuildRequires:  python3-libs
BuildRequires:  python3-setuptools
BuildRequires:  python3-xml
%if %{with_check}
BuildRequires:  python-requests
BuildRequires:  python-pip
BuildRequires:  python3-requests
BuildRequires:  curl-devel
BuildRequires:  openssl-devel
%endif
Requires:       python2
Requires:       python2-libs

BuildArch:      noarch

%description
Werkzeug started as simple collection of various utilities for WSGI applications and has become one of the most advanced WSGI utility modules. It includes a powerful debugger, full featured request and response objects, HTTP utilities to handle entity tags, cache control headers, HTTP dates, cookie handling, file uploads, a powerful URL routing system and a bunch of community contributed addon modules.

%package -n     python3-werkzeug
Summary:        python-werkzeug
Requires:       python3
Requires:       python3-libs
%description -n python3-werkzeug
Python 3 version.

%prep
%setup -q -n Werkzeug-%{version}

%build
python2 setup.py build
python3 setup.py build

%install
python2 setup.py install --prefix=%{_prefix} --root=%{buildroot}
python3 setup.py install --prefix=%{_prefix} --root=%{buildroot}

%check
# Remove unmaintained cache tests. See https://github.com/pallets/werkzeug/pull/1391
rm -vf tests/contrib/test_cache.py
rm -vf tests/contrib/cache/test_cache.py
pip install tox
LANG=en_US.UTF-8 tox -e py27

%files
%defattr(-,root,root)
%license LICENSE
%{python2_sitelib}/*

%files -n python3-werkzeug
%defattr(-,root,root)
%{python3_sitelib}/*

%changelog
*   Wed Mar 03 2021 Andrew Phelps <anphel@microsoft.com> 0.14.1-6
-   Remove test_cache.py tests. Use tox for tests.
*   Sat May 09 2020 Nick Samson <nisamson@microsoft.com> 0.14.1-5
-   Added %%license line automatically
*   Tue Apr 07 2020 Pawel Winogrodzki <pawelwi@microsoft.com> 0.14.1-4
-   Fixed "Source0" tag.
-   License verified.
*   Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 0.14.1-3
-   Initial CBL-Mariner import from Photon (license: Apache2).
*   Mon Dec 03 2018 Tapas Kundu <tkundu@vmware.com> 0.14.1-2
-   Fix make check
-   Moved buildrequires from subpackage
*   Sun Sep 09 2018 Tapas Kundu <tkundu@vmware.com> 0.14.1-1
-   Update to version 0.14.1
*   Tue Jul 25 2017 Divya Thaluru <dthaluru@vmware.com> 0.12.1-2
-   Fixed rpm check errors
*   Thu Mar 30 2017 Siju Maliakkal <smaliakkal@vmware.com> 0.12.1-1
-   Updating package to latest
*   Mon Mar 06 2017 Xiaolin Li <xiaolinl@vmware.com> 0.11.15-1
-   Initial packaging for Photon.
