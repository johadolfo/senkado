"""student_management_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include
from psp_cash_app import views, HodViews, MembreViews, ADMViews
from psp_cash import settings

urlpatterns = [

    path('demo', views.showDemoPage),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    #path('', views.home, name="home"),
    path('', views.ShowLoginPage, name="show_login"),

    path('get_user_details', views.GetUserDetails),
    path('logout_user', views.logout_user, name="logout"),
    path('doLogin', views.doLogin, name="do_login"),

    #adm home
    path('add_compagnie', ADMViews.add_compagnie, name="add_compagnie"),
    path('add_compagnie_save', ADMViews.add_compagnie_save, name="add_compagnie_save"),
    path('manage_compagnie', ADMViews.manage_compagnie, name="manage_compagnie"),
    path('edit_compagnie/<str:compagnie_id>', ADMViews.edit_compagnie, name="edit_compagnie"),
    path('edit_compagnie_save', ADMViews.edit_compagnie_save, name="edit_compagnie_save"),
    path('supprimer_compagnie/<str:compagnie_id>', ADMViews.supprimer_compagnie, name="supprimer_compagnie"),
    path('desactiver_compagnie/<str:compagnie_id>', ADMViews.desactiver_compagnie, name="desactiver_compagnie"),
    path('activer_compagnie/<str:compagnie_id>', ADMViews.activer_compagnie, name="activer_compagnie"),
   
    


    path('manage_user', ADMViews.manage_user, name="manage_user"),
    path('add_muso1', ADMViews.add_muso1, name="add_muso1"),
    path('add_muso1_save', ADMViews.add_muso1_save, name="add_muso1_save"),
    path('add_muso', ADMViews.add_muso, name="add_muso"),
    path('add_muso_save', ADMViews.add_muso_save, name="add_muso_save"),
    path('manage_muso', ADMViews.manage_muso, name="manage_muso"),
    path('adm_home', ADMViews.adm_home, name="adm_home"),
    path('edit_muso/<str:muso_id>', ADMViews.edit_muso, name="edit_muso"),
    path('edit_muso_save', ADMViews.edit_muso_save, name="edit_muso_save"),
    path('edit_user/<str:user_id>', ADMViews.edit_user, name="edit_user"),
    path('edit_user_save', ADMViews.edit_user_save, name="edit_user_save"),
    path('export_csv',ADMViews.export_csv, name="export_csv"),
    path('export_users_csv',ADMViews.export_users_csv, name="export_users_csv"),
    path('add_new_user',ADMViews.add_new_user, name="add_new_user"),
    path('add_customuser_save',ADMViews.add_customuser_save, name="add_customuser_save"),
    path('show_aceess',ADMViews.show_aceess, name="show_aceess"),
    path('load_more_data',ADMViews.load_more_data, name="load_more_data"),

   

    #admin home
    path('add_tbarticle', HodViews.add_tbarticle, name="add_tbarticle"),
    path('add_article_save', HodViews.add_article_save, name="add_article_save"),
    path('manage_article', HodViews.manage_article, name="manage_article"),
    path('edit_article/<str:article_id>', HodViews.edit_article, name="edit_article"),
    path('edit_article_save', HodViews.edit_article_save, name="edit_article_save"),
    path('ajuster_article/<str:article_id>', HodViews.ajuster_article, name="ajuster_article"),
    path('ajuster_article_save', HodViews.ajuster_article_save, name="ajuster_article_save"),
    path('supprimer_article/<str:article_id>', HodViews.supprimer_article, name="supprimer_article"),

    path('add_departement', HodViews.add_departement, name="add_departement"),
    path('add_departement_save', HodViews.add_departement_save, name="add_departement_save"),
    path('edit_departement/<str:departement_id>', HodViews.edit_departement, name="edit_departement"),
    path('edit_departement_save', HodViews.edit_departement_save, name="edit_departement_save"),
    path('supprimer_departement/<str:departement_id>', HodViews.supprimer_departement, name="supprimer_departement"),

    path('add_unite_mesure', HodViews.add_unite_mesure, name="add_unite_mesure"),
    path('add_unite_save', HodViews.add_unite_save, name="add_unite_save"),
    path('edit_unite/<str:unite_id>', HodViews.edit_unite, name="edit_unite"),
    path('edit_unite_save', HodViews.edit_unite_save, name="edit_unite_save"),
    path('supprimer_unite/<str:unite_id>', HodViews.supprimer_unite, name="supprimer_unite"),

    path('manage_ajustement', HodViews.manage_ajustement, name="manage_ajustement"),
    path('add_membre', HodViews.add_membre, name="add_membre"),
    path('add_membre_save', HodViews.add_membre_save, name="add_membre_save"),
    path('manage_employe', HodViews.manage_employe, name="manage_employe"),
    path('supprimer_employe/<str:employe_id>', HodViews.supprimer_employe, name="supprimer_employe"),
    path('edit_employe/<str:employe_id>', HodViews.edit_employe, name="edit_employe"),
    path('edit_employe_save', HodViews.edit_employe_save, name="edit_employe_save"),
    path('activer_employe/<str:employe_id>', HodViews.activer_employe, name="activer_employe"),
    path('desactiver_employe/<str:employe_id>', HodViews.desactiver_employe, name="desactiver_employe"),
    path('manage_receipt', HodViews.manage_receipt, name="manage_receipt"),
    path('add_receipt', HodViews.add_receipt, name="add_receipt"),
    #path('get_article_details', HodViews.get_article_details, name="get_article_details"),
    #path('add_receipt_save', HodViews.add_receipt_save, name="add_receipt_save"),

    path('remplirPanier/<str:article_id>', HodViews.remplirPanier, name="remplirPanier"),
    path('payer_panier', HodViews.payer_panier, name="payer_panier"),
    path('details_receipt/<str:receipt_id>', HodViews.details_receipt, name="details_receipt"),
    path('supprimer_receipt/<str:receipt_id>', HodViews.supprimer_receipt, name="supprimer_receipt"),
    path('hold_receipt', HodViews.hold_receipt, name="hold_receipt"),
    path('get_articles/', HodViews.get_articles, name='get_articles'),
    path('supprimer_receipthold/<str:receipt_id>', HodViews.supprimer_receipthold, name="supprimer_receipthold"),
    path('rapport_vente/', HodViews.rapport_vente, name='rapport_vente'),
    path('rapport_ventes/', HodViews.rapport_ventes, name='rapport_ventes'),
    path('rapport_stock/', HodViews.rapport_stock, name='rapport_stock'),
    path('tab_open/', HodViews.tab_open, name='tab_open'),
    path('add_depense/', HodViews.add_depense, name='add_depense'),
    path('add_depense_save/', HodViews.add_depense_save, name='add_depense_save'),
    path('supprimer_depense/<str:code_payout>', HodViews.supprimer_depense, name="supprimer_depense"),
    path('manage_membre/', HodViews.manage_membre, name='manage_membre'),
    
    path('check_email_exist', HodViews.check_email_exist, name="check_email_exist"),
    path('check_codeCredit_exist', HodViews.check_codeCredit_exist, name="check_codeCredit_exist"),
    path('check_codep_exist', HodViews.check_codep_exist, name="check_codep_exist"),
 


    path('admin_home', HodViews.admin_home, name="admin_home"),
    path('admin_profile', HodViews.admin_profile, name="admin_profile"),
    path('admin_profile_save', HodViews.admin_profile_save, name="admin_profile_save"),
    path('add_comments_save', HodViews.add_comments_save, name="add_comments_save"),
    path('profile_view', HodViews.profile_view, name="profile_view"),
    path('user_info', HodViews.user_info, name="user_info"),
    path('user_access', HodViews.user_access, name="user_access"),
    path('user_groups', HodViews.user_groups, name="user_groups"),

    ################################## membre home #######################################
    path('membre_home', MembreViews.membre_home, name="membre_home"),

    ########################################### ajout des droits ########################################################

    path('GUtilisateur', HodViews.GUtilisateur, name="GUtilisateur"),
    path('add_access_right', HodViews.add_access_right, name="add_access_right"),
    path('delete_permission', HodViews.delete_permission, name="delete_permission"),
    #path('supprimer_permission/<str:permission_id>', HodViews.supprimer_permission, name="supprimer_permission"),
    path('supprimer_permission/<str:permission_id>/<str:customer_id>/', HodViews.supprimer_permission, name="supprimer_permission"),
    ########################################### fin ajout droit #####################################################################

    ######################### modification gestion commande #######################################################
    
    path('add_receiptemp', MembreViews.add_receiptemp, name="add_receiptemp"),
    path('payer_panieremp', MembreViews.payer_panieremp, name="payer_panieremp"),
    path('hold_receiptemp', MembreViews.hold_receiptemp, name="hold_receiptemp"),
    path('tab_openemp/', MembreViews.tab_openemp, name='tab_openemp'),
    path('get_articlem/', MembreViews.get_articlem, name='get_articlem'),
    path('manage_receiptm/', MembreViews.manage_receiptm, name='manage_receiptm'),
    path('manage_membres', MembreViews.manage_membres, name="manage_membres"),

    path('membre_apply_leave', MembreViews.membre_apply_leave, name="membre_apply_leave"),
    path('membre_apply_leave_save', MembreViews.membre_apply_leave_save, name="membre_apply_leave_save"),
    path('membre_feedback', MembreViews.membre_feedback, name="membre_feedback"),
    path('membre_feedback_save', MembreViews.membre_feedback_save, name="membre_feedback_save"),
    path('membre_profile', MembreViews.membre_profile, name="membre_profile"),
    path('membre_profile_save', MembreViews.membre_profile_save, name="membre_profile_save"),

    

    path('add_mcomments_save', MembreViews.add_mcomments_save, name="add_mcomments_save"),
    path('profile_mview', MembreViews.profile_mview, name="profile_mview"),
    path('user_info', MembreViews.user_info, name="user_info"),

]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


