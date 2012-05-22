from pyramid.view import view_config

from lmkp.models.database_objects import *
from lmkp.models.meta import DBSession as Session

import uuid

from recaptcha.client import captcha

@view_config(route_name='comments_all', renderer='json')
def comments_all(request):
    """
    Return a JSON representation of comments to a certain object 
    (activity / stakeholder / involvement), based on its id.
    """
    ret = {'success': False}
    
    # collect needed values
    object = request.matchdict.get('object', None)
    uid = request.matchdict.get('uid', None)
    
    # check if needed values are available
    if object is None or uid is None:
        return ret
    
    if object == 'activity':
        # check if parameter 'uid' is a valid UUID
        try:
            uuid.UUID(uid)
        except ValueError:
            ret['message'] = 'Not a valid UUID.'
            return ret
        
        # look for comments
        comments = Session.query(Comment).filter(Comment.activity_identifier == uid).all()
        ret['comments'] = []
        for c in comments:
            ret['comments'].append({
                'id': c.id,
                'comment': c.comment,
                'timestamp': str(c.timestamp),
                'userid': c.user.id if c.user is not None else None,
                'username': c.user.username if c.user is not None else None
            })
        ret['total'] = len(comments)
    
    elif object == 'stakeholder':
        ret['message'] = 'Stakeholder comments are not yet implemented.'
        return ret
    
    elif object == 'involvement':
        ret['message'] = 'Involvement comments are not yet implemented.'
        return ret
    
    else:
        ret['message'] = 'Object not found.'
        return ret
    
    # if we've come this far, set success to 'True'
    ret['success'] = True
    
    return ret

@view_config(route_name='comment_add', renderer='json')
def comment_add(request):
    """
    Add a new comment
    """
    ret = {'success': False}
        
    # check if captcha is available
    if request.POST['recaptcha_challenge_field'] is None or request.POST['recaptcha_response_field'] is None:
        ret['message'] = 'No captcha provided.'
        return ret
    
    # check if object is available
    if request.POST['object'] is None:
        ret['message'] = 'No object to comment upon provided.'
        return ret
    
    # check if comment is available
    if request.POST['comment'] is None:
        ret['message'] = 'No comment provided.'
        return ret
    
     # check if identifier is available
    if request.POST['identifier'] is None:
        ret['message'] = 'No identifier provided.'
        return ret
    
    # check captcha
    private_key = '6LfqmNESAAAAAKM_cXox32Nnz0Zo7nlOeDPjgIoh'
    response = captcha.submit(
        request.POST['recaptcha_challenge_field'],
        request.POST['recaptcha_response_field'],
        private_key,
        request.referer
    )
    
    if not response.is_valid:
        # captcha not correct
        ret['message'] = 'Captcha not correct.'
        ret['captcha_reload'] = True
        return ret
    else:
        # captcha correct, try to do insert
        if request.POST['object'] == 'activity':
            # check if identifier is a valid UUID
            try:
                a_uuid = uuid.UUID(request.POST['identifier'])
            except ValueError:
                ret['message'] = 'Not a valid UUID.'
                return ret
            
            # prepare the insert
            comment = Comment(request.POST['comment'])
            comment.activity_identifier = a_uuid
            
            # do the insert
            Session.add(comment)
            ret['message'] = 'Comment successfully inserted.'
        
        elif request.POST['object'] == 'stakeholder':
            ret['message'] = 'Stakeholder comments are not yet implemented.'
            return ret
        
        elif request.POST['object'] == 'involvement':
            ret['message'] = 'Involvement comments are not yet implemented.'
            return ret
        
        else:
            ret['message'] = 'Object not found.'
            return ret

    # if we've come this far, set success to 'True'
    ret['success'] = True
    
    return ret
