// Copyright © 2016 Jeffery Harrell <jefferyharrell@gmail.com>
// See file 'LICENSE' for use and warranty information.
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

define(
    ['freeipa/builder',  'freeipa/_base/Spec_mod','freeipa/ipa', 'freeipa/menu', 'freeipa/phases', 'freeipa/reg', 'freeipa/user',  'freeipa/dialog'],
    function(builder,Spec_mod, IPA, menu, phases, reg,user,dialogs,user_mod) {
        function get_item_by_attrval(array, attr, value) {
            for (let i = 0, l = array.length; i < l; i++) {
                if (array[i][attr] === value) return array[i];
            }
            return null;
        }

        function get_index_by_attrval(array, attr, value) {
            for (let i = 0, l = array.length; i < l; i++) {
                if (array[i][attr] === value) return i;
            }
            return null;
        }


        var exp = IPA.postfixadmin = {};

        exp.configuration_spec = {
          name: 'configuration',
          defines_key: false,
          facets: [
            {
              $type: 'details',
              fields: [//'uid',
                {
                  $type: 'entity_select',
                  name: 'defaultdomain',
                  label: 'Default domain for ipa users\' mailbox',
                  other_entity: 'domain',
                  other_field: 'cn'
                }
              ]
            }
          ]
        }

  exp.list_of_domains_spec =  {
    name: 'domain',
    facet_groups: ['settings', 'mailboxesfacetgroup','aliasesfacetgroup','virtualdomainsfacetgroup'],
    facets: [
      {
        $type: 'search',
        columns:
          [
            'cn'
          ]
      },
      {
         $type: 'details',
         fields: [
           { name: 'cn'},
           { name: 'maxaliases' },
           { name: 'domainquota' },
           {  $type: 'checkbox', name: 'isbackupmx' },
           {  $type: 'checkbox', name: 'status' }
                 ]
      },
      {
          $type: 'nested_search',
          facet_group: 'mailboxesfacetgroup',
          nested_entity: 'mailbox',
          search_all_entries: true,
          label: 'Mailboxes',
          tab_label: 'Mailboxes',
          name: 'mailboxes',
          columns: [
            {
               name: 'uid'
            },
            {
               name: 'cn', label: 'Full Name'
            },
            {
               name: 'postfixmailaddress', label: 'Mailbox'
            },
            {
               name: 'mailquota'
            },
            {
               $type: 'boolean_status',name : 'status', label: '@i18n:status.label',
               formatter: {
                 $type: 'boolean_status',
                          }
            }
                  ]
       },
       {
          $type: 'nested_search',
          facet_group: 'aliasesfacetgroup',
          nested_entity: 'alias',
          search_all_entries: true,
          label: 'Aliases',
          tab_label: 'Aliases',
          name: 'aliases',
          columns: [
            {
              name: 'uid'
             },
            'postfixmaildestination',
            {
               $type: 'boolean_status',name : 'status', label: '@i18n:status.label',
               formatter: {
                 $type: 'boolean_status',
                          }
            }
                   ]
        },
        {
          $type: 'nested_search',
          facet_group: 'virtualdomainsfacetgroup',
          nested_entity: 'virtualdomain',
          search_all_entries: true,
          label: 'Virtual domains',
          tab_label: 'Alias domains',
          name: 'virtualdomains',
          columns: [
            { name: 'uid' },
            { name: 'realdomain'},
            {
               $type: 'boolean_status',
               name : 'status', 
               label: '@i18n:status.label',
               formatter: 
                 {
                    $type: 'boolean_status',
                 }
            }
                   ]
         }
     ],
     adder_dialog: 
       {
         fields: 
       [
             {
               name: 'cn',
             }
           ]
       }
  }

  exp.mailboxes_spec =  
    {
      name: 'mailbox',
      containing_entity: 'domain',
      facets: 
        [
          {
             $type: 'details',
             fields: 
               [
                  { name: 'postfixmailaddress', read_only: true, label: "Mailbox"},
                   //{ name: 'cn', readonly: true },
                  { name: 'givenname'},
                  { name: 'sn'},
                  { name: 'mailquota'},
                   //  { $type: 'password', name: 'userpassword', readonly: true},
                  { $type: 'checkbox',name : 'status' }
               ]
          }
        ],
      adder_dialog: 
        {
          fields: 
            [
               { name: 'uid',},
               { name: 'sn' },
               { name: 'givenname' },
               { name: 'mailquota'},
               { $type: 'password', name: 'userpassword'},
               { $type: 'checkbox',name : 'status' }
             ]
        }
  }

  exp.aliases_spec =  
	  {
      name: 'alias',
      containing_entity: 'domain',
      facets: 
        [
          {
             $type: 'details',
             fields: 
               [
                  { name: 'postfixmailalias', read_only: true, label: "Alias"},
                  { $type: 'multivalued', name: 'postfixmaildestination'},
                  //  { $type: 'password', name: 'userpassword', readonly: true},
                  { $type: 'checkbox',name : 'status' }
               ]
          }
         ],
      adder_dialog: 
			{  
           fields: 
             [
               { name: 'uid',tooltip: "Use '*' for a catchall address."},
               { $type: 'multivalued', name: 'postfixmaildestination'},
               { $type: 'checkbox',name : 'status' }
             ]
         }
  }

  exp.virtualdomains_spec =  
	  {
       name: 'virtualdomain',
       containing_entity: 'domain',
       facets: 
         [ 
           {
             $type: 'details',
             fields: 
               [
                  {  name: 'uid'},
                  { $type: 'checkbox', name : 'status' }
                  //  { $type: 'password', name: 'userpassword', readonly: true},
               ]
           }
         ],
	     adder_dialog: 
			   {
           fields: 
					   [
               { name: 'uid' },
               { $type: 'checkbox', name : 'status' }
             ]
         }
  };

  exp.mod_user_spec = function (entity) 
	  {
			let facet = get_item_by_attrval(entity.facets, '$type', 'details');
      let adder = entity.adder_dialog;
       //console.log(adder.sections[1]);
      adder.sections[1].fields.push(
        { $type: 'checkbox',
          name: 'createmailbox'
         }
      );

			
		//	if (postfixMailAdminValue.trim() !== '') {
			  let mail_section = {
			                 name: 'postfixMail',
			                 label: 'Mail',
			                 fields: [
			                   { name: 'postfixmailaddress', read_only: true, label: "Mailbox", tooltip: "If a mailbox for this user exists, its address will be shown here. Use the Actions menu to create a mailbox."},
			                    //{ name: 'cn', readonly: true },
		              
			                   { name: 'mailquota', label: "Quota"},
			                    //  { $type: 'password', name: 'userpassword', readonly: true},
			                   { $type: 'checkbox',name : 'status' }
					             ],
		                 
			             };
				facet.sections.splice(1, 0, mail_section);
//				facet.sections.push(mail_section);
		//	}
		
			facet.actions.push({
			   $factory: IPA.object_action,
			   name: 'create_mailbox',
			   method: 'create_mailbox',
			   label: 'Create mailbox',
				 hide_cond: ['postfixMailAddress']
			   
			   });
				 
	 			facet.actions.push({
	 			   $factory: IPA.object_action,
	 			   name: 'delete_mailbox',
	 			   method: 'delete_mailbox',
	 			   label: 'Delete mailbox',
	 				 hide_cond: ['postfixMailAddress','postfixMailBox']
			   
	 			   });
				
			facet.header_actions.push('create_mailbox');
			facet.header_actions.push('delete_mailbox');
			

  };

	  exp.user_override = function () {
	            exp.mod_user_spec(user.entity_spec);
	        };


        exp.register = function() {
            let e = reg.entity;
            let a = reg.action;
            let d = reg.dialog;

            e.register({type: 'domain', spec: exp.list_of_domains_spec});
            e.register({type: 'mailbox', spec: exp.mailboxes_spec});
            e.register({type: 'alias', spec: exp.aliases_spec});
            e.register({type: 'virtualdomain', spec: exp.virtualdomains_spec});
            e.register({type: 'configuration', spec: exp.configuration_spec});
           


        }


//// menu spec ////////////////////////////////////////////////////////////////


        exp.postfix_menu_spec = {
            name: 'postfix',
            label: 'Postfix',
            children: [
              {entity: 'configuration'},
              {entity: 'domain',
              children: [{entity: 'mailbox',hidden: true},
                         {entity: 'alias',hidden: true},
                         {entity: 'virtualdomain',hidden: true}
                        ]
              }

                       // {entity: 'mailbox', hidden: true}
                        ]
        }


        exp.add_menu_items = function() {
	      list_of_menus = menu.query();
            network_services_item = menu.query({name: 'identity'});

            if (network_services_item.length > 0) {
                menu.add_item( exp.postfix_menu_spec );

            }
        }

        phases.on('registration', exp.register);
        phases.on('profile', exp.add_menu_items, 20);
        phases.on('customization', exp.user_override);
  
    
        return exp;

    }
);
