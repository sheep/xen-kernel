%global __spec_install_pre %{___build_pre}

# Define ksbindir of /sbin or /usr/sbin/ based on rhel6 or rhel7
%if "%{rhel}" == "6"
%define ksbindir /sbin
%else
%define ksbindir /usr/sbin
%endif
 
# Define the version of the Linux Kernel Archive tarball.
%define LKAver 4.9.54 

# Define the buildid, if required.
#define buildid .1

# The following build options are enabled by default.
# Use either --without <option> on your rpmbuild command line
# or force the values to 0, here, to disable them.

# PAE kernel
%define with_std          %{?_without_std:          0} %{?!_without_std:          1}
# NONPAE kernel
%define with_nonpae       %{?_without_nonpae:       0} %{?!_without_nonpae:       1}
# kernel-doc
%define with_doc          %{?_without_doc:          0} %{?!_without_doc:          1}
# kernel-headers
%define with_headers      %{?_without_headers:      0} %{?!_without_headers:      1}
# kernel-firmware
%define with_firmware     %{?_without_firmware:     0} %{?!_without_firmware:     1}
# perf subpackage
%define with_perf         %{?_without_perf:         0} %{?!_without_perf:         1}
# vdso directories installed
%define with_vdso_install %{?_without_vdso_install: 0} %{?!_without_vdso_install: 1}
# use dracut instead of mkinitrd
%define with_dracut       %{?_without_dracut:       0} %{?!_without_dracut:       1}
# kernel-debuginfo
%define with_debuginfo %{?_without_debuginfo: 0} %{?!_without_debuginfo: 1}

%if !%{with_debuginfo}
%define _enable_debug_packages 0
%endif
%define debuginfodir /usr/lib/debug

# Build only the kernel-doc & kernel-firmware packages.
%ifarch noarch
%define with_std 0
%define with_nonpae 0
%define with_headers 0
%define with_perf 0
%define with_vdso_install 0
%define with_firmware 0
%define with_debuginfo 0
%endif

# Build only the 32-bit kernel-headers package.
%ifarch i386
%define with_std 0
%define with_nonpae 0
%define with_doc 0
%define with_firmware 0
%define with_perf 0
%define with_vdso_install 0
%endif

# Build only the 32-bit kernel packages.
%ifarch i686
%define with_nonpae 1
%define with_doc 0
%define with_firmware 0
%endif

# Build only the 64-bit kernel-headers & kernel packages.
%ifarch x86_64
%define with_nonpae 0
%define with_doc 0
%define with_firmware 0
%endif

# Define the asmarch.
%define asmarch x86

# Define the correct buildarch.
%define buildarch x86_64
%ifarch i386 i686
%define buildarch i386
%endif

# Define the vdso_arches.
%if %{with_vdso_install}
%define vdso_arches i686 x86_64
%endif

# Determine the sublevel number and set pkg_version.
%define sublevel %(echo %{LKAver} | %{__awk} -F\. '{ print $3 }')
%if "%{sublevel}" == ""
%define pkg_version %{LKAver}.0
%else
%define pkg_version %{LKAver}
%endif

# Set pkg_release.
%define pkg_release 29%{?buildid}%{?dist}

#
# Three sets of minimum package version requirements in the form of Conflicts.
#

#
# First the general kernel required versions, as per Documentation/Changes.
#
%define kernel_dot_org_conflicts  ppp < 2.4.3-3, isdn4k-utils < 3.2-32, nfs-utils < 1.0.7-12, e2fsprogs < 1.37-4, util-linux < 2.12, jfsutils < 1.1.7-2, reiserfs-utils < 3.6.19-2, xfsprogs < 2.6.13-4, procps < 3.2.5-6.3, oprofile < 0.9.1-2

#
# Then a series of requirements that are distribution specific, either because
# the older versions have problems with the newer kernel or lack certain things
# that make integration in the distro harder than needed.
#
%define package_conflicts initscripts < 7.23, udev < 145-11, iptables < 1.3.2-1, ipw2200-firmware < 2.4, iwl4965-firmware < 228.57.2, selinux-policy-targeted < 1.25.3-14, squashfs-tools < 4.0, wireless-tools < 29-3

#
# We moved the drm include files into kernel-headers, make sure there's
# a recent enough libdrm-devel on the system that doesn't have those.
#
%define kernel_headers_conflicts libdrm-devel < 2.4.0-0.15

#
# Packages that need to be installed before the kernel because the %post scripts make use of them.
#
%define kernel_prereq fileutils, module-init-tools, initscripts >= 8.11.1-1, grubby >= 7.0.4-1
%if %{with_dracut}
%define initrd_prereq dracut-kernel >= 002-18.git413bcf78
%else
%define initrd_prereq mkinitrd >= 6.0.61-1
%endif

Name: kernel
Summary: The Linux kernel. (The core of any Linux-based operating system.)
Group: System Environment/Kernel
License: GPLv2
URL: http://www.kernel.org/
Version: %{pkg_version}
Release: %{pkg_release}
ExclusiveArch: noarch i686 x86_64
ExclusiveOS: Linux
Provides: kernel = %{version}-%{release}
Provides: kernel-%{_target_cpu} = %{version}-%{release}
Provides: kernel-drm = 4.3.0
Provides: kernel-drm-nouveau = 16
Provides: kernel-modeset = 1
Provides: kernel-xen = %{version}-%{release}.%{_target_cpu}
Provides: kernel-uname-r = %{version}-%{release}.%{_target_cpu}
%if "%{rhel}" == "7"
Requires: linux-firmware >=  20140911
%else
Requires: kernel-firmware >= %{version}-%{release}
%endif
Requires(pre): %{kernel_prereq}
Requires(pre): %{initrd_prereq}
Requires(post): %{ksbindir}/new-kernel-pkg
Requires(preun): %{ksbindir}/new-kernel-pkg
Conflicts: %{kernel_dot_org_conflicts}
Conflicts: %{package_conflicts}
Conflicts: %{kernel_headers_conflicts}
# We can't let RPM do the dependencies automatically because it'll then pick up
# a correct but undesirable perl dependency from the module headers which
# isn't required for the kernel proper to function.
AutoReq: no
AutoProv: yes

#
# List the packages used during the kernel build.
#
BuildRequires: module-init-tools, patch >= 2.5.4, bash >= 2.03, sh-utils, tar
BuildRequires: bzip2, findutils, gzip, m4, perl, make >= 3.78, diffutils, gawk
BuildRequires: gcc >= 3.4.2, binutils >= 2.12, redhat-rpm-config
BuildRequires: net-tools, patchutils, rpm-build >= 4.8.0-7
BuildRequires: xmlto, asciidoc, bc
%if %{with_perf}
BuildRequires: elfutils-libelf-devel zlib-devel binutils-devel newt-devel, numactl-devel
BuildRequires: python-devel perl(ExtUtils::Embed) gtk2-devel bison 
BuildRequires: elfutils-devel systemtap-sdt-devel audit-libs-devel
%endif
BuildRequires: python openssl-devel

BuildConflicts: rhbuildsys(DiskFree) < 7Gb

# Sources.
Source0: ftp://ftp.kernel.org/pub/linux/kernel/v3.x/linux-%{LKAver}.tar.xz
Source1: config-i686
Source2: config-i686-NONPAE
Source3: config-x86_64

#Patches

Patch10000: blktap2.patch
Patch10001: export-for-xenfb2.patch
#Patch10002: xen-apic-id-fix.patch
#Patch10003: xen-nested-dom0-fix.patch
#Patch10004: xsa216-linux-4.11.patch
#Patch10005: xen-netback-correctly_schedule_rate-limited_queues.patch
#Patch10006: xsa229.patch
Patch10007: Destroy-ldisc-instance-hangup.patch

%description
This package provides the Linux kernel (vmlinuz), the core of any
Linux-based operating system. The kernel handles the basic functions
of the OS: memory allocation, process allocation, device I/O, etc.

%package devel
Summary: Development package for building kernel modules to match the kernel.
Group: System Environment/Kernel
Provides: kernel-devel-%{_target_cpu} = %{version}-%{release}
Provides: kernel-devel = %{version}-%{release}
Provides: kernel-devel-uname-r = %{version}-%{release}.%{_target_cpu}
Requires(pre): /usr/bin/find
AutoReqProv: no
%description devel
This package provides the kernel header files and makefiles
sufficient to build modules against the kernel package.

%if %{with_nonpae}
%package NONPAE
Summary: The Linux kernel for non-PAE capable processors.
Group: System Environment/Kernel
Provides: kernel = %{version}-%{release}
Provides: kernel-%{_target_cpu} = %{version}-%{release}NONPAE
Provides: kernel-NONPAE = %{version}-%{release}
Provides: kernel-NONPAE-%{_target_cpu} = %{version}-%{release}NONPAE
Provides: kernel-drm = 4.3.0
Provides: kernel-drm-nouveau = 16
Provides: kernel-modeset = 1
Provides: kernel-uname-r = %{version}-%{release}.%{_target_cpu}
Requires(pre): %{kernel_prereq}
Requires(pre): %{initrd_prereq}
Requires(post): %{ksbindir}/new-kernel-pkg
Requires(preun): %{ksbindir}/new-kernel-pkg
Conflicts: %{kernel_dot_org_conflicts}
Conflicts: %{package_conflicts}
Conflicts: %{kernel_headers_conflicts}
# We can't let RPM do the dependencies automatically because it'll then pick up
# a correct but undesirable perl dependency from the module headers which
# isn't required for the kernel proper to function.
AutoReq: no
AutoProv: yes
%description NONPAE
This package provides a version of the Linux kernel suitable for
processors without the Physical Address Extension (PAE) capability.
It can only address up to 4GB of memory.

%package NONPAE-devel
Summary: Development package for building kernel modules to match the non-PAE kernel.
Group: System Environment/Kernel
Provides: kernel-NONPAE-devel-%{_target_cpu} = %{version}-%{release}
Provides: kernel-NONPAE-devel = %{version}-%{release}NONPAE
Provides: kernel-NONPAE-devel-uname-r = %{version}-%{release}.%{_target_cpu}
Requires(pre): /usr/bin/find
AutoReqProv: no
%description NONPAE-devel
This package provides the kernel header files and makefiles
sufficient to build modules against the kernel package.
%endif

%if %{with_doc}
%package doc
Summary: Various bits of documentation found in the kernel sources.
Group: Documentation
Provides: kernel-doc = %{version}-%{release}
%description doc
This package provides documentation files from the kernel sources.
Various bits of information about the Linux kernel and the device
drivers shipped with it are documented in these files.

You\'ll want to install this package if you need a reference to the
options that can be passed to the kernel modules at load time.
%endif

%if %{with_headers}
%package headers
Summary: Header files for the Linux kernel for use by glibc
Group: Development/System
Obsoletes: glibc-kernheaders
Provides: glibc-kernheaders = 3.0-46
Provides: kernel-headers = %{version}-%{release}
Conflicts: kernel-headers < %{version}-%{release}
%description headers
This package provides the C header files that specify the interface
between the Linux kernel and userspace libraries & programs. The
header files define structures and constants that are needed when
building most standard programs. They are also required when
rebuilding the glibc package.
%endif

%if %{with_firmware}
%package firmware
Summary: Firmware files used by the Linux kernel
Group: Development/System
License: GPL+ and GPLv2+ and MIT and Redistributable, no modification permitted
Provides: kernel-firmware = %{version}-%{release}
Conflicts: kernel-firmware < %{version}-%{release}
%description firmware
This package provides the firmware files required for some devices to operate.
%endif

%if %{with_perf}
%package -n perf
Summary: Performance monitoring for the Linux kernel
Group: Development/System
License: GPLv2
Provides: perl(Perf::Trace::Context) = 0.01
Provides: perl(Perf::Trace::Core) = 0.01
Provides: perl(Perf::Trace::Util) = 0.01
%description -n perf
This package provides the perf tool and the supporting documentation.
%endif

%if %{with_debuginfo}
%package debuginfo
Summary: Kernel source files used by %{name}-debuginfo packages
Group: Development/Debug
%description debuginfo
This package provides debug information for kernel-%{version}-%{release}.
%endif

# Disable the building of the debug package(s).
%define debug_package %{nil}

%prep
%setup -q -n %{name}-%{version} -c
%{__mv} linux-%{LKAver} linux-%{version}-%{release}.%{_target_cpu}
pushd linux-%{version}-%{release}.%{_target_cpu} > /dev/null
%{__cp} %{SOURCE1} .
%{__cp} %{SOURCE2} .
%{__cp} %{SOURCE3} .

# to change firmware in the kernel
# now using linux-firmware package
# 
#%{__cp} %{SOURCE8} firmware/bnx2/
#%{__cp} %{SOURCE9} firmware/bnx2x/
#pushd firmware/bnx2/ > /dev/null
#tar xvzf $(basename %{SOURCE8})
#for fwfile in $(ls *.fw)
#  do
#    objcopy -O ihex -I binary $fwfile $fwfile.ihex
#  done
#popd > /dev/null
#pushd firmware/bnx2x/ > /dev/null
#tar xvzf $(basename %{SOURCE9})
#for fwfile in $(ls *.fw)
#  do
#    objcopy -O ihex -I binary $fwfile $fwfile.ihex
#  done
#popd > /dev/null

#roll in patches
%patch10000 -p1
%patch10001 -p1
#%patch10002 -p1
#%patch10003 -p1
#%patch10004 -p1
#%patch10005 -p1
#%patch10006 -p1
%patch10007 -p1

popd > /dev/null

%build

%if %{with_debuginfo}
# This override tweaks the kernel makefiles so that we run debugedit on an
# object before embedding it.  When we later run find-debuginfo.sh, it will
# run debugedit again.  The edits it does change the build ID bits embedded
# in the stripped object, but repeating debugedit is a no-op.  We do it
# beforehand to get the proper final build ID bits into the embedded image.
# This affects the vDSO images in vmlinux, and the vmlinux image in bzImage.
export AFTER_LINK=\
'sh -xc "/usr/lib/rpm/debugedit -b $$RPM_BUILD_DIR -d /usr/src/debug -i $@"'
%endif

BuildKernel() {
    Flavour=$1

    %{__make} -s mrproper

    # Select the correct flavour configuration file.
    if [ -z "${Flavour}" ]; then
      %{__cp} config-%{_target_cpu} .config
    else
      %{__cp} config-%{_target_cpu}-${Flavour} .config
    fi

    %define KVRFA %{version}-%{release}${Flavour}.%{_target_cpu}

    # Correctly set the EXTRAVERSION string in the main Makefile.
    %{__perl} -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -%{release}${Flavour}.%{_target_cpu}/" Makefile

    %{__make} -s CONFIG_DEBUG_SECTION_MISMATCH=y ARCH=%{buildarch} V=1 %{?_smp_mflags} bzImage
    %{__make} -s CONFIG_DEBUG_SECTION_MISMATCH=y ARCH=%{buildarch} V=1 %{?_smp_mflags} modules

    # Install the results into the RPM_BUILD_ROOT directory.
%if %{with_debuginfo}
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/boot
    install -m 644 System.map $RPM_BUILD_ROOT/%{debuginfodir}/boot/System.map-%{KVRFA}
%endif

    %{__mkdir_p} $RPM_BUILD_ROOT/boot
    %{__install} -m 644 .config $RPM_BUILD_ROOT/boot/config-%{KVRFA}
    %{__install} -m 644 System.map $RPM_BUILD_ROOT/boot/System.map-%{KVRFA}

%if %{with_dracut}
    # We estimate the size of the initramfs because rpm needs to take this size
    # into consideration when performing disk space calculations. (See bz #530778)
    dd if=/dev/zero of=$RPM_BUILD_ROOT/boot/initramfs-%{KVRFA}.img bs=1M count=20
%else
    dd if=/dev/zero of=$RPM_BUILD_ROOT/boot/initrd-%{KVRFA}.img bs=1M count=5
%endif

    %{__cp} arch/x86/boot/bzImage $RPM_BUILD_ROOT/boot/vmlinuz-%{KVRFA}
    %{__chmod} 755 $RPM_BUILD_ROOT/boot/vmlinuz-%{KVRFA}

    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}
    # Override $(mod-fw) because we don't want it to install any firmware
    # We'll do that ourselves with 'make firmware_install'
    %{__make} -s ARCH=%{buildarch} INSTALL_MOD_PATH=$RPM_BUILD_ROOT modules_install KERNELRELEASE=%{KVRFA} mod-fw=

%ifarch %{vdso_arches}
    %{__make} -s ARCH=%{buildarch} INSTALL_MOD_PATH=$RPM_BUILD_ROOT vdso_install KERNELRELEASE=%{KVRFA}
    if grep '^CONFIG_XEN=y$' .config > /dev/null; then
      echo > ldconfig-kernel.conf "\
# This directive teaches ldconfig to search in nosegneg subdirectories
# and cache the DSOs there with extra bit 0 set in their hwcap match
# fields.  In Xen guest kernels, the vDSO tells the dynamic linker to
# search in nosegneg subdirectories and to match this extra hwcap bit
# in the ld.so.cache file.
hwcap 1 nosegneg"
    fi
    if [ ! -s ldconfig-kernel.conf ]; then
      echo > ldconfig-kernel.conf "\
# Placeholder file, no vDSO hwcap entries used in this kernel."
    fi
    %{__install} -D -m 444 ldconfig-kernel.conf $RPM_BUILD_ROOT/etc/ld.so.conf.d/kernel-%{KVRFA}.conf
%endif

    # Save the headers/makefiles, etc, for building modules against.
    #
    # This looks scary but the end result is supposed to be:
    #
    # - all arch relevant include/ files
    # - all Makefile & Kconfig files
    # - all script/ files
    #
    %{__rm} -f $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    %{__rm} -f $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/source
    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    pushd $RPM_BUILD_ROOT/lib/modules/%{KVRFA} > /dev/null
    %{__ln_s} build source
    popd > /dev/null
    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/extra
    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/updates
    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/weak-updates

    # First copy everything . . .
    %{__cp} --parents `find  -type f -name "Makefile*" -o -name "Kconfig*"` $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    %{__cp} Module.symvers $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    %{__cp} System.map $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    if [ -s Module.markers ]; then
      %{__cp} Module.markers $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    fi

    %{__gzip} -c9 < Module.symvers > $RPM_BUILD_ROOT/boot/symvers-%{KVRFA}.gz

    # . . . then drop all but the needed Makefiles & Kconfig files.
    %{__rm} -rf $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/Documentation
    %{__rm} -rf $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/scripts
    %{__rm} -rf $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include
    %{__cp} .config $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    %{__cp} -a scripts $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    if [ -d arch/%{buildarch}/scripts ]; then
      %{__cp} -a arch/%{buildarch}/scripts $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/arch/%{_arch} || :
    fi
    if [ -f arch/%{buildarch}/*lds ]; then
      %{__cp} -a arch/%{buildarch}/*lds $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/arch/%{_arch}/ || :
    fi
    %{__rm} -f $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/scripts/*.o
    %{__rm} -f $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/scripts/*/*.o
    if [ -d arch/%{asmarch}/include ]; then
      %{__cp} -a --parents arch/%{asmarch}/include $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/
    fi
    if [ -d arch/%{asmarch}/syscalls ]; then
      %{__cp} -a --parents arch/%{asmarch}/syscalls $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/
    fi
    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include
    pushd include > /dev/null
    %{__cp} -a * $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include
    %{__rm} -f $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/Kbuild
    popd > /dev/null
    # Make a hard-link from the include/linux/ directory to the include/generated/autoconf.h file.
    %{__rm} -f $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/Kbuild
    # Ensure a copy of the version.h file is in the include/linux/ directory.
    %{__cp} usr/include/linux/version.h $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/linux/
    # Copy the generated autoconf.h file to the include/linux/ directory.
    %{__cp} include/generated/autoconf.h $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/linux/
    # Copy .config to include/config/auto.conf so a "make prepare" is unnecessary.
    %{__cp} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/.config $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/config/auto.conf
    # Now ensure that the Makefile, .config, version.h, autoconf.h and auto.conf files
    # all have matching timestamps so that external modules can be built.
    touch -r $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/Makefile $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/.config
    touch -r $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/Makefile $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/config/auto.conf
    touch -r $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/Makefile $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/linux/autoconf.h
    touch -r $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/Makefile $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/linux/version.h
    touch -r $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/Makefile $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/generated/autoconf.h
    touch -r $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/Makefile $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/generated/uapi/linux/version.h

    #
    # save the vmlinux file for kernel debugging into the kernel-debuginfo rpm
    #
%if %{with_debuginfo}
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/%{KVRFA}
    cp vmlinux $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/%{KVRFA}
%endif

    # Remove any 'left-over' .cmd files.
    /usr/bin/find $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/ -type f -name "*.cmd" | xargs --no-run-if-empty %{__rm} -f

    find $RPM_BUILD_ROOT/lib/modules/%{KVRFA} -name "*.ko" -type f > modnames

    # Mark the modules executable, so that strip-to-file can strip them.
    xargs --no-run-if-empty %{__chmod} u+x < modnames

    # Generate a list of modules for block and networking.
    fgrep /drivers/ modnames | xargs --no-run-if-empty nm -upA | sed -n 's,^.*/\([^/]*\.ko\):  *U \(.*\)$,\1 \2,p' > drivers.undef

    collect_modules_list()
    {
      sed -r -n -e "s/^([^ ]+) \\.?($2)\$/\\1/p" drivers.undef | LC_ALL=C sort -u > $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/modules.$1
    }

    collect_modules_list networking \
        'register_netdev|ieee80211_register_hw|usbnet_probe|phy_driver_register'

    collect_modules_list block \
        'ata_scsi_ioctl|scsi_add_host|scsi_add_host_with_dma|blk_init_queue|register_mtd_blktrans|scsi_esp_register|scsi_register_device_handler'

    collect_modules_list drm \
        'drm_open|drm_init'

    collect_modules_list modesetting \
        'drm_crtc_init'

    # Detect any missing or incorrect license tags.
    %{__rm} -f modinfo

    while read i
    do
        echo -n "${i#$RPM_BUILD_ROOT/lib/modules/%{KVRFA}/} " >> modinfo
        %{ksbindir}/modinfo -l $i >> modinfo
    done < modnames

    egrep -v 'GPL( v2)?$|Dual BSD/GPL$|Dual MPL/GPL$|GPL and additional rights$' modinfo && exit 1

    %{__rm} -f modinfo modnames

    # Remove all the files that will be auto generated by depmod at the kernel install time.
    for i in alias alias.bin ccwmap dep dep.bin ieee1394map inputmap isapnpmap ofmap pcimap seriomap symbols symbols.bin usbmap
    do
        %{__rm} -f $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/modules.$i
    done

    # Move the development files out of the /lib/modules/ file system.
    %{__mkdir_p} $RPM_BUILD_ROOT/usr/src/kernels
    %{__mv} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build $RPM_BUILD_ROOT/usr/src/kernels/%{KVRFA}
    %{__ln_s} -f ../../../usr/src/kernels/%{KVRFA} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
}

%{__rm} -rf $RPM_BUILD_ROOT

pushd linux-%{version}-%{release}.%{_target_cpu} > /dev/null

%if %{with_std}
BuildKernel
%endif

%if %{with_nonpae}
BuildKernel NONPAE
%endif

%if %{with_doc}
# Make the HTML and man pages.
%{__make} -s -j1 htmldocs mandocs 2> /dev/null || false

# Sometimes non-world-readable files sneak into the kernel source tree.
%{__chmod} -R a=rX Documentation
find Documentation -type d | xargs %{__chmod} u+w
%endif

%if %{with_perf}
%global perf_make \
  %{__make} -s %{?_smp_mflags} -C tools/perf V=1 HAVE_CPLUS_DEMANGLE=1 NO_DWARF=1 WERROR=0 prefix=%{_prefix}

%{perf_make} all
%{perf_make} man || false
%endif

popd > /dev/null

%if %{with_debuginfo}

%define __debug_install_post \
  /usr/lib/rpm/find-debuginfo.sh --strict-build-id %{_builddir}/%{?buildsubdir}\
%{nil}

%ifnarch noarch
%global __debug_package 1
%files -f debugfiles.list debuginfo
%defattr(-,root,root)
%endif

%endif

%install
pushd linux-%{version}-%{release}.%{_target_cpu} > /dev/null

%if %{with_doc}
docdir=$RPM_BUILD_ROOT%{_datadir}/doc/%{name}-doc-%{version}
man9dir=$RPM_BUILD_ROOT%{_datadir}/man/man9

# Copy the documentation over.
%{__mkdir_p} $docdir
%{__tar} -f - --exclude=man --exclude='.*' -c Documentation | %{__tar} xf - -C $docdir

# Install the man pages for the kernel API.
%{__mkdir_p} $man9dir
for file in $(find Documentation/DocBook/man -name '*.9.gz' | sort | uniq); do
%{__cp} -af $file $man9dir/
done
%endif

%if %{with_headers}
# Install the kernel headers.
%{__make} -s ARCH=%{buildarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_install

# Do a headers_check but don't die if it fails.
%{__make} -s ARCH=%{buildarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_check > hdrwarnings.txt || :
if grep -q exist hdrwarnings.txt; then
   sed s:^$RPM_BUILD_ROOT/usr/include/:: hdrwarnings.txt
   # Temporarily cause a build failure if there are header inconsistencies.
   # exit 1
fi

# Remove the unrequired files.
find $RPM_BUILD_ROOT/usr/include \
     \( -name .install -o -name .check -o \
        -name ..install.cmd -o -name ..check.cmd \) | xargs %{__rm} -f

# For now, glibc provides the scsi headers.
%{__rm} -rf $RPM_BUILD_ROOT/usr/include/scsi
%{__rm} -f $RPM_BUILD_ROOT/usr/include/asm*/atomic.h
%{__rm} -f $RPM_BUILD_ROOT/usr/include/asm*/io.h
%{__rm} -f $RPM_BUILD_ROOT/usr/include/asm*/irq.h
%endif

%if %{with_firmware}
# It's important NOT to have a .config file present, as it will just confuse the system.
%{__make} -s INSTALL_FW_PATH=$RPM_BUILD_ROOT/lib/firmware firmware_install
%endif

%if %{with_perf}
# perf tool binary and supporting scripts/binaries.
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install

# perf man pages. (Note: implicit rpm magic compresses them later.)
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install-man || false
%endif

popd > /dev/null

%clean
%{__rm} -rf $RPM_BUILD_ROOT

# Scripts section.
%if %{with_std}
%posttrans
NEWKERNARGS=""
(%{ksbindir}/grubby --info=`%{ksbindir}/grubby --default-kernel`) 2>/dev/null | grep -q crashkernel
if [ $? -ne 0 ]; then
        NEWKERNARGS="--kernel-args=\"crashkernel=auto\""
fi
%if %{with_dracut}
%{ksbindir}/new-kernel-pkg --package kernel --mkinitrd --dracut --depmod --update %{version}-%{release}.%{_target_cpu} $NEWKERNARGS || exit $?
%else
%{ksbindir}/new-kernel-pkg --package kernel --mkinitrd --depmod --update %{version}-%{release}.%{_target_cpu} $NEWKERNARGS || exit $?
%endif
%{ksbindir}/new-kernel-pkg --package kernel --rpmposttrans %{version}-%{release}.%{_target_cpu} || exit $?
if [ -x %{ksbindir}/weak-modules ]; then
    %{ksbindir}/weak-modules --add-kernel %{version}-%{release}.%{_target_cpu} || exit $?
fi
if [ -x %{ksbindir}/ldconfig ]
then
    %{ksbindir}/ldconfig -X || exit $?
fi

#added tp auto-install xen kernel in grub
%ifarch x86_64
if [ -e /etc/sysconfig/xen-kernel ] && [ -e /usr/bin/grub-bootxen.sh ] ; then
    kver="%{version}-%{release}.%{_target_cpu}" /usr/bin/grub-bootxen.sh
fi
%endif

%post
if [ `uname -i` == "i386" ] && [ -f /etc/sysconfig/kernel ]; then
    /bin/sed -r -i -e 's/^DEFAULTKERNEL=kernel-NONPAE$/DEFAULTKERNEL=kernel/' /etc/sysconfig/kernel || exit $?
fi
if grep --silent '^hwcap 0 nosegneg$' /etc/ld.so.conf.d/kernel-*.conf 2> /dev/null; then
    /bin/sed -i '/^hwcap 0 nosegneg$/ s/0/1/' /etc/ld.so.conf.d/kernel-*.conf
fi
%{ksbindir}/new-kernel-pkg --package kernel --install %{version}-%{release}.%{_target_cpu} || exit $?

%preun
%{ksbindir}/new-kernel-pkg --rminitrd --rmmoddep --remove %{version}-%{release}.%{_target_cpu} || exit $?
if [ -x %{ksbindir}/weak-modules ]; then
    %{ksbindir}/weak-modules --remove-kernel %{version}-%{release}.%{_target_cpu} || exit $?
fi
if [ -x %{ksbindir}/ldconfig ]
then
    %{ksbindir}/ldconfig -X || exit $?
fi

%post devel
if [ -f /etc/sysconfig/kernel ]; then
    . /etc/sysconfig/kernel || exit $?
fi
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ]; then
    pushd /usr/src/kernels/%{version}-%{release}.%{_target_cpu} > /dev/null
    /usr/bin/find . -type f | while read f; do
        hardlink -c /usr/src/kernels/*.fc*.*/$f $f
    done
    popd > /dev/null
fi
%endif

%if %{with_nonpae}
%posttrans NONPAE
NEWKERNARGS=""
(%{ksbindir}/grubby --info=`%{ksbindir}/grubby --default-kernel`) 2> /dev/null | grep -q crashkernel
if [ $? -ne 0 ]; then
    NEWKERNARGS="--kernel-args=\"crashkernel=auto\""
fi
%if %{with_dracut}
%{ksbindir}/new-kernel-pkg --package kernel-NONPAE --mkinitrd --dracut --depmod --update %{version}-%{release}NONPAE.%{_target_cpu} $NEWKERNARGS || exit $?
%else
%{ksbindir}/new-kernel-pkg --package kernel-NONPAE --mkinitrd --depmod --update %{version}-%{release}NONPAE.%{_target_cpu} $NEWKERNARGS || exit $?
%endif
%{ksbindir}/new-kernel-pkg --package kernel-NONPAE --rpmposttrans %{version}-%{release}NONPAE.%{_target_cpu} || exit $?
if [ -x %{ksbindir}/weak-modules ]; then
    %{ksbindir}/weak-modules --add-kernel %{version}-%{release}NONPAE.%{_target_cpu} || exit $?
fi
if [ -x %{ksbindir}/ldconfig ]
then
    %{ksbindir}/ldconfig -X || exit $?
fi

%post NONPAE
if [ `uname -i` == "i386" ] && [ -f /etc/sysconfig/kernel ]; then
    /bin/sed -r -i -e 's/^DEFAULTKERNEL=kernel$/DEFAULTKERNEL=kernel-NONPAE/' /etc/sysconfig/kernel || exit $?
fi
%{ksbindir}/new-kernel-pkg --package kernel-NONPAE --install %{version}-%{release}NONPAE.%{_target_cpu} || exit $?

%preun NONPAE
%{ksbindir}/new-kernel-pkg --rminitrd --rmmoddep --remove %{version}-%{release}NONPAE.%{_target_cpu} || exit $?
if [ -x %{ksbindir}/weak-modules ]; then
    %{ksbindir}/weak-modules --remove-kernel %{version}-%{release}NONPAE.%{_target_cpu} || exit $?
fi
if [ -x %{ksbindir}/ldconfig ]
then
    %{ksbindir}/ldconfig -X || exit $?
fi

%post NONPAE-devel
if [ -f /etc/sysconfig/kernel ]; then
    . /etc/sysconfig/kernel || exit $?
fi
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ]; then
    pushd /usr/src/kernels/%{version}-%{release}NONPAE.%{_target_cpu} > /dev/null
    /usr/bin/find . -type f | while read f; do
        hardlink -c /usr/src/kernels/*.fc*.*/$f $f
    done
    popd > /dev/null
fi
%endif

# Files section.
%if %{with_std}
%files
%defattr(-,root,root)
/boot/vmlinuz-%{version}-%{release}.%{_target_cpu}
/boot/System.map-%{version}-%{release}.%{_target_cpu}
/boot/symvers-%{version}-%{release}.%{_target_cpu}.gz
/boot/config-%{version}-%{release}.%{_target_cpu}
%dir /lib/modules/%{version}-%{release}.%{_target_cpu}
/lib/modules/%{version}-%{release}.%{_target_cpu}/kernel
/lib/modules/%{version}-%{release}.%{_target_cpu}/extra
/lib/modules/%{version}-%{release}.%{_target_cpu}/build
/lib/modules/%{version}-%{release}.%{_target_cpu}/source
/lib/modules/%{version}-%{release}.%{_target_cpu}/updates
/lib/modules/%{version}-%{release}.%{_target_cpu}/weak-updates
%ifarch %{vdso_arches}
/lib/modules/%{version}-%{release}.%{_target_cpu}/vdso
/etc/ld.so.conf.d/kernel-%{version}-%{release}.%{_target_cpu}.conf
%endif
/lib/modules/%{version}-%{release}.%{_target_cpu}/modules.*
%if %{with_dracut}
%ghost /boot/initramfs-%{version}-%{release}.%{_target_cpu}.img
%else
%ghost /boot/initrd-%{version}-%{release}.%{_target_cpu}.img
%endif

%files devel
%defattr(-,root,root)
%dir /usr/src/kernels
/usr/src/kernels/%{version}-%{release}.%{_target_cpu}
%endif

%if %{with_nonpae}
%files NONPAE
%defattr(-,root,root)
/boot/vmlinuz-%{version}-%{release}NONPAE.%{_target_cpu}
/boot/System.map-%{version}-%{release}NONPAE.%{_target_cpu}
/boot/symvers-%{version}-%{release}NONPAE.%{_target_cpu}.gz
/boot/config-%{version}-%{release}NONPAE.%{_target_cpu}
%dir /lib/modules/%{version}-%{release}NONPAE.%{_target_cpu}
/lib/modules/%{version}-%{release}NONPAE.%{_target_cpu}/kernel
/lib/modules/%{version}-%{release}NONPAE.%{_target_cpu}/extra
/lib/modules/%{version}-%{release}NONPAE.%{_target_cpu}/build
/lib/modules/%{version}-%{release}NONPAE.%{_target_cpu}/source
/lib/modules/%{version}-%{release}NONPAE.%{_target_cpu}/updates
/lib/modules/%{version}-%{release}NONPAE.%{_target_cpu}/weak-updates
%ifarch %{vdso_arches}
/lib/modules/%{version}-%{release}NONPAE.%{_target_cpu}/vdso
/etc/ld.so.conf.d/kernel-%{version}-%{release}NONPAE.%{_target_cpu}.conf
%endif
/lib/modules/%{version}-%{release}NONPAE.%{_target_cpu}/modules.*
%if %{with_dracut}
%ghost /boot/initramfs-%{version}-%{release}NONPAE.%{_target_cpu}.img
%else
%ghost /boot/initrd-%{version}-%{release}NONPAE.%{_target_cpu}.img
%endif

%files NONPAE-devel
%defattr(-,root,root)
%dir /usr/src/kernels
/usr/src/kernels/%{version}-%{release}NONPAE.%{_target_cpu}
%endif

%if %{with_doc}
%files doc
%defattr(-,root,root)
%{_datadir}/doc/%{name}-doc-%{version}/Documentation/*
%dir %{_datadir}/doc/%{name}-doc-%{version}/Documentation
%dir %{_datadir}/doc/%{name}-doc-%{version}
%{_datadir}/man/man9/*
%endif

%if %{with_headers}
%files headers
%defattr(-,root,root)
/usr/include/*
%endif

%if %{with_firmware}
%files firmware
%defattr(-,root,root)
/lib/firmware/*
%doc linux-%{version}-%{release}.%{_target_cpu}/firmware/WHENCE
%endif

%if %{with_perf}
%files -n perf
%defattr(-,root,root)
/etc/bash_completion.d/perf
%{_bindir}/perf
%{_bindir}/trace
%{_libdir}/libperf-gtk.so
%dir %{_libdir}/traceevent/plugins
%{_libdir}/traceevent/plugins/*
%dir %{_libexecdir}/perf-core
%{_libexecdir}/perf-core/*
%{_mandir}/man[1-8]/*
/usr/share/doc/perf-tip/tips.txt
/usr/share/perf-core/strace/groups/file
%endif

%changelog
* Tue Oct 10 2017 Johnny Hughes <johnny@centos.org> 4.9.54-29
- Upgraded to upstream 4.9.54

* Fri Sep  8 2017 Johnny Hughes <johnny@centos.org> 4.9.48-29
- Upgraded to upstream 4.9.48
- Added Destroy-ldisc-instance-hangup.patch
- Remove XSA-229 patch (rolled in upstream)
 
* Wed Aug 23 2017 Kevin Stange <kevin@steadfast.net> 4.9.44-29
- Upgraded to upstream 4.9.44
- Remove patch 10005, rolled in upstream
- Apply XSA-229

* Fri Jul 21 2017 Johnny Hughes <johnny@centos.org> 4.9.39-29
- Upgraded to upstream 4.9.39
- Switch from CONFIG_SLUB to CONFIG_SLAB to resolve some xen hypervisor
  related memory errors.

* Thu Jul 13 2017 Johnny Hughes <johnny@centos.org> 4.9.37-29
- Upgraded to upstream 4.9.37
- Remove patch 10004, rolled in upstream
- Modified x86_64 config to disable CONFIG_IO_STRICT_DEVMEM as it is
  causing issues with some iscsi configs

* Tue Jun 27 2017 Jean-Louis Dupond <jean-louis@dupond.be> 4.9.34-29
- Add xen-netback patch to fix lockup with rate-limiting

* Sun Jun 25 2017 Johnny Hughes <johnny@centos.org> 4.9.34-28
- Upgraded to upstream 4.9.34

* Thu Jun 15 2017 Sarah Newman <srn@prgmr.com> 4.9.31-28
- Add debuginfo package
- Enable additional features during with-perf
- Apply XSA-216
- Disable 'xen-nested-dom0-fix', already applied

* Wed Jun  7 2017 Johnny Hughes <johnny@centos.org> 4.9.31-27
- Upgraded to LTS 4.9.31, removed patch 10003 as it is now
  in the upstream kernel.

* Wed May  3 2017 Johnny Hughes <johnny@centos.org> 4.9.25-27
- Upgraded to LTS 4.9.25, removed patch 10002 as it is now 
  in the upstream kernel.

* Tue Apr 18 2017 Johnny Hughes <johnny@centos.org> 4.9.23-26
- upgrade to upstream 4.9.23 LTS

* Tue Apr  4 2017 Johnny Hughes <johnny@centos.org> 4.9.20-26
- modified NETFILTER and BRIDGE configs using fedora kernel

* Fri Mar 31 2017 Johnny Hughes <johnny@centos.org> 4.9.20-25
- upgraded to the upstream 4.9.20 LTS kernel

* Wed Mar 15 2017 Johnny Hughes <johnny@centos.org> 4.9.15-22
- Upgrade to upstream LTS 4.9.15 kernel

* Mon Feb 20 2017 Johnny Hughes <johnny@centos.org> 4.9.13-22
- rebase to upstream LTS 4.9.13 kernel, add back in blktap2 support
 
* Sun Feb 19 2017 Johnny Hughes <johnny@centos.org>  4.4.50-21
- upgrade to upstream LTS 4.4.50 kernel
- remove blktap2 support

* Tue Oct 25 2016 Johnny Hughes <johnny@centos.org>  3.18.44-20
- Upgrade to upstream 3.18.44
- CVE-2016-5195 (Dirty COW) fix 

* Wed Sep  7 2016 Johnny Hughes <johnny@centos.org> 3.18.41-20
- Upgrade to upstream 3.18.41
- Remove patch 10016 (rolled in upstream)

* Tue Aug 23 2016 Johnny Hughes <johnny@centos.org> 3.18.40-20 
- upgrade to upstream 3.18.40 kernel
- CVE-2016-5696 patch (Patch10016)

* Mon Aug 01 2016 Johnny Hughes <johnny@centos.org> 3.18.38-20
- upgrade to upstream 3.18.38 kernel

* Thu Jul 28 2016 Johnny Hughes <johnny@centos.org> 3.18.37-20
- upgrade to upstream 3.18.37 kernel

* Fri May 27 2016 Johnny Hughes <johnny@centos.org> 3.18.34-20
- upgrade to upstream 3.18.34 kernel
- Removed patch for XSA-174, rolled in upstream

* Mon May 09 2016 Johnny Hughes <johnny@centos.org> 3.18.32-20
- Upgrade to upstream kernel 3.18.32
- Removed patch for XSA-171, rolled in upstream

* Thu Apr 14 2016 Johnny Hughes <johnny@centos.org> 3.18.30-20
- Upgrade to upstream kernel 3.18.30
- Remove patches 10011, 10013, 10016, 10017 as they are upstream

* Tue Apr 12 2016 George Dunlap <george.dunlap@citrix.com> 3.18.25-20
- Roll in fix for XSA-174

* Tue Mar 15 2016 George Dunlap <george.dunlap@citrix.com> 3.18.25-19
- Refactor
- Roll in fix for XSA-171

* Tue Jan 19 2016 Johnny Hughes <johnny@centos.org> 3.18.25-18
- Roll in fix for CVE-2016-0728 (Patch200)

* Tue Jan 19 2016 Johnny Hughes <johnny@centos.org> 3.18.25-17
- upgrade to upstream 3.18.25 kernel

* Tue Dec 08 2015 Sarah Newman <srn@prgmr.com> - 3.18.21-17
- import XSAs 155 and 157

* Fri Sep 25 2015 Johnny Hughes <johnny@centos.org> - 3.18.21-16
- use linux-firmware from centos-7 kernel

* Wed Sep 23 2015 Johnny Hughes <johnny@centos.org> - 3.18.21-13
- upgrade to upstream 3.18.21

* Mon Jul  6 2015 Johnny Hughes <johnny@centos.org> - 3.18.17-13
- uprgade to upstream 3.18.17
- modified config-i686 and config-x86_64 to add new devices
- modified bn2x and bnx2x firmware to latest
 
* Tue Jun  9 2015 George Dunlap <george.dunlap@eu.citrix.com> - 3.18.12-12
- Replace /sbin with %{ksbindir} for C7 compatibility

* Tue May  5 2015 Johnny Hughes <johnny@centos.org> - 3.18.12-11
- Rebase on LTS kernel 3.18.12
- Modify patch 118, 119, 120 to work with 3.18.12

* Fri Feb  6 2015 Johnny Hughes <johnny@centos.org> - 3.10.68-11
- Upgrade to upstream 3.10.68
- Addresses CVE-2014-8134, CVE-2014-8989, CVE-2014-9529

* Tue Jan  6 2015 Johnny Hughes <johnny@centos.org> - 3.10.63-11
- Upgrade to upstream 3.10.63

* Thu Oct  9 2014 Johnny Hughes <johnny@centos.org> - 3.10.56-11
- upgraded to upstream 3.10.56
- added a grub-bootxen.sh to posttrans to autoinstall xen kernel

* Fri Sep 26 2014 Johnny Hughes <johnny@centos.org> - 3.10.55-11
- upgraded to upstream 3.10.55

* Mon Jun 16 2014 Johnny Hughes <johnny@centos.org> - 3.10.43-11
- upgraded to upstream 3.10.43
- addresses CVE-2014-0155, CVE-2014-0196, CVE-2014-1739, and CVE-2014-3153.

* Mon May  5 2014 Johnny Hughes <johnny@centos.org> - 3.10.38-11
- upgraded to upstream 3.10.38
- addresses CVE-2014-0055 and CVE-2014-0077

* Wed Mar 26 2014 Johnny Hughes <johnny@centos.org> - 3.10.34-11
- upgrade to upstream 3.10.34
- addresses CVE-2014-0049 and CVE-2014-0069

* Sun Feb 23 2014 Johnny Hughes <johnny@centos.org> - 3.10.32-11
- upgrade to upstream 3.10.32

* Tue Feb 11 2014 Johnny Hughes <johnny@centos.org> - 3.10.29-11
- upgrade to upstream 3.10.29
- addresses CVE-2014-0038 and CVE-2013-6885

* Fri Jan 24 2014 Johnny Hughes <johnny@centos.org> 3.10.27-11
- upgrade to upstream 3.10.27
- addresses CVE-2013-4579

* Fri Dec 27 2013 Johnny Hughes <johnny@centos.org> 3.10.25-11
- addresses CVE-2013-4587, CVE-2013-6367, CVE-2013-6368, CVE-2013-6376

* Tue Dec 10 2013 Johnny Hughes <johnny@centos.org> 3.10.23-11
- upgrade to upstream 3.10.23

* Sat Nov 23 2013 Johnny Hughes <johnny@centos.org> 3.10.20-11
- modified patch patch130 to add all bnx2 drivers

* Sat Nov 23 2013 Johnny Hughes <johnny@centos.org> 3.10.20-10
- upgraded to upstream version 3.10.20
- removed sources 4, 5, 6, and 7 to instead roll in all bnx2 and bnx2x firmware files
  instead of doing them individually
- created sources 8 and 9 that are tarballs of the latest bnx2 and bnx2x firmware files
  from kernel.org
- modified to spec file to extract sources 8 and 9 and build all fw files in bnx2 and bnx2x dirs

* Wed Nov 13 2013 Johnny Hughes <johnny@centos.org> 3.10.18-10
- upgraded to upstream version 3.10.18
- modified/enabled patch130 to work with the 3.10.x tree (new broadcom drivers)

* Tue Nov 12 2013 Johnny Hughes <johnny@centos.org> 3.10.12-10
- Move to the 3.10.12 LTS Kernel
- add /etc/bash_completion.d/perf to the kernel-perf package
- removed all patches except 118 and 119 to add blktap25 as they are upstream
- modified patches 118 and 119 to apply to the 3.10.x kernel tree

* Wed Sep 11 2013 Johnny Hughes <johnny@centos.org> 3.4.61-9
- upgrade to upstream 3.4.61
- added patch 133 to build docs/noarch (centos bug 6654) 

* Fri Aug 30 2013 Johnny Hughes <johnny@centos.org> 3.4.60-9
- upgrade top upstream 3.4.60

* Sat Aug 24 2013 Johnny Hughes <johnny@centos.org> 3.4.59-9
- fix issue with Source6 (centos bug 6609)

* Thu Aug 22 2013 Johnny Hughes <johnny@centos.org> 3.4.59-8
- upgraded to upstream 3.4.59
- added Source6 to fix a firmware issue (centos bug 6609)
- modified the x86_64 and i386 config files (centos bug 6619)

* Tue Aug 13 2013 Johnny Hughes <johnny@centos.org> 3.4.57-8
- upgraded to upstream 3.4.57
- removed patch 131 as it was rolled in upstream

* Mon Jul 22 2013 Johnny Hughes <johnny@centos.org> 3.4.54-8
- upgraded to upstream version 3.4.54
- Turned on CONFIG_XEN_BALLOON_MEMORY_HOTPLUG
  in this kernel (centos bug 6561)
- added patch 131 and patch 132 per centos bug 6570 
 
* Wed Jul 17 2013 Johnny Hughes <johnny@centos.org> 3.4.53-8
- upgraded to upstream version 3.4.53

* Thu Jun 20 2013 Johnny Hughes <johnny@centos.org> 3.4.50-8
- upgraded to upstream version 3.4.50
- removed patch 125 as it is now rolled into the upstream kernel
- added Source5 and updated Patch130 to fix CentOS bug #6513

* Tue May 21 2013 Johnny Hughes <johnny@centos.org> 3.4.46-8
- fix centos bug #6460 with Source4 and Patch130

* Mon May 20 2013 Johnny Hughes <johnny@centos.org> 3.4.46-7
- upgraded to upstream version 3.4.46

* Tue Apr 30 2013 Johnny Hughes <johnny@centos.org> 3.4.42-7
- upgrage to upstream kernel 3.4.42
- Added patches 123 through 129

* Wed Apr 17 2013 Johnny Hughes <johnny@centos.org> - 3.4.41-6
- upgrade to upstream kernel 3.4.41

* Tue Apr  2 2013 Johnny Hughes <johnny@centos.org> - 3.4.38-6
- upgraded to upstream kernel 3.4.38

* Fri Mar 15 2013 Johnny Hughes <johnny@centos.org> - 3.4.36-6
- upgraded to upstream kernel 3.4.36
- switched from tar.bz2 to tar.xz source file 

* Tue Feb 19 2013 Johnny Hughes <johnny@centos.org> - 3.4.32-6
- upgraded to upstream kernel 3.4.32
- fixes CVE-2013-0871 and CVE-2013-0228

* Fri Feb 15 2013 Johnny Hughes <johnny@centos.org> - 3.4.31-6
- upgraded to upstream kernel 3.4.31
 
* Mon Jan 28 2013 Johnny Hughes <johnny@centos.org> - 3.4.28-6
- removed Patch 120, it is rolled into the kernel as part of 3.4.27
- added Patch 122
- disabled CONFIG_XEN_BALLOON_MEMORY_HOTPLUG in the i686 and x86_64 configs 

* Tue Jan 22 2013 Johnny Hughes <johnny@centos.org> - 3.4.26-6
- made kernel require kernel-firmware >= its own version.

* Mon Jan 21 2013 Johnny Hughes <johnny@centos.org> - 3.4.26-5
- Rolled in patches: Patch118-Patch121
- CVE-2013-0190 is corrected in Patch120
- Rolled in blktap2.5 suppport (patches 118 and 119)

* Thu Jan 17 2013 Johnny Hughes <johnny@centos.org> - 3.4.26-4
- upgraded to upstream kernel 3.4.26

* Mon Jan 14 2013 Johnny Hughes <johnny@centos.org> - 3.4.25-4
- upgraded to upstream kernel 3.4.25

* Thu Jan  3 2013 Johnny Hughes <johnny@centos.org> - 3.4.24-4
- changed how patches area applied, from w/in the actual kernel directory

* Thu Jan  3 2013 Johnny Hughes <johnny@centos.org> - 3.4.24-3
- rolled in the following patches: Patch100-Patch117
  see the individual patches for the xen.org git paths and patch details

* Thu Dec 27 2012 Johnny Hughes <johnny@centos.org> - 3.4.24-2
- downgraded to the latest LTSI kernel, 3.4.24
- Remove the NONPAE kernel for i686

* Fri Nov 30 2012 Karanbir Singh <kbsingh@centos.org> - 3.6.8-2.1.el6.centos
- import into CentOS buildsystems

* Wed Nov 28 2012 Johnny Hughes <johnny@centos.org> 
- disable XEN_SELFBALLOONING
- remove the NoSource option for the kernel tarball.

* Wed Nov 28 2012 Johnny Hughes <johnny@centos.org>
- started with the 3.6.x kernel SOURCE RPM from http://elrepo.org/
