%global __strip %{_mingw32_strip}
%global __objdump %{_mingw32_objdump}
%global _use_internal_dependency_generator 0
%global __find_requires %{_mingw32_findrequires}
%global __find_provides %{_mingw32_findprovides}
%define __debug_install_post %{_mingw32_debug_install_post}

%global sonamever 5

%global name1 boost
%global vermajor 1
%global verminor 39
%global verrelease 0

%global verdot %{vermajor}.%{verminor}.%{verrelease}
%global verunderscore %{vermajor}_%{verminor}_%{verrelease}

Name:           mingw32-%{name1}
Version:        %{verdot}
Release:        2%{?dist}
Summary:        MinGW Windows port of Boost C++ Libraries

License:        Boost
Group:          Development/Libraries
URL:            http://www.boost.org/
Source0:        http://surfnet.dl.sourceforge.net/sourceforge/%{name1}/%{name1}_%{verunderscore}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Patch0: boost-version-override.patch
Patch2: boost-run-tests.patch
Patch3: boost-soname.patch
Patch4: boost-unneccessary_iostreams.patch
Patch5: boost-bitset.patch
Patch6: boost-function_template.patch
Patch10: boost-regexdll.patch

BuildArch:      noarch

BuildRequires:  file
BuildRequires:  mingw32-filesystem >= 52
BuildRequires:  mingw32-gcc
BuildRequires:  mingw32-gcc-c++
BuildRequires:  mingw32-binutils
BuildRequires:  mingw32-bzip2
BuildRequires:  mingw32-zlib
BuildRequires:  mingw32-expat
BuildRequires:  mingw32-pthreads
BuildRequires:  perl
# These are required by the native package:
#BuildRequires:  mingw32-python
#BuildRequires:  mingw32-libicu


%description
Boost provides free peer-reviewed portable C++ source libraries.  The
emphasis is on libraries which work well with the C++ Standard
Library, in the hopes of establishing "existing practice" for
extensions and providing reference implementations so that the Boost
libraries are suitable for eventual standardization. (Some of the
libraries have already been proposed for inclusion in the C++
Standards Committee's upcoming C++ Standard Library Technical Report.)

%package static
Summary:        Static version of the MinGW Windows Boost C++ library
Requires:       %{name} = %{version}-%{release}
Group:          Development/Libraries

%description static
Static version of the MinGW Windows Boost C++ library.


%{_mingw32_debug_package}

%prep
%setup -q -n %{name1}_%{verunderscore}
%patch0 -p0
%patch2 -p0
sed 's/_FEDORA_SONAME/%{sonamever}/' %{PATCH3} | %{__patch} -p0 --fuzz=0
%patch4 -p0
%patch5 -p0
%patch6 -p0
%patch10 -p0

%build
BOOST_ROOT=`pwd`
staged_dir=stage
export BOOST_ROOT

# build make tools, ie bjam, necessary for building libs, docs, and testing
(cd tools/jam/src && ./build.sh)
BJAM=`find tools/jam/src/ -name bjam -a -type f`

#BUILD_FLAGS="--with-toolset=gcc --prefix=$RPM_BUILD_ROOT%{_prefix}"
BUILD_FLAGS="--with-toolset=gcc --with-bjam=$BJAM"
#PYTHON_VERSION=$(python -c 'import sys; print sys.version[:3]')
#PYTHON_FLAGS="--with-python-root=/usr --with-python-version=$PYTHON_VERSION"
PYTHON_FLAGS="--without-libraries=python"
#REGEX_FLAGS="--with-icu"
REGEX_FLAGS="--without-icu"
EXPAT_INCLUDE=/usr/i686-pc-mingw32/sys-root/mingw/include
EXPAT_LIBPATH=/usr/i686-pc-mingw32/sys-root/mingw/lib
PTW32_INCLUDE=/usr/i686-pc-mingw32/sys-root/mingw/include
PTW32_LIB=/usr/i686-pc-mingw32/sys-root/mingw/lib
export EXPAT_INCLUDE EXPAT_LIBPATH PTW32_INCLUDE PTW32_LIB

./bootstrap.sh $BUILD_FLAGS $PYTHON_FLAGS $REGEX_FLAGS

# Make it use the cross-compiler instead of gcc.
echo "using gcc : : %{_mingw32_cxx}" > user-config.jam
echo "        : # options" >> user-config.jam
echo "          <rc>%{_mingw32_windres}" >> user-config.jam
echo "          <archiver>%{_mingw32_ar}" >> user-config.jam
echo "        ;" >> user-config.jam

BUILD_VARIANTS="variant=release threading=single,multi debug-symbols=on link=static,shared target-os=windows"
BUILD_FLAGS="-d2 --layout=system --user-config=user-config.jam $BUILD_VARIANTS"
$BJAM $BUILD_FLAGS %{?_smp_mflags} stage


%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_mingw32_bindir}
mkdir -p $RPM_BUILD_ROOT%{_mingw32_libdir}
mkdir -p $RPM_BUILD_ROOT%{_mingw32_includedir}

for i in `find bin.v2 -name '*.lib'`; do
  b=`basename $i .lib`
  d=`dirname $i`
  if [ -f $d/$b.dll ]; then
    install -m 644 -p $d/$b.dll $RPM_BUILD_ROOT%{_mingw32_bindir}/$b.dll
    install -m 644 -p $d/$b.lib $RPM_BUILD_ROOT%{_mingw32_libdir}/lib$b.dll.a
    %{_mingw32_ranlib} $RPM_BUILD_ROOT%{_mingw32_libdir}/lib$b.dll.a
  else
    install -m 644 -p $d/$b.lib $RPM_BUILD_ROOT%{_mingw32_libdir}/$b.a
    %{_mingw32_ranlib} $RPM_BUILD_ROOT%{_mingw32_libdir}/$b.a
  fi
done

# install include files
find boost -type d | while read a; do
  mkdir -p $RPM_BUILD_ROOT%{_mingw32_includedir}/$a
  find $a -mindepth 1 -maxdepth 1 -type f \
    | xargs -r install -m 644 -p -t $RPM_BUILD_ROOT%{_mingw32_includedir}/$a
done

# remove scripts used to generate include files
find $RPM_BUILD_ROOT%{_mingw32_includedir}/ \( -name '*.pl' -o -name '*.sh' \) -exec rm {} \;


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc LICENSE_1_0.txt
%{_mingw32_includedir}/boost
%{_mingw32_bindir}/boost_date_time.dll
%{_mingw32_libdir}/libboost_date_time.dll.a
%{_mingw32_bindir}/boost_date_time-mt.dll
%{_mingw32_libdir}/libboost_date_time-mt.dll.a
%{_mingw32_bindir}/boost_filesystem.dll
%{_mingw32_libdir}/libboost_filesystem.dll.a
%{_mingw32_bindir}/boost_filesystem-mt.dll
%{_mingw32_libdir}/libboost_filesystem-mt.dll.a
%{_mingw32_bindir}/boost_graph.dll
%{_mingw32_libdir}/libboost_graph.dll.a
%{_mingw32_bindir}/boost_graph-mt.dll
%{_mingw32_libdir}/libboost_graph-mt.dll.a
%{_mingw32_bindir}/boost_iostreams.dll
%{_mingw32_libdir}/libboost_iostreams.dll.a
%{_mingw32_bindir}/boost_iostreams-mt.dll
%{_mingw32_libdir}/libboost_iostreams-mt.dll.a
%{_mingw32_bindir}/boost_math_c99.dll
%{_mingw32_libdir}/libboost_math_c99.dll.a
%{_mingw32_bindir}/boost_math_c99f.dll
%{_mingw32_libdir}/libboost_math_c99f.dll.a
%{_mingw32_bindir}/boost_math_c99f-mt.dll
%{_mingw32_libdir}/libboost_math_c99f-mt.dll.a
%{_mingw32_bindir}/boost_math_c99l.dll
%{_mingw32_libdir}/libboost_math_c99l.dll.a
%{_mingw32_bindir}/boost_math_c99l-mt.dll
%{_mingw32_libdir}/libboost_math_c99l-mt.dll.a
%{_mingw32_bindir}/boost_math_c99-mt.dll
%{_mingw32_libdir}/libboost_math_c99-mt.dll.a
%{_mingw32_bindir}/boost_math_tr1.dll
%{_mingw32_libdir}/libboost_math_tr1.dll.a
%{_mingw32_bindir}/boost_math_tr1f.dll
%{_mingw32_libdir}/libboost_math_tr1f.dll.a
%{_mingw32_bindir}/boost_math_tr1f-mt.dll
%{_mingw32_libdir}/libboost_math_tr1f-mt.dll.a
%{_mingw32_bindir}/boost_math_tr1l.dll
%{_mingw32_libdir}/libboost_math_tr1l.dll.a
%{_mingw32_bindir}/boost_math_tr1l-mt.dll
%{_mingw32_libdir}/libboost_math_tr1l-mt.dll.a
%{_mingw32_bindir}/boost_math_tr1-mt.dll
%{_mingw32_libdir}/libboost_math_tr1-mt.dll.a
%{_mingw32_bindir}/boost_prg_exec_monitor.dll
%{_mingw32_libdir}/libboost_prg_exec_monitor.dll.a
%{_mingw32_bindir}/boost_prg_exec_monitor-mt.dll
%{_mingw32_libdir}/libboost_prg_exec_monitor-mt.dll.a
%{_mingw32_bindir}/boost_program_options.dll
%{_mingw32_libdir}/libboost_program_options.dll.a
%{_mingw32_bindir}/boost_program_options-mt.dll
%{_mingw32_libdir}/libboost_program_options-mt.dll.a
%{_mingw32_bindir}/boost_regex.dll
%{_mingw32_libdir}/libboost_regex.dll.a
%{_mingw32_bindir}/boost_regex-mt.dll
%{_mingw32_libdir}/libboost_regex-mt.dll.a
%{_mingw32_bindir}/boost_serialization.dll
%{_mingw32_libdir}/libboost_serialization.dll.a
%{_mingw32_bindir}/boost_serialization-mt.dll
%{_mingw32_libdir}/libboost_serialization-mt.dll.a
%{_mingw32_bindir}/boost_signals.dll
%{_mingw32_libdir}/libboost_signals.dll.a
%{_mingw32_bindir}/boost_signals-mt.dll
%{_mingw32_libdir}/libboost_signals-mt.dll.a
%{_mingw32_bindir}/boost_system.dll
%{_mingw32_libdir}/libboost_system.dll.a
%{_mingw32_bindir}/boost_system-mt.dll
%{_mingw32_libdir}/libboost_system-mt.dll.a
%{_mingw32_bindir}/boost_thread-mt.dll
%{_mingw32_libdir}/libboost_thread-mt.dll.a
%{_mingw32_bindir}/boost_unit_test_framework.dll
%{_mingw32_libdir}/libboost_unit_test_framework.dll.a
%{_mingw32_bindir}/boost_unit_test_framework-mt.dll
%{_mingw32_libdir}/libboost_unit_test_framework-mt.dll.a
%{_mingw32_bindir}/boost_wave.dll
%{_mingw32_libdir}/libboost_wave.dll.a
%{_mingw32_bindir}/boost_wave-mt.dll
%{_mingw32_libdir}/libboost_wave-mt.dll.a
%{_mingw32_bindir}/boost_wserialization.dll
%{_mingw32_libdir}/libboost_wserialization.dll.a
%{_mingw32_bindir}/boost_wserialization-mt.dll
%{_mingw32_libdir}/libboost_wserialization-mt.dll.a


%files static
%defattr(-,root,root,-)
%{_mingw32_libdir}/libboost_date_time.a
%{_mingw32_libdir}/libboost_date_time-mt.a
%{_mingw32_libdir}/libboost_filesystem.a
%{_mingw32_libdir}/libboost_filesystem-mt.a
%{_mingw32_libdir}/libboost_graph.a
%{_mingw32_libdir}/libboost_graph-mt.a
%{_mingw32_libdir}/libboost_iostreams.a
%{_mingw32_libdir}/libboost_iostreams-mt.a
%{_mingw32_libdir}/libboost_math_c99f.a
%{_mingw32_libdir}/libboost_math_c99f-mt.a
%{_mingw32_libdir}/libboost_math_c99.a
%{_mingw32_libdir}/libboost_math_c99l.a
%{_mingw32_libdir}/libboost_math_c99l-mt.a
%{_mingw32_libdir}/libboost_math_c99-mt.a
%{_mingw32_libdir}/libboost_math_tr1f.a
%{_mingw32_libdir}/libboost_math_tr1f-mt.a
%{_mingw32_libdir}/libboost_math_tr1.a
%{_mingw32_libdir}/libboost_math_tr1l.a
%{_mingw32_libdir}/libboost_math_tr1l-mt.a
%{_mingw32_libdir}/libboost_math_tr1-mt.a
%{_mingw32_libdir}/libboost_prg_exec_monitor.a
%{_mingw32_libdir}/libboost_prg_exec_monitor-mt.a
%{_mingw32_libdir}/libboost_program_options.a
%{_mingw32_libdir}/libboost_program_options-mt.a
%{_mingw32_libdir}/libboost_regex.a
%{_mingw32_libdir}/libboost_regex-mt.a
%{_mingw32_libdir}/libboost_serialization.a
%{_mingw32_libdir}/libboost_serialization-mt.a
%{_mingw32_libdir}/libboost_signals.a
%{_mingw32_libdir}/libboost_signals-mt.a
%{_mingw32_libdir}/libboost_system.a
%{_mingw32_libdir}/libboost_system-mt.a
%{_mingw32_libdir}/libboost_test_exec_monitor.a
%{_mingw32_libdir}/libboost_test_exec_monitor-mt.a
%{_mingw32_libdir}/libboost_thread-mt.a
%{_mingw32_libdir}/libboost_unit_test_framework.a
%{_mingw32_libdir}/libboost_unit_test_framework-mt.a
%{_mingw32_libdir}/libboost_wave.a
%{_mingw32_libdir}/libboost_wave-mt.a
%{_mingw32_libdir}/libboost_wserialization.a
%{_mingw32_libdir}/libboost_wserialization-mt.a


%changelog
* Mon Jun 22 2009 Thomas Sailer <t.sailer@alumni.ethz.ch> - 1.39.0-2
- add debuginfo packages

* Thu Jun 18 2009 Thomas Sailer <t.sailer@alumni.ethz.ch> - 1.39.0-1
- update to 1.39.0

* Thu May 28 2009 Thomas Sailer <t.sailer@alumni.ethz.ch> - 1.37.0-4
- use boost buildsystem to build DLLs

* Wed May 27 2009 Thomas Sailer <t.sailer@alumni.ethz.ch> - 1.37.0-3
- use mingw32 ar

* Tue May 26 2009 Thomas Sailer <t.sailer@alumni.ethz.ch> - 1.37.0-2
- fix %%defattr
- fix description of static package
- add comments that detail the failures linking the test framework / exec monitor DLL's

* Sun May 24 2009 Thomas Sailer <t.sailer@alumni.ethz.ch> - 1.37.0-1
- update to 1.37.0
- actually tell the build system about the target os
- build also boost DLL's that depend on other boost DLL's

* Fri Jan 23 2009 Richard W.M. Jones <rjones@redhat.com> - 1.34.1-4
- Include license file.

* Fri Jan 23 2009 Richard W.M. Jones <rjones@redhat.com> - 1.34.1-3
- Use _smp_mflags.

* Sat Oct 24 2008 Richard W.M. Jones <rjones@redhat.com> - 1.34.1-2
- Initial RPM release.
