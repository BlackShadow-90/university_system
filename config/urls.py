"""
URL configuration for university_system project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render, redirect
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import activate
from django.http import HttpResponseRedirect


def landing_page(request):
    return render(request, 'public/landing.html')


def about_page(request):
    return render(request, 'public/about.html')


def debug_i18n(request):
    """Debug view to check i18n status"""
    from django.utils.translation import get_language
    from django.http import JsonResponse
    
    return JsonResponse({
        'session_language': request.session.get('django_language'),
        'current_language': get_language(),
        'request_language_code': getattr(request, 'LANGUAGE_CODE', None),
        'test_students': str(_('Students')),
        'test_dashboard': str(_('Dashboard')),
    })


def root_redirect(request):
    """Redirect root URL to default language"""
    return redirect('/en/')


def set_language(request):
    """Custom language switcher that saves to session and redirects with proper language prefix"""
    from django.conf import settings
    
    language = request.POST.get('language', 'en')
    next_url = request.POST.get('next', '')
    
    # Validate language
    valid_languages = [lang[0] for lang in settings.LANGUAGES]
    if language in valid_languages:
        # Save to session
        request.session['django_language'] = language
        
        # Build URL with language prefix
        # Remove any existing language prefix from next_url
        for lang_code in valid_languages:
            if next_url.startswith(f'/{lang_code}/'):
                next_url = next_url[len(f'/{lang_code}'):]
                break
        
        # If next_url is empty or just '/', redirect to landing page with proper language prefix
        if not next_url or next_url == '/':
            next_url = f'/{language}/'
        else:
            # Add new language prefix
            if language != settings.LANGUAGE_CODE:
                next_url = f'/{language}{next_url}'
            else:
                # For default language, add prefix based on PREFIX_DEFAULT_LANGUAGE
                if getattr(settings, 'PREFIX_DEFAULT_LANGUAGE', False):
                    next_url = f'/{language}{next_url}'
    
    return HttpResponseRedirect(next_url)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('set-language/', set_language, name='set_language'),
    path('debug-i18n/', debug_i18n, name='debug_i18n'),
    path('', root_redirect, name='root_redirect'),
    # Explicit patterns for language root paths (to avoid 404s)
    path('en/', landing_page, name='landing_en'),
    path('zh-hans/', landing_page, name='landing_zh'),
]

urlpatterns += i18n_patterns(
    path('', landing_page, name='landing'),
    path('about/', about_page, name='about'),
    path('auth/', include('apps.accounts.urls')),
    path('admin-portal/', include('apps.core.admin_urls')),
    path('teacher-portal/', include('apps.core.teacher_urls')),
    path('student-portal/', include('apps.core.student_urls')),
    path('reports/', include('apps.reports.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
