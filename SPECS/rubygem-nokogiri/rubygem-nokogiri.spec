%global debug_package %{nil}
%global gemdir %(IFS=: R=($(gem env gempath)); echo ${R[${#R[@]}-1]})
%global gem_name nokogiri
Summary:        a Rubygem providing HTML, XML, SAX, and Reader parsers with XPath and CSS selector support
Name:           rubygem-nokogiri
Version:        1.11.0.rc2
Release:        1%{?dist}
License:        MIT
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          Development/Languages
URL:            https://rubygems.org/gems/%{gem_name}/versions/%{version}
Source0:        https://rubygems.org/downloads/%{gem_name}-%{version}.gem
BuildRequires:  ruby
BuildRequires:  rubygem-mini_portile2
Requires:       rubygem-mini_portile2

%description
Nokogiri (鋸) makes it easy and painless to work with XML and HTML from Ruby.
It provides a sensible, easy-to-understand API for reading, writing, modifying,
and querying documents. It is fast and standards-compliant by relying on native
parsers like libxml2 (C) and xerces (Java).

%prep
%setup -q -c -T

%build

%install
gem install -V --local --force --install-dir %{buildroot}/%{gemdir} %{SOURCE0}

%files
%defattr(-,root,root,-)
%license %{gemdir}/gems/%{gem_name}-%{version}/LICENSE.md
%{gemdir}

%changelog
* Mon Jan 04 2021 Henry Li <lihl@microsoft.com> - 1.11.0.rc2-1
- License verified
- Original version for CBL-Mariner