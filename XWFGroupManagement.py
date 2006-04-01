from Products.XWFMetadata.XWFMetadata import XWFMetadataValidation
from AccessControl.PermissionRole import rolesForPermissionOn
import types

class XWFGroupManagement(XWFMetadataValidation):
    meta_type = 'XWF Security Metadata'
    id = 'xwf_groups'
    
    label = "Visible to groups"
    hint = "To which groups should this item be visible"
    
    required = False
    requiredError = "One or more groups must be specified"
    
    def __init__(self, permission_to_manage='View'):
        self.permission_to_manage = permission_to_manage
        
    def xform_data(self, datacontainer, form):
        if form.has_key(self.id):
            groups = form[self.id]
            if type(groups) == types.StringType:
                groups = [groups]
        else:
            id = form.get('id', None)
            # if we have an ID, we should be dealing with the real object
            # rather than it's container
            if id:
                obj = getattr(datacontainer, id)
            else:
                obj = datacontainer
                
            groups = obj.groups_with_local_role('Viewer')
        
        f = """<%s>%s</%s>""" % (self.id, ' '.join(groups), self.id)
        
        return f
        
    def xform_control(self, obj, model_id, cssclass='text'):
        x = """<xf:item>
                  <xf:label>%s</xf:label>
                  <xf:value>%s</xf:value>
               </xf:item>"""
        
        items = []
        for element in obj.get_valid_groupids():
            items.append(x % (element, element))
        
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
        
    def set_permissions(self, obj, new_groups):
        roles = list(rolesForPermissionOn(self.permission_to_manage, obj))
        roles.sort()
        
        if 'Viewer' not in obj.__ac_roles__:
            obj._addRole('Viewer')
        
        if 'Viewer' not in roles:
            roles.append('Viewer')    
            obj.manage_permission(self.permission_to_manage, roles)
        
        for group in obj.groups_with_local_role('Viewer'):
            roles = list(obj.get_local_roles_for_groupid(group))
            roles.remove('Viewer')
            if roles:
                obj.manage_setLocalGroupRoles(group, roles)
            else:
                obj.manage_delLocalGroupRoles((group,))
        
        for group in new_groups:
            roles = obj.get_local_roles_for_groupid(group)
            if 'Viewer' not in roles:
                roles = list(roles)
                roles.append('Viewer')
                obj.manage_setLocalGroupRoles(group, roles)
        
            