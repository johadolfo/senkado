from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from django.http import HttpResponseRedirect


class LoginCheckMiddleWare(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename=view_func.__module__
        user=request.user
        if user.is_authenticated:
            if user.user_type == "1" :
                if modulename == "psp_cash_app.HodViews":
                    pass
                elif modulename == "psp_cash_app.views" or modulename == "django.views.static":
                    pass
                else:
                    return HttpResponseRedirect(reverse("admin_home"))
            elif user.user_type == "3":
                if modulename == "psp_cash_app.ADMViews":
                    pass
                elif modulename == "psp_cash_app.views" or modulename == "django.views.static":
                    pass
                else:
                    return HttpResponseRedirect(reverse("adm_home"))
            elif user.user_type == "2":
                if modulename == "psp_cash_app.MembreViews":
                    pass
                elif modulename == "psp_cash_app.views" or modulename == "django.views.static":
                    pass
                else:
                    return HttpResponseRedirect(reverse("membre_home"))
            else:
                return HttpResponseRedirect(reverse("show_login"))
        
        else:
            if request.path == reverse("show_login") or request.path == reverse("do_login") or modulename == "django.contrib.auth.views":
            #if request.path == reverse("show_login") or request.path == reverse("do_login") or modulename == "django.contrib.auth.views":
                pass
            else:
                #return HttpResponseRedirect(reverse("LoginPage"))
                return HttpResponseRedirect(reverse("show_login"))
