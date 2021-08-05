import re
from django.dispatch import receiver
from django_auth_ldap.backend import populate_user, LDAPBackend


@receiver(populate_user, sender=LDAPBackend)
def ldap_auth_handler(user, ldap_user, **kwargs):
  
    # Check all of the user's group names to see if they belong
    # in a group that match what we're looking for.
    for group_name in ldap_user.group_names:
            match = re.match(r"^Staff ([\w\d\s-]+)$", group_name)
        if match is None:
            continue
        
        # Store the market name
        market_name = match.group(1).strip()
        group_name = "Staff"
        
        # Since this signal is called BEFORE the user object is saved to the database,
        # we have to save it first so that we then can assign groups to it.
        user.save()
        
        # Add user to the Staff Django group.
        group = Group.objects.get(name=group_name)
        user.grous.add(group)
        
        try:
            market = Market.objects.get(name=market_name)
            user.markets.add(market)
        except ObjectDoesNotExist:
            logger.error(f"Attempted to add user to market {market_name} that doesnt exist")


  """
    Django Signal handler that assign user to Group 
    
    This signal gets called after Django Auth LDAP Package have populated
    the user with its data, but before the user is saved to the database.
    """