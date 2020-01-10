%global uses_tmpfs (0%{?fedora} >= 15)

Summary: A dynamic adaptive system tuning daemon
Name: tuned
Version: 0.2.19
Release: 16%{?dist}
License: GPLv2+
Group: System Environment/Daemons
# The source for this package was pulled from upstream git.  Use the
# following commands to get the corresponding tarball:
#  git clone git://git.fedorahosted.org/git/tuned.git
#  cd tuned
#  git checkout v%{version}
#  make archive
Source: tuned-%{version}.tar.bz2
Patch1: tuned-profile-fixes.patch
Patch2: tuned-man-pages.patch
Patch3: tuned-net-card-names.patch
Patch4: tuned-net-unsupported-mode.patch
Patch5: tuned-io-handling.patch
Patch6: tuned-net-device-type-determination.patch
Patch7: tuned-scheduler-vd.patch
Patch8: tuned-profile-virtual-host.patch
Patch9: tuned-profile-virtual-guest.patch
Patch10: tuned-stp-cmdline-errors.patch
Patch11: tuned-add-pmqos-static-script.patch
Patch12: tuned-verify-elevator-tune-devs.patch
Patch13: tuned-no-nobarriers-with-write-back-cache.patch
Patch14: tuned-pidfile-permissions.patch
Patch15: tuned-udev-new-disk-restart.patch
Patch16: tuned-thp-never.patch
Patch17: tuned-kvm-barriers.patch
Patch18: tuned-readahead-restore.patch
Patch19: tuned-udev-deferred-restart.patch
Patch20: tuned-silent-nobarriers.patch
Patch21: tuned-diskdevstat-names-fix.patch
Patch22: tuned-upstream-thp.patch
Patch23: tuned-pidfile-pmqos-static-perms.patch
Patch24: tuned-latency-performance-c1.patch
Patch25: tuned-adm-off-typo-fix.patch
Patch26: tuned-virtual-profiles-doc.patch
Patch27: tuned-ktune-sysctl-d.patch
Patch28: tuned-add-sap.patch
Patch29: tuned-virtual-host-sched-migration-cost.patch
Patch30: tuned-functions-fix.patch
Patch31: tuned-customizable-elevator.patch
Patch32: tuned-reverse-sysctl-post.patch
Patch33: tuned-latency-performance-typo-fix.patch
Patch34: tuned-dasd.patch
Patch35: tuned-xvd.patch
Patch36: tuned-sap-netweaver-increase-vm-max-map-count.patch
Patch37: tuned-add-oracle.patch
Patch38: tuned-ktune-sysctl-no-revert.patch

URL: https://fedorahosted.org/tuned/
Buildroot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildRequires: python
Requires: usermode ethtool udev
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
Requires(postun): initscripts
BuildArch: noarch

%description
The tuned package contains a daemon that tunes system settings dynamically.
It does so by monitoring the usage of several system components periodically.
Based on that information components will then be put into lower or higher
power saving modes to adapt to the current usage. Currently only ethernet
network and ATA harddisk devices are implemented.

%package utils
Summary: Disk and net statistic monitoring systemtap scripts
Requires: systemtap
Group: Applications/System

%description utils
The tuned-utils package contains several systemtap scripts to allow detailed
manual monitoring of the system. Instead of the typical IO/sec it collects
minimal, maximal and average time between operations to be able to
identify applications that behave power inefficient (many small operations
instead of fewer large ones).

%package profiles-sap
Summary: Additional tuned profile(s) targeted to SAP NetWeaver loads
Requires: %{name} = %{version}-%{release}

%description profiles-sap
Additional tuned profile(s) targeted to SAP NetWeaver loads.

%package profiles-sap-hana
Summary: Additional tuned profile(s) targeted to SAP HANA loads
Requires: %{name} = %{version}-%{release}

%description profiles-sap-hana
Additional tuned profile(s) targeted to SAP HANA loads.

%package profiles-oracle
Summary: Additional tuned profile(s) targeted to Oracle loads
Requires: %{name} = %{version}-%{release}

%description profiles-oracle
Additional tuned profile(s) targeted to Oracle loads.

%prep
%setup -q
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch14 -p1
%patch15 -p1
%patch16 -p1
%patch17 -p1
%patch18 -p1
%patch19 -p1
%patch20 -p1
%patch21 -p1
%patch22 -p1
%patch23 -p1
%patch24 -p1
%patch25 -p1
%patch26 -p1
%patch27 -p1
%patch28 -p1
%patch29 -p1
%patch30 -p1
%patch31 -p1
%patch32 -p1
%patch33 -p1
%patch34 -p1
%patch35 -p1
%patch36 -p1
%patch37 -p1
%patch38 -p1

# fix permissions on ktune scripts (some were created by the patches)
chmod 0755 tune-profiles/*/ktune.sh

%build

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}

%if !%uses_tmpfs
    rm -rf %{buildroot}%{_sysconfdir}/tmpfiles.d
%endif

%clean
rm -rf %{buildroot}

%post
/sbin/chkconfig --add tuned
/sbin/chkconfig --add ktune

%preun
if [ $1 = 0 ] ; then
    /sbin/service tuned stop >/dev/null 2>&1
    /sbin/chkconfig --del tuned
    /sbin/service ktune stop >/dev/null 2>&1
    /sbin/chkconfig --del ktune
fi

%postun
if [ "$1" -ge "1" ] ; then
    /sbin/service tuned condrestart >/dev/null 2>&1 || :
    /sbin/service ktune condrestart >/dev/null 2>&1 || :
fi

%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING INSTALL NEWS README doc/DESIGN.txt doc/TIPS.txt ktune/README.ktune doc/examples
%{_initddir}/tuned
%config(noreplace) %verify(not link) %{_sysconfdir}/tuned.conf
%config(noreplace) %{_sysconfdir}/pam.d/tuned-adm
%config(noreplace) %{_sysconfdir}/security/console.apps/tuned-adm
%{_sysconfdir}/bash_completion.d
%{_sbindir}/tuned
%{_sbindir}/tuned-adm
# consolehelper hard link
%{_bindir}/tuned-adm
%dir %{_sysconfdir}/tune-profiles
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/tune-profiles/active-profile
%{_sysconfdir}/tune-profiles/functions
%{_sysconfdir}/tune-profiles/default
%{_sysconfdir}/tune-profiles/desktop-powersave
%{_sysconfdir}/tune-profiles/enterprise-storage
%{_sysconfdir}/tune-profiles/laptop-ac-powersave
%{_sysconfdir}/tune-profiles/laptop-battery-powersave
%{_sysconfdir}/tune-profiles/latency-performance
%{_sysconfdir}/tune-profiles/server-powersave
%{_sysconfdir}/tune-profiles/spindown-disk
%{_sysconfdir}/tune-profiles/throughput-performance
%{_sysconfdir}/tune-profiles/virtual-guest
%{_sysconfdir}/tune-profiles/virtual-host
%{_datadir}/tuned
%{_mandir}/man1/tuned-adm.*
%{_mandir}/man5/tuned.conf.*
%{_mandir}/man7/tuned-profiles.7*
%{_mandir}/man8/tuned.*
%attr(0755,root,root) %{_initddir}/ktune
%config(noreplace) %verify(not link) %{_sysconfdir}/sysconfig/ktune
%config(noreplace) %verify(not link) %{_sysconfdir}/ktune.d/tunedadm.conf
%dir %{_sysconfdir}/ktune.d
%dir %{_localstatedir}/log/tuned
%dir %{_localstatedir}/run/tuned
%attr(0755,root,root) /lib/udev/tuned-mpath-iosched
%attr(0755,root,root) /lib/udev/tuned-request-ktune-restart
/lib/udev/rules.d/*
%{_libexecdir}/tuned/
%if %uses_tmpfs
%{_sysconfdir}/tmpfiles.d
%endif

%files utils
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
%{_sysconfdir}/tune-profiles/sap-netweaver
%{_mandir}/man7/tuned-profiles-sap.7*

%files profiles-sap-hana
%defattr(-,root,root,-)
%{_sysconfdir}/tune-profiles/sap-hana
%{_sysconfdir}/tune-profiles/sap-hana-vmware
%{_mandir}/man7/tuned-profiles-sap-hana.7*

%files profiles-oracle
%defattr(-,root,root,-)
%{_sysconfdir}/tune-profiles/oracle
%{_mandir}/man7/tuned-profiles-oracle.7*

%changelog
* Tue Nov 24 2015 Jaroslav Škarvada <jskarvad@redhat.com> - 0.2.19-16
- added oracle profile
  resolves: rhbz#1196294
- ktune now doesn't revert sysctl settings if not explictly requested
  resolves: rhbz#1111416

* Mon Feb  9 2015 Jaroslav Škarvada <jskarvad@redhat.com> - 0.2.19-15
- dynamically changing symlinks excluded from the RPM verification
  resolves: rhbz#1017366
- reversed reading of sysctl configuration in SYSCTL_POST to follow
  RHEL-6 behavior
  resolves: rhbz#1036049
- fixed typo in latency-performance profile regarding SYSCTL_POST
  resolves: rhbz#1064062
- added support for s390 block devices (/dev/dasd)
  resolves: rhbz#1129936
- added support for Xen VS devices (/dev/xvd)
  resolves: rhbz#1159963
- increased vm.max_map_count in sap-netweaver profile
  resolves: rhbz#1174253

* Wed Oct 15 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 0.2.19-14
- updated sap profiles and moved them to subpackages
  resolves: rhbz#1058389

* Mon Jul 22 2013 Jaroslav Škarvada <jskarvad@redhat.com> - 0.2.19-13
- add support for upstream THP
  resolves: rhbz#912788
- added sap profile, backported features it needs
  resolves: rhbz#910838
- made elevator settings customizable
  resolves: rhbz#987547
- fixed usb_autosuspend and bluetooth functions
  resolves: rhbz#982756
- increased kernel.sched_migration_cost in virtual-host profile
  resolves: rhbz#969491
- documented virtual-guest and virtual-host profiles
  resolves: rhbz#964187
- fixed typo in tuned-adm help
  resolves: rhbz#963821
- modified latency-performance profile to lock CPU to C1
  resolves: rhbz#961792
- added support for /etc/sysctl.d
  resolves: rhbz#959732
- fixed permissions of /var/run/tuned/pmqos-static.pid
  resolves: CVE-2013-1820
- fixed diskdevstat labels
  resolves: rhbz#885080
- quiet errors when remounting FS with nobarriers
  resolves: rhbz#838512

* Mon Feb 04 2013 Jaroslav Škarvada <jskarvad@redhat.com> - 0.2.19-12
- fix: tuned incorrectly sets readahead values when new device is inserted
  resolves: rhbz#905077
- fix: there is a race when multiple devices are inserted
  resolves: rhbz#904062

* Thu Jan  3 2013 Jaroslav Škarvada <jskarvad@redhat.com> - 0.2.19-11
- de-fuzzified thp-never patch to prevent patch of making auto-backup
  related: rhbz#887355

* Thu Jan  3 2013 Jaroslav Škarvada <jskarvad@redhat.com> - 0.2.19-10
- fix: virtual-guest profile should not deploy the nobarrier option
  resolves: rhbz#886956
- fix: disable transparent hugepages in latency-performance profile
  resolves: rhbz#887355

* Wed Oct 10 2012 Jan Vcelak <jvcelak@redhat.com> 0.2.19-9
- add udev rule to restart ktune in new block device is added (#847445)

* Thu Sep 27 2012 Jan Vcelak <jvcelak@redhat.com> 0.2.19-8
- fix: poor ping latency in 'latency-performance' profile (#714180)
- fix: ktune breaks disks when pecifying just the device for ELEVATOR_TUNE_DEVS (#784308)
- fix: should not disable barriers on devices with write back cache (#801561)
- fix: /var/run/tuned/tuned.pid created with insecure permissions (#845336)

* Mon Mar 05 2012 Jan Vcelak <jvcelak@redhat.com> 0.2.19-7
- fix: apply scheduler settings to vd* devices (#725497)
- enhancement: add virtual-host profile (#740976)
- enhancement: add virtual-guest profile (#740977)
- fix: diskdevstat and netdevstat command line error handling (#747210)

* Thu Jul 28 2011 Thomas Wörner <twoerner@redhat.com> 0.2.19-6
- fixed device type determination v2 (rhbz#707079)

* Thu Jul 28 2011 Thomas Wörner <twoerner@redhat.com> 0.2.19-5
- fixed handling of stdin/stdout/stderr during daemon creation (rhbz#695480)
- fixed device type determination (rhbz#707079)

* Wed Mar 30 2011 Jan Vcelak <jvcelak@redhat.com> 0.2.19-4
- fix: crash when parsing unsupported network card link mode (#689715)

* Thu Mar 10 2011 Jan Vcelak <jvcelak@redhat.com> 0.2.19-3
- universal ethernet card identifier detection (#682380)

* Thu Jan 13 2011 Jan Vcelak <jvcelak@redhat.com> 0.2.19-2
- add missing man pages (#625850)
- update profiles description (#619812)
- fix typos in laptop-battery-profile script
- disable tuned powersaving in disk-spindown, *-performance and enterprise-storage

* Mon Jan 10 2011 Jan Vcelak <jvcelak@redhat.com> 0.2.19-1
- reduced FSB support on Asus EEE netbooks with Intel Atom
- consolidate ktune script functions in tuning profiles
- disable tuned daemon on s390/s390x architectures
- set readahead by multiplying previous setting
- udev rules and script for CFQ and multipath devices scheduler tuning
- fix hal-disable-polling if no CD drives present
- added support for architecture-specific configuration files
- special sysctl setting for s390x arch in 'throughtput-performance' profile
- overall profiles update
- 'tuned-adm active' shows status of tuned and ktune services as well
- proper configuration files setup after fresh instalation
- tuned-utils: added license text
- bash completion support
- tuned-adm: profile validity check
- Fixed 577983 - AttributeError: Nettool instance has no attribute 'interface'

* Wed Sep 29 2010 Jan Vcelak <jvcelak@redhat.com> 0.2.11-9
- Apply I/O scheduler changes to device mapper devices (#636548)

* Tue Aug 17 2010 Jarod Wilson <jarod@redhat.com> 0.2.11-8
- Don't touch transparent hugepage or cpufreq settings if not supported (#621877)
- Add new enterprise-storage profile based on throughput-performance:
  * Disables barriers for all non-root non-/boot file systems (#624736)
  * Increases the default readahead value from 128kb to 512kb (#624828)

* Tue Aug 03 2010 Phil Knirsch <pknirsch@redhat.com> 0.2.11-7
- Fixes #620686 - Problem with network cards that provide unparsable supported network modes

* Wed Jul 14 2010 Jan Vcelak <jvcelak@redhat.com> 0.2.11-6
- Jarod Wilson: profiles update (#604046, #587432)
- fresh installation and SELinux fixes

* Thu Jun 17 2010 Jan Vcelak <jvcelak@redhat.com> 0.2.11-5
- Fixes #605217 - tuned-adm unsafe profiles loading
  tuned-adm tool updated to the newest upstream version

* Thu May 27 2010 Jan Vcelak <jvcelak@redhat.com> 0.2.11-4
- Fixes #596817 - spindown-disk profile requires hciconfig
  problematic profile was completely removed

* Thu May 06 2010 Jan Vcelak <jvcelak@redhat.com> 0.2.11-3
- Fixes #577971 - error: "net.bridge.bridge-nf-call-ip6tables" is an unknown key (Thomas Woerner)
- Fixes #588739 - tuned should not apply /etc/sysctl.ktune settings (Jan Vcelak)

* Tue Mar 30 2010 Jan Vcelak <jvcelak@redhat.com> 0.2.11-2
- Fixes: #578104

* Mon Mar 22 2010 Phil Knirsch <pknirsch@redhat.com> 0.2.11-1
- Added support for display of currently active profile
- Fix missing help command
- Large update to documentation and manpages
- Updated several of the profiles
- Updated ALPM powersave code in the various powersave profiles
- Disabled USB autosuspend in laptop-battery-powersave for now

* Wed Feb 03 2010 Jan Vcelak <jvcelak@redhat.com> 0.2.10-1
- Log file moved to separate directory.

* Mon Feb 01 2010 Jan Vcelak <jvcelak@redhat.com> 0.2.9-1
- New release.

* Tue Jan 26 2010 Jan Vcelak <jvcelak@redhat.com> 0.2.8-2
- Included Thomas Woerner's patch checking user rights when executing
  ktune service commands.
- Included Jan Vcelak's patch fixing logging module initialization.

* Fri Jan 08 2010 Jan Vcelak <jvcelak@redhat.com> 0.2.8-1
- New release. Adds logging support.

* Mon Dec 21 2009 Jan Vcelak <jvcelak@redhat.com> 0.2.7-2
- Fixed 542305 - [abrt] crash detected in tuned-0.2.5-2.fc12
  Some ethernet cards are not supported by 'ethtool'.

* Fri Dec 11 2009 Thomas Woerner <twoerner@redhat.com> 0.2.7-1
- Updated ktune to version 0.4-1
  - Supports start and stop options in profile scripts calls
  - Fixed CMDLINE_ELEVATOR test (rhbz#496940#c9)

* Tue Dec 08 2009 Phil Knirsch <pknirsch@redhat.com> 0.2.6-1
- Included Jan Vcelak's patch for pyo and pyc files
- Updated ktune.sh script for laptop-battery-powersave profile with latest
  ALPM mechanism
- Fixed ktune.sh script for laptop-battery-powersave profile to stop printing
  errors when files in /sys are missing

* Thu Nov 26 2009 Petr Lautrbach <plautrba@redhat.com> 0.2.5-2
- Added python into build requires
- Resolves: #539949

* Tue Nov 03 2009 Phil Knirsch <pknirsch@redhat.com> 0.2.5-1
- Moved from prerelease to normal
- Added missing ethtool requires
- Fixed 532209 - init priority wrong for ktune (Jan Vcelak)
- Fixed 530457 - [abrt] crash detected in tuned-0.2.5-0.1.fc12 (Jan Vcelak)
- Added detection of netcard supported speeds (Jan Vcelak)
- Fix ktune.sh script for stopping in regard to ALPM and CDROM polling (Phil Knirsch)

* Mon Oct 19 2009 Marcela Mašláňová <mmaslano@redhat.com> 0.2.5-0.3
- new release

* Thu Oct 15 2009 Petr Lautrbach <plautrba@redhat.com> 0.2.5-0.2
- Allow run tuned-adm as root for users at the physical console

* Mon Oct 12 2009 Petr Lautrbach <plautrba@redhat.com> 0.2.5-0.1
- Removed dependence on kobo
- Bumped to 0.2.5 pre release version

* Wed Sep 23 2009 Petr Lautrbach <plautrba@redhat.com> 0.2.4-2
- fixed url to fedorahosted project page
- Resolves: #519019

* Mon Sep 21 2009 Petr Lautrbach <plautrba@redhat.com> 0.2.4-1
- Update release to tuned-0.2.4
- Resolves: #523385

* Tue Aug 18 2009 Phil Knirsch <pknirsch@redhat.com> 0.2.3-1
- Updated documentation
- Few more fixes for tuned-adm

* Fri Aug 14 2009 Phil Knirsch <pknirsch@redhat.com>  0.2.2-1
- Updates to the ktune scripts
- Added support for start/stop of the ktune scripts and ktune initscript

* Tue Aug 04 2009 Phil Knirsch <pknirsch@redhat.com> - 0.2.1-1
- Added first set of profiles
- Added tuned-adm tool for profile switching
- Fixed several issues with the tuned-adm tool

* Mon Jul 27 2009 Thomas Woerner <twoerner@redhat.com> - 0.2.0-1
- Integrated ktune-0.4

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.1.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jul 16 2009 Phil Knirsch <pknirsch@redhat.com> - 0.1.7-1
- Added first version CPU tuning and monitoring plugins

* Thu Jun 25 2009 Petr Lautrbach <plautrba@redhat.com> - 0.1.6-1
- added scomes

* Wed Mar 25 2009 Phil Knirsch <pknirsch@redhat.com> - 0.1.5-1
- Updated documentation, thanks to Marcela Maslanova!
- Updated diskdevstat and netdevstat to have command line arguments
- Added the possibility to output a histogram at the end of the
  run for detailed information about the collected data

* Fri Mar 06 2009 Phil Knirsch <pknirsch@redhat.com> - 0.1.4-1
- Dropped unecessary kernel-debuginfo requires from tuned-utils

* Mon Mar 02 2009 Phil Knirsch <pknirsch@redhat.com> - 0.1.3-1
- Fixed placement of doc entry at tuned-utils package

* Thu Feb 26 2009 Phil Knirsch <pknirsch@redhat.com> - 0.1.2-1
- Added config file option to enable/disable plugins
- Switched from ConfigParser to RawConfigParser
- Renamed doc/README.txt to doc/DESIGN.txt
- Added tuned.conf man page
- Updated tuned man page
- Updated package descriptions (#487312)
- Added documentation for utils scripts (#487312)

* Wed Feb 25 2009 Phil Knirsch <pknirsch@redhat.com> - 0.1.1-1
- Bump version
- Added comment in empty __init__.py files
- Fixed BuildRoot tag to use latest recommendation of FPG
- Lots of whitespace changes
- Some minor README changes
- Added a changelog rule in Makefile
- Fixed rpmlint error messages
- Add init() methods to each plugin
- Call plugin init() methods during tuned's init()
- Add support for command line parameters
      o -c conffile|--config==conffile to specify the location of the config file
      o -d to start tuned as a daemon (instead of as normal app)
- Readded the debug output in case tuned isn't started as as daemon
- Fixed initialization of max transfer values for net tuning plugin
- Added complete cleanup code in case of tuned exiting and/or
  getting a SIGTERM to restore default values
- Made the disk tuning pluging less nosy if started as non-daemon
- Fixed missing self. in the tuned.py config handling
- Added a manpage
- Fixed summary
- Added missing GPL notic to tuned.py
- Added explanation for Source entry in specfile
- Added a distarchive target for the Makefile for proper tagging in git
- Added a explanation how to create the tarball via git in the specfile
- Fixed the defattr() lines in the specfile to conform FRG

* Mon Feb 23 2009 Phil Knirsch <pknirsch@redhat.com> - 0.1.0-1
- Initial version
