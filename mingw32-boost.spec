%global __strip %{_mingw32_strip}
%global __objdump %{_mingw32_objdump}
%global _use_internal_dependency_generator 0
%global __find_requires %{_mingw32_findrequires}
%global __find_provides %{_mingw32_findprovides}
%define __debug_install_post %{_mingw32_debug_install_post}

%global name1 boost

Name:           mingw32-%{name1}
Version:        1.46.0
%global version_enc 1_46_0_beta1
Release:        0.1.beta1%{?dist}
Summary:        MinGW Windows port of Boost C++ Libraries

License:        Boost
Group:          Development/Libraries
# The CMake build framework (set of CMakeLists.txt and module.cmake files) is
# added on top of the official Boost release (http://www.boost.org), thanks to
# a dedicated patch. That CMake framework (and patch) is hosted and maintained
# on GitHub, for now in the following Git repository:
#   https://github.com/denisarnaud/boost-cmake
# A clone also exists on Gitorious, where CMake-related work was formely done:
#   http://gitorious.org/~denisarnaud/boost/denisarnauds-cmake
# Upstream work is synchronised thanks to the Ryppl's hosted Git clone:
#   https://github.com/ryppl/boost-svn/tree/trunk
%define toplev_dirname %{name1}_%{version_enc}
URL:            http://www.boost.org
Source: http://downloads.sourceforge.net/%{name}/%{toplev_dirname}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Patch0:         boost-1.46.0-cmakeify.patch
Patch1:         boost-1.46.0-cmakeify-more.patch
Patch2:         boost-cmake-soname.patch

# https://svn.boost.org/trac/boost/ticket/4999
Patch3:         boost-1.46.0-signals-erase.patch

# https://svn.boost.org/trac/boost/ticket/5119
Patch4:         boost-1.46.0-unordered-cctor.patch

BuildArch:      noarch

BuildRequires:  cmake
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
%setup -q -n %{toplev_dirname}

# CMake framework (CMakeLists.txt, *.cmake and documentation files)
%patch0 -p1
%patch1 -p1
sed 's/_FEDORA_SONAME/%{sonamever}/' %{PATCH2} | %{__patch} -p0 --fuzz=0

# fixes
%patch3 -p1
%patch4 -p2

%build
# Support for building tests.
%global boost_testflags -DBUILD_TESTS="NONE"


-O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions --param=ssp-buffer-size=4 -mms-bitfields

( echo ============================= build serial ==================
  mkdir serial
  cd serial
  %_mingw32_cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo %{boost_testflags} \
                  -DENABLE_SINGLE_THREADED=YES -DINSTALL_VERSIONED=OFF \
                  -DWITH_MPI=OFF \
                  -DCMAKE_CXX_FLAGS="%{_mingw32_cflags} -DBOOST_IOSTREAMS_USE_DEPRECATED" \
                  ..
  make VERBOSE=1 %{?_smp_mflags}
)

%install
%{__rm} -rf $RPM_BUILD_ROOT

echo ============================= install serial ==================
DESTDIR=$RPM_BUILD_ROOT make -C serial VERBOSE=1 install
# Kill any debug library versions that may show up un-invited.
%{__rm} -f $RPM_BUILD_ROOT/%{_libdir}/*-d.*
# Remove cmake configuration files used to build the Boost libraries
find $RPM_BUILD_ROOT/%{_mingw32_libdir} -name '*.cmake' -exec %{__rm} -f {} \;

# Remove scripts used to generate include files
find $RPM_BUILD_ROOT%{_mingw32_includedir}/ \( -name '*.pl' -o -name '*.sh' \) -exec %{__rm} -f {} \;

# Move DLL's to bindir
%{__install} -d $RPM_BUILD_ROOT $RPM_BUILD_ROOT%{_mingw32_bindir}
mv $RPM_BUILD_ROOT%{_mingw32_libdir}/boost*.dll $RPM_BUILD_ROOT%{_mingw32_bindir}

%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc LICENSE_1_0.txt
%{_mingw32_includedir}/boost
%{_mingw32_bindir}/boost_date_time-gcc45-1_46.dll
%{_mingw32_libdir}/libboost_date_time-gcc45-1_46.dll.a
%{_mingw32_bindir}/boost_date_time-gcc45-d-1_46.dll
%{_mingw32_libdir}/libboost_date_time-gcc45-d-1_46.dll.a
%{_mingw32_bindir}/boost_date_time-gcc45-mt-1_46.dll
%{_mingw32_libdir}/libboost_date_time-gcc45-mt-1_46.dll.a
%{_mingw32_bindir}/boost_date_time-gcc45-mt-d-1_46.dll
%{_mingw32_libdir}/libboost_date_time-gcc45-mt-d-1_46.dll.a
%{_mingw32_bindir}/boost_filesystem-gcc45-1_46.dll
%{_mingw32_libdir}/libboost_filesystem-gcc45-1_46.dll.a
%{_mingw32_bindir}/boost_filesystem-gcc45-d-1_46.dll
%{_mingw32_libdir}/libboost_filesystem-gcc45-d-1_46.dll.a
%{_mingw32_bindir}/boost_filesystem-gcc45-mt-1_46.dll
%{_mingw32_libdir}/libboost_filesystem-gcc45-mt-1_46.dll.a
%{_mingw32_bindir}/boost_filesystem-gcc45-mt-d-1_46.dll
%{_mingw32_libdir}/libboost_filesystem-gcc45-mt-d-1_46.dll.a
%{_mingw32_bindir}/boost_graph-gcc45-1_46.dll
%{_mingw32_libdir}/libboost_graph-gcc45-1_46.dll.a
%{_mingw32_bindir}/boost_graph-gcc45-d-1_46.dll
%{_mingw32_libdir}/libboost_graph-gcc45-d-1_46.dll.a
%{_mingw32_bindir}/boost_graph-gcc45-mt-1_46.dll
%{_mingw32_libdir}/libboost_graph-gcc45-mt-1_46.dll.a
%{_mingw32_bindir}/boost_graph-gcc45-mt-d-1_46.dll
%{_mingw32_libdir}/libboost_graph-gcc45-mt-d-1_46.dll.a
%{_mingw32_bindir}/boost_iostreams-gcc45-1_46.dll
%{_mingw32_libdir}/libboost_iostreams-gcc45-1_46.dll.a
%{_mingw32_bindir}/boost_iostreams-gcc45-d-1_46.dll
%{_mingw32_libdir}/libboost_iostreams-gcc45-d-1_46.dll.a
%{_mingw32_bindir}/boost_iostreams-gcc45-mt-1_46.dll
%{_mingw32_libdir}/libboost_iostreams-gcc45-mt-1_46.dll.a
%{_mingw32_bindir}/boost_iostreams-gcc45-mt-d-1_46.dll
%{_mingw32_libdir}/libboost_iostreams-gcc45-mt-d-1_46.dll.a
%{_mingw32_bindir}/boost_prg_exec_monitor-gcc45-1_46.dll
%{_mingw32_libdir}/libboost_prg_exec_monitor-gcc45-1_46.dll.a
%{_mingw32_bindir}/boost_prg_exec_monitor-gcc45-d-1_46.dll
%{_mingw32_libdir}/libboost_prg_exec_monitor-gcc45-d-1_46.dll.a
%{_mingw32_bindir}/boost_prg_exec_monitor-gcc45-mt-1_46.dll
%{_mingw32_libdir}/libboost_prg_exec_monitor-gcc45-mt-1_46.dll.a
%{_mingw32_bindir}/boost_prg_exec_monitor-gcc45-mt-d-1_46.dll
%{_mingw32_libdir}/libboost_prg_exec_monitor-gcc45-mt-d-1_46.dll.a
%{_mingw32_bindir}/boost_program_options-gcc45-1_46.dll
%{_mingw32_libdir}/libboost_program_options-gcc45-1_46.dll.a
%{_mingw32_bindir}/boost_program_options-gcc45-d-1_46.dll
%{_mingw32_libdir}/libboost_program_options-gcc45-d-1_46.dll.a
%{_mingw32_bindir}/boost_program_options-gcc45-mt-1_46.dll
%{_mingw32_libdir}/libboost_program_options-gcc45-mt-1_46.dll.a
%{_mingw32_bindir}/boost_program_options-gcc45-mt-d-1_46.dll
%{_mingw32_libdir}/libboost_program_options-gcc45-mt-d-1_46.dll.a
%{_mingw32_bindir}/boost_regex-gcc45-1_46.dll
%{_mingw32_libdir}/libboost_regex-gcc45-1_46.dll.a
%{_mingw32_bindir}/boost_regex-gcc45-d-1_46.dll
%{_mingw32_libdir}/libboost_regex-gcc45-d-1_46.dll.a
%{_mingw32_bindir}/boost_regex-gcc45-mt-1_46.dll
%{_mingw32_libdir}/libboost_regex-gcc45-mt-1_46.dll.a
%{_mingw32_bindir}/boost_regex-gcc45-mt-d-1_46.dll
%{_mingw32_libdir}/libboost_regex-gcc45-mt-d-1_46.dll.a
%{_mingw32_bindir}/boost_serialization-gcc45-1_46.dll
%{_mingw32_libdir}/libboost_serialization-gcc45-1_46.dll.a
%{_mingw32_bindir}/boost_serialization-gcc45-d-1_46.dll
%{_mingw32_libdir}/libboost_serialization-gcc45-d-1_46.dll.a
%{_mingw32_bindir}/boost_serialization-gcc45-mt-1_46.dll
%{_mingw32_libdir}/libboost_serialization-gcc45-mt-1_46.dll.a
%{_mingw32_bindir}/boost_serialization-gcc45-mt-d-1_46.dll
%{_mingw32_libdir}/libboost_serialization-gcc45-mt-d-1_46.dll.a
%{_mingw32_bindir}/boost_signals-gcc45-1_46.dll
%{_mingw32_libdir}/libboost_signals-gcc45-1_46.dll.a
%{_mingw32_bindir}/boost_signals-gcc45-d-1_46.dll
%{_mingw32_libdir}/libboost_signals-gcc45-d-1_46.dll.a
%{_mingw32_bindir}/boost_signals-gcc45-mt-1_46.dll
%{_mingw32_libdir}/libboost_signals-gcc45-mt-1_46.dll.a
%{_mingw32_bindir}/boost_signals-gcc45-mt-d-1_46.dll
%{_mingw32_libdir}/libboost_signals-gcc45-mt-d-1_46.dll.a
%{_mingw32_bindir}/boost_system-gcc45-1_46.dll
%{_mingw32_libdir}/libboost_system-gcc45-1_46.dll.a
%{_mingw32_bindir}/boost_system-gcc45-d-1_46.dll
%{_mingw32_libdir}/libboost_system-gcc45-d-1_46.dll.a
%{_mingw32_bindir}/boost_system-gcc45-mt-1_46.dll
%{_mingw32_libdir}/libboost_system-gcc45-mt-1_46.dll.a
%{_mingw32_bindir}/boost_system-gcc45-mt-d-1_46.dll
%{_mingw32_libdir}/libboost_system-gcc45-mt-d-1_46.dll.a
%{_mingw32_bindir}/boost_thread-gcc45-mt-1_46.dll
%{_mingw32_libdir}/libboost_thread-gcc45-mt-1_46.dll.a
%{_mingw32_bindir}/boost_thread-gcc45-mt-d-1_46.dll
%{_mingw32_libdir}/libboost_thread-gcc45-mt-d-1_46.dll.a
%{_mingw32_bindir}/boost_unit_test_framework-gcc45-1_46.dll
%{_mingw32_libdir}/libboost_unit_test_framework-gcc45-1_46.dll.a
%{_mingw32_bindir}/boost_unit_test_framework-gcc45-d-1_46.dll
%{_mingw32_libdir}/libboost_unit_test_framework-gcc45-d-1_46.dll.a
%{_mingw32_bindir}/boost_unit_test_framework-gcc45-mt-1_46.dll
%{_mingw32_libdir}/libboost_unit_test_framework-gcc45-mt-1_46.dll.a
%{_mingw32_bindir}/boost_unit_test_framework-gcc45-mt-d-1_46.dll
%{_mingw32_libdir}/libboost_unit_test_framework-gcc45-mt-d-1_46.dll.a
%{_mingw32_bindir}/boost_wave-gcc45-mt-1_46.dll
%{_mingw32_libdir}/libboost_wave-gcc45-mt-1_46.dll.a
%{_mingw32_bindir}/boost_wave-gcc45-mt-d-1_46.dll
%{_mingw32_libdir}/libboost_wave-gcc45-mt-d-1_46.dll.a
%{_mingw32_bindir}/boost_wserialization-gcc45-1_46.dll
%{_mingw32_libdir}/libboost_wserialization-gcc45-1_46.dll.a
%{_mingw32_bindir}/boost_wserialization-gcc45-d-1_46.dll
%{_mingw32_libdir}/libboost_wserialization-gcc45-d-1_46.dll.a
%{_mingw32_bindir}/boost_wserialization-gcc45-mt-1_46.dll
%{_mingw32_libdir}/libboost_wserialization-gcc45-mt-1_46.dll.a
%{_mingw32_bindir}/boost_wserialization-gcc45-mt-d-1_46.dll
%{_mingw32_libdir}/libboost_wserialization-gcc45-mt-d-1_46.dll.a
%{_mingw32_datadir}/%{name1}-%{version}
%{_mingw32_datadir}/cmake/%{name1}/BoostConfig*.cmake

%files static
%defattr(-,root,root,-)
%{_mingw32_libdir}/libboost_date_time-gcc45-1_46.a
%{_mingw32_libdir}/libboost_date_time-gcc45-d-1_46.a
%{_mingw32_libdir}/libboost_date_time-gcc45-mt-1_46.a
%{_mingw32_libdir}/libboost_date_time-gcc45-mt-d-1_46.a
%{_mingw32_libdir}/libboost_filesystem-gcc45-1_46.a
%{_mingw32_libdir}/libboost_filesystem-gcc45-d-1_46.a
%{_mingw32_libdir}/libboost_filesystem-gcc45-mt-1_46.a
%{_mingw32_libdir}/libboost_filesystem-gcc45-mt-d-1_46.a
%{_mingw32_libdir}/libboost_iostreams-gcc45-1_46.a
%{_mingw32_libdir}/libboost_iostreams-gcc45-d-1_46.a
%{_mingw32_libdir}/libboost_iostreams-gcc45-mt-1_46.a
%{_mingw32_libdir}/libboost_iostreams-gcc45-mt-d-1_46.a
%{_mingw32_libdir}/libboost_prg_exec_monitor-gcc45-1_46.a
%{_mingw32_libdir}/libboost_prg_exec_monitor-gcc45-d-1_46.a
%{_mingw32_libdir}/libboost_prg_exec_monitor-gcc45-mt-1_46.a
%{_mingw32_libdir}/libboost_prg_exec_monitor-gcc45-mt-d-1_46.a
%{_mingw32_libdir}/libboost_program_options-gcc45-1_46.a
%{_mingw32_libdir}/libboost_program_options-gcc45-d-1_46.a
%{_mingw32_libdir}/libboost_program_options-gcc45-mt-1_46.a
%{_mingw32_libdir}/libboost_program_options-gcc45-mt-d-1_46.a
%{_mingw32_libdir}/libboost_regex-gcc45-1_46.a
%{_mingw32_libdir}/libboost_regex-gcc45-d-1_46.a
%{_mingw32_libdir}/libboost_regex-gcc45-mt-1_46.a
%{_mingw32_libdir}/libboost_regex-gcc45-mt-d-1_46.a
%{_mingw32_libdir}/libboost_serialization-gcc45-1_46.a
%{_mingw32_libdir}/libboost_serialization-gcc45-d-1_46.a
%{_mingw32_libdir}/libboost_serialization-gcc45-mt-1_46.a
%{_mingw32_libdir}/libboost_serialization-gcc45-mt-d-1_46.a
%{_mingw32_libdir}/libboost_signals-gcc45-1_46.a
%{_mingw32_libdir}/libboost_signals-gcc45-d-1_46.a
%{_mingw32_libdir}/libboost_signals-gcc45-mt-1_46.a
%{_mingw32_libdir}/libboost_signals-gcc45-mt-d-1_46.a
%{_mingw32_libdir}/libboost_system-gcc45-1_46.a
%{_mingw32_libdir}/libboost_system-gcc45-d-1_46.a
%{_mingw32_libdir}/libboost_system-gcc45-mt-1_46.a
%{_mingw32_libdir}/libboost_system-gcc45-mt-d-1_46.a
%{_mingw32_libdir}/libboost_test_exec_monitor-gcc45-1_46.a
%{_mingw32_libdir}/libboost_test_exec_monitor-gcc45-d-1_46.a
%{_mingw32_libdir}/libboost_test_exec_monitor-gcc45-mt-1_46.a
%{_mingw32_libdir}/libboost_test_exec_monitor-gcc45-mt-d-1_46.a
%{_mingw32_libdir}/libboost_thread-gcc45-mt-1_46.a
%{_mingw32_libdir}/libboost_thread-gcc45-mt-d-1_46.a
%{_mingw32_libdir}/libboost_unit_test_framework-gcc45-1_46.a
%{_mingw32_libdir}/libboost_unit_test_framework-gcc45-d-1_46.a
%{_mingw32_libdir}/libboost_unit_test_framework-gcc45-mt-1_46.a
%{_mingw32_libdir}/libboost_unit_test_framework-gcc45-mt-d-1_46.a
%{_mingw32_libdir}/libboost_wave-gcc45-mt-1_46.a
%{_mingw32_libdir}/libboost_wave-gcc45-mt-d-1_46.a
%{_mingw32_libdir}/libboost_wserialization-gcc45-1_46.a
%{_mingw32_libdir}/libboost_wserialization-gcc45-d-1_46.a
%{_mingw32_libdir}/libboost_wserialization-gcc45-mt-1_46.a
%{_mingw32_libdir}/libboost_wserialization-gcc45-mt-d-1_46.a


%changelog
* Wed Feb  9 2011 Thomas Sailer <t.sailer@alumni.ethz.ch> - 1.46.0-0.1.beta1
- update to 1.46.0-beta1

* Thu Nov 18 2010 Thomas Sailer <t.sailer@alumni.ethz.ch> - 1.44.0-1
- update to 1.44.0

* Thu Jun  3 2010 Thomas Sailer <t.sailer@alumni.ethz.ch> - 1.41.0-2
- update to gcc 4.5

* Wed Jan 20 2010 Thomas Sailer <t.sailer@alumni.ethz.ch> - 1.41.0-1
- update to 1.41.0

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.39.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

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
