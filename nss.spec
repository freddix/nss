%define		foover		%(echo %{version} | tr . _)
%define		nspr_req	4.10

Summary:	Network Security Services
Name:		nss
Version:	3.15.1
Release:	2
Epoch:		1
License:	GPL
Group:		Libraries
Source0:	http://ftp.mozilla.org/pub/mozilla.org/security/nss/releases/NSS_%{foover}_RTM/src/%{name}-%{version}.tar.gz
# Source0-md5:	fb68f4d210ac9397dd0d3c39c4f938eb
Source1:	%{name}.pc.in
Source2:	%{name}-config.in
Source3:	http://www.cacert.org/certs/root.der
# Source3-md5:	a61b375e390d9c3654eebd2031461f6b
Patch0:		%{name}-makefile.patch
URL:		http://www.mozilla.org/projects/security/pki/nss/
BuildRequires:	nspr-devel >= 1:%{nspr_req}
BuildRequires:	nss-tools
BuildRequires:	sqlite3-devel
BuildRequires:	zlib-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define         _noautostrip    .*%{_libdir}/libfreebl3.so\\|.*%{_libdir}/libsoftokn3.so
%define         _noautochrpath  .*%{_libdir}/libfreebl3.so\\|.*%{_libdir}/libsoftokn3.so

%description
NSS supports cross-platform development of security-enabled server
applications. Applications built with NSS can support PKCS #5,
PKCS #7, PKCS #11, PKCS #12, S/MIME, TLS, SSL v2 and v3, X.509 v3
certificates, and other security standards.

%package tools
Summary:	NSS command line tools and utilities
Group:		Applications
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description tools
The NSS Toolkit command line tool.

%package devel
Summary:	NSS - header files
Group:		Development/Libraries
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description devel
Development part of NSS library.

%package static
Summary:	NSS - static library
Group:		Development/Libraries
Requires:	%{name}-devel = %{epoch}:%{version}-%{release}

%description static
Static NSS Toolkit libraries.

%prep
%setup -q
%patch0 -p1

# strip before signing
%{__sed} -i -e '/export ADDON_PATH$/a\    echo STRIP \; %{__strip} --strip-unneeded -R.comment -R.note ${5}' nss/cmd/shlibsign/sign.sh

%build
cd nss

# http://wiki.cacert.org/wiki/NSSLib
addbuiltin -n "CAcert Inc." -t "CT,C,C" < %{SOURCE3} >> lib/ckfw/builtins/certdata.txt

%ifarch %{x8664} 
export USE_64=1
%endif
export BUILD_OPT=1
export FREEBL_NO_DEPEND=1
export LOWHASH_EXPORTS=nsslowhash.h
export MOZILLA_CLIENT=1
export NO_MDUPDATE=1
export NSDISTMODE=copy
export NSS_USE_SYSTEM_SQLITE=1
export NS_USE_GCC=1
export USE_PTHREADS=1
export USE_SYSTEM_ZLIB=1
export XCFLAGS="%{rpmcflags}"
export ZLIB_LIBS="-lz"

%{__make} -C coreconf -j1
%{__make} -j1 all

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_includedir}/nss,%{_libdir},%{_pkgconfigdir}}

install dist/private/nss/* $RPM_BUILD_ROOT%{_includedir}/nss
install dist/public/dbm/* $RPM_BUILD_ROOT%{_includedir}/nss
install dist/public/nss/* $RPM_BUILD_ROOT%{_includedir}/nss
install dist/*.OBJ/bin/* $RPM_BUILD_ROOT%{_bindir}
install dist/*.OBJ/lib/* $RPM_BUILD_ROOT%{_libdir}

# instal pc file
%{__sed} -e "
	s,%prefix%,%{_prefix},g
	s,%exec_prefix%,%{_bindir},g
	s,%libdir%,%{_libdir},g
	s,%includedir%,%{_includedir}/nss,g
	s,%NSS_VERSION%,%{version},g
	s,%NSPR_VERSION%,%{nspr_req},g
	s,%nspr_includedir%,`pkg-config --cflags nspr`,g
" %{SOURCE1} > $RPM_BUILD_ROOT%{_pkgconfigdir}/nss.pc

# isntall nss-config file
NSS_VMAJOR=$(awk '/#define.*NSS_VMAJOR/ {print $3}' nss/lib/nss/nss.h)
NSS_VMINOR=$(awk '/#define.*NSS_VMINOR/ {print $3}' nss/lib/nss/nss.h)
NSS_VPATCH=$(awk '/#define.*NSS_VPATCH/ {print $3}' nss/lib/nss/nss.h)
%{__sed} -e "
	s,@libdir@,%{_libdir},g
	s,@prefix@,%{_prefix},g
	s,@exec_prefix@,%{_prefix},g
	s,@includedir@,%{_includedir}/nss,g
	s,@MOD_MAJOR_VERSION@,$NSS_VMAJOR,g
	s,@MOD_MINOR_VERSION@,$NSS_VMINOR,g
	s,@MOD_PATCH_VERSION@,$NSS_VPATCH,g
" %{SOURCE2} > $RPM_BUILD_ROOT%{_bindir}/nss-config
chmod +x $RPM_BUILD_ROOT%{_bindir}/nss-config

[ -f "$RPM_BUILD_ROOT%{_includedir}/nss/nsslowhash.h" ] || exit 1

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /usr/sbin/ldconfig
%postun	-p /usr/sbin/ldconfig

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libfreebl3.so
%attr(755,root,root) %{_libdir}/libnss3.so
%attr(755,root,root) %{_libdir}/libnssckbi.so
%attr(755,root,root) %{_libdir}/libnssdbm3.so
%attr(755,root,root) %{_libdir}/libnssutil3.so
%attr(755,root,root) %{_libdir}/libsmime3.so
%attr(755,root,root) %{_libdir}/libsoftokn3.so
%attr(755,root,root) %{_libdir}/libssl3.so
%{_libdir}/libnssdbm3.chk
%{_libdir}/libsoftokn3.chk
%{_libdir}/libfreebl3.chk

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/nss-config
%{_includedir}/nss
%{_libdir}/libcrmf.a
%{_pkgconfigdir}/nss.pc

%files static
%defattr(644,root,root,755)
%{_libdir}/libcertdb.a
%{_libdir}/libcerthi.a
%{_libdir}/libcryptohi.a
%{_libdir}/libdbm.a
%{_libdir}/libfreebl3.a
%{_libdir}/libjar.a
%{_libdir}/libnss3.a
%{_libdir}/libnssb.a
%{_libdir}/libnssckfw.a
%{_libdir}/libnssdbm3.a
%{_libdir}/libnssdev.a
%{_libdir}/libnsspki3.a
%{_libdir}/libnssutil3.a
%{_libdir}/libpk11wrap3.a
%{_libdir}/libpkcs12.a
%{_libdir}/libpkcs7.a
%{_libdir}/libpkixcertsel.a
%{_libdir}/libpkixchecker.a
%{_libdir}/libpkixcrlsel.a
%{_libdir}/libpkixmodule.a
%{_libdir}/libpkixparams.a
%{_libdir}/libpkixpki.a
%{_libdir}/libpkixresults.a
%{_libdir}/libpkixstore.a
%{_libdir}/libpkixsystem.a
%{_libdir}/libpkixtop.a
%{_libdir}/libpkixutil.a
%{_libdir}/libsectool.a
%{_libdir}/libsmime3.a
%{_libdir}/libsoftokn3.a
%{_libdir}/libssl3.a

%files tools
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/*
%exclude %{_bindir}/nss-config

