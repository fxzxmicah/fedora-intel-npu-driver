%global driver_version 1.32.1
%global driver_tag v%{driver_version}
%global npu_compiler_revision da4d79af8cb4bef6a71394bf0e22d998e5fe5b3a
%global npu_compiler_openvino_revision b7f9dbfa7944a1c576b87a4061c298636ae9f2a7
%global npu_compiler_elf_revision 82c444bcb9feb0f55fa33e18fbd711ec35426fba
%global npu_compiler_llvm_revision cf3934f4e8ada928544a743481e037935a21e857
%global npu_compiler_vpucostmodel_revision 33ef9a69b4e694ad5bfc521af829a9cc9ce19b4c
%global level_zero_npu_extensions_revision 42768cc73e74f6d371bd9dd51b1860b07774e7ec

%global debug_package %{nil}

Name:           intel-npu-driver
Version:        %{driver_version}
Release:        1%{?dist}
Summary:        Intel NPU user mode driver
License:        MIT
URL:            https://github.com/intel/linux-npu-driver

Source0:        https://github.com/intel/linux-npu-driver/archive/refs/tags/%{driver_tag}.tar.gz
Source1:        https://github.com/openvinotoolkit/npu_compiler/archive/%{npu_compiler_revision}.tar.gz#/npu_compiler-%{npu_compiler_revision}.tar.gz
Source2:        https://github.com/openvinotoolkit/openvino/archive/%{npu_compiler_openvino_revision}.tar.gz#/openvino-%{npu_compiler_openvino_revision}.tar.gz
Source3:        https://github.com/openvinotoolkit/npu_compiler_elf/archive/%{npu_compiler_elf_revision}.tar.gz#/npu_compiler_elf-%{npu_compiler_elf_revision}.tar.gz
Source4:        https://github.com/intel-staging/npu-compiler-llvm/archive/%{npu_compiler_llvm_revision}.tar.gz#/npu-compiler-llvm-%{npu_compiler_llvm_revision}.tar.gz
Source5:        https://github.com/intel/npu-nn-cost-model/archive/%{npu_compiler_vpucostmodel_revision}.tar.gz#/npu-nn-cost-model-%{npu_compiler_vpucostmodel_revision}.tar.gz
Source6:        https://github.com/intel/level-zero-npu-extensions/archive/%{level_zero_npu_extensions_revision}.tar.gz#/level-zero-npu-extensions-%{level_zero_npu_extensions_revision}.tar.gz

Patch1:         0001-intel-npu-driver-local-compiler-sources.patch
Patch2:         0002-intel-npu-driver-openvino-system-flatbuffers.patch
Patch3:         0003-intel-npu-driver-openvino-xbyak-system-includes.patch
Patch4:         0004-intel-npu-driver-npu-compiler-disable-tests.patch

ExclusiveArch:  x86_64

BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  flatbuffers-compiler
BuildRequires:  oneapi-level-zero-devel
BuildRequires:  cmake(xbyak)
BuildRequires:  cmake(libxml2)
BuildRequires:  cmake(pugixml)
BuildRequires:  cmake(nlohmann_json)
BuildRequires:  cmake(flatbuffers)
BuildRequires:  cmake(tbb)
BuildRequires:  cmake(zlib)
BuildRequires:  python3

%description
Intel NPU user mode driver and Level Zero runtime library for Intel Neural
Processing Unit hardware.

%package compiler
Summary:        Intel NPU driver-side compiler
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description compiler
Driver-side compiler library for Intel NPU hardware. This library enables
compilation of OpenVINO IR models through the Level Zero Graph Extension API.

%prep
%autosetup -N -n linux-npu-driver-%{version}
%setup -q -T -D -n linux-npu-driver-%{version} -a1 -a2 -a3 -a4 -a5 -a6

mkdir -p compiler/third_party
mv -T npu_compiler-%{npu_compiler_revision} compiler/third_party/npu_compiler
mv -T openvino-%{npu_compiler_openvino_revision} compiler/third_party/npu_compiler_openvino
mv -T npu_compiler_elf-%{npu_compiler_elf_revision} compiler/third_party/npu_compiler/thirdparty/elf
mv -T npu-compiler-llvm-%{npu_compiler_llvm_revision} compiler/third_party/npu_compiler/thirdparty/llvm-project
mv -T npu-nn-cost-model-%{npu_compiler_vpucostmodel_revision} compiler/third_party/npu_compiler/thirdparty/vpucostmodel
mv -T level-zero-npu-extensions-%{level_zero_npu_extensions_revision} third_party/level-zero-npu-extensions

%autopatch -p1

%build
%cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_INSTALL_LIBDIR=%{_lib} \
    -DBUILD_SHARED_LIBS=ON \
    -DENABLE_NPU_COMPILER_BUILD=ON \
    -DENABLE_NPU_PERFETTO_BUILD=OFF \
    -DENABLE_VALIDATION_BUILD=OFF \
    -DSKIP_UNIT_TESTS=ON \
    -DENABLE_TOOLS_BUILD=OFF \
    -DENABLE_OPENVINO_PACKAGE=OFF

%cmake_build

%install
%cmake_install

# clean up
rm -rf %{buildroot}/lib/firmware
rm -f %{buildroot}%{_libdir}/libze_intel_npu.so

%files
%doc README.md
%license LICENSE.md
%{_libdir}/libze_intel_npu.so.*

%files compiler
%{_libdir}/libnpu_driver_compiler.so

%changelog
* Thu May 07 2026 Fxzx micah <48860358+fxzxmicah@users.noreply.github.com> - 1.32.1-1
- Package Intel NPU driver runtime and compiler as separate RPMs.
