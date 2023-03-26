# freeipa-postfixadmin
A [FreeIPA](https://www.freeipa.org) plugin for mimicking PostfixAdmin functionality

## Warning!

This is not a ready product, and some functionality is missing. Even when that functionality is added, not sure if everything one would expect from this plugin is implemented. This was written with small deployments in mind. 

### Description

This plugin attemps to create an interface that mimics [Postfix Admin](https://github.com/postfixadmin/postfixadmin). I want to migrate my mailbox configuration from MySQL to FreeIPA, and thus being able to get better synchronization of mailbox configuration (currently I am using MySQL replication).

### Isn't there a plugin for that already?

Yes. [FreeIPA-mailserver](https://github.com/Carbenium/freeipa-mailserver) is an excellent plugin, and it is production ready, in my opinion. The reason why I decided to write my own is that I want to have more separation between FreeIPA users and groups from Postfix virtual mailboxes, aliases and virtual domains. 

I am writing this plugin to replicate as much as possible my current experience with Postfix Admin.

### Description of the elements:

This plugin creates a few `objectClasses` so that few attributes present on FreeIPA are reused, so that other plugins might not use the same components here. A notable exception is the attributeType `status`, which is used to enable/disable items such as domains, mailboxes and aliases.

- `domains` are containers under `cn=postfix,cn=mailserver,cn=etc`. They contain `mailboxes`, `aliases` and `domain aliases`.
- `mailboxes` can be attributted to normal ipa users or to records created under domains. So a postfix query needs to check for the objectclass `postfixMailBox` under a domain container and to normal ipa users records under `cn=users...`.
- `aliases` are records with a `postfixMailDestination` address, which is supposed to be a mailbox.
- `virtual domains` are domains that points to another domain.

There is also a configuration for the default domain for new mailboxes - similarly to the Ipa Server configuration for default e-mail domains. 

Ipa users can have only one mailbox (`postfixMailAddress`) attribute. When adding a new user, the admin will be able to create this mailbox, which will always be `uid`@`defaultDomain`.

### To-Do

- Finishing the UI for adding a mailbox to new and existing users
- Adding validations everywhere (for example, so that a new user mailbox won't be a duplicate of an existing non-user mailbox). Validations are also needed regarding e-mail addresses.
- Streamlined installation and installation instructions;
- Documentation on how to configure Postfix and Dovecot to query the right objects.
- Permission configurations. As of now there is no permission configuration for the mailboxes, domains, etc. Only admins can edit Postfix configurations.

### Notable features from Postfix Admin not available here

- Color tagging different status, such as aliases to e-mails that are not known to the server;
- Sending test and welcome e-mails;
- Changing passwords of mailboxes - This will be developed at some point, but my main goal is to use Keycloak to provide a user interface for this. 

### Screenshots

Here are some screenshots for how it looks so far:

<img width="1098" alt="Screenshot 2023-03-26 at 21 50 22" src="https://user-images.githubusercontent.com/6791923/227801359-4cf03e81-0d2a-4037-9f51-ebd121fc0240.png">
<img width="1106" alt="Screenshot 2023-03-26 at 21 50 37" src="https://user-images.githubusercontent.com/6791923/227801370-1b3be507-3856-45c8-9248-5e0e8f9e2002.png">



<img width="1102" alt="Screenshot 2023-03-26 at 21 51 12" src="https://user-images.githubusercontent.com/6791923/227801377-df45bc97-5ea6-4949-804e-c79547580c2d.png">
<img width="1098" alt="Screenshot 2023-03-26 at 21 52 36" src="https://user-images.githubusercontent.com/6791923/227801392-e3fa0176-2655-49bf-8e00-1585650dc53f.png">

<img width="1099" alt="Screenshot 2023-03-26 at 21 52 24" src="https://user-images.githubusercontent.com/6791923/227801398-efd5becd-051f-4a9a-9286-5b7964fa195e.png">
