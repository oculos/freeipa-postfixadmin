#! /bin/bash

cp config/70-postfixadmin.* /usr/share/ipa/update/.
cp plugin/postfixadmin.py /usr/lib/python3.9/site-packages/ipaserver/plugins/.
mkdir -p /usr/share/ipa/ui/js/plugins/postfixadmin
cp ui/postfixadmin.js /usr/share/ipa/ui/js/plugins/postfixadmin/postfixadmin.js


ipa-ldap-updater --schema-file "/usr/share/ipa/updates/70-postfixadmin.ldif"
ipa config-mod --addattr=ipaUserObjectClasses=postfixMailBox
systemctl restart httpd
