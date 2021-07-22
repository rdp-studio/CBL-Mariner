%global debug_package %{nil}
%global gemdir %(IFS=: R=($(gem env gempath)); echo ${R[${#R[@]}-1]})
%global gem_name rake
Summary:        A make-like build utility for Ruby
Name:           rubygem-rake
Version:        13.0.1
Release:        1%{?dist}
License:        MIT
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          Development/Languages
URL:            https://rubygems.org/gems/%{gem_name}/versions/%{version}
Source0:        https://rubygems.org/downloads/%{gem_name}-%{version}.gem
BuildRequires:  ruby

%description
Rake is a Make-like program implemented in Ruby. Tasks and
dependencies are specified in standard Ruby syntax.

%prep
%setup -q -c -T

%build

%install
gem install -V --local --force --install-dir %{buildroot}/%{gemdir} %{SOURCE0}

%files
%defattr(-,root,root,-)
%license %{gemdir}/gems/%{gem_name}-%{version}/MIT-LICENSE
%{gemdir}

%changelog
* Mon Jan 04 2021 Henry Li <lihl@microsoft.com> - 13.0.1-1
- License verified
- Original version for CBL-Mariner