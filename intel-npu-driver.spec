%global driver_version 1.38.0
%global driver_tag v%{driver_version}
%global npu_compiler_revision 0b38f7d42113ff329ac2bdd33583d123de4ccf2f
%global npu_compiler_openvino_revision d8047fb380b27a9d5827cb3f22aec7781ae5ac82
%global npu_compiler_elf_revision d325f45f2cb405b5fa2ff17a30de9469f1641b73
%global npu_compiler_llvm_revision 8f3977c01be0f24be98b67ef2c911fd82657f30c
%global npu_compiler_vpucostmodel_revision 4b5da8484d7a5c8cb097486c1248c4d2a753ae4b
%global level_zero_npu_extensions_revision f9ad3bf89c2418d714aef2e6b96a5aafb12a1971

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
Patch2:         0002-intel-npu-driver-minimal-build.patch
Patch3:         0003-intel-npu-driver-compiler-elf-package.patch
Patch4:         0004-intel-npu-driver-consistent-git-executable.patch
Patch5:         0005-intel-npu-driver-npu-compiler-source-fallbacks.patch
Patch6:         0006-intel-npu-driver-npu-compiler-minimal-targets.patch
Patch7:         0007-intel-npu-driver-npu-compiler-system-flatbuffers.patch
Patch8:         0008-intel-npu-driver-vpunn-minimal-build.patch
Patch9:         0009-intel-npu-driver-openvino-system-flatbuffers.patch
Patch10:        0010-intel-npu-driver-openvino-xbyak-system-includes.patch
Patch11:        0011-intel-npu-driver-openvino-consistent-git-executable.patch
Patch12:        0012-intel-npu-driver-openvino-multiclass-nms-move.patch
Patch13:        0013-intel-npu-driver-npu-elf-git-fallback.patch
Patch14:        0014-intel-npu-driver-vpunn-optional-http-client.patch

ExclusiveArch:  x86_64

BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  flatbuffers-compiler
BuildRequires:  oneapi-level-zero-devel >= 1.32.0
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
    -DENABLE_OFFLINE_COMPILATION_SUPPORT=OFF \
    -DENABLE_COMPILATION_FLAGS_OVERRIDE=OFF \
    -DENABLE_NPU_ELF_BUILD=OFF \
    -DENABLE_NPU_ALT_DEPENDENCY_PATH_OVERRIDE=OFF \
    -DENABLE_NPU_LOGGING=OFF \
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
%{_libdir}/libopenvino_intel_npu_compiler.so
%{_libdir}/libopenvino_intel_npu_compiler_loader.so

%changelog
* Sun Sep 20 2026 Fxzx micah <48860358+fxzxmicah@users.noreply.github.com> - 1.38.0-1
- Update to linux-npu-driver 1.38.0.
- Refresh bundled compiler revisions and Fedora build patches.
- Disable tests, profiling, tools, and other optional components for a smaller build.

* Thu May 07 2026 Fxzx micah <48860358+fxzxmicah@users.noreply.github.com> - 1.32.1-1
- Package Intel NPU driver runtime and compiler as separate RPMs.
