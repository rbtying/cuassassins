import ldap

def search(uni):
    ld = ldap.initialize('ldap://ldap.columbia.edu')
    try:
        ld.simple_bind_s()
        basedn = "ou=People,o=Columbia University,c=US"
        filter = "(uni=" + uni + ")"
        results = ld.search_s(basedn, ldap.SCOPE_SUBTREE, filter)
    except ldap.LDAPError, e:
        if type(e.message) == dict and e.message.has_key('desc'):
            print e.message['desc']
        else: 
            print e
    finally:
        ld.unbind()
    if len(results) == 0:
        return None
    return results[0][1]

def verify_uni(uni):
    response = search(uni)
    return not response == None
