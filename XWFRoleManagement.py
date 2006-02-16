from Products.XWFMetadata.XWFMetadata import XWFMetadataValidation
from AccessControl.PermissionRole import rolesForPermissionOn
import types

class XWFRoleManagement(XWFMetadataValidation):
    meta_type = 'XWF Security Metadata'
    id = 'xwf_roles'
    
    label = "Visible to roles"
    hint = "To which roles should this item be visible"
    
    required = True
    requiredError = "One or more roles must be specified"
    
    def __init__(self, permission_to_manage='View'):
        self.permission_to_manage = permission_to_manage
        
    def xform_data(self, datacontainer, form):
        if form.has_key(self.id):
            roles = form[self.id]
            if type(roles) == types.StringType:
                roles = [roles]
        else:
            id = form.get('id', None)
            # if we have an ID, we should be dealing with the real object
            # rather than it's container
            if id:
                obj = getattr(datacontainer, id)
            else:
                obj = datacontainer
                
            roles = rolesForPermissionOn(self.permission_to_manage, obj)
        
        # we remove the Manager role, because we should never be adding/removing
        # it
        try:
            roles.remove('Manager')
        except:
            pass
        
        f = """<%s>%s</%s>""" % (self.id, ' '.join(roles), self.id)
        
        return f
        
    def xform_control(self, obj, model_id, cssclass='text'):
        x = """<xf:item>
                  <xf:label>%s</xf:label>
                  <xf:value>%s</xf:value>
               </xf:item>"""
        
        items = []
        for role in obj.valid_roles():
            if role != 'Manager':
                items.append(x % (role, role))
        
        f = """<xf:select appearance="minimal"
                          model="%s"
                          %s="%s" class="%s">
                   <xf:label>%s</xf:label>
                   <xf:hint>%s</xf:hint>
                   %s
                </xf:select>""" % (model_id, self.required and 'bind' or 'ref',
                                   self.id, cssclass, self.label, 
                                   self.hint, '\n'.join(items))
        return f
        
    def set_permissions(self, obj, new_roles, assume_acquire=True):
        roles = list(rolesForPermissionOn(self.permission_to_manage, obj))
        new_roles = list(new_roles)
        roles.sort()
        new_roles.sort()
        # if assume_acquire is set, we assume that if the new_roles match
        # the existing roles, we are wanting to keep getting those roles via
        # acquisition, or at least, that we shouldn't do anything
        if assume_acquire and roles == new_roles:
            return
        
        # We _always_ want the Manager role added, otherwise we might never get
        # indexed!
        new_roles.append('Manager')
        
        obj.manage_permission(self.permission_to_manage, new_roles)
