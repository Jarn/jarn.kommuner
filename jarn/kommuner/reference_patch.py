from Products.CMFCore.utils import getToolByName


def referenceFieldGet(self, instance, aslist=False, **kwargs):
    """
    Patch to ReferenceField get. We do that because reference catalog has
    no security. Check that whatever objects are returned can be viewed by
    the user. 
    """
    references = self._old_get(instance, aslist=aslist, **kwargs)
    mtool=getToolByName(instance, 'portal_membership')
    if not self.multiValued:
        if references is None:
            return None
        if mtool.checkPermission('View', references):
            return references
        else:
            return None
    return [obj
            for obj in references
            if mtool.checkPermission('View', obj)]


def backreferenceFieldGet(self, instance, aslist=False, **kwargs):
    """
    Patch to BackReferenceField get. We do that because reference catalog has
    no security. Check that whatever objects are returned can be viewed by
    the user. Note that in this case we do not keep the old get as _old_get.
    This is because monkeypatcher is confused by the monkey patching occuring
    in the ReferenceField get.
    """

    references = instance.getBRefs(relationship=self.relationship)

    #singlevalued ref fields return only the object, not a list,
    #unless explicitely specified by the aslist option
    if not self.multiValued and not aslist:
        if references:
            assert len(references) == 1
            references =references[0]
        else:
            references = None

    mtool=getToolByName(instance, 'portal_membership')
    if not self.multiValued:
        if references is None:
            return None
        if mtool.checkPermission('View', references):
            return references
        else:
            return None
    return [obj
            for obj in references
            if mtool.checkPermission('View', obj)]
