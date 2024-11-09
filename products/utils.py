def get_user_or_guest_id(request):
    user = request.user
    if user.is_authenticated:
        return user, ""
    session_key = request.session.session_key
    if not session_key:
        request.session.save()
    return None, request.session.session_key
