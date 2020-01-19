#%%global prerelease rc
#%%global prereleasenum 1

%global prerel1 %{?prerelease:.%{prerelease}%{prereleasenum}}
%global prerel2 %{?prerelease:-%{prerelease}.%{prereleasenum}}

Summary: A dynamic adaptive system tuning daemon
Name: tuned
Version: 2.10.0
Release: 6%{?prerel1}%{?dist}.4
License: GPLv2+
Source: https://github.com/redhat-performance/%{name}/archive/v%{version}%{?prerel2}.tar.gz#/%{name}-%{version}%{?prerel2}.tar.gz
URL: http://www.tuned-project.org/
BuildArch: noarch
BuildRequires: python, systemd, desktop-file-utils
Requires(post): systemd, virt-what
Requires(preun): systemd
Requires(postun): systemd
Requires: python-decorator, dbus-python, pygobject3-base, python-pyudev
# kernel-tools, hdparm dependencies are not met on s390
Requires: virt-what, python-configobj, ethtool, gawk
Requires: util-linux, python-perf, dbus, polkit, python-linux-procfs
Requires: python-schedutils
Patch0: tuned-2.10.0-gtk-3.8.patch
Patch1: tuned-2.10.0-use-online-cpus.patch
Patch2: tuned-2.10.0-realtime-virtual-enable-rt-entsk.patch
Patch3: tuned-2.10.0-disable-ksm-once.patch
Patch4: tuned-2.10.0-update-kvm-modprobe-file.patch
Patch5: tuned-2.10.0-realtime-virtual-host-pin-only-vcpu-thread-to-isolated-pcpu.patch

%description
The tuned package contains a daemon that tunes system settings dynamically.
It does so by monitoring the usage of several system components periodically.
Based on that information components will then be put into lower or higher
power saving modes to adapt to the current usage. Currently only ethernet
network and ATA harddisk devices are implemented.

%if 0%{?rhel} <= 7 && 0%{!?fedora:1}
# RHEL <= 7
%global docdir %{_docdir}/%{name}-%{version}
%else
# RHEL > 7 || fedora
%global docdir %{_docdir}/%{name}
%endif

%package gtk
Summary: GTK GUI for tuned
Requires: %{name} = %{version}-%{release}
Requires: powertop, pygobject3-base, polkit

%description gtk
GTK GUI that can control tuned and provides simple profile editor.

%package utils
Requires: %{name} = %{version}-%{release}
Requires: powertop
Summary: Various tuned utilities

%description utils
This package contains utilities that can help you to fine tune and
debug your system and manage tuned profiles.

%package utils-systemtap
Summary: Disk and net statistic monitoring systemtap scripts
Requires: %{name} = %{version}-%{release}
Requires: systemtap

%description utils-systemtap
This package contains several systemtap scripts to allow detailed
manual monitoring of the system. Instead of the typical IO/sec it collects
minimal, maximal and average time between operations to be able to
identify applications that behave power inefficient (many small operations
instead of fewer large ones).

%package profiles-sap
Summary: Additional tuned profile(s) targeted to SAP NetWeaver loads
Requires: %{name} = %{version}

%description profiles-sap
Additional tuned profile(s) targeted to SAP NetWeaver loads.

%package profiles-mssql
Summary: Additional tuned profile(s) for MS SQL Server
Requires: %{name} = %{version}

%description profiles-mssql
Additional tuned profile(s) for MS SQL Server.

%package profiles-oracle
Summary: Additional tuned profile(s) targeted to Oracle loads
Requires: %{name} = %{version}

%description profiles-oracle
Additional tuned profile(s) targeted to Oracle loads.

%package profiles-sap-hana
Summary: Additional tuned profile(s) targeted to SAP HANA loads
Requires: %{name} = %{version}

%description profiles-sap-hana
Additional tuned profile(s) targeted to SAP HANA loads.

%package profiles-atomic
Summary: Additional tuned profile(s) targeted to Atomic
Requires: %{name} = %{version}

%description profiles-atomic
Additional tuned profile(s) targeted to Atomic host and guest.

%package profiles-realtime
Summary: Additional tuned profile(s) targeted to realtime
Requires: %{name} = %{version}
Requires: tuna

%description profiles-realtime
Additional tuned profile(s) targeted to realtime.

%package profiles-nfv-guest
Summary: Additional tuned profile(s) targeted to Network Function Virtualization (NFV) guest
Requires: %{name} = %{version}
Requires: %{name}-profiles-realtime = %{version}
Requires: tuna

%description profiles-nfv-guest
Additional tuned profile(s) targeted to Network Function Virtualization (NFV) guest.

%package profiles-nfv-host
Summary: Additional tuned profile(s) targeted to Network Function Virtualization (NFV) host
Requires: %{name} = %{version}
Requires: %{name}-profiles-realtime = %{version}
Requires: tuna, qemu-kvm-tools-rhev

%description profiles-nfv-host
Additional tuned profile(s) targeted to Network Function Virtualization (NFV) host.

# this is kept for backward compatibility, it should be dropped for RHEL-8
%package profiles-nfv
Summary: Additional tuned profile(s) targeted to Network Function Virtualization (NFV)
Requires: %{name} = %{version}
Requires: %{name}-profiles-nfv-guest = %{version}
Requires: %{name}-profiles-nfv-host = %{version}

%description profiles-nfv
Additional tuned profile(s) targeted to Network Function Virtualization (NFV).

%package profiles-cpu-partitioning
Summary: Additional tuned profile(s) optimized for CPU partitioning
Requires: %{name} = %{version}

%description profiles-cpu-partitioning
Additional tuned profile(s) optimized for CPU partitioning.

%package profiles-compat
Summary: Additional tuned profiles mainly for backward compatibility with tuned 1.0
Requires: %{name} = %{version}

%description profiles-compat
Additional tuned profiles mainly for backward compatibility with tuned 1.0.
It can be also used to fine tune your system for specific scenarios.

%prep
%setup -q -n %{name}-%{version}%{?prerel2}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1

# workaround for https://bugzilla.redhat.com/show_bug.cgi?id=1626473
chmod 0755 profiles/realtime-virtual-guest/script.sh

%build


%install
make install DESTDIR=%{buildroot} DOCDIR=%{docdir} PYTHON=python2
%if 0%{?rhel}
sed -i 's/\(dynamic_tuning[ \t]*=[ \t]*\).*/\10/' %{buildroot}%{_sysconfdir}/tuned/tuned-main.conf
%endif

# conditional support for grub2, grub2 is not available on all architectures
# and tuned is noarch package, thus the following hack is needed
mkdir -p %{buildroot}%{_datadir}/tuned/grub2
mv %{buildroot}%{_sysconfdir}/grub.d/00_tuned %{buildroot}%{_datadir}/tuned/grub2/00_tuned
rmdir %{buildroot}%{_sysconfdir}/grub.d

# ghost for persistent storage
mkdir -p %{buildroot}%{_var}/lib/tuned

# ghost for NFV
mkdir -p %{buildroot}%{_sysconfdir}/modprobe.d
touch %{buildroot}%{_sysconfdir}/modprobe.d/kvm.rt.tuned.conf

# validate desktop file
desktop-file-validate %{buildroot}%{_datadir}/applications/tuned-gui.desktop

mkdir -p %{buildroot}%{_sysconfdir}/tuned/recommend.d

%post
%systemd_post tuned.service

# convert active_profile from full path to name (if needed)
sed -i 's|.*/\([^/]\+\)/[^\.]\+\.conf|\1|' /etc/tuned/active_profile

# convert GRUB_CMDLINE_LINUX to GRUB_CMDLINE_LINUX_DEFAULT
if [ -r "%{_sysconfdir}/default/grub" ]; then
  sed -i 's/GRUB_CMDLINE_LINUX="$GRUB_CMDLINE_LINUX \\$tuned_params"/GRUB_CMDLINE_LINUX_DEFAULT="$GRUB_CMDLINE_LINUX_DEFAULT \\$tuned_params"/' \
    %{_sysconfdir}/default/grub
fi


%preun
%systemd_preun tuned.service
if [ "$1" == 0 ]; then
# clear persistent storage
  rm -f %{_var}/lib/tuned/*
# clear temporal storage
  rm -f /run/tuned/*
fi


%postun
%systemd_postun_with_restart tuned.service

# conditional support for grub2, grub2 is not available on all architectures
# and tuned is noarch package, thus the following hack is needed
if [ "$1" == 0 ]; then
  rm -f %{_sysconfdir}/grub.d/00_tuned || :
# unpatch /etc/default/grub
  if [ -r "%{_sysconfdir}/default/grub" ]; then
    sed -i '/GRUB_CMDLINE_LINUX_DEFAULT="${GRUB_CMDLINE_LINUX_DEFAULT:+$GRUB_CMDLINE_LINUX_DEFAULT }\\$tuned_params"/d' %{_sysconfdir}/default/grub
  fi
fi


%triggerun -- tuned < 2.0-0
# remove ktune from old tuned, now part of tuned
/usr/sbin/service ktune stop &>/dev/null || :
/usr/sbin/chkconfig --del ktune &>/dev/null || :


%posttrans
# conditional support for grub2, grub2 is not available on all architectures
# and tuned is noarch package, thus the following hack is needed
if [ -d %{_sysconfdir}/grub.d ]; then
  cp -a %{_datadir}/tuned/grub2/00_tuned %{_sysconfdir}/grub.d/00_tuned
  selinuxenabled &>/dev/null && \
    restorecon %{_sysconfdir}/grub.d/00_tuned &>/dev/null || :
fi


%post gtk
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :


%postun gtk
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache -f %{_datadir}/icons/hicolor &>/dev/null || :
fi


%posttrans gtk
/usr/bin/gtk-update-icon-cache -f %{_datadir}/icons/hicolor &>/dev/null || :


%files
%defattr(-,root,root,-)
%exclude %{docdir}/README.utils
%exclude %{docdir}/README.scomes
%exclude %{docdir}/README.NFV
%doc %{docdir}
%{_datadir}/bash-completion/completions/tuned-adm
%exclude %{python_sitelib}/tuned/gtk
%{python_sitelib}/tuned
%{_sbindir}/tuned
%{_sbindir}/tuned-adm
%exclude %{_sysconfdir}/tuned/realtime-variables.conf
%exclude %{_sysconfdir}/tuned/realtime-virtual-guest-variables.conf
%exclude %{_sysconfdir}/tuned/realtime-virtual-host-variables.conf
%exclude %{_sysconfdir}/tuned/cpu-partitioning-variables.conf
%exclude %{_sysconfdir}/tuned/sap-hana-vmware-variables.conf
%exclude %{_prefix}/lib/tuned/default
%exclude %{_prefix}/lib/tuned/desktop-powersave
%exclude %{_prefix}/lib/tuned/laptop-ac-powersave
%exclude %{_prefix}/lib/tuned/server-powersave
%exclude %{_prefix}/lib/tuned/laptop-battery-powersave
%exclude %{_prefix}/lib/tuned/enterprise-storage
%exclude %{_prefix}/lib/tuned/spindown-disk
%exclude %{_prefix}/lib/tuned/sap-netweaver
%exclude %{_prefix}/lib/tuned/sap-hana
%exclude %{_prefix}/lib/tuned/sap-hana-vmware
%exclude %{_prefix}/lib/tuned/mssql
%exclude %{_prefix}/lib/tuned/oracle
%exclude %{_prefix}/lib/tuned/atomic-host
%exclude %{_prefix}/lib/tuned/atomic-guest
%exclude %{_prefix}/lib/tuned/realtime
%exclude %{_prefix}/lib/tuned/realtime-virtual-guest
%exclude %{_prefix}/lib/tuned/realtime-virtual-host
%exclude %{_prefix}/lib/tuned/cpu-partitioning
%{_prefix}/lib/tuned
%dir %{_sysconfdir}/tuned
%dir %{_sysconfdir}/tuned/recommend.d
%dir %{_libexecdir}/tuned
%{_libexecdir}/tuned/defirqaffinity*
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/tuned/active_profile
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/tuned/profile_mode
%config(noreplace) %{_sysconfdir}/tuned/tuned-main.conf
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/tuned/bootcmdline
%{_sysconfdir}/dbus-1/system.d/com.redhat.tuned.conf
%verify(not size mtime md5) %{_sysconfdir}/modprobe.d/tuned.conf
%{_tmpfilesdir}/tuned.conf
%{_unitdir}/tuned.service
%dir %{_localstatedir}/log/tuned
%dir /run/tuned
%dir %{_var}/lib/tuned
%{_mandir}/man5/tuned*
%{_mandir}/man7/tuned-profiles.7*
%{_mandir}/man8/tuned*
%dir %{_datadir}/tuned
%{_datadir}/tuned/grub2
%{_datadir}/polkit-1/actions/com.redhat.tuned.policy
%ghost %{_sysconfdir}/modprobe.d/kvm.rt.tuned.conf

%files gtk
%defattr(-,root,root,-)
%{_sbindir}/tuned-gui
%{python_sitelib}/tuned/gtk
%{_datadir}/tuned/ui
%{_datadir}/polkit-1/actions/com.redhat.tuned.gui.policy
%{_datadir}/icons/hicolor/scalable/apps/tuned.svg
%{_datadir}/applications/tuned-gui.desktop

%files utils
%doc COPYING
%{_bindir}/powertop2tuned
%{_libexecdir}/tuned/pmqos-static*

%files utils-systemtap
%defattr(-,root,root,-)
%doc doc/README.utils
%doc doc/README.scomes
%doc COPYING
%{_sbindir}/varnetload
%{_sbindir}/netdevstat
%{_sbindir}/diskdevstat
%{_sbindir}/scomes
%{_mandir}/man8/varnetload.*
%{_mandir}/man8/netdevstat.*
%{_mandir}/man8/diskdevstat.*
%{_mandir}/man8/scomes.*

%files profiles-sap
%defattr(-,root,root,-)
%{_prefix}/lib/tuned/sap-netweaver
%{_mandir}/man7/tuned-profiles-sap.7*

%files profiles-sap-hana
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/tuned/sap-hana-vmware-variables.conf
%{_prefix}/lib/tuned/sap-hana
%{_prefix}/lib/tuned/sap-hana-vmware
%{_mandir}/man7/tuned-profiles-sap-hana.7*

%files profiles-mssql
%defattr(-,root,root,-)
%{_prefix}/lib/tuned/mssql
%{_mandir}/man7/tuned-profiles-mssql.7*

%files profiles-oracle
%defattr(-,root,root,-)
%{_prefix}/lib/tuned/oracle
%{_mandir}/man7/tuned-profiles-oracle.7*

%files profiles-atomic
%defattr(-,root,root,-)
%{_prefix}/lib/tuned/atomic-host
%{_prefix}/lib/tuned/atomic-guest
%{_mandir}/man7/tuned-profiles-atomic.7*

%files profiles-realtime
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/tuned/realtime-variables.conf
%{_prefix}/lib/tuned/realtime
%{_mandir}/man7/tuned-profiles-realtime.7*

%files profiles-nfv-guest
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/tuned/realtime-virtual-guest-variables.conf
%{_prefix}/lib/tuned/realtime-virtual-guest
%{_mandir}/man7/tuned-profiles-nfv-guest.7*

%files profiles-nfv-host
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/tuned/realtime-virtual-host-variables.conf
%{_prefix}/lib/tuned/realtime-virtual-host
%{_mandir}/man7/tuned-profiles-nfv-host.7*

%files profiles-nfv
%defattr(-,root,root,-)
%doc %{docdir}/README.NFV

%files profiles-cpu-partitioning
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/tuned/cpu-partitioning-variables.conf
%{_prefix}/lib/tuned/cpu-partitioning
%{_mandir}/man7/tuned-profiles-cpu-partitioning.7*

%files profiles-compat
%defattr(-,root,root,-)
%{_prefix}/lib/tuned/default
%{_prefix}/lib/tuned/desktop-powersave
%{_prefix}/lib/tuned/laptop-ac-powersave
%{_prefix}/lib/tuned/server-powersave
%{_prefix}/lib/tuned/laptop-battery-powersave
%{_prefix}/lib/tuned/enterprise-storage
%{_prefix}/lib/tuned/spindown-disk
%{_mandir}/man7/tuned-profiles-compat.7*

%changelog
* Wed Jul 10 2019 Jaroslav Škarvada <jskarvad@redhat.com> - 2.10.0-6.4
- realtime-virtual-host: pin only the vcpu thread to isolated pcpu
  Resolves: rhbz#1728699

* Tue Nov 27 2018 Jaroslav Škarvada <jskarvad@redhat.com> - 2.10.0-6.3
- Reworked setup_kvm_mod_low_latency to count with kernel changes
  Resolves: rhbz#1653767

* Tue Nov 27 2018 Jaroslav Škarvada <jskarvad@redhat.com> - 2.10.0-6.2
- Updated disable-ksm-once patch
  Related: rhbz#1652822

* Fri Nov 23 2018 Jaroslav Škarvada <jskarvad@redhat.com> - 2.10.0-6.1
- Disable ksm once, re-enable it on full rollback
  Resolves: rhbz#1652822

* Fri Sep  7 2018 Jaroslav Škarvada <jskarvad@redhat.com> - 2.10.0-6
- Added workaround for rpmbuild bug 1626473
  related: rhbz#1616043

* Thu Sep  6 2018 Jaroslav Škarvada <jskarvad@redhat.com> - 2.10.0-5
- Fixed realtime-virtual-guest profile to call script.sh
  related: rhbz#1616043

* Wed Sep  5 2018 Jaroslav Škarvada <jskarvad@redhat.com> - 2.10.0-4
- De-fuzzified realtime-virtual-enable-rt-entsk patch
  related: rhbz#1616043

* Wed Sep  5 2018 Jaroslav Škarvada <jskarvad@redhat.com> - 2.10.0-3
- realtime-virtual-guest/host: start/stop rt-entsk daemon on
  initialization/shutdown
  resolves: rhbz#1616043

* Tue Aug  7 2018 Jaroslav Škarvada <jskarvad@redhat.com> - 2.10.0-2
- use online CPUs for cpusets calculations instead of present CPUs
  resolves: rhbz#1613478

* Wed Jul  4 2018 Jaroslav Škarvada <jskarvad@redhat.com> - 2.10.0-1
- new release
  - rebased tuned to latest upstream
    related: rhbz#1546598
  - IRQ affinity handled by scheduler plugin
    resolves: rhbz#1590937

* Mon Jun 11 2018 Jaroslav Škarvada <jskarvad@redhat.com> - 2.10.0-0.1.rc1
- new release
  - rebased tuned to latest upstream
    resolves: rhbz#1546598
  - script: show stderr output in the log
  - realtime-virtual-host: script.sh: add error checking
  - man: improved tuned-profiles-cpu-partitioning.7
  - bootloader: check if grub2_cfg_file_name is None in _remove_grub2_tuning()
  - plugin_scheduler: whitelist/blacklist processed also for thread names
  - bootloader: patch all GRUB2 config files
  - profiles: added mssql profile
  - tuned-adm: print log excerpt when changing profile
  - cpu-partitioning: use no_balance_cores instead of no_rebalance_cores
  - sysctl: support assignment modifiers as other plugins do
  - oracle: fixed ip_local_port_range parity warning
    resolves: rhbz#1527219
  - Fix verifying cpumask on systems with more than 32 cores
    resolves: rhbz#1528368
  - oracle: updated the profile to be in sync with KCS 39188
    resolves: rhbz#1447323

* Sun Oct 29 2017 Jaroslav Škarvada <jskarvad@redhat.com> - 2.9.0-1
- new release
  - rebased tuned to latest upstream
    related: rhbz#1467576

* Fri Oct 20 2017 Jaroslav Škarvada <jskarvad@redhat.com> - 2.9.0-0.2.rc2
- new release
  - rebased tuned to latest upstream
    related: rhbz#1467576
  - fixed expansion of the variables in the 'devices' section
    related: rhbz#1490399
  - cpu-partitioning: add no_rebalance_cores= option
    resolves: rhbz#1497182

* Thu Oct 12 2017 Jaroslav Škarvada <jskarvad@redhat.com> - 2.9.0-0.1.rc1
- new release
  - rebased tuned to latest upstream
    resolves: rhbz#1467576
  - added recommend.d functionality
    resolves: rhbz#1459146
  - recommend: added support for matching of processes
    resolves: rhbz#1461838
  - cpu-partitioning: used tuned instead of tuna for cores isolation
    resolves: rhbz#1442229
  - bootloader: splitted string for removal from cmdline
    resolves: rhbz#1461279
  - network-latency: added skew_tick=1 kernel command line parameter
    resolves: rhbz#1451073
  - bootloader: accepted only certain values for initrd_remove_dir
    resolves: rhbz#1455161
  - increased udev monitor buffer size, made it configurable
    resolves: rhbz#1442306
  - bootloader: don't add nonexistent overlay image to grub.cfg
    resolves: rhbz#1454340
  - plugin_cpu: don't log error in execute() if EPB is not supported
    resolves: rhbz#1443182
  - sap-hana: fixed description of the sap-hana profiles
    resolves: rhbz#1482005
  - plugin_systemd: on full_rollback notify about need of initrd regeneration
    resolves: rhbz#1469258
  - don't log errors about missing files on verify with ignore_missing set
    resolves: rhbz#1451435
  - plugin_scheduler: improved logging
    resolves: rhbz#1474961
  - improved checking if we are rebooting or not
    resolves: rhbz#1475571
  - started dbus exports after a profile is applied
    resolves: rhbz#1443142
  - sap-hana: changed force_latency to 70
    resolves: rhbz#1501252
  - plugin_video: added support for the 'dpm' power method
  - list available profiles on 'tuned-adm profile'

* Mon Jun 12 2017 Jaroslav Škarvada <jskarvad@redhat.com> - 2.8.0-5
- realtime: re-assigned kernel thread priorities
  resolves: rhbz#1452357

* Tue Jun  6 2017 Jaroslav Škarvada <jskarvad@redhat.com> - 2.8.0-4
- added skew_tick=1 to realtime and simplified bootcmdline inheritance
  resolves: rhbz#1447938

* Fri May  5 2017 Jaroslav Škarvada <jskarvad@redhat.com> - 2.8.0-3
- added workaround for old pyudev
  related: rhbz#1251240

* Thu Apr 13 2017 Jaroslav Škarvada <jskarvad@redhat.com> - 2.8.0-2
- respin
  related: rhbz#1388454
- systemd: added support for older systemd CPUAffinity syntax
  resolves: rhbz#1441791
- scheduler: added workarounds for low level exceptions from
  python-linux-procfs
  resolves: rhbz#1441792
- bootloader: workaround for adding tuned_initrd to new kernels on restart
  resolves: rhbz#1441797
- cpu-partitioning: use tuna for cores isolation
  related: rhbz#1403309

* Fri Apr  7 2017 Jaroslav Škarvada <jskarvad@redhat.com> - 2.8.0-1
- new release
  - rebase tuned to latest upstream
    resolves: rhbz#1388454
  - cpu-partitioning: enabled timer migration
    resolves: rhbz#1408308
  - cpu-partitioning: disabled kvmclock sync and ple
    resolves: rhbz#1395855
  - spec: muted error if there is no selinux support
    resolves: rhbz#1404214
  - units: implemented instance priority
    resolves: rhbz#1246172
  - bootloader: added support for initrd overlays
    resolves: rhbz#1414098
  - cpu-partitioning: set CPUAffinity early in initrd image
    resolves: rhbz#1394965
  - cpu-partitioning: set workqueue affinity early
    resolves: rhbz#1395899
  - scsi_host: fixed probing of ALPM, missing ALPM logged as info
    resolves: rhbz#1416712
  - added new profile cpu-partitioning
    resolves: rhbz#1359956
  - bootloader: improved inheritance
    resolves: rhbz#1274464
  - units: mplemented udev-based regexp device matching
    resolves: rhbz#1251240
  - units: introduced pre_script, post_script
    resolves: rhbz#1246176
  - realtime-virtual-host: accommodate new ktimersoftd thread
    resolves: rhbz#1332563
  - defirqaffinity: fixed traceback due to syntax error
    resolves: rhbz#1369791
  - variables: support inheritance of variables
    resolves: rhbz#1433496
  - scheduler: added support for cores isolation
    resolves: rhbz#1403309
  - tuned-profiles-nfv splitted to host/guest and dropped unneeded dependency
    resolves: rhbz#1413111
  - desktop: fixed typo in profile summary
    resolves: rhbz#1421238
  - with systemd don't do full rollback on shutdown / reboot
    resolves: rhbz#1421286
  - builtin functions: added virt_check function and support to include
    resolves: rhbz#1426654
  - cpulist_present: explicitly sorted present CPUs
    resolves: rhbz#1432240
  - plugin_scheduler: fixed initialization
    resolves: rhbz#1433496
  - log errors when applying a profile fails
    resolves: rhbz#1434360

* Tue Nov  8 2016 Jaroslav Škarvada <jskarvad@redhat.com> - 2.7.1-4
- Fixed timeout if non-existent profile is requested
  resolves: rhbz#1369502

* Mon Sep 12 2016 Ondřej Lysoněk <olysonek@redhat.com> - 2.7.1-3
- Fixed a traceback
  resolves: rhbz#1372298

* Wed Aug 10 2016 Jaroslav Škarvada <jskarvad@redhat.com> - 2.7.1-2
- fixed Tuned restart from GUI
  resolves: rhbz#1365533

* Tue Aug  2 2016 Jaroslav Škarvada <jskarvad@redhat.com> - 2.7.1-1
- - new-release
  - rebase tuned to latest upstream
    resolves: rhbz#1289048
  - gui: fixed traceback caused by DBus paths copy&paste error
    related: rhbz#1356369
  - tuned-adm: fixed traceback of 'tuned-adm list' if daemon is not running
    resolves: rhbz#1358857

* Tue Jul 19 2016 Jaroslav Škarvada <jskarvad@redhat.com> - 2.7.0-1
- new-release
  - rebase tuned to latest upstream
    resolves: rhbz#1289048
  - gui: fixed save profile
    resolves: rhbz#1242491
  - tuned-adm: added --ignore-missing parameter
    resolves: rhbz#1243807
  - plugin_vm: added transparent_hugepage alias
    resolves: rhbz#1249610
  - plugins: added modules plugin
    resolves: rhbz#1249618
  - plugin_cpu: do not show error if cpupower or x86_energy_perf_policy are
    missing
    resolves: rhbz#1254417
  - tuned-adm: fixed restart attempt if tuned is not running
    resolves: rhbz#1258755
  - nfv: avoided race condition by using synchronous mode
    resolves: rhbz#1259039
  - realtime: added check for isolcpus sanity
    resolves: rhbz#1264128
  - pm_qos: fixed exception if PM_QoS is not available
    resolves: rhbz#1296137
  - plugin_sysctl: reapply system sysctl after Tuned sysctl are applied
    resolves: rhbz#1302953
  - atomic: increase number of inotify watches
    resolves: rhbz#1322001
  - realtime-virtual-host/guest: added rcu_nocbs kernel boot parameter
    resolves: rhbz#1334479
  - realtime: fixed kernel.sched_rt_runtime_us to be -1
    resolves: rhbz#1346715
  - tuned-adm: fixed detection of no_daemon mode
    resolves: rhbz#1351536
  - plugin_base: correctly strip assignment modifiers even if not used
    resolves: rhbz#1353142
  - plugin_disk: try to workaround embedded '/' in device names
    related: rhbz#1353142
  - sap-hana: explicitly setting kernel.numa_balancing = 0 for better performance
    resolves: rhbz#1355768
  - libexec: fixed listdir and isdir in defirqaffinity.py
    resolves: rhbz#1252160
  - plugin_cpu: save and restore only intel pstate attributes that were changed
    resolves: rhbz#1252156
  - functions: fixed sysfs save to work with options
    resolves: rhbz#1251507
  - functions: fixed restore_logs_syncing to preserve SELinux context on rsyslog.conf
    resolves: rhbz#1268901
  - spec: correctly remove tuned footprint from /etc/default/grub
    resolves: rhbz#1268845
  - gui: fixed creation of new profile
    resolves: rhbz#1274609

* Tue Feb  9 2016 Jaroslav Škarvada <jskarvad@redhat.com> - 2.5.1-7
- fixed traceback during restart attempt
  resolves: rhbz#1265660

* Wed Jan 13 2016 Jaroslav Škarvada <jskarvad@redhat.com> - 2.5.1-6
- fixed race in modprobe in realtime-virtual-host profile and extended
  stop action to have hint why it is called
  resolves: rhbz#1292117

* Mon Nov 16 2015 Jaroslav Škarvada <jskarvad@redhat.com> - 2.5.1-5
- fixed various verification issues (by verification-fixes patch)
  resolves: rhbz#1252153
- realtime profile now sets cpumask of unbound workqueues
  (by realtime-set-unbound-workqueues patch)
  resolves: rhbz#1259043
- fixed lapic_timer_adv_ns cache in realtime-virtual-host profile
  (by lapic-timer-adv-ns-cache-fix patch)
  resolves: rhbz#1259452
- fixed find-lapictscdeadline-optimal-fix in realtime-virtual-host profile
  (by find-lapictscdeadline-optimal-fix patch)
  resolves: rhbz#1267284
- removed nohz_full from the realtime profile (by realtime-remove-nohz-full
  patch)
  resolves: rhbz#1274486

* Wed Sep 23 2015 Jaroslav Škarvada <jskarvad@redhat.com> - 2.5.1-4
- grub support in post scriptlet made conditional not to break s390(x)
  resolves: rhbz#1265654

* Fri Aug 28 2015 Jaroslav Škarvada <jskarvad@redhat.com> - 2.5.1-3
- patched files are not backed up
  related: rhbz#1254538

* Fri Aug 28 2015 Jaroslav Škarvada <jskarvad@redhat.com> - 2.5.1-2
- unquoted sysctl values
  resolves: rhbz#1254538

* Tue Aug  4 2015 Jaroslav Škarvada <jskarvad@redhat.com> - 2.5.1-1
- new-release
  related: rhbz#1155052
  - plugin_scheduler: work with nohz_full
    resolves: rhbz#1247184
  - fixed realtime-virtual-guest/host profiles packaged twice
    resolves: rhbz#1249028
  - fixed requirements of realtime and nfv profiles
  - fixed tuned-gui not starting
  - various other minor fixes
  - defuzzified gtk-3.8 patch

* Sun Jul  5 2015 Jaroslav Škarvada <jskarvad@redhat.com> - 2.5.0-1
- new-release
  resolves: rhbz#1155052
  - add support for ethtool -C to tuned network plugin
    resolves: rhbz#1152539
  - add support for ethtool -K to tuned network plugin
    resolves: rhbz#1152541
  - add support for calculation of values for the kernel command line
    resolves: rhbz#1191595
  - no error output if there is no hdparm installed
    resolves: rhbz#1191775
  - do not run hdparm on hotplug events if there is no hdparm tuning
    resolves: rhbz#1193682
  - add oracle tuned profile
    resolves: rhbz#1196298
  - fix bash completions for tuned-adm
    resolves: rhbz#1207668
  - add glob support to tuned sysfs plugin
    resolves: rhbz#1212831
  - add tuned-adm verify subcommand
    resolves: rhbz#1212836
  - do not install tuned kernel command line to rescue kernels
    resolves: rhbz#1223864
  - add variables support
    resolves: rhbz#1225124
  - add built-in support for unit conversion into tuned
    resolves: rhbz#1225135
  - fixed vm.max_map_count setting in sap-netweaver profile
    resolves: rhbz#1228562
  - create tuned profile for RHEL-RT
    resolves: rhbz#1228801
  - plugin_scheduler: added support for runtime tuning of processes
    resolves: rhbz#1148546
  - add support for changing elevators on xvd* devices (Amazon EC2)
    resolves: rhbz#1170152
  - add workaround to be run after systemd-sysctl
    resolves: rhbz#1189263
  - do not change settings of transparent hugepages if set in kernel cmdline
    resolves: rhbz#1189868
  - add tuned profiles for RHEL-NFV
    resolves: rhbz#1228803
  - plugin_bootloader: apply $tuned_params to existing kernels
    resolves: rhbz#1233004
  - add support for no daemon mode
    resolves: rhbz#1068663

* Thu Oct 16 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 2.4.1-1
- new-release
  resolves: rhbz#1093883

* Tue Oct  7 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 2.4.0-6
- add autodetection of grub2 to plugin_bootloader
  resolves: rhbz#1150047

* Mon Oct  6 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 2.4.0-5
- fixed tuned-adm list traceback
  resolves: rhbz#1149162

* Mon Oct  6 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 2.4.0-4
- fixed cmdline handling in bootloader plugin
  related: rhbz#1148711

* Mon Oct  6 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 2.4.0-3
- grub template 00_tuned, do not return error if there is no cmdline
  resolves: rhbz#1148711

* Wed Oct  1 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 2.4.0-2
- fixed tuned-gui polkit path
  related: rhbz#1093883

* Wed Oct  1 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 2.4.0-1
- new-release
  resolves: rhbz#1093883
  - fixed traceback if profile cannot be loaded
    related: rhbz#953128
  - powertop2tuned: fixed traceback if rewriting file instead of dir
  - daemon: fixed race condition in start/stop
  - balanced: used medium_power ALPM policy
  - balanced: used conservative CPU governor
    resolves: rhbz#1124125
  - plugins: added selinux plugin
  - plugin_net: added nf_conntrack_hashsize parameter
  - profiles: included sap-hana and sap-hana-vmware profiles
  - profiles: sap-profiles in individual subpackages
    resolves: rhbz#1058483
  - man: structured profiles manual pages according to sub-packages
  - improved error handling of switch_profile
  - tuned-adm: active: detect whether tuned deamon is running
  - removed active_profile from RPM verification
    resolves: rhbz#1104126
  - plugin_disk: readahead value can be now specified in sectors
    resolves: rhbz#1127127
  - plugins: added bootloader plugin
    resolves: rhbz#1044111
  - plugin_disk: added error counter to hdparm calls
  - plugins: added scheduler plugin
    resolves: rhbz#1100826
  - added tuned-gui

* Fri Sep 19 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 2.3.0-16
- autodetecting initial profile in runtime, not int post install
  resolves: rhbz#1144067

* Tue Sep  2 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 2.3.0-15
- updated man page to include atomic-host and atomic-guest profiles
  related: rhbz#1091977, rhbz#1091979

* Wed Aug 27 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 2.3.0-14
- add atomic-host and atomic-guest profiles
  resolves: rhbz#1091977, rhbz#1091979

* Mon May 12 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 2.3.0-13
- add support for assignment modifiers
  resolves: rhbz#1096917

* Wed May  7 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 2.3.0-12
- handle root block devices
  resolves: rhbz#1033251

* Fri Mar  7 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 2.3.0-11
- reverted fix for bug 1073008, dependency is not met on s390
  related: rhbz#1073008

* Thu Mar  6 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 2.3.0-10
- added requirement to kernel-tools
  resolves: rhbz#1073008
- made cpupower.service conflicting
  resolves: rhbz#1073392

* Tue Mar  4 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 2.3.0-9
- re-arranged profile autoselection patches for better maintainability
  related: rhbz#1069123

* Mon Mar  3 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 2.3.0-8
- fixed profile autoselection
  resolves: rhbz#1069123

* Fri Feb 14 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 2.3.0-7
- throughput-performance is default for the server
  resolves: rhbz#1063481
- THP not disabled in the latency-performance profile
  resolves: rhbz#1064510
- added network-latency profile
  resolves: rhbz#1052418
- added network-throughput profile
  resolves: rhbz#1052421

* Tue Jan  7 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 2.3.0-6
- altered dirty ratios of troughput-performance for better performance
  resolves: rhbz#1043533

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 2.3.0-5
- Mass rebuild 2013-12-27

* Fri Nov 22 2013 Jaroslav Škarvada <jskarvad@redhat.com> - 2.3.0-4
- removed useless find from the spindown-disk profile
  resolves: rhbz#1030439

* Fri Nov  8 2013 Jaroslav Škarvada <jskarvad@redhat.com> - 2.3.0-3
- defuzzified patches
  related: rhbz#1028119, rhbz#1028122

* Fri Nov  8 2013 Jaroslav Škarvada <jskarvad@redhat.com> - 2.3.0-2
- fixed race condition in the start/stop code
  resolves: rhbz#1028119
- improved tuned responsiveness
  resolves: rhbz#1028122

* Wed Nov  6 2013 Jaroslav Škarvada <jskarvad@redhat.com> - 2.3.0-1
- new-release
  resolves: rhbz#1020743
  - audio plugin: fixed audio settings in standard profiles
  - video plugin: fixed tunings
  - daemon: fixed crash if preset profile is not available
  - man: various updates and corrections
  - functions: fixed usb and bluetooth handling
  - tuned: switched to lightweighted pygobject3-base
  - daemon: added global config for dynamic_tuning
  - utils: added pmqos-static script for debug purposes
  - throughput-performance: various fixes
  - tuned: added global option update_interval
  - plugin_cpu: added support for x86_energy_perf_policy
    resolves: rhbz#1015675
  - dbus: fixed KeyboardInterrupt handling
  - plugin_cpu: added support for intel_pstate
    resolves: rhbz#996722
  - profiles: various fixes
  - profiles: added desktop profile
    resolves: rhbz#996723
  - tuned-adm: implemented non DBus fallback control
  - profiles: added sap profile
  - tuned: lowered CPU usage due to python bug

* Wed Oct 16 2013 Jaroslav Škarvada <jskarvad@redhat.com> - 2.2.2-4
- lock CPU to C1 instead of C0 in latency-performance profile
  resolves: rhbz#1013085
- readahed multiply set to 4 in throughput-performance profile
  resolves: rhbz#987570
- packaged pmqos-static script for debugging purposes
  resolves: rhbz#1015676
- added global configuration file with the possibility to globally
  disable the dynamic tuning and it is by default disabled on RHEL
  resolves: rhbz#1006427

* Thu Jul 25 2013 Jaroslav Škarvada <jskarvad@redhat.com> - 2.2.2-3
- do not package backup file
  related: rhbz#986468

* Thu Jul 25 2013 Jaroslav Škarvada <jskarvad@redhat.com> - 2.2.2-2
- used pygobject3-base instead of pygobject2
  resolves: rhbz#986468

* Tue Mar 19 2013 Jaroslav Škarvada <jskarvad@redhat.com> - 2.2.2-1
- new-release:
  - cpu plugin: fixed cpupower workaround
  - cpu plugin: fixed crash if cpupower is installed

* Fri Mar  1 2013 Jaroslav Škarvada <jskarvad@redhat.com> - 2.2.1-1
- new release:
  - audio plugin: fixed error handling in _get_timeout
  - removed cpupower dependency, added sysfs fallback
  - powertop2tuned: fixed parser crash on binary garbage
    resolves: rhbz#914933
  - cpu plugin: dropped multicore_powersave as kernel upstream already did
  - plugins: options manipulated by dynamic tuning are now correctly saved and restored
  - powertop2tuned: added alias -e for --enable option
  - powertop2tuned: new option -m, --merge-profile to select profile to merge
  - prefer transparent_hugepage over redhat_transparent_hugepage
  - recommend: use recommend.conf not autodetect.conf
  - tuned.service: switched to dbus type service
    resolves: rhbz#911445
  - tuned: new option --pid, -P to write PID file
  - tuned, tuned-adm: added new option --version, -v to show version
  - disk plugin: use APM value 254 for cleanup / APM disable instead of 255
    resolves: rhbz#905195
  - tuned: new option --log, -l to select log file
  - powertop2tuned: avoid circular deps in include (one level check only)
  - powertop2tuned: do not crash if powertop is not installed
  - net plugin: added support for wake_on_lan static tuning
    resolves: rhbz#885504
  - loader: fixed error handling
  - spec: used systemd-rpm macros
    resolves: rhbz#850347

* Mon Jan 28 2013 Jan Vcelak <jvcelak@redhat.com> 2.2.0-1
- new release:
  - remove nobarrier from virtual-guest (data loss prevention)
  - devices enumeration via udev, instead of manual retrieval
  - support for dynamically inserted devices (currently disk plugin)
  - dropped rfkill plugins (bluetooth and wifi), the code didn't work

* Wed Jan  2 2013 Jaroslav Škarvada <jskarvad@redhat.com> - 2.1.2-1
- new release:
  - systemtap {disk,net}devstat: fix typo in usage
  - switched to configobj parser
  - latency-performance: disabled THP
  - fixed fd leaks on subprocesses

* Thu Dec 06 2012 Jan Vcelak <jvcelak@redhat.com> 2.1.1-1
- fix: powertop2tuned execution
- fix: ownership of /etc/tuned

* Mon Dec 03 2012 Jan Vcelak <jvcelak@redhat.com> 2.1.0-1
- new release:
  - daemon: allow running without selected profile
  - daemon: fix profile merging, allow only safe characters in profile names
  - daemon: implement missing methods in DBus interface
  - daemon: implement profile recommendation
  - daemon: improve daemonization, PID file handling
  - daemon: improved device matching in profiles, negation possible
  - daemon: various internal improvements
  - executables: check for EUID instead of UID
  - executables: run python with -Es to increase security
  - plugins: cpu - fix cpupower execution
  - plugins: disk - fix option setting
  - plugins: mounts - new, currently supports only barriers control
  - plugins: sysctl - fix a bug preventing settings application
  - powertop2tuned: speedup, fix crashes with non-C locales
  - powertop2tuned: support for powertop 2.2 output
  - profiles: progress on replacing scripts with plugins
  - tuned-adm: bash completion - suggest profiles from all supported locations
  - tuned-adm: complete switch to D-bus
  - tuned-adm: full control to users with physical access

* Mon Oct 08 2012 Jaroslav Škarvada <jskarvad@redhat.com> - 2.0.2-1
- New version
- Systemtap scripts moved to utils-systemtap subpackage

* Sun Jul 22 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jun 12 2012 Jaroslav Škarvada <jskarvad@redhat.com> - 2.0.1-3
- another powertop-2.0 compatibility fix
  Resolves: rhbz#830415

* Tue Jun 12 2012 Jan Kaluza <jkaluza@redhat.com> - 2.0.1-2
- fixed powertop2tuned compatibility with powertop-2.0

* Tue Apr 03 2012 Jaroslav Škarvada <jskarvad@redhat.com> - 2.0.1-1
- new version

* Fri Mar 30 2012 Jan Vcelak <jvcelak@redhat.com> 2.0-1
- first stable release
