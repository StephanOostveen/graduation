FROM ubuntu:18.04

RUN apt-get update && apt-get install -y ccache ninja-build python3 python3-pip git libssl-dev build-essential lld vim

# Get CMake and LLVM source code
WORKDIR /opt
RUN git clone -b llvmorg-15.0.6 --depth=1 https://github.com/llvm/llvm-project.git
RUN git clone -b v3.25.0 --depth=1 https://github.com/Kitware/CMake.git

# Build and install modern version of CMake that is able to compile llvm
RUN mkdir cmake-build llvm-build
WORKDIR /opt/cmake-build
RUN ../CMake/bootstrap --parallel=12 --generator=Ninja && ninja && ninja install

# Build and install modern version of Clang and Clang-tools-extra
WORKDIR /opt
# Copy necessary patches to llvm and vehicle repository
COPY *.patch .
RUN git apply --directory llvm-project palvar_check.patch

RUN cmake -G Ninja -Hllvm-project/llvm -Bllvm-build \
          -DCMAKE_BUILD_TYPE=Release \
          -DCLANG_ENABLE_BOOTSTRAP=On \
          -DLLVM_CCACHE_BUILD=ON \
          -DLLVM_USE_LINKER=lld \
          -DBUILD_SHARED_LIBS=OFF \
          -DLLVM_BUILD_BENCHMARKS=OFF \
          -DLLVM_BUILD_DOCS=OFF \
          -DLLVM_BUILD_INSTRUMENTED_COVERAGE=OFF \
          -DLLVM_BUILD_TESTS=OFF \
          -DLLVM_OPTIMIZED_TABLEGEN=ON \
          -DLLVM_ENABLE_PROJECTS="clang;clang-tools-extra;lld" \
          -DLLVM_ENABLE_RUNTIMES="compiler-rt;libcxx;libcxxabi;libunwind"\
          -DLLVM_PARALLEL_LINK_JOBS=6 \
          -DLLVM_TARGETS_TO_BUILD="X86"\
          -DCLANG_BOOTSTRAP_PASSTHROUGH="LLVM_BUILD_DOCS;LLVM_BUILD_INSTRUMENTED_COVERAGE;LLVM_BUILD_TESTS;LLVM_ENABLE_LTO;LLVM_OPTIMIZED_TABLEGEN;LLVM_PARALLEL_LINK_JOBS;LLVM_TARGETS_TO_BUILD" \
          -DBOOTSTRAP_LLVM_ENABLE_LTO=Thin 

RUN cmake --build llvm-build --target stage2-install 
RUN cmake --build llvm-build --target install-clang-tidy
# Setup ssh key
COPY id_ed25519 /root/.ssh/id_ed25519
COPY id_ed25519.pub /root/.ssh/id_ed25519.pub
RUN chmod 600 /root/.ssh/id_ed25519 && ssh-keyscan -t rsa bitbucket.org >> /root/.ssh/known_hosts
# Clone lyswe-vehicle
RUN git clone -b release/i88-2 --depth=1 git@bitbucket.org:lightyear-company/lyswe-vehicle.git && git -C lyswe-vehicle submodule update --init --jobs 10

# Apply patches
RUN git apply --directory lyswe-vehicle lyswe-vehicle.patch && git apply --directory lyswe-vehicle/superrepo/inVehicle/logical/esc_controller esc_controller.patch && git apply --directory lyswe-vehicle/superrepo/inVehicle/logical/vehicle_power_controller vehicle_power_controller.patch && git apply --directory lyswe-vehicle/superrepo/library/pal pal.patch

# Setup lyswe environment
WORKDIR /opt/lyswe-vehicle
RUN pip3 install jsonschema virtualenv && ./run.py install
# Apply fixes to recursive submodules that are pulled by run.py install
RUN git apply --directory superrepo/inVehicle/logical/ssc/superrepo/library/pal ../pal.patch && git apply --directory superrepo/inVehicle/logical/ssc/superrepo/library/commdb ../commdb.patch && git apply --directory superrepo/inVehicle/mock/steering_column_module_delphi/superrepo/library/pal ../pal_scm_delphi_mock.patch && git apply --directory superrepo/inVehicle/mock/authentication_vouch/superrepo/library/pal ../pal_authentication_vouch_mock.patch && git apply --directory superrepo/inVehicle/mock/abs_system/superrepo/library/pal ../pal_scm_delphi_mock.patch && git apply --directory superrepo/inVehicle/mock/motor_controller/superrepo/library/pal/ ../pal_scm_delphi_mock.patch && git apply --directory superrepo/inVehicle/mock/vdy/superrepo/library/pal/ ../pal_scm_delphi_mock.patch && git apply --directory superrepo/inVehicle/mock/12v_sensor_icd/superrepo/library/pal/ ../pal_scm_delphi_mock.patch && git apply --directory superrepo/inVehicle/mock/hvlv_converter_brusa/superrepo/library/pal/ ../pal_scm_delphi_mock.patch && git apply --directory superrepo/inVehicle/mock/hv_battery/superrepo/library/pal ../pal_scm_delphi_mock.patch && git apply --directory superrepo/inVehicle/mock/on_board_charger_brusa/superrepo/library/pal ../pal_scm_delphi_mock.patch && git apply --directory superrepo/inVehicle/mock/charger_control_unit/superrepo/library/pal ../pal_scm_delphi_mock.patch && git apply --directory superrepo/inVehicle/mock/door_latch/superrepo/library/pal ../pal_scm_delphi_mock.patch && git apply --directory superrepo/inVehicle/mock/airbag_control_unit/superrepo/library/pal ../pal_scm_delphi_mock.patch && git apply --directory superrepo/inVehicle/mock/windscreen_wipers/superrepo/library/pal ../pal_authentication_vouch_mock.patch && git apply --directory superrepo/inVehicle/mock/ev_supply_equipment/superrepo/library/pal ../pal_scm_delphi_mock.patch && git apply --directory superrepo/inVehicle/mock/lv_battery/superrepo/library/pal ../pal_scm_delphi_mock.patch && git apply --directory superrepo/inVehicle/mock/hvlv_converter/superrepo/library/pal ../pal_scm_delphi_mock.patch && git apply --directory superrepo/inVehicle/mock/solar_conversion_system/superrepo/library/pal ../pal_scm_delphi_mock.patch
RUN CC='clang -fuse-ld=lld' CXX='clang++ -fuse-ld=lld' ./run.py build --config=config/prod.networkcfg --can-forwarding-settings config/forwarding_settings.json --target RAFT --ignore-warnings
CMD ["/bin/bash"]