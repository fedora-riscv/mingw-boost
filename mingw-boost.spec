%?mingw_package_header

%global name1 boost
Name:           mingw-%{name1}
Version:        1.63.0
%global version_enc 1_63_0
Release:        1%{?dist}
Summary:        MinGW Windows port of Boost C++ Libraries

%global toplev_dirname %{name1}_%{version_enc}

License:        Boost
Group:          Development/Libraries
URL:            http://www.boost.org
Source0:        http://downloads.sourceforge.net/%{name1}/%{toplev_dirname}.tar.bz2

# https://svn.boost.org/trac/boost/ticket/6150
Patch4: boost-1.50.0-fix-non-utf8-files.patch

# Add a manual page for bjam, based on the on-line documentation:
# http://www.boost.org/boost-build2/doc/html/bbv2/overview.html
Patch5: boost-1.48.0-add-bjam-man-page.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=828856
# https://bugzilla.redhat.com/show_bug.cgi?id=828857
# https://svn.boost.org/trac/boost/ticket/6701
Patch15: boost-1.58.0-pool.patch

# https://svn.boost.org/trac/boost/ticket/5637
Patch25: boost-1.57.0-mpl-print.patch

# https://svn.boost.org/trac/boost/ticket/9038
Patch51: boost-1.58.0-pool-test_linking.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1102667
Patch61: boost-1.57.0-python-libpython_dep.patch
Patch62: boost-1.57.0-python-abi_letters.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1190039
Patch65: boost-1.57.0-build-optflags.patch

# Prevent gcc.jam from setting -m32 or -m64.
Patch68: boost-1.58.0-address-model.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1318383
Patch82: boost-1.60.0-no-rpath.patch

# https://github.com/boostorg/build/issues/163
Patch83: boost-1.63.0-dual-python-build.patch

# https://svn.boost.org/trac/boost/ticket/7262
Patch1000:      boost-mingw.patch

# Fix FTBFS on recent mingw-w64 and also use intrinsics based
# versions of the Interlocked symbols which are better optimized
Patch1001:      boost-include-intrin-h-on-mingw-w64.patch

# https://github.com/boostorg/serialization/pull/42
Patch1002:      boost-1.63.0-codecvtwchar.patch

BuildArch:      noarch

BuildRequires:  file
BuildRequires:  mingw32-filesystem >= 95
BuildRequires:  mingw32-gcc
BuildRequires:  mingw32-gcc-c++
BuildRequires:  mingw32-binutils
BuildRequires:  mingw32-bzip2
BuildRequires:  mingw32-zlib
BuildRequires:  mingw32-expat
BuildRequires:  mingw32-pthreads

BuildRequires:  mingw64-filesystem >= 95
BuildRequires:  mingw64-gcc
BuildRequires:  mingw64-gcc-c++
BuildRequires:  mingw64-binutils
BuildRequires:  mingw64-bzip2
BuildRequires:  mingw64-zlib
BuildRequires:  mingw64-expat
BuildRequires:  mingw64-pthreads

BuildRequires:  perl
# These are required by the native package:
#BuildRequires:  mingw32-python
#BuildRequires:  mingw32-libicu
#BuildRequires:  mingw64-python
#BuildRequires:  mingw64-libicu


%description
Boost provides free peer-reviewed portable C++ source libraries.  The
emphasis is on libraries which work well with the C++ Standard
Library, in the hopes of establishing "existing practice" for
extensions and providing reference implementations so that the Boost
libraries are suitable for eventual standardization. (Some of the
libraries have already been proposed for inclusion in the C++
Standards Committee's upcoming C++ Standard Library Technical Report.)

# Win32
%package -n mingw32-boost
Summary:         MinGW Windows Boost C++ library for the win32 target

%description -n mingw32-boost
Boost provides free peer-reviewed portable C++ source libraries.  The
emphasis is on libraries which work well with the C++ Standard
Library, in the hopes of establishing "existing practice" for
extensions and providing reference implementations so that the Boost
libraries are suitable for eventual standardization. (Some of the
libraries have already been proposed for inclusion in the C++
Standards Committee's upcoming C++ Standard Library Technical Report.)

%package -n mingw32-boost-static
Summary:        Static version of the MinGW Windows Boost C++ library
Requires:       mingw32-boost = %{version}-%{release}

%description -n mingw32-boost-static
Static version of the MinGW Windows Boost C++ library.

# Win64
%package -n mingw64-boost
Summary:         MinGW Windows Boost C++ library for the win64 target

%description -n mingw64-boost
Boost provides free peer-reviewed portable C++ source libraries.  The
emphasis is on libraries which work well with the C++ Standard
Library, in the hopes of establishing "existing practice" for
extensions and providing reference implementations so that the Boost
libraries are suitable for eventual standardization. (Some of the
libraries have already been proposed for inclusion in the C++
Standards Committee's upcoming C++ Standard Library Technical Report.)

%package -n mingw64-boost-static
Summary:        Static version of the MinGW Windows Boost C++ library
Requires:       mingw64-boost = %{version}-%{release}

%description -n mingw64-boost-static
Static version of the MinGW Windows Boost C++ library.


%?mingw_debug_package


%prep
%setup -qc
mv %{toplev_dirname} win32

pushd win32
# Fixes
%patch4 -p1
%patch5 -p1
%patch15 -p0
%patch25 -p1
%patch51 -p1
%patch61 -p1
%patch62 -p1
%patch65 -p1
%patch68 -p1
%patch82 -p0
%patch83 -p1
%patch1000 -p0 -b .mingw
%patch1001 -p0 -b .interlocked
%patch1002 -p1 -b .codecvtwchar
popd

cp -r win32 win64

%build
%if 0%{?mingw_build_win32} == 1
pushd win32
cat >> ./tools/build/src/user-config.jam << EOF
using gcc : : i686-w64-mingw32-g++ : <rc>/usr/bin/i686-w64-mingw32-windres ;
EOF

./bootstrap.sh --with-toolset=gcc --with-icu=%{mingw32_prefix}

echo ============================= build serial ==================
./b2 -d+2 -q %{?_smp_mflags} --layout=tagged \
	--without-mpi --without-graph_parallel --without-python --build-dir=serial \
	variant=release threading=single,multi debug-symbols=on pch=off \
	link=shared,static target-os=windows stage
popd
%endif
%if 0%{?mingw_build_win64} == 1
pushd win64
cat >> ./tools/build/src/user-config.jam << EOF
using gcc : : x86_64-w64-mingw32-g++ : <rc>/usr/bin/x86_64-w64-mingw32-windres ;
EOF

./bootstrap.sh --with-toolset=gcc --with-icu=%{mingw64_prefix}

echo ============================= build serial ==================
./b2 -d+2 -q %{?_smp_mflags} --layout=tagged \
	--without-mpi --without-graph_parallel --without-python --build-dir=serial \
	variant=release threading=single,multi debug-symbols=on pch=off \
	link=shared,static target-os=windows stage
popd
%endif

%install
%if 0%{?mingw_build_win32} == 1
pushd win32
echo ============================= install serial ==================
./b2 -d+2 -q %{?_smp_mflags} --layout=tagged \
	--without-mpi --without-graph_parallel --without-python --build-dir=serial \
	--prefix=$RPM_BUILD_ROOT%{mingw32_prefix} \
	--libdir=$RPM_BUILD_ROOT%{mingw32_libdir} \
	variant=release threading=single,multi debug-symbols=on pch=off \
	link=shared,static target-os=windows install
popd
mkdir -p $RPM_BUILD_ROOT%{mingw32_bindir}
mv $RPM_BUILD_ROOT%{mingw32_libdir}/*.dll $RPM_BUILD_ROOT%{mingw32_bindir}
%endif
%if 0%{?mingw_build_win64} == 1
pushd win64
echo ============================= install serial ==================
./b2 -d+2 -q %{?_smp_mflags} --layout=tagged \
	--without-mpi --without-graph_parallel --without-python --build-dir=serial \
	--prefix=$RPM_BUILD_ROOT%{mingw64_prefix} \
	--libdir=$RPM_BUILD_ROOT%{mingw64_libdir} \
	variant=release threading=single,multi debug-symbols=on pch=off \
	link=shared,static target-os=windows install
popd
mkdir -p $RPM_BUILD_ROOT%{mingw64_bindir}
mv $RPM_BUILD_ROOT%{mingw64_libdir}/*.dll $RPM_BUILD_ROOT%{mingw64_bindir}
%endif

# Win32
%files -n mingw32-boost
%doc win32/LICENSE_1_0.txt
%{mingw32_includedir}/boost
%{mingw32_bindir}/libboost_atomic-mt.dll
%{mingw32_bindir}/libboost_chrono.dll
%{mingw32_bindir}/libboost_chrono-mt.dll
%{mingw32_bindir}/libboost_container.dll
%{mingw32_bindir}/libboost_container-mt.dll
%{mingw32_bindir}/libboost_context-mt.dll
%{mingw32_bindir}/libboost_coroutine.dll
%{mingw32_bindir}/libboost_coroutine-mt.dll
%{mingw32_bindir}/libboost_date_time.dll
%{mingw32_bindir}/libboost_date_time-mt.dll
%{mingw32_bindir}/libboost_filesystem.dll
%{mingw32_bindir}/libboost_filesystem-mt.dll
%{mingw32_bindir}/libboost_graph.dll
%{mingw32_bindir}/libboost_graph-mt.dll
%{mingw32_bindir}/libboost_iostreams.dll
%{mingw32_bindir}/libboost_iostreams-mt.dll
%{mingw32_bindir}/libboost_locale-mt.dll
%{mingw32_bindir}/libboost_log.dll
%{mingw32_bindir}/libboost_log-mt.dll
%{mingw32_bindir}/libboost_log_setup.dll
%{mingw32_bindir}/libboost_log_setup-mt.dll
%{mingw32_bindir}/libboost_math_c99.dll
%{mingw32_bindir}/libboost_math_c99f.dll
%{mingw32_bindir}/libboost_math_c99f-mt.dll
%{mingw32_bindir}/libboost_math_c99l.dll
%{mingw32_bindir}/libboost_math_c99l-mt.dll
%{mingw32_bindir}/libboost_math_c99-mt.dll
%{mingw32_bindir}/libboost_math_tr1.dll
%{mingw32_bindir}/libboost_math_tr1f.dll
%{mingw32_bindir}/libboost_math_tr1f-mt.dll
%{mingw32_bindir}/libboost_math_tr1l.dll
%{mingw32_bindir}/libboost_math_tr1l-mt.dll
%{mingw32_bindir}/libboost_math_tr1-mt.dll
%{mingw32_bindir}/libboost_prg_exec_monitor.dll
%{mingw32_bindir}/libboost_prg_exec_monitor-mt.dll
%{mingw32_bindir}/libboost_program_options.dll
%{mingw32_bindir}/libboost_program_options-mt.dll
%{mingw32_bindir}/libboost_random.dll
%{mingw32_bindir}/libboost_random-mt.dll
%{mingw32_bindir}/libboost_regex.dll
%{mingw32_bindir}/libboost_regex-mt.dll
%{mingw32_bindir}/libboost_serialization.dll
%{mingw32_bindir}/libboost_serialization-mt.dll
%{mingw32_bindir}/libboost_signals.dll
%{mingw32_bindir}/libboost_signals-mt.dll
%{mingw32_bindir}/libboost_system.dll
%{mingw32_bindir}/libboost_system-mt.dll
%{mingw32_bindir}/libboost_thread-mt.dll
%{mingw32_bindir}/libboost_timer.dll
%{mingw32_bindir}/libboost_timer-mt.dll
%{mingw32_bindir}/libboost_type_erasure.dll
%{mingw32_bindir}/libboost_type_erasure-mt.dll
%{mingw32_bindir}/libboost_unit_test_framework.dll
%{mingw32_bindir}/libboost_unit_test_framework-mt.dll
%{mingw32_bindir}/libboost_wave-mt.dll
%{mingw32_bindir}/libboost_wserialization.dll
%{mingw32_bindir}/libboost_wserialization-mt.dll
%{mingw32_libdir}/libboost_atomic-mt.dll.a
%{mingw32_libdir}/libboost_chrono.dll.a
%{mingw32_libdir}/libboost_chrono-mt.dll.a
%{mingw32_libdir}/libboost_container.dll.a
%{mingw32_libdir}/libboost_container-mt.dll.a
%{mingw32_libdir}/libboost_context-mt.dll.a
%{mingw32_libdir}/libboost_coroutine.dll.a
%{mingw32_libdir}/libboost_coroutine-mt.dll.a
%{mingw32_libdir}/libboost_date_time.dll.a
%{mingw32_libdir}/libboost_date_time-mt.dll.a
%{mingw32_libdir}/libboost_filesystem.dll.a
%{mingw32_libdir}/libboost_filesystem-mt.dll.a
%{mingw32_libdir}/libboost_graph.dll.a
%{mingw32_libdir}/libboost_graph-mt.dll.a
%{mingw32_libdir}/libboost_iostreams.dll.a
%{mingw32_libdir}/libboost_iostreams-mt.dll.a
%{mingw32_libdir}/libboost_locale-mt.dll.a
%{mingw32_libdir}/libboost_log.dll.a
%{mingw32_libdir}/libboost_log-mt.dll.a
%{mingw32_libdir}/libboost_log_setup.dll.a
%{mingw32_libdir}/libboost_log_setup-mt.dll.a
%{mingw32_libdir}/libboost_math_c99.dll.a
%{mingw32_libdir}/libboost_math_c99f.dll.a
%{mingw32_libdir}/libboost_math_c99f-mt.dll.a
%{mingw32_libdir}/libboost_math_c99l.dll.a
%{mingw32_libdir}/libboost_math_c99l-mt.dll.a
%{mingw32_libdir}/libboost_math_c99-mt.dll.a
%{mingw32_libdir}/libboost_math_tr1.dll.a
%{mingw32_libdir}/libboost_math_tr1f.dll.a
%{mingw32_libdir}/libboost_math_tr1f-mt.dll.a
%{mingw32_libdir}/libboost_math_tr1l.dll.a
%{mingw32_libdir}/libboost_math_tr1l-mt.dll.a
%{mingw32_libdir}/libboost_math_tr1-mt.dll.a
%{mingw32_libdir}/libboost_prg_exec_monitor.dll.a
%{mingw32_libdir}/libboost_prg_exec_monitor-mt.dll.a
%{mingw32_libdir}/libboost_program_options.dll.a
%{mingw32_libdir}/libboost_program_options-mt.dll.a
%{mingw32_libdir}/libboost_random.dll.a
%{mingw32_libdir}/libboost_random-mt.dll.a
%{mingw32_libdir}/libboost_regex.dll.a
%{mingw32_libdir}/libboost_regex-mt.dll.a
%{mingw32_libdir}/libboost_serialization.dll.a
%{mingw32_libdir}/libboost_serialization-mt.dll.a
%{mingw32_libdir}/libboost_signals.dll.a
%{mingw32_libdir}/libboost_signals-mt.dll.a
%{mingw32_libdir}/libboost_system.dll.a
%{mingw32_libdir}/libboost_system-mt.dll.a
%{mingw32_libdir}/libboost_thread-mt.dll.a
%{mingw32_libdir}/libboost_timer.dll.a
%{mingw32_libdir}/libboost_timer-mt.dll.a
%{mingw32_libdir}/libboost_type_erasure.dll.a
%{mingw32_libdir}/libboost_type_erasure-mt.dll.a
%{mingw32_libdir}/libboost_unit_test_framework.dll.a
%{mingw32_libdir}/libboost_unit_test_framework-mt.dll.a
%{mingw32_libdir}/libboost_wave-mt.dll.a
%{mingw32_libdir}/libboost_wserialization.dll.a
%{mingw32_libdir}/libboost_wserialization-mt.dll.a

%files -n mingw32-boost-static
%{mingw32_libdir}/libboost_atomic-mt.a
%{mingw32_libdir}/libboost_chrono.a
%{mingw32_libdir}/libboost_chrono-mt.a
%{mingw32_libdir}/libboost_container.a
%{mingw32_libdir}/libboost_container-mt.a
%{mingw32_libdir}/libboost_context-mt.a
%{mingw32_libdir}/libboost_coroutine.a
%{mingw32_libdir}/libboost_coroutine-mt.a
%{mingw32_libdir}/libboost_date_time.a
%{mingw32_libdir}/libboost_date_time-mt.a
%{mingw32_libdir}/libboost_filesystem.a
%{mingw32_libdir}/libboost_filesystem-mt.a
%{mingw32_libdir}/libboost_graph.a
%{mingw32_libdir}/libboost_graph-mt.a
%{mingw32_libdir}/libboost_iostreams.a
%{mingw32_libdir}/libboost_iostreams-mt.a
%{mingw32_libdir}/libboost_locale-mt.a
%{mingw32_libdir}/libboost_log.a
%{mingw32_libdir}/libboost_log-mt.a
%{mingw32_libdir}/libboost_log_setup.a
%{mingw32_libdir}/libboost_log_setup-mt.a
%{mingw32_libdir}/libboost_math_c99.a
%{mingw32_libdir}/libboost_math_c99f.a
%{mingw32_libdir}/libboost_math_c99f-mt.a
%{mingw32_libdir}/libboost_math_c99l.a
%{mingw32_libdir}/libboost_math_c99l-mt.a
%{mingw32_libdir}/libboost_math_c99-mt.a
%{mingw32_libdir}/libboost_math_tr1.a
%{mingw32_libdir}/libboost_math_tr1f.a
%{mingw32_libdir}/libboost_math_tr1f-mt.a
%{mingw32_libdir}/libboost_math_tr1l.a
%{mingw32_libdir}/libboost_math_tr1l-mt.a
%{mingw32_libdir}/libboost_math_tr1-mt.a
%{mingw32_libdir}/libboost_prg_exec_monitor.a
%{mingw32_libdir}/libboost_prg_exec_monitor-mt.a
%{mingw32_libdir}/libboost_program_options.a
%{mingw32_libdir}/libboost_program_options-mt.a
%{mingw32_libdir}/libboost_random.a
%{mingw32_libdir}/libboost_random-mt.a
%{mingw32_libdir}/libboost_regex.a
%{mingw32_libdir}/libboost_regex-mt.a
%{mingw32_libdir}/libboost_serialization.a
%{mingw32_libdir}/libboost_serialization-mt.a
%{mingw32_libdir}/libboost_signals.a
%{mingw32_libdir}/libboost_signals-mt.a
%{mingw32_libdir}/libboost_system.a
%{mingw32_libdir}/libboost_system-mt.a
%{mingw32_libdir}/libboost_thread-mt.a
%{mingw32_libdir}/libboost_timer.a
%{mingw32_libdir}/libboost_timer-mt.a
%{mingw32_libdir}/libboost_type_erasure.a
%{mingw32_libdir}/libboost_type_erasure-mt.a
%{mingw32_libdir}/libboost_unit_test_framework.a
%{mingw32_libdir}/libboost_unit_test_framework-mt.a
%{mingw32_libdir}/libboost_wave-mt.a
%{mingw32_libdir}/libboost_wserialization.a
%{mingw32_libdir}/libboost_wserialization-mt.a
# static only libraries
%{mingw32_libdir}/libboost_exception-mt.a
%{mingw32_libdir}/libboost_exception.a
%{mingw32_libdir}/libboost_test_exec_monitor-mt.a
%{mingw32_libdir}/libboost_test_exec_monitor.a

# Win64
%files -n mingw64-boost
%doc win64/LICENSE_1_0.txt
%{mingw64_includedir}/boost
%{mingw64_bindir}/libboost_atomic-mt.dll
%{mingw64_bindir}/libboost_chrono.dll
%{mingw64_bindir}/libboost_chrono-mt.dll
%{mingw64_bindir}/libboost_container.dll
%{mingw64_bindir}/libboost_container-mt.dll
%{mingw64_bindir}/libboost_context-mt.dll
%{mingw64_bindir}/libboost_coroutine.dll
%{mingw64_bindir}/libboost_coroutine-mt.dll
%{mingw64_bindir}/libboost_date_time.dll
%{mingw64_bindir}/libboost_date_time-mt.dll
%{mingw64_bindir}/libboost_filesystem.dll
%{mingw64_bindir}/libboost_filesystem-mt.dll
%{mingw64_bindir}/libboost_graph.dll
%{mingw64_bindir}/libboost_graph-mt.dll
%{mingw64_bindir}/libboost_iostreams.dll
%{mingw64_bindir}/libboost_iostreams-mt.dll
%{mingw64_bindir}/libboost_locale-mt.dll
%{mingw64_bindir}/libboost_log.dll
%{mingw64_bindir}/libboost_log-mt.dll
%{mingw64_bindir}/libboost_log_setup.dll
%{mingw64_bindir}/libboost_log_setup-mt.dll
%{mingw64_bindir}/libboost_math_c99.dll
%{mingw64_bindir}/libboost_math_c99f.dll
%{mingw64_bindir}/libboost_math_c99f-mt.dll
%{mingw64_bindir}/libboost_math_c99l.dll
%{mingw64_bindir}/libboost_math_c99l-mt.dll
%{mingw64_bindir}/libboost_math_c99-mt.dll
%{mingw64_bindir}/libboost_math_tr1.dll
%{mingw64_bindir}/libboost_math_tr1f.dll
%{mingw64_bindir}/libboost_math_tr1f-mt.dll
%{mingw64_bindir}/libboost_math_tr1l.dll
%{mingw64_bindir}/libboost_math_tr1l-mt.dll
%{mingw64_bindir}/libboost_math_tr1-mt.dll
%{mingw64_bindir}/libboost_prg_exec_monitor.dll
%{mingw64_bindir}/libboost_prg_exec_monitor-mt.dll
%{mingw64_bindir}/libboost_program_options.dll
%{mingw64_bindir}/libboost_program_options-mt.dll
%{mingw64_bindir}/libboost_random.dll
%{mingw64_bindir}/libboost_random-mt.dll
%{mingw64_bindir}/libboost_regex.dll
%{mingw64_bindir}/libboost_regex-mt.dll
%{mingw64_bindir}/libboost_serialization.dll
%{mingw64_bindir}/libboost_serialization-mt.dll
%{mingw64_bindir}/libboost_signals.dll
%{mingw64_bindir}/libboost_signals-mt.dll
%{mingw64_bindir}/libboost_system.dll
%{mingw64_bindir}/libboost_system-mt.dll
%{mingw64_bindir}/libboost_thread-mt.dll
%{mingw64_bindir}/libboost_timer.dll
%{mingw64_bindir}/libboost_timer-mt.dll
%{mingw64_bindir}/libboost_type_erasure.dll
%{mingw64_bindir}/libboost_type_erasure-mt.dll
%{mingw64_bindir}/libboost_unit_test_framework.dll
%{mingw64_bindir}/libboost_unit_test_framework-mt.dll
%{mingw64_bindir}/libboost_wave-mt.dll
%{mingw64_bindir}/libboost_wserialization.dll
%{mingw64_bindir}/libboost_wserialization-mt.dll
%{mingw64_libdir}/libboost_atomic-mt.dll.a
%{mingw64_libdir}/libboost_chrono.dll.a
%{mingw64_libdir}/libboost_chrono-mt.dll.a
%{mingw64_libdir}/libboost_container.dll.a
%{mingw64_libdir}/libboost_container-mt.dll.a
%{mingw64_libdir}/libboost_context-mt.dll.a
%{mingw64_libdir}/libboost_coroutine.dll.a
%{mingw64_libdir}/libboost_coroutine-mt.dll.a
%{mingw64_libdir}/libboost_date_time.dll.a
%{mingw64_libdir}/libboost_date_time-mt.dll.a
%{mingw64_libdir}/libboost_filesystem.dll.a
%{mingw64_libdir}/libboost_filesystem-mt.dll.a
%{mingw64_libdir}/libboost_graph.dll.a
%{mingw64_libdir}/libboost_graph-mt.dll.a
%{mingw64_libdir}/libboost_iostreams.dll.a
%{mingw64_libdir}/libboost_iostreams-mt.dll.a
%{mingw64_libdir}/libboost_locale-mt.dll.a
%{mingw64_libdir}/libboost_log.dll.a
%{mingw64_libdir}/libboost_log-mt.dll.a
%{mingw64_libdir}/libboost_log_setup.dll.a
%{mingw64_libdir}/libboost_log_setup-mt.dll.a
%{mingw64_libdir}/libboost_math_c99.dll.a
%{mingw64_libdir}/libboost_math_c99f.dll.a
%{mingw64_libdir}/libboost_math_c99f-mt.dll.a
%{mingw64_libdir}/libboost_math_c99l.dll.a
%{mingw64_libdir}/libboost_math_c99l-mt.dll.a
%{mingw64_libdir}/libboost_math_c99-mt.dll.a
%{mingw64_libdir}/libboost_math_tr1.dll.a
%{mingw64_libdir}/libboost_math_tr1f.dll.a
%{mingw64_libdir}/libboost_math_tr1f-mt.dll.a
%{mingw64_libdir}/libboost_math_tr1l.dll.a
%{mingw64_libdir}/libboost_math_tr1l-mt.dll.a
%{mingw64_libdir}/libboost_math_tr1-mt.dll.a
%{mingw64_libdir}/libboost_prg_exec_monitor.dll.a
%{mingw64_libdir}/libboost_prg_exec_monitor-mt.dll.a
%{mingw64_libdir}/libboost_program_options.dll.a
%{mingw64_libdir}/libboost_program_options-mt.dll.a
%{mingw64_libdir}/libboost_random.dll.a
%{mingw64_libdir}/libboost_random-mt.dll.a
%{mingw64_libdir}/libboost_regex.dll.a
%{mingw64_libdir}/libboost_regex-mt.dll.a
%{mingw64_libdir}/libboost_serialization.dll.a
%{mingw64_libdir}/libboost_serialization-mt.dll.a
%{mingw64_libdir}/libboost_signals.dll.a
%{mingw64_libdir}/libboost_signals-mt.dll.a
%{mingw64_libdir}/libboost_system.dll.a
%{mingw64_libdir}/libboost_system-mt.dll.a
%{mingw64_libdir}/libboost_thread-mt.dll.a
%{mingw64_libdir}/libboost_timer.dll.a
%{mingw64_libdir}/libboost_timer-mt.dll.a
%{mingw64_libdir}/libboost_type_erasure.dll.a
%{mingw64_libdir}/libboost_type_erasure-mt.dll.a
%{mingw64_libdir}/libboost_unit_test_framework.dll.a
%{mingw64_libdir}/libboost_unit_test_framework-mt.dll.a
%{mingw64_libdir}/libboost_wave-mt.dll.a
%{mingw64_libdir}/libboost_wserialization.dll.a
%{mingw64_libdir}/libboost_wserialization-mt.dll.a

%files -n mingw64-boost-static
%{mingw64_libdir}/libboost_atomic-mt.a
%{mingw64_libdir}/libboost_chrono.a
%{mingw64_libdir}/libboost_chrono-mt.a
%{mingw64_libdir}/libboost_container.a
%{mingw64_libdir}/libboost_container-mt.a
%{mingw64_libdir}/libboost_context-mt.a
%{mingw64_libdir}/libboost_coroutine.a
%{mingw64_libdir}/libboost_coroutine-mt.a
%{mingw64_libdir}/libboost_date_time.a
%{mingw64_libdir}/libboost_date_time-mt.a
%{mingw64_libdir}/libboost_filesystem.a
%{mingw64_libdir}/libboost_filesystem-mt.a
%{mingw64_libdir}/libboost_graph.a
%{mingw64_libdir}/libboost_graph-mt.a
%{mingw64_libdir}/libboost_iostreams.a
%{mingw64_libdir}/libboost_iostreams-mt.a
%{mingw64_libdir}/libboost_locale-mt.a
%{mingw64_libdir}/libboost_log.a
%{mingw64_libdir}/libboost_log-mt.a
%{mingw64_libdir}/libboost_log_setup.a
%{mingw64_libdir}/libboost_log_setup-mt.a
%{mingw64_libdir}/libboost_math_c99.a
%{mingw64_libdir}/libboost_math_c99f.a
%{mingw64_libdir}/libboost_math_c99f-mt.a
%{mingw64_libdir}/libboost_math_c99l.a
%{mingw64_libdir}/libboost_math_c99l-mt.a
%{mingw64_libdir}/libboost_math_c99-mt.a
%{mingw64_libdir}/libboost_math_tr1.a
%{mingw64_libdir}/libboost_math_tr1f.a
%{mingw64_libdir}/libboost_math_tr1f-mt.a
%{mingw64_libdir}/libboost_math_tr1l.a
%{mingw64_libdir}/libboost_math_tr1l-mt.a
%{mingw64_libdir}/libboost_math_tr1-mt.a
%{mingw64_libdir}/libboost_prg_exec_monitor.a
%{mingw64_libdir}/libboost_prg_exec_monitor-mt.a
%{mingw64_libdir}/libboost_program_options.a
%{mingw64_libdir}/libboost_program_options-mt.a
%{mingw64_libdir}/libboost_random.a
%{mingw64_libdir}/libboost_random-mt.a
%{mingw64_libdir}/libboost_regex.a
%{mingw64_libdir}/libboost_regex-mt.a
%{mingw64_libdir}/libboost_serialization.a
%{mingw64_libdir}/libboost_serialization-mt.a
%{mingw64_libdir}/libboost_signals.a
%{mingw64_libdir}/libboost_signals-mt.a
%{mingw64_libdir}/libboost_system.a
%{mingw64_libdir}/libboost_system-mt.a
%{mingw64_libdir}/libboost_thread-mt.a
%{mingw64_libdir}/libboost_timer.a
%{mingw64_libdir}/libboost_timer-mt.a
%{mingw64_libdir}/libboost_type_erasure.a
%{mingw64_libdir}/libboost_type_erasure-mt.a
%{mingw64_libdir}/libboost_unit_test_framework.a
%{mingw64_libdir}/libboost_unit_test_framework-mt.a
%{mingw64_libdir}/libboost_wave-mt.a
%{mingw64_libdir}/libboost_wserialization.a
%{mingw64_libdir}/libboost_wserialization-mt.a
# static only libraries
%{mingw64_libdir}/libboost_exception-mt.a
%{mingw64_libdir}/libboost_exception.a
%{mingw64_libdir}/libboost_test_exec_monitor-mt.a
%{mingw64_libdir}/libboost_test_exec_monitor.a

%changelog
* Wed Mar 01 2017 Thomas Sailer <t.sailer@alumni.ethz.ch> - 1.63.0-1
- update to 1.63.0

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.60.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Feb 02 2016 Thomas Sailer <t.sailer@alumni.ethz.ch> - 1.60.0-1
- update to 1.60.0

* Wed Sep 02 2015 Thomas Sailer <t.sailer@alumni.ethz.ch> - 1.59.0-1
- update to 1.59.0

* Wed Sep 02 2015 Thomas Sailer <t.sailer@alumni.ethz.ch> - 1.58.0-1
- update to 1.58.0

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.57.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon May  4 2015 Thomas Sailer <t.sailer@alumni.ethz.ch> - 1.57.0-1
- update to 1.57.0

* Mon Jun 30 2014 Thomas Sailer <t.sailer@alumni.ethz.ch> - 1.55.0-1
- update to 1.55.0

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.54.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Jul 30 2013 Thomas Sailer <t.sailer@alumni.ethz.ch> - 1.54.0-1
- update to 1.54.0

* Sat Jul 20 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 1.53.0-2
- Fix the build when the native libicu-devel is installed
- Fix FTBFS on recent mingw-w64 and also use intrinsics based
  versions of the Interlocked symbols which are better optimized

* Sun Mar  3 2013 Thomas Sailer <t.sailer@alumni.ethz.ch> - 1.53.0-1
- update to 1.53.0

* Sun Jan 27 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 1.50.0-2
- Rebuild against mingw-gcc 4.8 (win64 uses SEH exceptions now)

* Tue Dec  4 2012 Thomas Sailer <t.sailer@alumni.ethz.ch> - 1.50.0-1
- update to 1.50.0
- revert to bjam build

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.48.0-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jun 15 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 1.48.0-9
- Improved summary (RHBZ #831849)

* Wed Apr 25 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 1.48.0-8
- Rebuild against mingw-bzip2

* Fri Mar 16 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 1.48.0-7
- Added win64 support (contributed by Jay Higley)

* Wed Mar 07 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 1.48.0-6
- Renamed the source package to mingw-boost (RHBZ #800845)
- Fixed source URL
- Use mingw macros without leading underscore
- Dropped unneeded RPM tags

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

* Fri Oct 24 2008 Richard W.M. Jones <rjones@redhat.com> - 1.34.1-2
- Initial RPM release.
