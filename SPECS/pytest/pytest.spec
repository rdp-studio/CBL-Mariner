%{!?python2_sitelib: %define python2_sitelib %(python2 -c "from distutils.sysconfig import get_python_lib;print(get_python_lib())")}
%{!?python3_sitelib: %define python3_sitelib %(python3 -c "from distutils.sysconfig import get_python_lib;print(get_python_lib())")}
%{!?python2_version: %define python2_version %(python2 -c "import sys; sys.stdout.write(sys.version[:3])")}
%{!?python3_version: %define python3_version %(python3 -c "import sys; sys.stdout.write(sys.version[:3])")}

Name:           pytest
Version:        3.8.2
Release:        6%{?dist}
Summary:        pytest is a mature full-featured Python testing tool that helps you write better programs
License:        MIT
Group:          Development/Languages/Python
URL:            https://docs.pytest.org
Vendor:         Microsoft Corporation
Distribution:   Mariner
#Source0:        https://github.com/pytest-dev/pytest/archive/%{version}.tar.gz
Source0:        https://files.pythonhosted.org/packages/5f/d2/7f77f406ac505abda02ab4afb50d06ebf304f6ea42fca34f8f37529106b2/pytest-%{version}.tar.gz

BuildRequires:  python2
BuildRequires:  python2-devel
BuildRequires:  python2-libs
BuildRequires:  python-setuptools
BuildRequires:  python-py
BuildRequires:  python-xml
BuildRequires:  python-hypothesis
BuildRequires:  python-twisted
BuildRequires:  python-setuptools_scm
BuildRequires:  python3
BuildRequires:  python3-devel
BuildRequires:  python3-py
BuildRequires:  python3-hypothesis
BuildRequires:  python3-twisted
BuildRequires:  python3-setuptools
BuildRequires:  python3-xml
BuildRequires:  python3-setuptools_scm
Requires:       python2
Requires:       python2-libs
Requires:       python-py

BuildArch:      noarch

%description
pytest framework makes it easy to write small tests, yet scales to support complex functional testing for applications and libraries.

%package -n     python3-pytest
Summary:        pytest is a mature full-featured Python testing tool that helps you write better programs
Requires:       python3
Requires:       python3-libs
Requires:       python3-py

%description -n python3-pytest

Python 3 version.

%prep
%setup -q
rm -rf ../p3dir
cp -a . ../p3dir

%build
python2 setup.py build
pushd ../p3dir
python3 setup.py build
popd

%install
python2 setup.py install --prefix=%{_prefix} --root=%{buildroot}

mv %{buildroot}%{_bindir}/pytest %{buildroot}%{_bindir}/pytest%{python2_version}
ln -snf pytest%{python2_version} %{buildroot}%{_bindir}/pytest2
mv %{buildroot}%{_bindir}/py.test %{buildroot}%{_bindir}/py.test%{python2_version}
ln -snf py.test%{python2_version} %{buildroot}%{_bindir}/py.test2


pushd ../p3dir
python3 setup.py install --prefix=%{_prefix} --root=%{buildroot}
mv %{buildroot}%{_bindir}/pytest %{buildroot}%{_bindir}/pytest%{python3_version}
ln -snf pytest%{python3_version} %{buildroot}%{_bindir}/pytest3
mv %{buildroot}%{_bindir}/py.test %{buildroot}%{_bindir}/py.test%{python3_version}
ln -snf py.test%{python3_version} %{buildroot}%{_bindir}/py.test3
popd

%check
make -k check |& tee %{_specdir}/%{name}-check-log || %{nocheck}

%files
%defattr(-,root,root,-)
%license LICENSE
%{_bindir}/pytest2
%{_bindir}/pytest%{python2_version}
%{_bindir}/py.test2
%{_bindir}/py.test%{python2_version}
%{python2_sitelib}/*

%files -n python3-pytest
%defattr(-,root,root,-)
%{_bindir}/pytest3
%{_bindir}/pytest%{python3_version}
%{_bindir}/py.test3
%{_bindir}/py.test%{python3_version}
%{python3_sitelib}/*

%changelog
* Sat May 09 2020 Nick Samson <nisamson@microsoft.com> - 3.8.2-6
- Added %%license line automatically

*   Thu Apr 30 2020 Emre Girgin <mrgirgin@microsoft.com> 3.8.2-5
-   Renaming python-pytest to pytest
*   Tue Apr 28 2020 Emre Girgin <mrgirgin@microsoft.com> 3.8.2-4
-   Renaming python-Twisted to python-twisted
*   Mon Apr 20 2020 Eric Li <eli@microsoft.com> 3.8.2-3
-   Update Source0:, add #Source0, and delete sha1. License verified.
*   Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 3.8.2-2
-   Initial CBL-Mariner import from Photon (license: Apache2).
*   Tue Oct 09 2018 Tapas Kundu <tkundu@vmware.com> 3.8.2-1
-   Updated to release 3.8.2
-   Removed buildrequires from subpackage.
*   Wed Jun 07 2017 Xiaolin Li <xiaolinl@vmware.com> 3.0.7-3
-   Add python3-setuptools and python3-xml to python3 sub package Buildrequires.
*   Thu Jun 01 2017 Dheeraj Shetty <dheerajs@vmware.com> 3.0.7-2
-   Use python2 instead of python and rename the scripts in bin directory
*   Tue Apr 25 2017 Dheeraj Shetty <dheerajs@vmware.com> 3.0.7-1
-   Initial
