
#--------------------------
# Metadata
#-------------------------- 
Name:          RemoteHostFileSyncService
Summary:       remote host file sync Service package
Version:       1.00
Release:       1
BuildArch:     x86_64
Group:         Applications/Other
Packager:      rhfs Core Build Service
%description

+ remote_host_file_sync_service-1.0.0-py2.7.egg
+ rhfsservice

%define _unpackaged_files_terminate_build 0

#--------------------------
# install
#-------------------------- 
%pre
exit 0

%install
exit 0

%post
chkconfig --add rhfsservice
exit 0

#--------------------------
# uninstall
#-------------------------- 
%preun
exit 0

%postun
# Post uninstall runs AFTER the install of a new upgrade RPM
# so we need to check for the upgrade condition and only run
# when this is not an upgrade.
# $1 == 1 on upgrade
# $1 == 0 on uninstall
#
#if [ $1 -lt 1 ] ; then
#fi
chkconfig --del rhfsservice
exit 0

#--------------------------
# File list
#-------------------------- 
%files

%attr(644,root,root) /opt/plugins/remote_host_file_sync_service-1.0.0-py2.7.egg
%attr(755,root,root) /etc/init.d/rhfsservice

