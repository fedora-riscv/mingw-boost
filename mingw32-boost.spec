%global __strip %{_mingw32_strip}
%global __objdump %{_mingw32_objdump}
%global _use_internal_dependency_generator 0
%global __find_requires %{_mingw32_findrequires}
%global __find_provides %{_mingw32_findprovides}
%define __debug_install_post %{_mingw32_debug_install_post}

%global name1 boost

Name:           mingw32-%{name1}
Version:        1.48.0
%define version_enc 1_48_0
%global dllboostver 1_48
%global dllgccver gcc47
Release:        5%{?dist}
Summary:        MinGW Windows port of Boost C++ Libraries

License:        Boost
Group:          Development/Libraries
# The CMake build framework (set of CMakeLists.txt and module.cmake files) is
# added on top of the official Boost release (http://www.boost.org), thanks to
# a dedicated patch. That CMake framework (and patch) is hosted and maintained
# on GitHub, for now in the following Git repository:
#   https://github.com/pocb/boost.git
# A clone also exists on Gitorious, where CMake-related work was formely done:
#   http://gitorious.org/boost/cmake
# Upstream work is synchronised thanks to the Ryppl's hosted Git clone:
#   https://github.com/ryppl/boost-svn/tree/trunk
%define toplev_dirname %{name1}_%{version_enc}
URL:            http://www.boost.org
Source0:        http://downloads.sourceforge.net/%{name}/%{toplev_dirname}.tar.bz2

# CMake-related files (CMakeLists.txt and module.cmake files).
# That patch also contains Web-related documentation for the Trac Wiki
# devoted to "old" Boost-CMake (up-to-date until Boost-1.41.0).
Patch0:         boost-1.48.0-cmakeify-full.patch
Patch1:         boost-cmake-soname.patch

# The patch may break c++03, and there is therefore no plan yet to include
# it upstream: https://svn.boost.org/trac/boost/ticket/4999
Patch2:         boost-1.48.0-signals-erase.patch

# https://svn.boost.org/trac/boost/ticket/5731
Patch3:         boost-1.48.0-exceptions.patch

# https://svn.boost.org/trac/boost/ticket/6150
Patch4:         boost-1.48.0-fix-non-utf8-files.patch

# Add a manual page for the sole executable, namely bjam, based on the
# on-line documentation:
# http://www.boost.org/boost-build2/doc/html/bbv2/overview.html
Patch5:         boost-1.48.0-add-bjam-man-page.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=757385
# https://svn.boost.org/trac/boost/ticket/6182
Patch6:         boost-1.48.0-lexical_cast-incomplete.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=756005
# https://svn.boost.org/trac/boost/ticket/6131
Patch7:         boost-1.48.0-foreach.patch

# https://svn.boost.org/trac/boost/ticket/6165
Patch8:         boost-1.48.0-gcc47-pthreads.patch

# https://svn.boost.org/trac/boost/ticket/6165
Patch9:         boost-1.48.0-gcc47-winthreads.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=781751
Patch10:        boost-1.48.0-mingw32.patch

# Make sure the boost dll's are installed in %{mingw32_bindir}
# instead of %{mingw32_libdir}
Patch11:        boost-install-dlls-to-bindir.patch

# Fix compilation when using c++11 mode
# https://bugzilla.redhat.com/show_bug.cgi?id=799332
# https://svn.boost.org/trac/boost/changeset/75396
Patch12:        changeset_75396.diff

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
sed 's/_FEDORA_SONAME/%{sonamever}/' %{PATCH1} | %{__patch} -p0 --fuzz=0

# Fixes
%patch2 -p1
%patch3 -p0
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p2
%patch8 -p0
%patch9 -p0 -b .gcc47wt
%patch10 -p0 -b .mingw32
%patch11 -p0 -b .bindir
%patch12 -p1 -b .c++11


%build
# Support for building tests.
%global boost_testflags -DBUILD_TESTS="NONE"

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
find $RPM_BUILD_ROOT -name '*.cmake' -exec %{__rm} -f {} \;

# Remove scripts used to generate include files
find $RPM_BUILD_ROOT%{_mingw32_includedir}/ \( -name '*.pl' -o -name '*.sh' \) -exec %{__rm} -f {} \;


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc LICENSE_1_0.txt
%{_mingw32_includedir}/boost
%{_mingw32_bindir}/boost_chrono-%{dllgccver}-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_chrono-%{dllgccver}-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_chrono-%{dllgccver}-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_chrono-%{dllgccver}-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_chrono-%{dllgccver}-mt-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_chrono-%{dllgccver}-mt-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_chrono-%{dllgccver}-mt-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_chrono-%{dllgccver}-mt-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_date_time-%{dllgccver}-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_date_time-%{dllgccver}-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_date_time-%{dllgccver}-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_date_time-%{dllgccver}-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_date_time-%{dllgccver}-mt-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_date_time-%{dllgccver}-mt-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_date_time-%{dllgccver}-mt-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_date_time-%{dllgccver}-mt-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_filesystem-%{dllgccver}-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_filesystem-%{dllgccver}-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_filesystem-%{dllgccver}-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_filesystem-%{dllgccver}-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_filesystem-%{dllgccver}-mt-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_filesystem-%{dllgccver}-mt-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_filesystem-%{dllgccver}-mt-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_filesystem-%{dllgccver}-mt-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_graph-%{dllgccver}-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_graph-%{dllgccver}-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_graph-%{dllgccver}-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_graph-%{dllgccver}-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_graph-%{dllgccver}-mt-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_graph-%{dllgccver}-mt-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_graph-%{dllgccver}-mt-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_graph-%{dllgccver}-mt-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_iostreams-%{dllgccver}-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_iostreams-%{dllgccver}-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_iostreams-%{dllgccver}-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_iostreams-%{dllgccver}-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_iostreams-%{dllgccver}-mt-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_iostreams-%{dllgccver}-mt-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_iostreams-%{dllgccver}-mt-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_iostreams-%{dllgccver}-mt-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_locale-%{dllgccver}-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_locale-%{dllgccver}-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_locale-%{dllgccver}-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_locale-%{dllgccver}-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_locale-%{dllgccver}-mt-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_locale-%{dllgccver}-mt-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_locale-%{dllgccver}-mt-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_locale-%{dllgccver}-mt-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_math_c99-%{dllgccver}-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_math_c99-%{dllgccver}-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_math_c99-%{dllgccver}-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_math_c99-%{dllgccver}-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_math_c99-%{dllgccver}-mt-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_math_c99-%{dllgccver}-mt-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_math_c99-%{dllgccver}-mt-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_math_c99-%{dllgccver}-mt-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_math_c99f-%{dllgccver}-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_math_c99f-%{dllgccver}-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_math_c99f-%{dllgccver}-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_math_c99f-%{dllgccver}-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_math_c99f-%{dllgccver}-mt-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_math_c99f-%{dllgccver}-mt-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_math_c99f-%{dllgccver}-mt-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_math_c99f-%{dllgccver}-mt-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_math_c99l-%{dllgccver}-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_math_c99l-%{dllgccver}-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_math_c99l-%{dllgccver}-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_math_c99l-%{dllgccver}-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_math_c99l-%{dllgccver}-mt-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_math_c99l-%{dllgccver}-mt-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_math_c99l-%{dllgccver}-mt-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_math_c99l-%{dllgccver}-mt-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_math_tr1-%{dllgccver}-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_math_tr1-%{dllgccver}-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_math_tr1-%{dllgccver}-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_math_tr1-%{dllgccver}-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_math_tr1-%{dllgccver}-mt-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_math_tr1-%{dllgccver}-mt-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_math_tr1-%{dllgccver}-mt-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_math_tr1-%{dllgccver}-mt-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_math_tr1f-%{dllgccver}-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_math_tr1f-%{dllgccver}-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_math_tr1f-%{dllgccver}-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_math_tr1f-%{dllgccver}-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_math_tr1f-%{dllgccver}-mt-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_math_tr1f-%{dllgccver}-mt-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_math_tr1f-%{dllgccver}-mt-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_math_tr1f-%{dllgccver}-mt-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_math_tr1l-%{dllgccver}-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_math_tr1l-%{dllgccver}-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_math_tr1l-%{dllgccver}-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_math_tr1l-%{dllgccver}-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_math_tr1l-%{dllgccver}-mt-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_math_tr1l-%{dllgccver}-mt-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_math_tr1l-%{dllgccver}-mt-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_math_tr1l-%{dllgccver}-mt-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_prg_exec_monitor-%{dllgccver}-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_prg_exec_monitor-%{dllgccver}-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_prg_exec_monitor-%{dllgccver}-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_prg_exec_monitor-%{dllgccver}-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_prg_exec_monitor-%{dllgccver}-mt-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_prg_exec_monitor-%{dllgccver}-mt-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_prg_exec_monitor-%{dllgccver}-mt-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_prg_exec_monitor-%{dllgccver}-mt-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_program_options-%{dllgccver}-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_program_options-%{dllgccver}-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_program_options-%{dllgccver}-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_program_options-%{dllgccver}-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_program_options-%{dllgccver}-mt-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_program_options-%{dllgccver}-mt-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_program_options-%{dllgccver}-mt-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_program_options-%{dllgccver}-mt-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_random-%{dllgccver}-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_random-%{dllgccver}-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_random-%{dllgccver}-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_random-%{dllgccver}-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_random-%{dllgccver}-mt-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_random-%{dllgccver}-mt-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_random-%{dllgccver}-mt-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_random-%{dllgccver}-mt-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_regex-%{dllgccver}-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_regex-%{dllgccver}-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_regex-%{dllgccver}-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_regex-%{dllgccver}-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_regex-%{dllgccver}-mt-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_regex-%{dllgccver}-mt-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_regex-%{dllgccver}-mt-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_regex-%{dllgccver}-mt-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_serialization-%{dllgccver}-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_serialization-%{dllgccver}-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_serialization-%{dllgccver}-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_serialization-%{dllgccver}-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_serialization-%{dllgccver}-mt-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_serialization-%{dllgccver}-mt-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_serialization-%{dllgccver}-mt-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_serialization-%{dllgccver}-mt-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_signals-%{dllgccver}-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_signals-%{dllgccver}-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_signals-%{dllgccver}-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_signals-%{dllgccver}-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_signals-%{dllgccver}-mt-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_signals-%{dllgccver}-mt-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_signals-%{dllgccver}-mt-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_signals-%{dllgccver}-mt-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_system-%{dllgccver}-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_system-%{dllgccver}-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_system-%{dllgccver}-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_system-%{dllgccver}-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_system-%{dllgccver}-mt-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_system-%{dllgccver}-mt-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_system-%{dllgccver}-mt-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_system-%{dllgccver}-mt-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_thread-%{dllgccver}-mt-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_thread-%{dllgccver}-mt-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_thread-%{dllgccver}-mt-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_thread-%{dllgccver}-mt-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_timer-%{dllgccver}-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_timer-%{dllgccver}-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_timer-%{dllgccver}-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_timer-%{dllgccver}-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_timer-%{dllgccver}-mt-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_timer-%{dllgccver}-mt-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_timer-%{dllgccver}-mt-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_timer-%{dllgccver}-mt-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_unit_test_framework-%{dllgccver}-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_unit_test_framework-%{dllgccver}-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_unit_test_framework-%{dllgccver}-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_unit_test_framework-%{dllgccver}-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_unit_test_framework-%{dllgccver}-mt-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_unit_test_framework-%{dllgccver}-mt-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_unit_test_framework-%{dllgccver}-mt-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_unit_test_framework-%{dllgccver}-mt-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_wave-%{dllgccver}-mt-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_wave-%{dllgccver}-mt-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_wave-%{dllgccver}-mt-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_wave-%{dllgccver}-mt-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_wserialization-%{dllgccver}-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_wserialization-%{dllgccver}-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_wserialization-%{dllgccver}-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_wserialization-%{dllgccver}-d-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_wserialization-%{dllgccver}-mt-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_wserialization-%{dllgccver}-mt-%{dllboostver}.dll.a
%{_mingw32_bindir}/boost_wserialization-%{dllgccver}-mt-d-%{dllboostver}.dll
%{_mingw32_libdir}/libboost_wserialization-%{dllgccver}-mt-d-%{dllboostver}.dll.a

%files static
%defattr(-,root,root,-)
%{_mingw32_libdir}/libboost_chrono-%{dllgccver}-%{dllboostver}.a
%{_mingw32_libdir}/libboost_chrono-%{dllgccver}-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_chrono-%{dllgccver}-mt-%{dllboostver}.a
%{_mingw32_libdir}/libboost_chrono-%{dllgccver}-mt-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_date_time-%{dllgccver}-%{dllboostver}.a
%{_mingw32_libdir}/libboost_date_time-%{dllgccver}-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_date_time-%{dllgccver}-mt-%{dllboostver}.a
%{_mingw32_libdir}/libboost_date_time-%{dllgccver}-mt-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_filesystem-%{dllgccver}-%{dllboostver}.a
%{_mingw32_libdir}/libboost_filesystem-%{dllgccver}-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_filesystem-%{dllgccver}-mt-%{dllboostver}.a
%{_mingw32_libdir}/libboost_filesystem-%{dllgccver}-mt-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_iostreams-%{dllgccver}-%{dllboostver}.a
%{_mingw32_libdir}/libboost_iostreams-%{dllgccver}-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_iostreams-%{dllgccver}-mt-%{dllboostver}.a
%{_mingw32_libdir}/libboost_iostreams-%{dllgccver}-mt-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_locale-%{dllgccver}-%{dllboostver}.a
%{_mingw32_libdir}/libboost_locale-%{dllgccver}-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_locale-%{dllgccver}-mt-%{dllboostver}.a
%{_mingw32_libdir}/libboost_locale-%{dllgccver}-mt-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_math_c99-%{dllgccver}-%{dllboostver}.a
%{_mingw32_libdir}/libboost_math_c99-%{dllgccver}-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_math_c99-%{dllgccver}-mt-%{dllboostver}.a
%{_mingw32_libdir}/libboost_math_c99-%{dllgccver}-mt-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_math_c99f-%{dllgccver}-%{dllboostver}.a
%{_mingw32_libdir}/libboost_math_c99f-%{dllgccver}-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_math_c99f-%{dllgccver}-mt-%{dllboostver}.a
%{_mingw32_libdir}/libboost_math_c99f-%{dllgccver}-mt-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_math_c99l-%{dllgccver}-%{dllboostver}.a
%{_mingw32_libdir}/libboost_math_c99l-%{dllgccver}-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_math_c99l-%{dllgccver}-mt-%{dllboostver}.a
%{_mingw32_libdir}/libboost_math_c99l-%{dllgccver}-mt-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_math_tr1-%{dllgccver}-%{dllboostver}.a
%{_mingw32_libdir}/libboost_math_tr1-%{dllgccver}-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_math_tr1-%{dllgccver}-mt-%{dllboostver}.a
%{_mingw32_libdir}/libboost_math_tr1-%{dllgccver}-mt-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_math_tr1f-%{dllgccver}-%{dllboostver}.a
%{_mingw32_libdir}/libboost_math_tr1f-%{dllgccver}-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_math_tr1f-%{dllgccver}-mt-%{dllboostver}.a
%{_mingw32_libdir}/libboost_math_tr1f-%{dllgccver}-mt-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_math_tr1l-%{dllgccver}-%{dllboostver}.a
%{_mingw32_libdir}/libboost_math_tr1l-%{dllgccver}-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_math_tr1l-%{dllgccver}-mt-%{dllboostver}.a
%{_mingw32_libdir}/libboost_math_tr1l-%{dllgccver}-mt-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_prg_exec_monitor-%{dllgccver}-%{dllboostver}.a
%{_mingw32_libdir}/libboost_prg_exec_monitor-%{dllgccver}-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_prg_exec_monitor-%{dllgccver}-mt-%{dllboostver}.a
%{_mingw32_libdir}/libboost_prg_exec_monitor-%{dllgccver}-mt-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_program_options-%{dllgccver}-%{dllboostver}.a
%{_mingw32_libdir}/libboost_program_options-%{dllgccver}-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_program_options-%{dllgccver}-mt-%{dllboostver}.a
%{_mingw32_libdir}/libboost_program_options-%{dllgccver}-mt-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_random-%{dllgccver}-%{dllboostver}.a
%{_mingw32_libdir}/libboost_random-%{dllgccver}-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_random-%{dllgccver}-mt-%{dllboostver}.a
%{_mingw32_libdir}/libboost_random-%{dllgccver}-mt-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_regex-%{dllgccver}-%{dllboostver}.a
%{_mingw32_libdir}/libboost_regex-%{dllgccver}-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_regex-%{dllgccver}-mt-%{dllboostver}.a
%{_mingw32_libdir}/libboost_regex-%{dllgccver}-mt-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_serialization-%{dllgccver}-%{dllboostver}.a
%{_mingw32_libdir}/libboost_serialization-%{dllgccver}-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_serialization-%{dllgccver}-mt-%{dllboostver}.a
%{_mingw32_libdir}/libboost_serialization-%{dllgccver}-mt-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_signals-%{dllgccver}-%{dllboostver}.a
%{_mingw32_libdir}/libboost_signals-%{dllgccver}-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_signals-%{dllgccver}-mt-%{dllboostver}.a
%{_mingw32_libdir}/libboost_signals-%{dllgccver}-mt-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_system-%{dllgccver}-%{dllboostver}.a
%{_mingw32_libdir}/libboost_system-%{dllgccver}-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_system-%{dllgccver}-mt-%{dllboostver}.a
%{_mingw32_libdir}/libboost_system-%{dllgccver}-mt-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_test_exec_monitor-%{dllgccver}-%{dllboostver}.a
%{_mingw32_libdir}/libboost_test_exec_monitor-%{dllgccver}-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_test_exec_monitor-%{dllgccver}-mt-%{dllboostver}.a
%{_mingw32_libdir}/libboost_test_exec_monitor-%{dllgccver}-mt-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_timer-%{dllgccver}-%{dllboostver}.a
%{_mingw32_libdir}/libboost_timer-%{dllgccver}-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_timer-%{dllgccver}-mt-%{dllboostver}.a
%{_mingw32_libdir}/libboost_timer-%{dllgccver}-mt-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_thread-%{dllgccver}-mt-%{dllboostver}.a
%{_mingw32_libdir}/libboost_thread-%{dllgccver}-mt-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_unit_test_framework-%{dllgccver}-%{dllboostver}.a
%{_mingw32_libdir}/libboost_unit_test_framework-%{dllgccver}-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_unit_test_framework-%{dllgccver}-mt-%{dllboostver}.a
%{_mingw32_libdir}/libboost_unit_test_framework-%{dllgccver}-mt-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_wave-%{dllgccver}-mt-%{dllboostver}.a
%{_mingw32_libdir}/libboost_wave-%{dllgccver}-mt-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_wserialization-%{dllgccver}-%{dllboostver}.a
%{_mingw32_libdir}/libboost_wserialization-%{dllgccver}-d-%{dllboostver}.a
%{_mingw32_libdir}/libboost_wserialization-%{dllgccver}-mt-%{dllboostver}.a
%{_mingw32_libdir}/libboost_wserialization-%{dllgccver}-mt-d-%{dllboostver}.a


%changelog
* Sat Mar  3 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 1.48.0-5
- Fix compilation failure when including interlocked.hpp in c++11 mode (RHBZ #799332)

* Tue Feb 28 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 1.48.0-4
- Rebuild against the mingw-w64 toolchain

* Fri Feb 10 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 1.48.0-3
- Don't provide the cmake files any more as they are broken and cmake
  itself already provides its own boost detection mechanism.
  Should fix detection of boost by mingw32-qpid-cpp. RHBZ #597020, RHBZ #789399
- Added patch which makes boost install dll's to %%{_mingw32_bindir}
  instead of %%{_mingw32_libdir}. The hack in the %%install section
  to manually move the dll's is dropped now

* Sat Jan 14 2012 Thomas Sailer <t.sailer@alumni.ethz.ch> - 1.48.0-2
- update cmakeify patch

* Sat Jan 14 2012 Thomas Sailer <t.sailer@alumni.ethz.ch> - 1.48.0-1
- update to 1.48.0

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.47.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri Sep  2 2011 Thomas Sailer <t.sailer@alumni.ethz.ch> - 1.47.0-1
- update to 1.47.0

* Tue Jun 28 2011 Kalev Lember <kalev@smartlink.ee> - 1.46.1-2
- Rebuilt for mingw32-gcc 4.6

* Tue Jun 21 2011 Thomas Sailer <t.sailer@alumni.ethz.ch> - 1.46.1-1
- update to 1.46.1

* Sat May 21 2011 Kalev Lember <kalev@smartlink.ee> - 1.46.0-0.3.beta1
- Own the _mingw32_datadir/cmake/boost/ directory

* Fri Apr 22 2011 Kalev Lember <kalev@smartlink.ee> - 1.46.0-0.2.beta1
- Rebuilt for pseudo-reloc version mismatch (#698827)

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
