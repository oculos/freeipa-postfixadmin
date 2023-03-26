from ipalib import _, Bool, Str, errors, Int, Flag, ngettext
from ipalib import output, api, Command
from ipalib.output import Output, Entry, ListOfEntries
from ipalib.plugable import Registry
from ipalib.util import validate_domain_name
from ipalib.parameters import *
from ipapython.dn import DN
from ipapython.ipavalidate import Email
from ipaserver.plugins.baseldap import LDAPDelete, LDAPCreate,LDAPObject, LDAPUpdate, LDAPRetrieve, LDAPSearch, add_missing_object_class, LDAPQuery, pkey_to_value
from ipaserver.plugins.group import group, group_add, group_mod
from ipaserver.plugins.host import host, host_add
from ipaserver.plugins.user import user, user_add, user_mod, user_show

__doc__ = _("""
Mail server configuration

Configure mailboxes and mail routing.
""")

register = Registry()


@register()
class domain(LDAPObject):
    """
    Global postfix configuration (e.g virtual domains)
    """
    object_name = _('postfix configuration')
    default_attributes = [
        'cn'
    ]
    container_dn = DN(('cn', 'postfix'), ('cn', 'mailserver'), ('cn', 'etc'))
    permission_filter_objectclasses = ["postfixDomain"]
    object_class = ['postfixDomain']
    search_attributes = [ 'cn' ]
    label = _('Domains')
    label_singular = _('Domain')

    takes_params = (
        Str('cn',
            cli_name='domain',
            label=_('Domain'),
            primary_key = True
            ),
        Str('maxaliases?',
            cli_name='maxaliases',
            label=_('Max aliases')
	    ),
       Str('domainquota?',
            cli_name='quota',
            label=_('Domain quota')
	    ),
        Bool('status',
             cli_name='active',
             label=_('Active domain'),
             default=False,
 	    ),
        Bool('isbackupmx',
             cli_name='active',
             label=_('Is backup MX'),
             default=False
 	    ),
    )


@register()
class domain_mod(LDAPUpdate):
    __doc__ = _('Modify Postfix configuration')

    def pre_callback(self, ldap, dn, entry_attrs, attrs_list, *keys, **options):
        if 'cn' in entry_attrs:
                try:
                    validate_domain_name(entry_attrs['cn'])
                except ValueError:
                    raise errors.ValidationError(name='cn', error=_('Invalid domain format'))

        return dn

@register()
class domain_show(LDAPRetrieve):
    __doc__ = _('Show Postfix configuration')



@register()
class domain_find(LDAPSearch):
    __doc__ = _('Search Domains');
    msg_summary = ngettext(
        '%(count)d Domain matched',
        '%(count)d Domains matched', 0
        )


@register()
class domain_del(LDAPDelete):
    __doc__ = _('Delete a virtual domain.');
    msg_summary = _('Deleted virtual domain %(value)s')

@register()
class domain_add(LDAPCreate):
    __doc__ = _('Create a new Domain.')
    msg_summary = _('Created the domain %(value)s.')


    def pre_callback(self, ldap, dn, entry_attrs, attrs_list, *keys, **options):
        if 'cn' in entry_attrs:
                try:
                    validate_domain_name(entry_attrs['cn'])
                except ValueError:
                    raise errors.ValidationError(name='cn', error=_('Invalid domain format'))
        
        entry_attrs['objectClass'] = ['postfixDomain','nsContainer'] 
        return dn


    def post_callback(self, ldap, dn, entry_attrs, *keys, **options):
        return dn
        
        
@register()
class mailbox(LDAPObject):
    """
    Global postfix configuration for virtual mailboxes, ie., mailboxes for non-ipausers
    """
    container_dn = DN(('cn', 'postfix'), ('cn', 'mailserver'), ('cn', 'etc'))
    parent_object = 'domain'
    object_class = ['postfixMailbox']
    object_name = _('Mailboxes configuration')
    default_attributes = [
        'uid','cn','postfixMailAddress','status'
    ]
    password_attributes = [('userPassword','userpassword')]
#    container_dn = container_dn
    permission_filter_objectclasses = ["postfixMailbox"]
    search_attributes = [ 'uid','cn','status' ,'postfixMailAddress']
    label = _('Mailboxes')
    label_singular = _('Mailbox')

    takes_params = (
        Str('uid',
            cli_name='mailbox',
            label=_('Mailbox'),
            primary_key = True
            ),
        Str('givenname',
            cli_name='givenname',
            label=_('Given Name'),
            ),
        
        Str('sn',
            cli_name='surname',
            label=_('Surname'),
            ),
        Int('mailquota',
            cli_name='mailquota',
            label=_('Mail Quota'),
            required=False
        ),

        Password('userpassword',
            cli_name='password',
            label=_('Password'),
            ),
        Bool('status',
            cli_name='active',
            label=_('Active'),
            default=False
             )
    )


@register()
class mailbox_mod(LDAPUpdate):
    __doc__ = _('Modify Mailbox attributes')

    def pre_callback(self, ldap, dn, entry_attrs, attrs_list, *keys, **options):
        attrs = ldap.get_entry(dn)
        
        sn = entry_attrs['sn'] if 'sn' in entry_attrs else attrs['sn'][0]
        givenName = entry_attrs['givenName'] if 'givenName' in entry_attrs else attrs['givenName'][0]
        print (sn)
        print (givenName)
        entry_attrs['cn'] = givenName+' '+sn

        return dn
    
    

@register()
class mailbox_show(LDAPRetrieve):
    __doc__ = _('Show Mailboxes')



@register()
class mailbox_find(LDAPSearch):
    __doc__ = _('Search Mailboxes');
    msg_summary = ngettext(
        '%(count)d Domain matched',
        '%(count)d Domains matched', 0
    )

@register()
class mailbox_del(LDAPDelete):
    __doc__ = _('Delete a virtual domain.');
    msg_summary = _('Deleted virtual domain %(value)s')

@register()
class mailbox_add(LDAPCreate):
    __doc__ = _('Create a new Mailbox.')
    msg_summary = _('Created the domain %(value)s.')


    def pre_callback(self, ldap, dn, entry_attrs, attrs_list, *keys, **options):
        
        entry_attrs['objectClass'] = ['postfixMailbox','person', 'inetOrgPerson','inetUser']
        entry_attrs['cn'] = entry_attrs['givenName']+' '+entry_attrs['sn'] 
        entry_attrs['postfixMailAddress'] = entry_attrs['uid']+"@"+keys[0]
        #exists = ldap.find_entry_by_attr('postfixMailAddress',entry_attrs['postfixMailAddress'],'postfixMailbox')
        #if exists:
        #    raise errors.ValidationError(name='mailbox', error=_('The e-mail address already exists.'))
        
        return dn


    def post_callback(self, ldap, dn, entry_attrs, *keys, **options):
        return dn
        

@register()
class alias(LDAPObject):
    """
    Global postfix configuration for mail aliases
    """
    container_dn = DN(('cn', 'postfix'), ('cn', 'mailserver'), ('cn', 'etc'))
    parent_object = 'domain'
    object_name = _('Aliases configuration')
    object_class = ['postfixAlias']
    default_attributes = [
        'uid','cn','postfixMailAlias','status','postfixMailDestination'
    ]
    #password_attributes = [('userPassword','userpassword')]
#    container_dn = container_dn
    permission_filter_objectclasses = ["postfixAlias"]
    search_attributes = [ 'uid','cn','status' ,'postfixMailAlias','postfixMailDestination']
    label = _('Aliases')
    label_singular = _('Aliases')

    takes_params = (
        Str('uid',
            cli_name='alias',
            label=_('Alias'),
            primary_key = True
            ),
        Str('postfixmaildestination+',
            cli_name='mailbox',
            label=_('Mailbox'),
            ),
        Bool('status',
            cli_name='active',
            label=_('Active')
             )
    )


@register()
class alias_mod(LDAPUpdate):
    __doc__ = _('Modify Mailbox attributes')

    def pre_callback(self, ldap, dn, entry_attrs, attrs_list, *keys, **options):
        attrs = ldap.get_entry(dn)
        return dn
    
@register()
class alias_show(LDAPRetrieve):
    __doc__ = _('Show Mailboxes')



@register()
class alias_find(LDAPSearch):
    __doc__ = _('Search Aliases');
    msg_summary = ngettext(
        '%(count)d Alias matched',
        '%(count)d Aliases matched', 0
    )

@register()
class alias_del(LDAPDelete):
    __doc__ = _('Delete a mail alias.');
    msg_summary = _('Deleted mail alias %(value)s')

@register()
class alias_add(LDAPCreate):
    __doc__ = _('Create a new Mail Alias.')
    msg_summary = _('Created the mail alias %(value)s.')


    def pre_callback(self, ldap, dn, entry_attrs, attrs_list, *keys, **options):
        
        entry_attrs['objectClass'] = ['postfixAlias']
        #entry_attrs['cn'] = entry_attrs['givenName']+' '+entry_attrs['sn'] 
        entry_attrs['postfixMailAlias'] = entry_attrs['uid']+"@"+keys[0]
        #exists = ldap.find_entry_by_attr('postfixMailAddress',entry_attrs['postfixMailAddress'],'postfixMailbox')
        #if exists:
        #    raise errors.ValidationError(name='mailbox', error=_('The e-mail address already exists.'))
        
        return dn


    def post_callback(self, ldap, dn, entry_attrs, *keys, **options):
        return dn
        
@register()
class virtualdomain(LDAPObject):
    """
    Virtual domains - domain aliases
    """
    parent_object = 'domain'
    object_name = _('Virtual domains')
    object_class = ['postfixVirtualDomain']
    default_attributes = [
        'uid', 'status'
    ]
    container_dn = DN(('cn', 'postfix'), ('cn', 'mailserver'), ('cn', 'etc'))
    permission_filter_objectclasses = ["postfixVirtualDomain"]
    search_attributes = [ 'uid','realDomain','status' ]
    label = _('Alias domains')
    label_singular = _('Alias domain')

    takes_params = (
        Str('uid',
            cli_name='alias',
            label=_('Alias domain'),
            primary_key = True
            ),
        Bool('status',
            cli_name='active',
            label=_('Active'),
            default=False
             )
    )


@register()
class virtualdomain_mod(LDAPUpdate):
    __doc__ = _('Modify Postfix configuration')

    def pre_callback(self, ldap, dn, entry_attrs, attrs_list, *keys, **options):
        if 'uid' in entry_attrs:
                try:
                    validate_domain_name(entry_attrs['uid'])
                except ValueError:
                    raise errors.ValidationError(name='uid', error=_('Invalid domain name format'))

        return dn

@register()
class virtualdomain_show(LDAPRetrieve):
    __doc__ = _('Show Postfix configuration')



@register()
class virtualdomain_find(LDAPSearch):
    __doc__ = _('Search Domains');
    msg_summary = ngettext(
        '%(count)d Domain matched',
        '%(count)d Domains matched', 0
    )

@register()
class virtualdomain_del(LDAPDelete):
    __doc__ = _('Delete a virtual domain.');
    msg_summary = _('Deleted virtual domain %(value)s')

@register()
class virtualdomain_add(LDAPCreate):
    __doc__ = _('Create a new Domain.')
    msg_summary = _('Created the domain %(value)s.')


    def pre_callback(self, ldap, dn, entry_attrs, attrs_list, *keys, **options):
        entry_attrs['objectClass'] = ['postfixVirtualDomain'] 
        entry_attrs['realDomain'] = keys[0]
        if 'uid' in entry_attrs:
                try:
                    validate_domain_name(entry_attrs['uid'])
                except ValueError:
                    raise errors.ValidationError(name='cn', error=_('Invalid domain name format'))
        
        return dn


    def post_callback(self, ldap, dn, entry_attrs, *keys, **options):
        return dn

@register()
class configuration(LDAPObject):
    """
    Virtual domains - domain aliases
    """
    object_name = _('Virtual domains')
    object_class = ['postfixConfig']
    default_attributes = [
        'uid', 'defaultDomain'
    ]
    container_dn = DN(('uid','config'),('cn', 'postfix'), ('cn', 'mailserver'), ('cn', 'etc'))
    permission_filter_objectclasses = ["postfixConfig"]
    search_attributes = [ 'uid','defaultdomain' ]
    label = _('Configurations')
    label_singular = _('Configuration')

    takes_params = (
  
       
        Str('defaultdomain',
            cli_name='defaultdomain',
            label=_('Fuck this shit')
        )
    )
    
    def get_dn(self, *keys, **kwargs):
        return DN(('uid', 'config'),('cn','postfix'),('cn','mailserver'), ('cn', 'etc'), api.env.basedn)


@register()
class configuration_mod(LDAPUpdate):
    __doc__ = _('Modify Postfix configuration')

    def pre_callback(self, ldap, dn, entry_attrs, attrs_list, *keys, **options):

        return dn

@register()
class configuration_show(LDAPRetrieve):
    __doc__ = _('Show Postfix configuration')
 


@register()
class configuration_del(LDAPDelete):
    __doc__ = _('Delete a virtual domain.');
    msg_summary = _('Deleted virtual domain %(value)s')


# User configuration
user.takes_params += (
    Bool('status',
        cli_name='activemailbox',
        label=_('Active postfix mailbox'),
        default=False
         ),
    Bool('createmailbox',
        cli_name='createmailbox',
        label=_('Create mailbox'),
        flags=['virtual_attribute'],
        required=False)
        )

user.default_attributes = user.default_attributes + ['postfixmailaddress','mailquota','status']

def useradd_pre_callback(self, ldap, dn, entry_attrs, attrs_list, *keys, **options):
    #add_missing_object_class(ldap, 'postfixMailBox', dn, entry_attrs, update=False)
    config = ldap.find_entry_by_attr('uid','config','postfixConfig')
    #entry_attrs['objectClass'].append('postfixMailBox')
    #entry_attrs['postfixMailAddress'] = entry_attrs['uid']+'@'+config['defaultDomain'][0]
    return dn
    
user_add.register_pre_callback(useradd_pre_callback)