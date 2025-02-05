# from django.shortcuts import redirect
# from django.conf import settings
# import urllib.parse

# def google_login_redirect(request):
#     base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    
#     params = {
#         "client_id": settings.SOCIALACCOUNT_PROVIDERS["google"]["APP"]["client_id"],
#         "redirect_uri": "https://wikitube-new.vercel.app/accounts/google/login/callback/",
#         "response_type": "code",
#         "scope": "email",
#         "prompt": "select_account",
#         "access_type": "offline"
#     }

#     auth_url = f"{base_url}?{urllib.parse.urlencode(params)}"
#     return redirect(auth_url)
