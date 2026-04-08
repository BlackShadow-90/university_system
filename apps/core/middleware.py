"""
Custom Locale Middleware that ensures session language takes priority
"""
from django.conf import settings
from django.utils.translation import activate, get_language
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)


class ForceSessionLocaleMiddleware(MiddlewareMixin):
    """
    This middleware ensures that the language saved in session
    takes priority over URL prefix. It activates the session language
    after Django's LocaleMiddleware processes the request.
    """
    
    def process_request(self, request):
        # Get language from session
        session_lang = request.session.get('django_language')
        current_url_lang = getattr(request, 'LANGUAGE_CODE', None)
        
        logger.info(f"ForceSessionLocaleMiddleware: session_lang={session_lang}, url_lang={current_url_lang}")
        
        if session_lang and session_lang in [lang[0] for lang in settings.LANGUAGES]:
            # Only activate if different from current
            if session_lang != current_url_lang:
                logger.info(f"Activating session language: {session_lang}")
                activate(session_lang)
                request.LANGUAGE_CODE = session_lang
        
        # Store the active language for templates
        request.current_language = get_language()
        logger.info(f"Final language: {request.current_language}")
