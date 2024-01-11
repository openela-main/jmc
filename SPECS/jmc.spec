# Version
%global major 8
%global minor 0
%global patchlevel 1

# Revision
%global revnum 4
# set to 1 for snapshots, 0 for release
%global usesnapshot 0

# SNAPSHOT version
%global revhash 699a121bd449fe8a9350221282bd3f809691a766
%global revdate 20210623

%global tarball_name jmc-%{revhash}

# Install jmc in /usr/lib/jmc (arch-specific and multilib exempt)
%global _jmcdir %{_prefix}/lib/%{name}

%global debug_package %{nil}

%if %{usesnapshot}
  %global releasestr %{revnum}.%{revdate}
%else
  %global releasestr %{revnum}
%endif

%ifarch %{ix86}
    %global eclipse_arch x86
%endif
%ifarch %{arm}
    %global eclipse_arch arm
%endif
%ifarch s390x x86_64 aarch64 ppc64le
    %global eclipse_arch %{_arch}
%endif

# Don't export Eclipse libraries
%global __provides_exclude_from ^%{_jmcdir}/plugins/org.eclipse.*$
%global __requires_exclude_from ^%{_jmcdir}/plugins/org.eclipse.*$

%global __requires_exclude ^osgi\\((javax|org\\.apache|org\\.eclipse|org\\.sat4j).*$
%global __provides_exclude ^osgi\\((com|javax|org\\.apache|org\\.glassfish|org\\.kxml2|org\\.sat4j|org\\.tukaani|org\\.w3c|org\\.xmlpull).*$

Name:       jmc
Version:    %{major}.%{minor}.%{patchlevel}
Release:    %{releasestr}%{?dist}
Summary:    JDK Mission Control is a profiling and diagnostics tool

License:    UPL
URL:        http://openjdk.java.net/projects/jmc/

Source0:    https://github.com/openjdk/jmc/archive/%{revhash}.tar.gz
Source1:    %{name}.desktop
Source2:    %{name}.1
Source3:    symlink_libs.sh

# Remove optional twitter related functionality
Patch0:     0-remove-twitter.patch
# Remove maven build profiles that won't be used in local build
Patch1:     1-remove-profiles.patch
# Remove localization files that currently cannot be supported
# due to a packaging issue for Eclipse language packs
# eclipse-nls-ja and eclipse-nls-zh
# They currently provide multiple archs within the same package
# and the local build system cannot fulfill dependencies from them
Patch2:     2-remove-localization.patch
# Remove unused module org.openjdk.jmc.ide.jdt
Patch3:     3-remove-ide-jdt.patch
# Remove unused remote repository definition
Patch4:     4-remove-buchen-repo.patch
# Add dependency on org. hamcrest-core to provide class used in unit tests
Patch5:     5-add-hamcrest.patch
# Remove windows and mac arches
Patch6:     6-remove-arch.patch
# Remove unnecessary dependency
Patch7:     7-remove-jacoco-dep.patch
# Revert downloading of flameview assets from the web
Patch8:     8-revert-flameview.patch
# Drop JFR flags (temporary)
Patch9:     9-update-flags.patch
# Revert the adjusted lz4-java name as seen in jmc
Patch10:    10-revert-lz4-java-name-override.patch
# Patch pom.xml Use to tycho version 2.1
Patch11:    11-tycho.patch
# Revert downloading of graphview assets from the web
Patch12:    12-revert-graphview.patch
# Simplify the path to the jmc product
Patch13:    13-revert-6852.patch
# Update javamail dependency names
Patch14:    14-fix-javamail.patch
# Revert usage of ResourceLocator as it isn't available in Eclipse 4.12
Patch15:    15-revert-resourcelocator.patch
# Remove Chromium (currently Windows-only) from the plugin list
Patch16:    16-remove-chromium.patch
# Revert usage of List.of in GraphView
Patch17:    17-revert-list-of.patch

ExclusiveArch: x86_64

BuildRequires:  desktop-file-utils
BuildRequires:  java-11-openjdk
BuildRequires:  libappstream-glib
BuildRequires:  maven-local

BuildRequires:  eclipse-pde
BuildRequires:  tycho

BuildRequires:  HdrHistogram >= 2.1.11
BuildRequires:  javamail
BuildRequires:  mvn(org.commonjava.maven.plugins:directory-maven-plugin)
BuildRequires:  mvn(com.sun.activation:jakarta.activation)
BuildRequires:  mvn(org.openjdk.jmc:common)
BuildRequires:  osgi(org.openjdk.jmc.flightrecorder.test)
BuildRequires:  osgi(javax.annotation-api)

Requires:  java-openjdk >= 1:1.8
Requires:  lz4-java

Requires:  osgi(com.sun.activation.jakarta.activation)
Requires:  osgi(org.openjdk.jmc.common)
Requires:  osgi(org.openjdk.jmc.flightrecorder)
Requires:  osgi(org.openjdk.jmc.flightrecorder.rules)
Requires:  osgi(org.openjdk.jmc.flightrecorder.rules.jdk)
Requires:  osgi(org.owasp.encoder)
Requires:  osgi(org.hdrhistogram.HdrHistogram) >= 2.1.11

Requires: gtk3
Requires: webkitgtk4
Requires: libGLU.so.1()(64bit)

%description
JDK Mission Control is a powerful profiler for HotSpot JVMs and has an
advanced set of tools that enables efficient and detailed analysis of the
extensive data collected by JDK Flight Recorder. The tool chain enables
developers and administrators to collect and analyze data from Java
applications running locally or deployed in production environments.

%prep
%setup -q -n %{tarball_name}

%patch0 -p1
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

%pom_disable_module releng
%pom_disable_module l10n application
%pom_disable_module org.openjdk.jmc.updatesite.ide application
%pom_disable_module org.openjdk.jmc.updatesite.rcp application

# disable tests that require the use of jfr
%pom_disable_module org.openjdk.jmc.rjmx.services.jfr.test application/tests
%pom_disable_module org.openjdk.jmc.flightrecorder.controlpanel.ui.test application/tests

%pom_remove_plugin com.github.spotbugs:spotbugs-maven-plugin
%pom_remove_plugin :maven-enforcer-plugin

%pom_remove_plugin :jacoco-maven-plugin application/tests
%pom_remove_plugin :jacoco-maven-plugin application/uitests
%pom_disable_module coverage application

# Info.plist are mac files and we only build for Linux
%pom_remove_plugin name.abuchen:fix-info-plist-maven-plugin application/org.openjdk.jmc.rcp.product

%pom_remove_plugin org.codehaus.mojo:buildnumber-maven-plugin
%pom_remove_plugin org.apache.maven.plugins:maven-deploy-plugin

TYCHO_ENV="<environment><os>linux</os><ws>gtk</ws><arch>%{eclipse_arch}</arch></environment>"
%pom_xpath_set "pom:configuration/pom:environments" "$TYCHO_ENV"

%build

# some tests require large heap and fail with OOM
# depending on the builder resources
%mvn_build -j -- -Dmaven.test.failure.ignore=true -DbuildId=rhel -DbuildNumber=%{revhash} -Dbuild.date=%{revdate}

%install

# not using mvn_install macro because it installs JMC as an Eclipse plugin
# we want to install JMC as an RCP application

# change jmc.ini to use system java (remove -vm option line)
sed -i '/^-vm$/d' %{_builddir}/%{tarball_name}/target/products/org.openjdk.jmc/%{_os}/gtk/%{eclipse_arch}/%{name}.ini
sed -i '/^..\/..\/bin\/$/d' %{_builddir}/%{tarball_name}/target/products/org.openjdk.jmc/%{_os}/gtk/%{eclipse_arch}/%{name}.ini

# add IgnoreUnrecognizedVMOptions flag to allow running on OpenJDK 8 without 'Unrecognized VM option' error
sed -i '/^-vmargs$/a -XX:+IgnoreUnrecognizedVMOptions' %{_builddir}/%{tarball_name}/target/products/org.openjdk.jmc/%{_os}/gtk/%{eclipse_arch}/%{name}.ini

# move contents of target/products/org.openjdk.jmc/${_os}/gtk/%{eclipse_arch}/ to /usr/lib/jmc/
install -d -m 755 %{buildroot}%{_jmcdir}
cp -p -r %{_builddir}/%{tarball_name}/target/products/org.openjdk.jmc/%{_os}/gtk/%{eclipse_arch}/* %{buildroot}%{_jmcdir}/

# move jmc.ini to /etc/jmc.ini
install -d -m 755 %{buildroot}%{_sysconfdir}
mv %{buildroot}%{_jmcdir}/%{name}.ini %{buildroot}%{_sysconfdir}/%{name}.ini
ln -s %{_sysconfdir}/%{name}.ini %{buildroot}%{_jmcdir}/%{name}.ini

# create symlink to jmc in /usr/bin/
install -d -m 755 %{buildroot}%{_bindir}
ln -s %{_jmcdir}/%{name} %{buildroot}%{_bindir}/%{name}

# replace jars with symlinks to installed libraries
bash %{SOURCE3} %{buildroot}%{_jmcdir}/plugins %{_javadir} %{_jnidir} %{_javadir_maven} %{_jnidir_maven} %{_javadir}/jmc-core

# create application launcher in desktop menu
install -d -m 755 %{buildroot}%{_datadir}/pixmaps
mv %{buildroot}%{_jmcdir}/icon.xpm %{buildroot}%{_datadir}/pixmaps/%{name}.xpm
chmod 644 %{buildroot}%{_datadir}/pixmaps/%{name}.xpm
desktop-file-install --dir=%{buildroot}%{_datadir}/applications %{SOURCE1}

# install pom file
install -d -m 755 %{buildroot}%{_datadir}/maven-poms/%{name}
install -p -m 644 %{_builddir}/%{tarball_name}/pom.xml %{buildroot}%{_datadir}/maven-poms/%{name}/%{name}.pom

# install manpage and insert location of config file
install -d -m 755 %{buildroot}%{_mandir}/man1
install -p -m 644 %{SOURCE2} %{buildroot}%{_mandir}/man1/%{name}.1
sed -i "/.SH FILES/a .I %{_sysconfdir}/%{name}.ini" %{buildroot}%{_mandir}/man1/%{name}.1

%files
%license license/LICENSE.txt
%license license/THIRDPARTYREADME.txt
%doc README.md
%config(noreplace) %{_sysconfdir}/%{name}.ini
%{_jmcdir}
%{_mandir}/man1/%{name}.1*
%{_bindir}/%{name}
%{_datadir}/maven-poms/%{name}
%{_datadir}/pixmaps/%{name}.xpm
%{_datadir}/applications/%{name}.desktop

%changelog
* Tue Oct 05 2021 Alex Macdonald <almacdon@redhat.com> - 8.0.1-4
- Rebuild with updated dependencies

* Thu Aug 26 2021 Alex Macdonald <almacdon@redhat.com> - 8.0.1-3
- Bump version to build with updated tycho

* Wed Aug 19 2021 Alex Macdonald <almacdon@redhat.com> - 8.0.1-2
- Re-set the buildId, buildNumber, and build.date during maven build

* Tue Aug 10 2021 Alex Macdonald <almacdon@redhat.com> - 8.0.0-1
- Update to jmc 8.0.1-ga

* Tue Aug 10 2021 Alex Macdonald <almacdon@redhat.com> - 8.1.0-1
- Update to jmc-ga tagged commit d0f89f0

* Wed Feb 24 2021 Alex Macdonald <almacdon@redhat.com> - 8.0.0-8
- Set the buildId, buildNumber, and build.date during maven build

* Fri Feb 19 2021 Alex Macdonald <almacdon@redhat.com> - 8.0.0-7
- Fix incorrect macro for name

* Fri Feb 19 2021 Alex Macdonald <almacdon@redhat.com> - 8.0.0-6
- Revert previous JAVA_HOME export
- Add patch to remove use of List.of in GraphView

* Fri Feb 19 2021 Alex Macdonald <almacdon@redhat.com> - 8.0.0-5
- Export JAVA_HOME to be openjdk 11 

* Thu Feb 18 2021 Alex Macdonald <almacdon@redhat.com> - 8.0.0-4
- Revert usage of ResourceLocator to be eclipse 4.12 compliant

* Wed Feb 17 2021 Alex Macdonald <almacdon@redhat.com> - 8.0.0-3
- Revert removal of fix-javamail patch

* Wed Feb 17 2021 Alex Macdonald <almacdon@redhat.com> - 8.0.0-2
- Revert osgi reference from jakarta.annotation to javax.annotation

* Fri Feb 12 2021 Alex Macdonald <almacdon@redhat.com> - 8.0.0-1
- Update to jmc8 branch commit 8ab40bf

* Thu Apr 23 2020 Alex Macdonald <almacdon@redhat.com> - 7.1.1-5
- Update jacoco removal patch

* Thu Apr 23 2020 Alex Macdonald <almacdon@redhat.com> - 7.1.1-4
- Update to latest commit e67446b5fc9d

* Fri Apr 17 2020 Alex Macdonald <almacdon@redhat.com> - 7.1.1-3
- include jmc-core in the directories to search in symlink_libs.sh

* Fri Apr 17 2020 Alex Macdonald <almacdon@redhat.com> - 7.1.1-2
- Remove jacoco from the pom and disable coverage

* Thu Apr 16 2020 Alex Macdonald <almacdon@redhat.com> - 7.1.1-1
- Updated to version 7.1.1

* Thu Nov 14 2019 Jie Kang <jkang@redhat.com> - 7.0.0-4
- Fix requires

* Wed Nov 13 2019 Jie Kang <jkang@redhat.com> - 7.0.0-3
- Fix exclusions

* Wed Nov 13 2019 Jie Kang <jkang@redhat.com> - 7.0.0-2
- Update require and provide exclusions

* Tue Mar 12 2019 Jie Kang <jkang@redhat.com> - 7.0.0-1
- Initial package
