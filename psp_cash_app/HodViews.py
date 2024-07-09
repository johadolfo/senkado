from django.shortcuts import render
from django.http import HttpResponseNotAllowed, HttpResponseRedirect, HttpResponse, HttpResponseServerError
import traceback
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from psp_cash_app.models import CustomUser, Membre, tbajustement, tbajustementarticle, tbarticle, tbconfiguration, tbcotisation, tbcredit, tbdepartement, tbpaiement, tbpayout, tbreceipt, tbreceiptarticle, tbremboursement,FeedBackMembre,LeaveReportMembre,CustomUser, tbdepense, tbdetailproduit, tbdetailcredit, Comment, tbcompagnie, tbtypecotisation, tbunitemesure
from .forms import EditMembreForm
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.core.paginator import Paginator
from django.db.models import Sum, Count,  F
from django.db import connection
import csv
from django.db import transaction
from django.db.models import F
import io
import xlrd
import datetime , openpyxl
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.db.models.functions import Coalesce
from datetime import datetime, timedelta, date
from calendar import monthrange
from django.http import JsonResponse
from django.db.models import Func
from django.db.models.functions import Substr
from django.db.models import F, ExpressionWrapper, CharField
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission, PermissionsMixin,User,AbstractUser,Group,AbstractBaseUser
from django.contrib.auth import models as auth_models
from django.db.models import F, ExpressionWrapper, DecimalField
from django.db.models.functions import Coalesce
from django.db.models import Sum, FloatField
from django.db.models import F, ExpressionWrapper, FloatField, Subquery, OuterRef
from django.shortcuts import render, get_object_or_404
import random
from django.utils import timezone
import sqlite3
from psp_cash_app.models import CustomUserPermission 
import json
from psp_cash_app.models import CustomUserPermission
from django.http import HttpRequest
from django.utils.timezone import make_aware
from django.db.models import Sum, Case, When, F

from django.db.models import Sum, Case, When, F, FloatField
from django.db.models import  Q

def admin_home(request):
    current_user = request.user
  
    #num_visitor = random.randint(0, 100000000)
    num_visitor = request.session.get('visitor_count', 0)

    membre_count=Membre.objects.filter(membre_actif='True', admin__compagnie=current_user.compagnie).count()
    cotisation_info=tbcotisation.objects.all().filter(code_membre__admin__compagnie=current_user.compagnie,code_membre__membre_actif='True' )
    montant_tot = sum(cotisation_info.values_list('montant', flat=True))



    cotisation_int = tbcotisation.objects.filter(code_membre__admin__compagnie=current_user.compagnie,code_membre__membre_actif='True')
    interet_tot = format(sum(cotisation_int.values_list('interet', flat=True)),'.2f')

    valeur2 = tbremboursement.objects.filter(faites_par__admin__compagnie=current_user.compagnie).values('date_remb').order_by('date_remb').annotate(sum=Sum('interet_remb'))
  
    credit_info = tbcredit.objects.filter(credit_status__icontains="En cour", code_membre__admin__compagnie=current_user.compagnie)
    montant_credit = sum(credit_info.values_list('montant_credit', flat=True))

    remb_info = tbremboursement.objects.filter(faites_par__admin__compagnie=current_user.compagnie, codecredit__credit_status__icontains="En cour").values('codecredit_id').order_by('codecredit_id').annotate(capital_remb=Sum('capital_remb'))
    montant_rembourse = format(sum(remb_info.values_list('capital_remb', flat=True)),'.2f')

    remboursement_info = tbremboursement.objects.filter(
    faites_par_id__admin_id__compagnie_id=current_user.compagnie
    ).values('date_remb').annotate(
        total_interet=Sum('interet_remb'),
        total_penalite=Sum('penalite'),
        montant_total_rembourse=Sum('montant_a_remb') + Sum('interet_remb'),
        quantite_remboursement=Count('id')
    ).order_by('date_remb')
    cotisation_info = tbcotisation.objects.filter(code_membre__admin_id__compagnie_id=current_user.compagnie)
    penalite_total_cot =sum(cotisation_info.values_list('penalite', flat=True))
    penalite_total = sum(remboursement_info.values_list('penalite', flat=True)) + penalite_total_cot

    #modification psp cash
    receipt = tbreceipt.objects.filter(compagnie=current_user.compagnie, statut='CLOSED')
    
    montant_total_receipt = receipt.aggregate(Sum('total_price'))['total_price__sum']

    receipt1 = tbreceipt.objects.filter(compagnie=current_user.compagnie, statut='OPENNED')
    
    montant_total_openreceipt = receipt1.aggregate(Sum('total_price'))['total_price__sum']

    nbre_receipt_open = tbreceipt.objects.filter(compagnie=current_user.compagnie, statut='OPENNED').count()
   
    nbre_receipt = tbreceipt.objects.filter(compagnie=current_user.compagnie).count()

    paiements = tbpaiement.objects.filter(receipt__compagnie=current_user.compagnie)
    total_account = sum(p.montant for p in paiements if p.type_paiement == 'Account')

    total_cash = sum(p.montant for p in paiements if p.type_paiement == 'Cash')
    total_us_cash = sum(p.montant for p in paiements if p.type_paiement == 'US Cash')
    #total_account = sum(p.montant for p in paiements if p.type_paiement == 'Account')
    total_check = sum(p.montant for p in paiements if p.type_paiement == 'Check')
    total_complementary = sum(p.montant for p in paiements if p.type_paiement == 'Complementary')
    total_natcash = sum(p.montant for p in paiements if p.type_paiement == 'Natcash')
    total_moncash = sum(p.montant for p in paiements if p.type_paiement == 'Moncash')
    total_zelle = sum(p.montant for p in paiements if p.type_paiement == 'Zelle')
    total_cashapp = sum(p.montant for p in paiements if p.type_paiement == 'Cash App')
    total_unicarte = sum(p.montant for p in paiements if p.type_paiement == 'Unicarte')
    total_sogecarte = sum(p.montant for p in paiements if p.type_paiement == 'SogeCarte')
    total_dollarcard = sum(p.montant for p in paiements if p.type_paiement == 'Dollar Card')

    result = tbreceiptarticle.objects.values('article__description') \
                                  .annotate(quantity=Sum('quantite')) \
                                  .order_by()  # Pour éviter le group_by automatique

    stock_article = tbarticle.objects.filter(compagnie=current_user.compagnie)
    #-----
    creditencour = tbcredit.objects.filter(code_membre__admin_id__compagnie_id=current_user.compagnie, credit_status='En cour')
    
    montant_total_credit_encour = creditencour.aggregate(Sum('montant_credit'))['montant_credit__sum']
    
    creditssencour = creditencour.annotate(
        interet_montant=F('montant_credit') * F('interet_credit') * F('nbre_de_mois')
    )
    
    interet_total_encour = creditssencour.aggregate(Sum('interet_montant'))['interet_montant__sum']

    #------------
    remboursements_info = tbremboursement.objects.filter(codecredit__code_membre__admin__compagnie_id=current_user.compagnie).aggregate(total_montant_remb=Sum('montant_a_remb'),total_interet_remb=Sum('interet_remb'))
   #-------------------
    db_path = "db.sqlite3"
    
    query = """
        SELECT 
    psp_cash_app_tbcredit.numero AS codecredit_id,
    COUNT(psp_cash_app_tbremboursement.id) AS quantite_remboursement,
    (psp_cash_app_tbcredit.nbre_de_mois - COUNT(psp_cash_app_tbremboursement.id)) AS Qtee_restant,
    IFNULL(SUM(psp_cash_app_tbremboursement.capital_remb), 0) + IFNULL(SUM(psp_cash_app_tbremboursement.interet_remb), 0) AS montant_total_rembourse,
    (((psp_cash_app_tbcredit.nbre_de_mois * (psp_cash_app_tbcredit.interet_credit * psp_cash_app_tbcredit.montant_credit)) + psp_cash_app_tbcredit.montant_credit) - (sum(IFNULL(psp_cash_app_tbremboursement.capital_remb, 0) + (IFNULL(psp_cash_app_tbremboursement.interet_remb, 0))))) AS montant_total_Restant,
    IFNULL(SUM(psp_cash_app_tbremboursement.interet_remb), 0) AS total_interet,
    (psp_cash_app_tbcredit.nbre_de_mois * (psp_cash_app_tbcredit.interet_credit * psp_cash_app_tbcredit.montant_credit)) + psp_cash_app_tbcredit.montant_credit AS Montant_tot,
    (IFNULL(SUM(psp_cash_app_tbremboursement.interet_remb), 0) * nbre_de_mois) - IFNULL(SUM(psp_cash_app_tbremboursement.interet_remb), 0) AS total_interet_restant,
    psp_cash_app_tbcredit.date_debut, psp_cash_app_tbcredit.date_fin,
    psp_cash_app_membre.profile_pic, psp_cash_app_membre.prenomp, psp_cash_app_membre.nomp,
    SUM(penalite) AS total_penalite, (psp_cash_app_tbcredit.interet_credit * psp_cash_app_tbcredit.montant_credit) AS interetCredit
    FROM
        psp_cash_app_tbcredit 
    LEFT JOIN
        psp_cash_app_tbremboursement  ON psp_cash_app_tbcredit.numero = psp_cash_app_tbremboursement.codecredit_id
    JOIN
        psp_cash_app_Membre  ON psp_cash_app_tbcredit.code_membre_id = psp_cash_app_Membre.id
    JOIN
        psp_cash_app_CustomUser  ON psp_cash_app_Membre.admin_id = psp_cash_app_CustomUser.id
    WHERE
        (psp_cash_app_tbcredit.credit_status = 'En cour' OR psp_cash_app_tbremboursement.id IS NULL)
        AND psp_cash_app_CustomUser.compagnie_id = ?
        
    GROUP BY
        psp_cash_app_tbcredit.numero, psp_cash_app_tbcredit.nbre_de_mois, psp_cash_app_tbcredit.interet_credit, psp_cash_app_tbcredit.montant_credit,
        psp_cash_app_tbcredit.date_debut, psp_cash_app_tbcredit.date_fin,
        psp_cash_app_Membre.profile_pic, psp_cash_app_Membre.prenomp, psp_cash_app_Membre.nomp
    ORDER BY
        codecredit_id ASC;
    """

    # Créez une connexion à la base de données
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    current_users = request.user
   
    # Exécutez la requête
    cursor.execute(query, (current_users.compagnie_id,))

    # Parcourez les résultats pour calculer la somme du montant_total_Restant
    montant_total_restant = 0
    Total_interet_restant = 0
    for row in cursor.fetchall():
        montant_total_restant += row[4]
        Total_interet_restant += row[7]

    #-------------interet anticipe------------
    interet_anticipe = tbcredit.objects.filter(
    tbremboursement__interet_remb=0,
    code_membre__admin__compagnie_id=current_user.compagnie
    ).aggregate(
    interet_anticipe=Sum(F('montant_credit') * F('interet_credit'))
    )['interet_anticipe']
    return render(request, "hod_template/home_content.html",{"total_natcash":total_natcash,"total_moncash":total_moncash,"receipt1":receipt1,"result":result,"stock_article":stock_article, "total_account":total_account, "nbre_receipt":nbre_receipt,"interet_anticipe":interet_anticipe, "Total_interet_restant":Total_interet_restant, "montant_total_restant":montant_total_restant, "nbre_receipt_open": nbre_receipt_open, "montant_total_receipt":montant_total_receipt,"montant_total_openreceipt":montant_total_openreceipt, "interet_total_encour":interet_total_encour, "remboursements_info":remboursements_info,   "credit_info":credit_info, "membre_count":membre_count, "montant_tot":montant_tot, "montant_credit":montant_credit,"montant_rembourse":montant_rembourse, "remb_info":remb_info, "valeur2":valeur2, "interet_tot":interet_tot, "num_visitor":num_visitor, "penalite_total":penalite_total, "total_cash":total_cash, "total_us_cash":total_us_cash, "total_dollarcard":total_dollarcard, "total_segracrte":total_sogecarte, "total_unicarte":total_unicarte, "total_zelle":total_zelle, "total_cashapp":total_cashapp, "total_complementary":total_complementary, "total_check":total_check})

def add_tbarticle(request):
    #form = AddMembreForm()
    current_user = request.user
    unite_mesure = tbunitemesure.objects.filter(compagnie=current_user.compagnie)
    departement = tbdepartement.objects.filter(compagnie=current_user.compagnie)
    return render(request, "hod_template/add_article_template.html",{"unite_mesure": unite_mesure, "departement":departement})

def add_article_save(request):
    current_user = request.user
    if request.method !="POST":
        return HttpResponse("Method Not Allowed")
    else:
        current_user = request.user
        #compagnie_id = current_user.compagnie
        code_articl = request.POST.get("code_article")
        description = request.POST.get("description")
        description2 = request.POST.get("description2")
        quantite = request.POST.get("quantite")
        departement = request.POST.get("departement")
        unite = request.POST.get("unite_mesure")
        cout = request.POST.get("cout")
        prix = request.POST.get("prix")
        reoderpoint = request.POST.get("reoderpoint")
        date_expiration = request.POST.get("date_expiration")

        #profile_pic = request.FILES['profile_pic']
        #fs = FileSystemStorage()
        #filename = fs.save(profile_pic.name, profile_pic)
        #profile_pic_url = fs.url(filename)

        try:
            article=tbarticle(code_articl=code_articl, description=description, description2=description2, cout_unit=cout, quantite=quantite, prix=prix, reoderpoint=reoderpoint, date_expiration=date_expiration, compagnie=current_user.compagnie, code_departement_id=departement, unite_mesure_id=unite )
            article.save()
           
            messages.success(request,"Successfully Added Article")
            return HttpResponseRedirect(reverse("manage_article")) 
        except Exception as e:
            messages.error(request,traceback.format_exc())
            return HttpResponseRedirect(reverse("manage_article"))

def manage_articless(request):
    current_user = request.user
    compagnie_id = current_user.compagnie_id
    id_compagnie = 1
    query = """
     select a.code_articl, b.departement, a.description, a.description2, c.unite_mesure, a.cout_unit, a.quantite, a.prix, a.reoderpoint, a.date_expiration 
    from psp_cash_app_tbarticle a, psp_cash_app_tbdepartement b, psp_cash_app_tbunitemesure c
    where a.code_departement_id = b.id and a.unite_mesure_id = c.id and a.compagnie_id = %s
        """

    with connection.cursor() as cursor:
        cursor.execute(query, [int(id_compagnie)])
        article_info = cursor.fetchall()

    if 'q' in request.GET:
        q = request.GET['q']
        queryparametre = """
        select a.code_articl, b.departement, a.description, a.description2, c.unite_mesure, a.cout_unit, a.quantite, a.prix, a.reoderpoint, a.date_expiration 
        from psp_cash_app_tbarticle a, psp_cash_app_tbdepartement b, psp_cash_app_tbunitemesure c
        where a.code_departement_id = b.id and a.unite_mesure_id = c.id and a.compagnie_id = %s and a.code_articl=%s 
        """
        
        with connection.cursor() as cursor:
            cursor.execute(queryparametre, [int(id_compagnie), q])
            all_article_info = cursor.fetchall()
    else:
        all_article_info = article_info
    
    paginator = Paginator(all_article_info, 15)
    page = request.GET.get('page')
    article_info_paginated = paginator.get_page(page)
    return render(request, "hod_template/manage_article_template.html", { "article_info": article_info_paginated })

def manage_article(request):
    current_user = request.user
    articles = tbarticle.objects.filter(compagnie=current_user.compagnie).select_related('code_departement', 'unite_mesure')

    q = request.GET.get('q')
    if q:
        articles = articles.filter(code_articl=q, compagnie=current_user.compagnie)

    paginator = Paginator(articles, 20)
    page_number = request.GET.get('page')
    article_info_paginated = paginator.get_page(page_number)

    return render(request, "hod_template/manage_article_template.html", { "article_info": article_info_paginated })

def edit_article(request, article_id):
    #membre_info = Membre.objects.all()
    article = tbarticle.objects.get(code_articl=article_id)
    departement_info = tbdepartement.objects.all()
    unite_mesure = tbunitemesure.objects.all()
    #membres = CustomUser.objects.filter(user_type=2)
    return render(request, "hod_template/edit_article_template.html", {"article":article, "departement_info":departement_info, "unite_mesure": unite_mesure})

def edit_article_save(request):
    if request.method !="POST":
        return HttpResponse("<h2> Methode Not Allowed </h2>")
    else:
        code_article = request.POST.get("code_article")
        description = request.POST.get("description")
        description2 = request.POST.get("description2")
        departement = request.POST.get("departement")
        cout = request.POST.get("cout")
        quantite = request.POST.get("quantite")
        unite_mesure = request.POST.get("unite_mesure")
        prix = request.POST.get("prix")
        reoderpoint = request.POST.get("reoderpoint")
        date_expiration = request.POST.get("date_expiration")
       
        try:
            article=tbarticle.objects.get(code_articl=code_article)
            article.description=description
            article.description2 = description2
            article.departement = departement
            article.cout = cout
            article.quantite = quantite
            article.reoderpoint = reoderpoint
            article.unite_mesure = tbunitemesure.objects.get(pk=unite_mesure)
            article.prix = prix
            article.date_expiration = date_expiration
            article.save()

            messages.success(request,"Successfully Edited Article")
            return HttpResponseRedirect(reverse("edit_article",kwargs={"article_id":code_article}))
        except:
            messages.error(request,traceback.format_exc())
            return HttpResponseRedirect(reverse("edit_article",kwargs={"article_id":code_article}))

def ajuster_article(request, article_id):
    article = tbarticle.objects.get(id=article_id)
    return render(request, "hod_template/ajustement_article_template.html", {"article":article})

def ajuster_article_save(request):
    date_now = datetime.now().date()
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        code_article = request.POST.get("code_article")
        ancienne_quantite = request.POST.get("ancienne_quantite")
        nouvelle_quantite = request.POST.get("nouvelle_quantite")
        ancien_cout = request.POST.get("ancien_cout")
        nouveau_cout = request.POST.get("nouveau_cout")
        ancien_prix = request.POST.get("ancien_prix")
        nouveau_prix = request.POST.get("nouveau_prix")
        memo = request.POST.get("memo")
        #valider_par = request.POST.get("recu_par")
        try:
            # Enregistrer l'ajustement
            ajustement = tbajustement.objects.create(date_ajustement=date_now,  memo=memo, recu_par=request.user.username)
            # Obtenir l'ID de l'ajustement nouvellement inséré
            latest_ajustement_id = ajustement.id

            article=tbarticle.objects.get(id=code_article)
            article.cout = nouveau_cout
            article.quantite = nouvelle_quantite
            article.prix = nouveau_prix
            article.save()

            # Enregistrer les détails de l'ajustement d'article
            ajustementarticle = tbajustementarticle.objects.create(
                anc_quantite=float(ancienne_quantite),
                nouv_quantite=float(nouvelle_quantite),
                anc_cout=float(ancien_cout),
                nouv_cout=float(nouveau_cout),
                anc_prix=float(ancien_prix),
                nouv_prix=float(nouveau_prix),
                memo=memo,
                code_ajustement = tbajustement.objects.get(pk=latest_ajustement_id),
                code_article=tbarticle.objects.get(pk=code_article)
            )
            
            messages.success(request, "Successfully Added Ajustement")
            return HttpResponseRedirect(reverse("ajuster_article", kwargs={"article_id": code_article}))
        except Exception as e:
            messages.error(request, traceback.format_exc())
            return HttpResponseRedirect(reverse("ajuster_article", kwargs={"article_id": code_article}))

def supprimer_article(request, article_id):
    article = tbarticle.objects.get(code_articl=article_id)
    article.delete()
    id_compagnie = 1
    articles = tbarticle.objects.filter(compagnie_id=id_compagnie).select_related('code_departement', 'unite_mesure')

    q = request.GET.get('q')
    if q:
        articles = articles.filter(code_articl=q)

    paginator = Paginator(articles, 15)
    page_number = request.GET.get('page')
    article_info_paginated = paginator.get_page(page_number)
    return render(request, "hod_template/manage_article_template.html", { "article_info": article_info_paginated })

def add_departement(request):
    current_user = request.user
    departement_info = tbdepartement.objects.filter(compagnie=current_user.compagnie)
    return render(request, "hod_template/add_departement_template.html", {"departement_info":departement_info})

def add_departement_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        current_user = request.user
        code_compagnie = current_user.compagnie
        print_in_kitchen = request.POST.get("print_in_kitchen") == 'on'  # Vérifie si la case est cochée
        print_in_bar = request.POST.get("print_in_bar") == 'on'  # Vérifie si la case est cochée
        departement = request.POST.get("departement")
        code_dept = request.POST.get("code_departement")

        # Convertir les valeurs booléennes en entiers
        print_in_kitchen = int(print_in_kitchen)
        print_in_bar = int(print_in_bar)

        try:
            departement = tbdepartement.objects.create(
                code_departement=code_dept,
                departement=departement,
                print_in_kitchen=print_in_kitchen,
                print_bar=print_in_bar,
               compagnie = current_user.compagnie
            )
            messages.success(request, "Successfully Added Departement")
            return HttpResponseRedirect(reverse("add_departement")) 
        except Exception as e:
            messages.error(request, traceback.format_exc())
            return HttpResponseRedirect(reverse("add_departement"))

def edit_departement(request, departement_id):
    departement = tbdepartement.objects.get(code_departement=departement_id)
    return render(request, "hod_template/edit_departement_template.html", {"departement":departement})

def edit_departement_save(request):
    if request.method == "POST":

        print_in_kitchen = request.POST.get("print_in_kitchen") == 'on'  # Vérifie si la case est cochée
        print_in_bar = request.POST.get("print_bar") == 'on'  # Vérifie si la case est cochée
        print_in_kitchen = int(print_in_kitchen)
        print_in_bar = int(print_in_bar)

        departement = tbdepartement.objects.get(code_departement=request.POST.get("code_departement"))
        departement.departement = request.POST.get("departement")
        departement.print_in_kitchen =print_in_kitchen  # Convertir en booléen
        departement.print_in_bar = print_in_bar # Convertir en booléen
        departement.save()
        messages.success(request, "Département édité avec succès")
        return HttpResponseRedirect(reverse("add_departement"))
    else:
        return HttpResponse("Méthode non autorisée")

def supprimer_departement(request, departement_id):
    departement = tbdepartement.objects.get(code_departement=departement_id)
    departement.delete()
    departement_info = tbdepartement.objects.all()
    return render(request, "hod_template/add_departement_template.html", { "departement_info": departement_info })

def add_unite_mesure(request):
    current_user = request.user
    unite_info = tbunitemesure.objects.filter(compagnie=current_user.compagnie)
    return render(request, "hod_template/add_unite_template.html", {"unite_info":unite_info})

def add_unite_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        current_user = request.user
        code_compagnie = current_user.compagnie
        unite_mesure = request.POST.get("unite_mesure")
        try:
            unite_mesure = tbunitemesure.objects.create(
                unite_mesure = unite_mesure, 
                compagnie_id = current_user.compagnie
            )
            messages.success(request, "Successfully Added Unite de Mesures")
            return HttpResponseRedirect(reverse("add_unite_mesure")) 
        except Exception as e:
            messages.error(request, traceback.format_exc())
            return HttpResponseRedirect(reverse("add_unite_mesure"))
        
def supprimer_unite(request, unite_id):
    unite = tbunitemesure.objects.get(id=unite_id)
    unite.delete()
    unite_info = tbunitemesure.objects.all()
    return render(request, "hod_template/add_unite_template.html", { "unite_info": unite_info })

def edit_unite(request, unite_id):
    unite = tbunitemesure.objects.get(id=unite_id)
    return render(request, "hod_template/edit_unite_template.html", {"unite":unite})

def edit_unite_save(request):
    if request.method == "POST":
        id_unite =request.POST.get("id_unite") 
        unite_mesure = request.POST.get("unite_mesure") 
        unite = tbunitemesure.objects.get(id=id_unite)
        unite.unite_mesure = unite_mesure
        unite.save()
        messages.success(request, "Unité édité avec succès")
        return HttpResponseRedirect(reverse("add_unite_mesure"))
    else:
        return HttpResponse("Méthode non autorisée")
    
def manage_ajustement(request):
    id_compagnie = 1
    ajustements = tbajustementarticle.objects.all().select_related('code_ajustement', 'code_article')

    q = request.GET.get('q')
    if q:
        ajustements = ajustements.filter(code_article=q)

    paginator = Paginator(ajustements, 50)
    page_number = request.GET.get('page')
    ajustement_info_paginated = paginator.get_page(page_number)
    return render(request, "hod_template/manage_ajustement_template.html", {"ajustement_info_paginated":ajustement_info_paginated})

def add_personne(request):
    pass

def add_membre(request):
    #form = AddMembreForm()
    return render(request, "hod_template/add_membre_templates.html")

def add_membre_save(request):
    if request.method !="POST":
        return HttpResponse("Method Not Allowed")
    else:
        current_user = request.user
        compagnie_id = current_user.compagnie
        prenomp = request.POST.get("prenom")
        nomp = request.POST.get("nom")
        codep = request.POST.get("code_employe")
        email = request.POST.get("email")
        password = request.POST.get("password")
        adressep = request.POST.get("adresse")
        sexep = request.POST.get("sexe")
        nifp = request.POST.get("nif")
        cin = request.POST.get("cin")
        tel_mob = request.POST.get("tel_mobile")
        tel_house = request.POST.get("tel_house")
        credit_limit = request.POST.get("credit_limit")
        account = request.POST.get("account")
        
        
        profile_pic = request.FILES['profile_pic']
        fs = FileSystemStorage()
        filename = fs.save(profile_pic.name, profile_pic)
        profile_pic_url = fs.url(filename)

        try:
            user=CustomUser.objects.create_user(username=prenomp +' '+ nomp, password=password, email=email, last_name=nomp, first_name=prenomp, user_type=2, compagnie=compagnie_id )
            user.membre.codep=codep
            user.membre.nomp = nomp
            user.membre.prenomp=prenomp
            user.membre.sexep = sexep
            user.membre.tel_mob=tel_mob
            user.membre.tel_house=tel_house
            user.membre.adresse=adressep
            user.membre.cin = cin
            user.membre.nif=nifp
            user.membre.credit_limit = credit_limit
            user.membre.account=account
            user.membre.profile_pic=profile_pic_url
            user.membre.save()
           
            messages.success(request,"Successfully Added Employe")
            return HttpResponseRedirect(reverse("add_membre")) 
        except Exception as e:
            messages.error(request,traceback.format_exc())
            return HttpResponseRedirect(reverse("add_membre"))

def manage_employe(request):
    current_user = request.user
    compagnie_id = current_user.compagnie_id
    employe_info = Membre.objects.filter(admin__compagnie=current_user.compagnie)

    if 'q' in request.GET:
        q = request.GET['q']
        
        all_employe_list = Membre.objects.filter( Q(nomp__icontains=q) | Q(prenomp__icontains=q) | Q(codep__icontains=q) )
    else:
        all_employe_list = Membre.objects.filter(admin__compagnie=current_user.compagnie)
    paginator = Paginator(all_employe_list,15,orphans=5)
    page = request.GET.get('page')
    employe_info = paginator.get_page(page)
    return render(request, "hod_template/manage_employe_template.html", { "employe_info": employe_info })

def supprimer_employe(request, employe_id):
    current_user = request.user
    compagnie_id = current_user.compagnie_id
    employe = Membre.objects.get(codep=employe_id)
    employe.delete()
    employe_info = Membre.objects.filter(admin__compagnie=current_user.compagnie)
    return render(request, "hod_template/manage_employe_template.html", { "employe_info": employe_info })

def edit_employe(request, employe_id):
    current_user = request.user
    compagnie_id = current_user.compagnie_id
    employe_info = Membre.objects.get(admin_id=employe_id, admin__compagnie=current_user.compagnie)
    return render(request, "hod_template/edit_employe_template.html", { "employe_info": employe_info })

def edit_employe_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Methode Not Allowed</h2>")
    else:
        membre_id = request.POST.get("id_emp")
        
        try:
            # Gestion de la photo de profil
            if 'profile_pic' in request.FILES:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None
            
            # Récupération de l'utilisateur et du membre associé
            user = CustomUser.objects.get(id=membre_id)
            membre = Membre.objects.get(admin_id=membre_id)
            
            # Mise à jour des données de l'utilisateur
            user.first_name = request.POST.get("prenom")
            user.last_name = request.POST.get("nom")
            user.email = request.POST.get("email")
            password = request.POST.get("password")
            if password:
                user.set_password(password)
            user.save()
            
            # Mise à jour des données du membre
            membre.adresse = request.POST.get("adresse")
           
            membre.codep = request.POST.get("code_employe")
            membre.nomp = request.POST.get("nom")
            membre.prenomp = request.POST.get("prenom")
            membre.tel_mob = request.POST.get("tel_mobile")
            membre.tel_house = request.POST.get("tel_house")
            membre.credit_limit = request.POST.get("credit_limit")
            membre.account = request.POST.get("account")
            membre.nif = request.POST.get("nif")
            membre.cin = request.POST.get("cin")
            if profile_pic_url:
                membre.profile_pic = profile_pic_url
            membre.save()
            
            current_user = request.user
            compagnie_id = current_user.compagnie_id
            employe_info = Membre.objects.filter(admin__compagnie=current_user.compagnie)
            messages.success(request,"Successfully Edited Employe")
            return render(request, "hod_template/manage_employe_template.html", { "employe_info": employe_info })
        except Exception as e:
            messages.error(request,traceback.format_exc())
            return render(request, "hod_template/manage_employe_template.html", { "employe_info": employe_info })
    
def desactiver_employe(request, employe_id):
    employe = Membre.objects.get(codep=employe_id)
    employe.membre_actif = 0
    employe.save()
    messages.success(request, "Employe édité avec succès")
    return HttpResponseRedirect(reverse("manage_employe"))
    
def activer_employe(request, employe_id):
    employe = Membre.objects.get(codep=employe_id)
    employe.membre_actif = 1
    employe.save()
    messages.success(request, "Employe édité avec succès")
    return HttpResponseRedirect(reverse("manage_employe"))

def manage_receipt(request):
    current_user = request.user
    #compagnie_id = current_user.compagnie_id
    receipt_info = tbreceipt.objects.filter(compagnie_id=current_user.compagnie).order_by('num_receipt')

    if 'q' in request.GET:
        q = request.GET['q']
        
        all_receipt_list = tbreceipt.objects.filter(compagnie_id=current_user.compagnie).order_by('num_receipt')
    else:
        all_receipt_list = tbreceipt.objects.filter(compagnie_id=current_user.compagnie).order_by('num_receipt')
    paginator = Paginator(all_receipt_list,250,orphans=5)
    page = request.GET.get('page')
    receipt_info = paginator.get_page(page)
    return render(request, "hod_template/manage_receipt_template.html", { "receipt_info": receipt_info })

def add_receipt(request):
    current_user = request.user
    compagnie_id = current_user.compagnie
    configuration_info = tbconfiguration.objects.filter(compagnie = compagnie_id)
    categories = tbdepartement.objects.all()
    articles = tbarticle.objects.all()
    receipt_articles = tbreceiptarticle.objects.filter(receipt_id=103).values(
        'receipt_id', 'article_id', 'article__description', 'quantite', 'cout', 'prix'
    )
   
    with connection.cursor() as cursor:
        cursor.execute("SELECT num_receipt, num_bath, client, user_receipt, date_receipt, total_article, tax, total_cost, total_price, receipt_discount, balance, observation, statut, deposit, service_charge, type_receipt FROM psp_cash_app_tbreceipt WHERE statut = 'OPENNED' and compagnie_id=1 ")
        opentap = cursor.fetchall()
    # Exécution de la requête SQL pour compter les reçus ouverts
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(num_receipt) FROM psp_cash_app_tbreceipt WHERE statut = 'OPENNED' and compagnie_id=1 ")
        opened_receipt_count = cursor.fetchone()[0]

    # Passage du nombre de reçus ouverts au contexte de rendu
    context = {
        'categories': categories,
        'articles': articles,
        'opened_receipt_count': opened_receipt_count,
        'opentap': opentap,
        'receipt_articles':receipt_articles,
        'configuration_info': configuration_info
    }
    #print(opentap)
    return render(request, "hod_template/add_receipt_template.html", context)

def get_articles(request):
    if request.method == 'GET' and 'receipt_id' in request.GET:
        receipt_id = request.GET.get('receipt_id')
        articles = tbreceiptarticle.objects.filter(receipt_id=receipt_id).values(
            'article_id', 'article__description', 'quantite', 'prix', 'cout'
        )
        return JsonResponse(list(articles), safe=False)
    else:
        return JsonResponse({'error': 'Invalid request'})

def payer_panier(request):

    current_user = request.user
    compagnie_id = current_user.compagnie
    date_now = timezone.now() 
    if request.method == 'POST':
        #la table n'est pas ouverte
        if request.POST.get('selected_tab') != "open":
            try:
                # Récupérer la valeur de la taxe à partir de la requête POST
                tax = request.POST.get('tax1')
                # Récupérer la valeur du service charge à partir de la requête POST
                service_charge = request.POST.get('service_charge1')
                # Récupérer la valeur du discount à partir de la requête POST
                discount = request.POST.get('discount1')
                # Récupérer la valeur du montant TTC à partir de la requête POST
                montant_ttc = request.POST.get('montant_ttc1')
                quantite_tot = request.POST.get('quantitetot1')
                panier_data = request.POST.get('panier_data')
                cout_total =request.POST.get('couttotal1')
                balance = request.POST.get('balance1')
                date_1 =request.POST.get('date_paie')
                if date_1 is not None:
                    # Assurez-vous que date_1 et date_2 sont bien des objets str avant d'appeler la méthode replace
                    date_now = date_1.replace('T', ' ')
                else:
                    date_now = request.POST.get('date_paie')
                deposit = request.POST.get('deposit1')
                monnaie = request.POST.get('montant_monnaie')
                montant_client = request.POST.get('montant_donne')
                print("Contenu du panier :", panier_data)  # Vérification des données du panier
                
                if panier_data:
                    panier = json.loads(panier_data)
                    receipt = tbreceipt.objects.create(
                        num_bath="100",
                        client="100",
                        total_article=quantite_tot,
                        tax=tax,
                        total_cost=cout_total,
                        total_price=montant_ttc,
                        receipt_discount=discount,
                        balance=balance,
                        observation="ok",
                        statut="CLOSED",
                        deposit=deposit,
                        service_charge=service_charge,
                        type_receipt="IN",
                        date_close=date_now,
                        close_by="Jojo"
                    )
                    #latest_receipt_id = receipt.num_receipt
                    # enregistrer paiement
                    if request.POST.get('typepaiement')=="Check" or request.POST.get('typepaiement')=="Unicarte" or request.POST.get('typepaiement')=="SogeCarte" or request.POST.get('typepaiement')=="Natcash" or request.POST.get('typepaiement')=="Moncash" or request.POST.get('typepaiement')=="Complementary" or request.POST.get('typepaiement')=="Account" or request.POST.get('typepaiement')=="Cash":
                        paiement = tbpaiement.objects.create(
                            receipt=receipt,
                            date_paiement=date_now,
                            type_paiement=request.POST.get('typepaiement'),
                            montant=montant_ttc,
                            tender=montant_client,
                            day_rate=1,
                            user_paie="Jojo"
                        )
                    elif request.POST.get('typepaiement')=="US Cash" or request.POST.get('typepaiement')=="Dollar Card" or request.POST.get('typepaiement')=="Zelle" or request.POST.get('typepaiement')=="Cash App":
                        configuration_taux = tbconfiguration.objects.get(compagnie=compagnie_id)
                        paiement = tbpaiement.objects.create(
                            receipt=receipt,
                            date_paiement=date_now,
                            type_paiement=request.POST.get('typepaiement'),
                            montant=montant_ttc,
                            tender=montant_client,
                            day_rate=configuration_taux.other_curr_rate,
                            user_paie="Jojo"
                        )

                    #enregistrer receipt article
                    for item in panier:
                        article = tbarticle.objects.get(id=item['article_id'])  # Utiliser get au lieu de filter
                        tbreceiptarticle.objects.create(
                            num_ligne=1,
                            receipt=receipt,
                            article=article,
                            quantite=item['quantite'],
                            cout=article.cout_unit,  # Utiliser directement l'attribut de l'objet article
                            prix=item['prix'],
                            discount_article=0,
                            observation="",
                            statut="CLOSED",
                            user_added_byreceipt="Jojo",
                            date_added=date_now
                        )
                    return redirect('add_receipt')
                    
            except Exception as e:
                # Capturer l'exception et afficher un message d'erreur (ou journaliser l'erreur)
                print("Une erreur s'est produite lors du traitement du panier :", str(e))
                return HttpResponseServerError("Une erreur s'est produite lors du traitement du panier. Veuillez contacter l'administrateur.")
                
        #la table est ouverte
        else:
            receipt_id = request.POST.get('receipt_id_hold')
            date_1 =request.POST.get('date_paie')
            if date_1 is not None:
                    # Assurez-vous que date_1 et date_2 sont bien des objets str avant d'appeler la méthode replace
                date_now = date_1.replace('T', ' ')
            else:
                date_now = request.POST.get('date_paie')
            supprimer_receipthold(request, receipt_id)
            try:
                # Récupérer la valeur de la taxe à partir de la requête POST
                tax = request.POST.get('tax1')
                # Récupérer la valeur du service charge à partir de la requête POST
                service_charge = request.POST.get('service_charge1')
                # Récupérer la valeur du discount à partir de la requête POST
                discount = request.POST.get('discount1')
                # Récupérer la valeur du montant TTC à partir de la requête POST
                montant_ttc = request.POST.get('montant_ttc1')
                quantite_tot = request.POST.get('quantitetot1')
                panier_data = request.POST.get('panier_data')
                cout_total =request.POST.get('couttotal1')
                balance = request.POST.get('balance1')
                deposit = request.POST.get('deposit1')
                
                print("Contenu du panier :", panier_data)  # Vérification des données du panier
                
                if panier_data:
                    panier = json.loads(panier_data)
                    receipt = tbreceipt.objects.create(
                        num_receipt = receipt_id,
                        num_bath="100",
                        client="100",
                        total_article=quantite_tot,
                        tax=tax,
                        total_cost=cout_total,
                        total_price=montant_ttc,
                        receipt_discount=discount,
                        balance=balance,
                        observation="ok",
                        statut="CLOSED",
                        deposit=deposit,
                        service_charge=service_charge,
                        type_receipt="IN",
                        date_close=date_now,
                        close_by="Jojo"
                    )
                    #latest_receipt_id = receipt.num_receipt
                    
                    for item in panier:
                        article = tbarticle.objects.get(id=item['article_id'])  # Utiliser get au lieu de filter
                        receipt = tbreceipt.objects.get(num_receipt=receipt_id)
                        tbreceiptarticle.objects.create(
                            num_ligne=1,
                            receipt=receipt,
                            article=article,
                            quantite=item['quantite'],
                            cout=article.cout_unit,  # Utiliser directement l'attribut de l'objet article
                            prix=item['prix'],
                            discount_article=0,
                            observation="",
                            statut="CLOSED",
                            user_added_byreceipt="Jojo",
                            date_added=date_now
                        )
                    return redirect('manage_receipt')
            except Exception as e:
                # Capturer l'exception et afficher un message d'erreur (ou journaliser l'erreur)
                print("Une erreur s'est produite lors du traitement du panier :", str(e))
                return HttpResponseServerError("Une erreur s'est produite lors du traitement du panier. Veuillez contacter l'administrateur.")
            
        return redirect('manage_receipt')
    

def supprimer_receipthold(request, receipt_id):
    try:
        receipt_del = tbreceipt.objects.get(num_receipt=receipt_id)
        receipt_del.delete()
    except ObjectDoesNotExist:
        # Gérer le cas où le tbreceipt avec num_receipt spécifié n'existe pas
        # Vous pouvez journaliser un avertissement ou effectuer toute autre action nécessaire
        print(f"tbreceipt avec num_receipt {receipt_id} n'existe pas.")

def hold_receipt(request):
    
    if request.method == 'POST':
        #la table n'est pas ouverte
        if request.POST.get('selected_tab_open') != "open":
            try:
                # Récupérer la valeur de la taxe à partir de la requête POST
                tax = request.POST.get('tax')
                # Récupérer la valeur du service charge à partir de la requête POST
                service_charge = request.POST.get('service_charge')
                # Récupérer la valeur du discount à partir de la requête POST
                discount = request.POST.get('discount')
                # Récupérer la valeur du montant TTC à partir de la requête POST
                montant_ttc = request.POST.get('montant_ttc')
                quantite_tot = request.POST.get('quantitetot')
                panier_data = request.POST.get('panier_data')
                date_1 =request.POST.get('date_paie_hold')

                if date_1 is not None:
                    # Assurez-vous que date_1 et date_2 sont bien des objets str avant d'appeler la méthode replace
                    date_now = date_1.replace('T', ' ')
                else:
                    date_now = request.POST.get('date_paie_hold')

                cout_total = request.POST.get('couttotal')
                balance = request.POST.get('balance')
                deposit = request.POST.get('deposit')
                
                print("Montant TTC :", montant_ttc)  # Vérification des données du panier
                print("Montant Tax :", tax)  # Vérification des données du panier
                print("Quantite TOT :", quantite_tot)  # Vérification des données du panier
                
                if panier_data:
                    panier = json.loads(panier_data)
                    receipt = tbreceipt.objects.create(
                        num_bath="100",
                        client="100",
                        total_article=quantite_tot,
                        tax=tax,
                        total_cost=cout_total,
                        total_price=montant_ttc,
                        receipt_discount=discount,
                        balance=balance,
                        observation="ok",
                        statut="OPENNED",
                        deposit=deposit,
                        service_charge=service_charge,
                        type_receipt="IN",
                        date_close=date_now,
                        close_by="Jojo"
                    )
                    #latest_receipt_id = receipt.num_receipt
                    
                    for item in panier:
                        article = tbarticle.objects.get(id=item['article_id'])  # Utiliser get au lieu de filter
                        tbreceiptarticle.objects.create(
                            num_ligne=1,
                            receipt=receipt,
                            article=article,
                            quantite=item['quantite'],
                            cout=article.cout_unit,  # Utiliser directement l'attribut de l'objet article
                            prix=item['prix'],
                            discount_article=0,
                            observation="",
                            statut="OPENNED",
                            user_added_byreceipt="Jojo",
                            date_added=date_now
                        )
                    return redirect('add_receipt')
            except Exception as e:
                # Capturer l'exception et afficher un message d'erreur (ou journaliser l'erreur)
                print("Une erreur s'est produite lors du traitement du panier :", str(e))
                return HttpResponseServerError("Une erreur s'est produite lors du traitement du panier. Veuillez contacter l'administrateur.")
                
        #la table est ouverte
        else:
            receipt_id = request.POST.get('receipt_id_holdtab')
            
            supprimer_receipthold(request, receipt_id)
            try:
                # Récupérer la valeur de la taxe à partir de la requête POST
                tax = request.POST.get('tax')
                # Récupérer la valeur du service charge à partir de la requête POST
                service_charge = request.POST.get('service_charge')
                # Récupérer la valeur du discount à partir de la requête POST
                discount = request.POST.get('discount')
                # Récupérer la valeur du montant TTC à partir de la requête POST
                montant_ttc = request.POST.get('montant_ttc')
                quantite_tot = request.POST.get('quantitetot')
                panier_data = request.POST.get('panier_data')
                date_1 =request.POST.get('date_paie_hold')
                if date_1 is not None:
                    date_now = date_1.replace('T', ' ')
                else:
                    date_now = request.POST.get('date_paie_hold')
                cout_total =request.POST.get('couttotal')
                balance = request.POST.get('balance')
                deposit = request.POST.get('deposit')
                
                print("Contenu du panier :", panier_data)  # Vérification des données du panier
                
                if panier_data:
                    panier = json.loads(panier_data)
                    receipt = tbreceipt.objects.create(
                        num_receipt = receipt_id,
                        num_bath="100",
                        client="100",
                        total_article=quantite_tot,
                        tax=tax,
                        total_cost=cout_total,
                        total_price=montant_ttc,
                        receipt_discount=discount,
                        balance=balance,
                        observation="ok",
                        statut="OPENNED",
                        deposit=deposit,
                        service_charge=service_charge,
                        type_receipt="IN",
                        date_close=date_now,
                        close_by="Jojo"
                    )
                    #latest_receipt_id = receipt.num_receipt
                    
                    for item in panier:
                        article = tbarticle.objects.get(id=item['article_id'])  # Utiliser get au lieu de filter
                        receipt = tbreceipt.objects.get(num_receipt=receipt_id)
                        tbreceiptarticle.objects.create(
                            num_ligne=1,
                            receipt=receipt,
                            article=article,
                            quantite=item['quantite'],
                            cout=article.cout_unit,  # Utiliser directement l'attribut de l'objet article
                            prix=item['prix'],
                            discount_article=0,
                            observation="",
                            statut="OPENNED",
                            user_added_byreceipt="Jojo",
                            date_added=date_now
                        )
                    return redirect('manage_receipt')
            except Exception as e:
                # Capturer l'exception et afficher un message d'erreur (ou journaliser l'erreur)
                print("Une erreur s'est produite lors du traitement du panier :", str(e))
                return HttpResponseServerError("Une erreur s'est produite lors du traitement du panier. Veuillez contacter l'administrateur.")       
        return redirect('manage_receipt')

def rapport_vente(request):
    current_user = request.user
    compagnie_id = current_user.compagnie
    date_debut_str = request.GET.get('date_debut')
    date_fin_str = request.GET.get('date_fin')
    employe_info = Membre.objects.filter(admin__compagnie=current_user.compagnie_id, membre_actif='True')
    aggregate_data = None  # Initialisation de la variable
    grands_total = 0  # Initialisation de grands_total
    gains = 0
    #exchange_us = 0
    date_debut = datetime.now()
    date_fin = datetime.now()

    if date_debut_str and date_fin_str:
        date_debut = datetime.strptime(date_debut_str, "%Y-%m-%dT%H:%M")
        date_fin = datetime.strptime(date_fin_str, "%Y-%m-%dT%H:%M")
    
    date1 = request.GET.get('verif')
    date2 = request.GET.get('verif2')
        # Récupérer toutes les données pertinentes de la base de données
    receipt_info = tbreceipt.objects.all()
    
    total_tax = sum(receipt_info.values_list('tax', flat=True))
    if total_tax is None:
        total_tax = 0

    total_discount = sum(receipt_info.values_list('receipt_discount', flat=True))
    if total_discount is None:
        total_discount = 0

    total_servicecharge = sum(receipt_info.values_list('service_charge', flat=True))
    if total_servicecharge is None:
        total_servicecharge =0
    paiements = tbpaiement.objects.all()
    #filter(date_paiement__range=(date1, date2))

        # Calculer les agrégations conditionnelles en Python
    total_cash = sum(p.montant for p in paiements if p.type_paiement == 'Cash')
    total_us_cash = sum(p.montant for p in paiements if p.type_paiement == 'US Cash')
    total_account = sum(p.montant for p in paiements if p.type_paiement == 'Account')
    total_check = sum(p.montant for p in paiements if p.type_paiement == 'Check')
    total_complementary = sum(p.montant for p in paiements if p.type_paiement == 'Complementary')
    total_natcash = sum(p.montant for p in paiements if p.type_paiement == 'Natcash')
    total_moncash = sum(p.montant for p in paiements if p.type_paiement == 'Moncash')
    total_zelle = sum(p.montant for p in paiements if p.type_paiement == 'Zelle')
    total_cashapp = sum(p.montant for p in paiements if p.type_paiement == 'Cash App')
    total_unicarte = sum(p.montant for p in paiements if p.type_paiement == 'Unicarte')
    total_sogecarte = sum(p.montant for p in paiements if p.type_paiement == 'SogeCarte')
    total_dollarcard = sum(p.montant for p in paiements if p.type_paiement == 'Dollar Card')
     #grands_total = sum(aggregate_data.values())
    grands_total = total_cash + total_account + total_check + total_complementary 
    gains = grands_total - total_complementary
    taux_du_jr = tbconfiguration.objects.get(compagnie = compagnie_id)
    
    exchange_us = total_us_cash * taux_du_jr.other_curr_rate
    exchange_dollarcard = total_dollarcard * taux_du_jr.other_curr_rate
    exchange_zelle = total_zelle * taux_du_jr.other_curr_rate
    exchange_cashapp = total_cashapp * taux_du_jr.other_curr_rate
    paiement_info = tbpaiement.objects.filter(receipt__compagnie=compagnie_id)
        # Créer le dictionnaire de données agrégées
    aggregate_data = {
            'total_cash': total_cash,
            'total_us_cash': total_us_cash,
            'total_account': total_account,
            'total_check': total_check,
            'total_complementary': total_complementary,
            'total_natcash':total_natcash,
            'total_moncash':total_moncash,
            'total_zelle':total_zelle,
            'total_cashapp':total_cashapp,
            'total_unicarte':total_unicarte,
            'total_sogecarte':total_sogecarte,
            'total_dollarcard':total_dollarcard,
            'total_tax':total_tax,
            'total_discount': total_discount, 
            'total_servicecharge':total_servicecharge,
            'exchange_us':exchange_us,
            'exchange_dollarcard':exchange_dollarcard,
            'exchange_zelle':exchange_zelle,
            'exchange_cashapp':exchange_cashapp,
            'grands_total':grands_total,
            'gains':gains,
            'paiement_info':paiement_info,
            'employe_info':employe_info,
        }

        # Calculer le total général et les gains
    #grands_total = sum(aggregate_data.values())
    gains = grands_total - aggregate_data['total_complementary']


        # Afficher les valeurs agrégées
    print("la date de debut est:", date1)
    print("la date de fin est:", date2)
    print(total_cash)
    print(total_us_cash)
    print(grands_total)

    return render(request, "hod_template/manage_rapportvente_template.html", aggregate_data)

def rapport_ventes(request):
    
    date_debut_str = request.GET.get('date_debut')
    date_fin_str = request.GET.get('date_fin')

    aggregate_data = None  # Initialisation de la variable
    grands_total = 0  # Initialisation de grands_total
    gains = 0

    current_user = request.user
    compagnie_id = current_user.compagnie
    paiement_info = tbpaiement.objects.filter(receipt__compagnie =compagnie_id)
    configuration_info = tbconfiguration.objects.filter(compagnie = compagnie_id)
    categories = tbdepartement.objects.all()
    articles = tbarticle.objects.all()
    receipt_articles = tbreceiptarticle.objects.filter(receipt_id=103).values(
        'receipt_id', 'article_id', 'article__description', 'quantite', 'cout', 'prix'
        )
    
    with connection.cursor() as cursor:
            cursor.execute("SELECT num_receipt, num_bath, client, user_receipt, date_receipt, total_article, tax, total_cost, total_price, receipt_discount, balance, observation, statut, deposit, service_charge, type_receipt FROM psp_cash_app_tbreceipt WHERE statut = 'OPENNED' and compagnie_id=1 ")
            opentap = cursor.fetchall()
        # Exécution de la requête SQL pour compter les reçus ouverts
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(num_receipt) FROM psp_cash_app_tbreceipt WHERE statut = 'OPENNED' and compagnie_id=1 ")
        opened_receipt_count = cursor.fetchone()[0]

        # Passage du nombre de reçus ouverts au contexte de rendu
    with connection.cursor() as cursor:
        cursor.execute ("SELECT SUM(CASE WHEN type_paiement = 'Cash' THEN montant ELSE 0 END) AS Cash, SUM(CASE WHEN type_paiement = 'US Cash' THEN montant ELSE 0 END) AS US_Cash, SUM(CASE WHEN type_paiement = 'Account' THEN montant ELSE 0 END) AS Account, SUM(CASE WHEN type_paiement = 'Check' THEN montant ELSE 0 END) AS Check_Payment, SUM(CASE WHEN type_paiement = 'Complementary' THEN montant ELSE 0 END) AS Complementary, SUM(CASE WHEN type_paiement = 'Unicarte' THEN montant ELSE 0 END) AS Unicarte, SUM(CASE WHEN type_paiement = 'SogeCarte' THEN montant ELSE 0 END) AS SogeCarte, SUM(CASE WHEN type_paiement = 'Dollar Card' THEN montant ELSE 0 END) AS Dollar_Card, SUM(CASE WHEN type_paiement = 'Zelle' THEN montant ELSE 0 END) AS Zelle, SUM(CASE WHEN type_paiement = 'Cash App' THEN montant ELSE 0 END) AS Cash_App, SUM(CASE WHEN type_paiement = 'Natcash' THEN montant ELSE 0 END) AS Natcash, SUM(CASE WHEN type_paiement = 'Moncash' THEN montant ELSE 0 END) AS Moncash, SUM(CASE WHEN type_paiement = 'Split' THEN montant ELSE 0 END) AS Split, ( SELECT SUM(a.total_article) AS totalArticleSale FROM psp_cash_app_tbreceipt a ) AS totalArticleSale, ( SELECT SUM(a.tax) AS totalTaxSale FROM psp_cash_app_tbreceipt a ) AS totalTaxSale, ( SELECT SUM(a.total_cost) AS totalCostSale FROM psp_cash_app_tbreceipt a ) AS totalCostSale, ( SELECT SUM(a.total_price) AS totalPriceSale FROM psp_cash_app_tbreceipt a ) AS totalPriceSale, ( SELECT SUM(a.receipt_discount) AS totalDiscountSale FROM psp_cash_app_tbreceipt a ) AS totalDiscountSale, ( SELECT SUM(a.service_charge) AS totalServiceChargeSale FROM psp_cash_app_tbreceipt a) AS totalServiceChargeSale FROM psp_cash_app_tbpaiement")
        receipt_info = cursor.fetchall()
        grand_total = sum([row[i] for row in receipt_info for i in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15)])
        gain = grand_total - receipt_info[0][15]
        grand_total_without_tca_complementary = sum([row[i] for row in receipt_info for i in (0, 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 15)])
        gain_without_tca_complementary = grand_total_without_tca_complementary - receipt_info[0][15]
        
    if date_debut_str and date_fin_str:
        date_debut = datetime.strptime(date_debut_str, "%Y-%m-%dT%H:%M:%S.%f")
        date_fin = datetime.strptime(date_fin_str, "%Y-%m-%dT%H:%M:%S.%f")

        # Récupérer toutes les données pertinentes de la base de données
        paiements = tbpaiement.objects.filter(date_paiement__range=(date_debut, date_fin))

        # Calculer les agrégations conditionnelles en Python
        total_cash = sum(p.montant for p in paiements if p.type_paiement == 'Cash')
        total_us_cash = sum(p.montant for p in paiements if p.type_paiement == 'US Cash')
        total_account = sum(p.montant for p in paiements if p.type_paiement == 'Account')
        total_check = sum(p.montant for p in paiements if p.type_paiement == 'Check')
        total_complementary = sum(p.montant for p in paiements if p.type_paiement == 'Complementary')

        # Créer le dictionnaire de données agrégées
        aggregate_data = {
            'total_cash': total_cash,
            'total_us_cash': total_us_cash,
            'total_account': total_account,
            'total_check': total_check,
            'total_complementary': total_complementary,
        }

        # Calculer le total général et les gains
        grands_total = sum(aggregate_data.values())
        gains = grands_total - aggregate_data['total_complementary']
            
        
    response_data = {
        'message': 'Données reçues avec succès',
        'aggregate_data': aggregate_data,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'categories': categories,
        'articles': articles,
        'opened_receipt_count': opened_receipt_count,
        'opentap': opentap,
        'receipt_articles':receipt_articles,
        'configuration_info': configuration_info,
        'paiement_info':paiement_info,
        'receipt_info':receipt_info,
        'grand_total':grand_total,
        'gain':gain,
        'grand_total_without_tca_complementary':grand_total_without_tca_complementary,
        'gain_without_tca_complementary':gain_without_tca_complementary,
        'grands_total':grands_total,
        'gains':gains,
        }
    #print(receipt_info)
    return render(request, "hod_template/manage_rapportvente_template.html", response_data)

def rapport_stock(request):
    current_user = request.user
    compagnie_id = current_user.compagnie
    employe_info = Membre.objects.filter(admin__compagnie=current_user.compagnie_id, membre_actif='True')
    departement = tbdepartement.objects.all().filter(compagnie_id = 1)
    date_debut_str = request.GET.get('date_debut')
    date_fin_str = request.GET.get('date_fin')
    stock = tbreceiptarticle.objects.filter(receipt__compagnie=compagnie_id)
    
    # Calculer la marge pour chaque article
    for article in stock:
        article.margin = (article.prix - article.cout) * article.quantite
        article.total_prix = (article.prix * article.quantite)
        article.tax = ((article.prix * article.quantite) * 0.01)
    
    response_data = {
        'date_debut_str': date_debut_str,
        'date_fin_str': date_fin_str,
        'stock': stock,
        'employe_info':employe_info,
        'departement':departement,
    }
    return render(request, "hod_template/manage_rapportstock_template.html", response_data)

def tab_open(request):
    current_user = request.user
    compagnie_id = current_user.compagnie
    configuration_info = tbconfiguration.objects.filter(compagnie = compagnie_id)
    categories = tbdepartement.objects.all()
    articles = tbarticle.objects.all()
    receipt_articles = tbreceiptarticle.objects.filter(receipt_id=103).values(
        'receipt_id', 'article_id', 'article__description', 'quantite', 'cout', 'prix'
    )
   
    with connection.cursor() as cursor:
        cursor.execute("SELECT num_receipt, num_bath, client, user_receipt, date_receipt, total_article, tax, total_cost, total_price, receipt_discount, balance, observation, statut, deposit, service_charge, type_receipt FROM psp_cash_app_tbreceipt WHERE statut = 'OPENNED' and compagnie_id=1 ")
        opentap_info = cursor.fetchall()
    # Exécution de la requête SQL pour compter les reçus ouverts
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(num_receipt) FROM psp_cash_app_tbreceipt WHERE statut = 'OPENNED' and compagnie_id=1 ")
        opened_receipt_count = cursor.fetchone()[0]

    # Passage du nombre de reçus ouverts au contexte de rendu
    context = {
        'categories': categories,
        'articles': articles,
        'opened_receipt_count': opened_receipt_count,
        'opentap_info': opentap_info,
        'receipt_articles':receipt_articles,
        'configuration_info': configuration_info
    }
    #print(opentap)
    return render(request, "hod_template/liste_tabopen.html", context)

def count_opened_receipts(self):
        # Exécuter la requête SQL raw
        query = "SELECT COUNT(num_receipt) FROM psp_cash_app_tbreceipt WHERE statut='OPENNED'"
        result = self.raw(query)
        # Récupérer le résultat
        count = None
        for row in result:
            count = row.count
            break  # Pour ne récupérer que la première ligne
        return count
    
def details_receipt(request, receipt_id):
    receipt = tbreceipt.objects.get(num_receipt=receipt_id)
    receipt_info = tbreceiptarticle.objects.filter(receipt=receipt)
    return render(request, "hod_template/manage_detailscommande_template.html", { "receipt": receipt, "receipt_info": receipt_info })

def supprimer_receipt(request, receipt_id):
    
    receipt_del = tbreceipt.objects.get(num_receipt=receipt_id)
    receipt_del.delete()
    current_user = request.user
    #compagnie_id = current_user.compagnie_id
    receipt_info = tbreceipt.objects.filter(compagnie_id=current_user.compagnie).order_by('num_receipt')

    if 'q' in request.GET:
        q = request.GET['q']
        
        all_receipt_list = tbreceipt.objects.filter(compagnie_id=current_user.compagnie).order_by('num_receipt')
    else:
        all_receipt_list = tbreceipt.objects.filter(compagnie_id=current_user.compagnie).order_by('num_receipt')
    paginator = Paginator(all_receipt_list,250,orphans=5)
    page = request.GET.get('page')
    receipt_info = paginator.get_page(page)
    return render(request, "hod_template/manage_receipt_template.html", { "receipt_info": receipt_info })

def add_depense(request):
    depense_info = tbpayout.objects.all()
    return render(request, "hod_template/add_payout_template.html", {"depense_info":depense_info})

def add_depense_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        current_user = request.user
        #code_compagnie = current_user.compagnie
        payout = request.POST.get("payout")
        date_payout = request.POST.get("date_payout")
        payout_comment = request.POST.get("description")
        try:
            depense = tbpayout.objects.create(
                payout=payout,
                date_payout=date_payout,
                payout_comment=payout_comment,
                userAdded=request.user.username,
                compagnie = current_user.compagnie
            )
            messages.success(request, "Successfully Added Depense")
            return HttpResponseRedirect(reverse("add_depense")) 
        except Exception as e:
            messages.error(request, traceback.format_exc())
            return HttpResponseRedirect(reverse("add_depense"))

def supprimer_depense(request, code_payout):
    depense = tbpayout.objects.get(code_payout=code_payout)
    depense.delete()
    depense_info = tbpayout.objects.all()
    return render(request, "hod_template/add_payout_template.html", { "depense_info": depense_info })

def manage_membre(request):
    current_user = request.user
    compagnie_id = current_user.compagnie_id
    membres = Membre.objects.filter(admin__compagnie=current_user.compagnie)

    if 'q' in request.GET:
        q = request.GET['q']
        
        all_membre_list = Membre.objects.filter( Q(nomp__icontains=q) | Q(prenomp__icontains=q) | Q(codep__icontains=q) | Q(referencep__icontains=q))
    else:
        all_membre_list = Membre.objects.filter(admin__compagnie=current_user.compagnie)
        #all_membre_list = Membre.objects.prefetch_related('CustomUser').filter(compagnie=2)
    paginator = Paginator(all_membre_list,15,orphans=5)
    page = request.GET.get('page')
    membres = paginator.get_page(page)
    return render(request, "hod_template/manage_membre_template.html", { "membres": membres })



def remplirPanier(request, article_id):
    current_user = request.user
    compagnie_id = current_user.compagnie_id
    articles = tbarticle.objects.all()
    article_info = tbarticle.objects.filter(code_articl=article_id)
    article = tbarticle.objects.get(code_articl=article_id)
    total = article.prix * 1
    return render(request, "hod_template/add_receipt_template.html", { "article_info": article_info , "articles": articles, "total":total})








    return render(request, "hod_template/manage_session_template.html")

@csrf_exempt
def check_email_exist(request):
    email=request.POST.get("email")
    user_obj=CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)

@csrf_exempt
def check_codep_exist(request):
    codep=request.POST.get("codep")
    user_obj=Membre.objects.filter(codep=codep).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)

@csrf_exempt
def check_codeCredit_exist(request):
    codec=request.POST.get("numero_credit")
    user_obj=tbcredit.objects.filter(numero=codec).exists()
    if user_obj:
        return HttpResponse(True)
        capital = user_obj.montant_credit / user_obj.nbre_de_mois
        interet = user_obj.montant_credit * 0.1
        montant_ = capital + interet
    else:
        return HttpResponse(False)

def membre_feedback_message(request):
    current_user = request.user
    compagnie_id = current_user.compagnie_id
    feedbacks=FeedBackMembre.objects.filter(code_membre__admin__compagnie = compagnie_id)
    return render(request, "hod_template/membre_feedback_template.html", {"feedbacks":feedbacks})

@csrf_exempt
def membre_feedback_message_replied(request):
    current_user = request.user
    compagnie_id = current_user.compagnie_id
    feedback_id=request.POST.get("id_message")
    feedback_message=request.POST.get("reponse_message")
    try:
        feedback=FeedBackMembre.objects.get(id=feedback_id)
        feedback.feedback_reply=feedback_message
        feedback.save()
        messages.success(request,"Successfully Responded")
        return HttpResponseRedirect(reverse("membre_feedback_message"))
        #return HttpResponse(True)
    except:
        messages.error(request,traceback.format_exc())
        return HttpResponseRedirect(reverse("membre_feedback_message"))
        #return HttpResponse(False)

def membre_leave_view(request):
    current_user = request.user
    compagnie_id = current_user.compagnie_id
    leaves =LeaveReportMembre.objects.filter(code_membre__admin__compagnie = compagnie_id)
    return render(request, "hod_template/membre_leave_view.html",{"leaves":leaves})

def membre_approve_leave(request, leave_id):
    current_user = request.user
    compagnie_id = current_user.compagnie_id
    leave=LeaveReportMembre.objects.get(id=leave_id)
    leave.leave_status=1
    leave.save()
    return HttpResponseRedirect(reverse("membre_leave_view"))

def membre_disapprove_leave(request, leave_id):
    current_user = request.user
    compagnie_id = current_user.compagnie_id
    #return HttpResponse("ID : "+leave_id)
    leave=LeaveReportMembre.objects.get(id=leave_id)
    leave.leave_status=2
    leave.save()
    return HttpResponseRedirect(reverse("membre_leave_view"))

def comiteSMS_feedback(request):
    feedback_data=FeedBackMembre.objects.all()
    return render(request, "hod_template/comiteSMS_feedback.html",{"membre_data":feedback_data})

def comiteSMS_feedback_save(request):
    current_user = request.user
    compagnie_id = current_user.compagnie
 
    if request.method !="POST":
        return HttpResponse("Method Not Allowed")
    else:
        #date_depense = request.POST.get("date_depense")
        feedback_msg=request.POST.get("feedback_msg")

        try:
            ####################################
            feedback=FeedBackMembre(code_membre=request.user.id, feedback=feedback_msg, feedback_reply="")
            feedback.save()
            messages.success(request,"Successfully Message Sended")
            return HttpResponseRedirect(reverse("comiteSMS_feedback")) 
        except Exception as e:
            messages.error(request,traceback.format_exc())
            return HttpResponseRedirect(reverse("comiteSMS_feedback"))
    
def admin_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    #membre_infocon = Membre.object.get(id=1)
    #membre_info=Membre.objects.get(admin=request.user.id)
    return render(request,"hod_template/admin_profile.html",{"user":user})

def admin_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("admin_profile"))
    else:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password = request.POST.get("password")
       
    try:
        customuser=CustomUser.objects.get(id=request.user.id)
        customuser.first_name=first_name
        customuser.last_name=last_name
        if password != None and password !="":
            customuser.set_password(password)
        customuser.save()
        messages.success(request,"Successfully Update Profile")
        return HttpResponseRedirect(reverse("admin_profile"))
    except:
        messages.success(request,"Failed Update Profile")
        return HttpResponseRedirect(reverse("admin_profile"))

def import_datadepensee_csv(request):
    if request.method == 'POST':
        file = request.FILES['file']

        # Check if the uploaded file is a CSV file
        if not file.name.endswith('.csv'):
            messages.error(request, 'This is not a CSV file')
            return render(request, 'manage_depense_template.html')

        # Read the CSV file
        data = csv.reader(file.read().decode('utf-8').splitlines())

        # Loop through the rows in the CSV file and insert them into the database
        for row in data:
            tbdepense.objects.create(date_depense=row[0], description=row[1], depense_unit=row[2], quantite_dep=row[2])

        messages.success(request, 'Data imported successfully')
        return render(request, 'manage_depense_template.html')

    return render(request, 'manage_depense_template.html')

def import_data(request):
  if request.method == 'POST':
    file = request.FILES['file']
    print(f'File uploaded: {file}')

# importer les donnees
def import_datadepensees_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES['csv_file']

        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'This is not a CSV file')
        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        next(io_string)

        for column in csv.reader(io_string, delimiter=',', quotechar='"'):
            _, created = tbdepense.objects.update_or_create(
                date_depense=column[0],
                description=column[1],
                depense_unit=column[2],
                quantite_dep=column[3]
            )

        return render(request, 'import.html')

    return render(request, 'import.html')

def import_datadepenseers_csv(request):
    if request.method == 'POST':
        file = request.FILES['csv_file']

        # Check if the uploaded file is a CSV file
        if not file.name.endswith('.xlsx'):
            messages.error(request, 'This is not a CSV file')
            return render(request, 'hod_template/manage_depense_template.html')

        # Read the CSV file with the correct encoding
        data = csv.reader(file.read().decode('latin1').splitlines())

        # Loop through the rows in the CSV file and insert them into the database
        for row in data:
            tbdepense.objects.create(date_depense=row[0], description=row[1], depense_unit=row[2], quantite_dep=row[2])

        messages.success(request, 'Data imported successfully')
        return render(request, 'hod_template/manage_depense_template.html')

    return render(request, 'hod_template/manage_depense_template.html')

def import_datadepensesss_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES['csv_file']

        # Check if the uploaded file is a CSV file
        if not csv_file.name.endswith('.xlsx'):
            messages.error(request, 'This is not a CSV file')
            return render(request, 'hod_template/manage_depense_template.html')

        # Read the CSV file and remove any null characters
        file_data = csv_file.read().decode('utf-8').replace('\0', '')

        # Create a CSV reader and skip the header row
        data = csv.reader(file_data.splitlines())
        next(data)

        # Loop through the rows in the CSV file and insert them into the database
        for row in data:
            tbdepense.objects.create(date_depense=row[0], description=row[1], depense_unit=row[2], quantite_dep=row[2])

        messages.success(request, 'Data imported successfully')
        return render(request, 'hod_template/manage_depense_template.html')

    return render(request, 'hod_template/manage_depense_template.html')

def import_datadepense_csvs(request):
    if request.method == 'POST':
        csv_file = request.FILES['csv_file']
        # Vérifiez que le fichier est bien un fichier Excel
        if not csv_file.name.endswith('.xlsx'):
            messages.error(request, 'Le fichier doit être au format Excel')
            return render(request, 'hod_template/manage_depense_template.html')
        # Ouvrez le fichier Excel
        workbook = xlrd.open_workbook(file_contents=csv_file.read())
        worksheet = workbook.sheet_by_index(0)
        # Parcourez les lignes du fichier Excel et créez des objets MyModel
        for row_num in range(1, worksheet.nrows):
            row = worksheet.row_values(row_num)
            obj = tbdepense()
            obj.date_depense=datetime.datetime(*xlrd.xldate_as_tuple(row[0], workbook.datemode)),
            obj.description=row[1],
            obj.depense_unit=row[2],
            obj.quantite_dep=row[3]
            # Ajuster les autres champs en fonction des colonnes du fichier Excel
            obj.save()
        messages.success(request, 'Les données ont été importées avec succès')
        return render(request, 'hod_template/manage_depense_template.html')
    else:
        return render(request, 'hod_template/manage_depense_template.html')
    
def import_datadepense_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES['csv_file']

        # Check if the uploaded file is an Excel file
        if not csv_file.name.endswith('.xlsx'):
            messages.error(request, 'This is not an Excel file')
            return render(request, 'hod_template/manage_depense_template.html')

        # Load the Excel file using openpyxl
        wb = openpyxl.load_workbook(csv_file)
        sheet = wb.active

        # Loop through the rows in the Excel file and insert them into the database
        for row in sheet.iter_rows(min_row=2, values_only=True):
            tbdepense.objects.create(date_depense=row[0], description=row[1], depense_unit=row[2], quantite_dep=row[2])

        messages.success(request, 'Data imported successfully')
        return render(request, 'hod_template/manage_depense_template.html')

    return render(request, 'hod_template/manage_depense_template.html')

    #----------------------- exporter fichier excel --------------------------------------
    # export tous les users       

# Exportation sur EXCEL----------------------------------------------------------------------------------
def export_membres_csv(request):
    current_user = request.user
    compagnie_id = current_user.compagnie_id
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Liste_membre.csv"'

    writer = csv.writer(response)
    writer.writerow(['Id','codep', 'nomp', 'prenomp', 'sexep', 'lieunaissance', 'adressep', 'activiteprofessionp','referencep', 'Date Ajout',  'Admin_id', 'membre_actif']) # Add column headers

    my_data = Membre.objects.filter(admin__compagnie=current_user.compagnie)
    for item in my_data:
        writer.writerow([item.id, item.codep, item.nomp,item.prenomp, item.sexep, item.lieunaissancep, item.adressep, item.activiteprofessionp, item.referencep,item.dateajout, item.admin_id,  item.membre_actif]) # Add data rows
    return response

def export_cotisation_csv(request):
    current_user = request.user
    compagnie_id = current_user.compagnie_id
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Liste_cotisation.csv"'

    writer = csv.writer(response)
    writer.writerow(['Id','typecotisation', 'montant', 'interet', 'balance', 'date_fait', 'code_membre', 'penalite','recu_par']) # Add column headers
    my_data = tbcotisation.objects.filter(code_membre_id__admin__compagnie=current_user.compagnie)
    for item in my_data:
        writer.writerow([item.id, item.typecotisation, item.montant,item.interet, item.balance, item.date_fait, item.code_membre_id, item.penalite, item.recu_par]) # Add data rows
    return response

def export_credit_csv(request):
    current_user = request.user
    compagnie_id = current_user.compagnie_id
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Liste_credit.csv"'

    writer = csv.writer(response)
    #credit=tbcredit(numero=numero_credit, date_credit=date_credit, nbre_de_mois=nbre_de_mois,date_debut=date_debut, date_fin=date_fin, montant_credit=float(montant_recu), interet_credit=float(interet_recu), code_membre=code_membre, commentaire=commentaire, valider_par=valider_par)
    writer.writerow(['numero','date_credit', 'nbre_de_mois', 'date_debut', 'date_fin', 'montant_credit', 'interet_credit', 'code_membre','commentaire','valider_par']) # Add column headers
    my_data = tbcredit.objects.filter(code_membre_id__admin__compagnie=current_user.compagnie)
    for item in my_data:
        writer.writerow([item.numero, item.date_credit, item.nbre_de_mois,item.date_debut, item.date_fin, item.montant_credit, item.interet_credit, item.code_membre, item.commentaire, item.valider_par]) # Add data rows
    return response

def export_remboursement_csv(request):
    current_user = request.user
    compagnie_id = current_user.compagnie_id
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Liste_remboursement.csv"'

    writer = csv.writer(response)
    #remboursement=tbremboursement(date_remb=date_remboursement,  montant_a_remb=float(montant_recu),capital_remb=float(capital_recu), interet_remb=float(interet_recu), balance=float(balance_recu), penalite=float(penalite_recu), commentaire=commentaire, recu_par=valider_par, codecredit=code_credit, faites_par=code_membre)
    writer.writerow(['ID','date_remb', 'montant_a_remb', 'capital_remb', 'interet_remb', 'balance', 'penalite','commentaire', 'recu_par','codecredit_id', 'faites_par_id']) # Add column headers
    my_data = tbremboursement.objects.filter(faites_par_id__admin__compagnie=current_user.compagnie)
    for item in my_data:
        writer.writerow([item.id, item.date_remb, item.montant_a_remb,item.capital_remb, item.interet_remb, item.balance, item.penalite,item.commentaire, item.recu_par, item.codecredit_id, item.faites_par_id]) # Add data rows
    return response

def export_detailcredit_csv(request):
    current_user = request.user
    compagnie_id = current_user.compagnie_id
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Liste_detail_credit.csv"'

    writer = csv.writer(response)
    #remboursement=tbremboursement(date_remb=date_remboursement,  montant_a_remb=float(montant_recu),capital_remb=float(capital_recu), interet_remb=float(interet_recu), balance=float(balance_recu), penalite=float(penalite_recu), commentaire=commentaire, recu_par=valider_par, codecredit=code_credit, faites_par=code_membre)
    writer.writerow(['codecredit','date_pret', 'montant_pret', 'montant_capital', 'montant_interet', 'total_montant', 'total_montant_rest']) # Add column headers
    my_data = tbdetailcredit.objects.filter(Q(codecredit_id__in=tbcredit.objects.filter( code_membre_id__in=Membre.objects.filter(admin_id__in=CustomUser.objects.filter(compagnie_id=compagnie_id))).values('numero')))
    for item in my_data:
        writer.writerow([item.codecredit_id, item.date_pret, item.montant_pret,item.montant_capital, item.montant_interet, item.total_montant_jr, item.total_montant_rest]) # Add data rows
    return response

def export_depense_csv(request):
    current_user = request.user
    compagnie_id = current_user.compagnie_id
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Liste_depense.csv"'

    writer = csv.writer(response)
    # depense=tbdepense(date_depense=date_depense,  description=description, depense_unit=float(depense_unit), quantite_dep=float(quantite_dep), compagnie_id=compagnie_id)
    writer.writerow(['ID','date_depense', 'description', 'depense_unit', 'quantite_dep']) # Add column headers
    my_data = tbdepense.objects.filter(compagnie_id=current_user.compagnie)
    for item in my_data:
        writer.writerow([item.id, item.date_depense, item.description,item.depense_unit, item.quantite_dep]) # Add data rows
    return response

def export_detailalimentaire_csv(request):
    current_user = request.user
    compagnie_id = current_user.compagnie_id
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Liste_detailAlimentaire.csv"'

    writer = csv.writer(response)
    #detailproduct=tbdetailproduit(codecredit=code_credit,  description=description, quantite_prod=float(quantite), prix_unitaire=float(prix_unitaire), prix_total=float(prix_total), frais_transport=float(frais_transport), prix_de_revient=float(prix_revient), prix_de_vente=float(prix_vente))
    writer.writerow(['No','codecredit', 'description', 'quantite_prod', 'prix_unitaire', 'prix_total', 'frais_transport', 'prix_de_revient','prix_de_vente']) # Add column headers
    my_data = tbdetailproduit.objects.filter(codecredit_id__code_membre_id__admin__compagnie=current_user.compagnie)
    for item in my_data:
        writer.writerow([item.no, item.codecredit, item.description,item.quantite_prod, item.prix_unitaire, item.prix_total, item.frais_transport, item.prix_de_revient, item.prix_de_vente]) # Add data rows
    return response

def export_statistique_cotisation_csv(request):
    current_user = request.user
    compagnie_id = str(current_user.compagnie_id)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="statistique_cotisation.csv"'

    writer = csv.writer(response)
    # depense=tbdepense(date_depense=date_depense,  description=description, depense_unit=float(depense_unit), quantite_dep=float(quantite_dep), compagnie_id=compagnie_id)
    
    writer.writerow(['ID','code_membre', 'nom_membre', 'montant_caisse_verte', 'montant_caisse_rouge', 'fond_urgence', 'montant_interet', 'montant_penalite', 'montant_penalite']) # Add column headers
    #my_data = tbdepense.objects.filter(compagnie_id=current_user.compagnie)
    query = """
        select a.id, codep,  nomp || ' ' || prenomp AS nom_membre, sum(case when typecotisation = "Fond de Credit" then montant else 0 END) as Montantcredit, sum(case when typecotisation = "Fond de Fonctionnement" then montant END) as MontantFonct, sum(case when typecotisation = "Fond d'Urgence" then montant else 0 END) as MontantUrgence, sum(interet) as MontantInteret,sum(penalite) as penalite, (sum(interet)+ sum(case when typecotisation = "Fond de Credit" then montant else 0 END)+sum(case when typecotisation = "Fond d'Urgence" then montant else 0 END)) as Montanttotal  from psp_cash_app_membre a, psp_cash_app_tbcotisation b, psp_cash_app_customuser c where code_membre_id=a.id and a.admin_id=c.id and c.compagnie_id = %s group by code_membre_id 
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [compagnie_id])
        my_data = cursor.fetchall()

    for item in my_data:
        writer.writerow([item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8]]) # Add data rows
            #writer.writerow([item.codecredit_id, item.quantite_remboursement, item.Qtee_restant, item.montant_total_rembourse, item.montant_total_Restant, item.total_interet, item.total_interet_restant, item.total_penalite]) # Add data rows
    return response

def export_statistique_remboursement_csv(request):
    current_user = request.user
    compagnie_id = str(current_user.compagnie_id)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="statistique_remboursement.csv"'

    writer = csv.writer(response)
    # depense=tbdepense(date_depense=date_depense,  description=description, depense_unit=float(depense_unit), quantite_dep=float(quantite_dep), compagnie_id=compagnie_id)
    
    writer.writerow(['ID','qte_rembourser', 'qte_restant', 'montant_rambourser', 'montant_restant', 'total_interet', 'Interet_restant', 'total_penalite']) # Add column headers
    #my_data = tbdepense.objects.filter(compagnie_id=current_user.compagnie)
    query = """
        SELECT 
    codecredit_id,
    COUNT(psp_cash_app_tbremboursement.id) AS quantite_remboursement,
	(psp_cash_app_tbcredit.nbre_de_mois- COUNT(psp_cash_app_tbremboursement.id)) as Qtee_restant,
    SUM(capital_remb) + SUM(interet_remb) AS montant_total_rembourse,
	(((capital_remb+interet_remb)*nbre_de_mois) - (SUM(capital_remb) + SUM(interet_remb))) AS montant_total_Restant,
    SUM(interet_remb) AS total_interet,
	(interet_remb*nbre_de_mois) - SUM(interet_remb) AS total_interet_restant,
    SUM(penalite) AS total_penalite
    FROM
        psp_cash_app_tbremboursement,psp_cash_app_membre ,psp_cash_app_customuser, psp_cash_app_tbcredit
    WHERE
        psp_cash_app_tbremboursement.faites_par_id = psp_cash_app_membre.id and psp_cash_app_membre.admin_id = psp_cash_app_customuser.id and psp_cash_app_tbremboursement.codecredit_id = psp_cash_app_tbcredit.numero and psp_cash_app_customuser.compagnie_id = %s
    GROUP BY
        codecredit_id
    ORDER BY
        codecredit_id ASC
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [compagnie_id])
        my_data = cursor.fetchall()

    for item in my_data:
        writer.writerow([item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7]]) # Add data rows
            #writer.writerow([item.codecredit_id, item.quantite_remboursement, item.Qtee_restant, item.montant_total_rembourse, item.montant_total_Restant, item.total_interet, item.total_interet_restant, item.total_penalite]) # Add data rows
    return response

def export_statistique_credit_csv(request):
    current_user = request.user
    compagnie_id = current_user.compagnie_id

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="statistique_remboursement.csv"'

    writer = csv.writer(response)

    writer.writerow(['numero', 'Montant_Credit', 'Montant_rembourser', 'Montant_interet', 'Date_credit'])  # Add column headers

    subquery = tbremboursement.objects.filter(codecredit_id=OuterRef('numero')).values('codecredit_id')
    credit_info = tbcredit.objects.annotate(
        montant_rembourser=ExpressionWrapper(
            (F('montant_credit') * F('interet_credit') * F('nbre_de_mois')) + F('montant_credit'),
            output_field=FloatField()
        ),
        interet_total_credit=ExpressionWrapper(
            ((F('montant_credit') * F('interet_credit') * F('nbre_de_mois')) + F('montant_credit')) - F('montant_credit'),
            output_field=FloatField()
        ),
    ).filter(
        code_membre__id=F('code_membre_id'),
        code_membre__admin__id=F('code_membre__admin__id'),
        code_membre__admin__compagnie_id=compagnie_id,
        pk__in=Subquery(subquery)
    ).values(
        'numero',
        'montant_credit',
        'date_debut',
        'montant_rembourser',
        'interet_total_credit'
    ).order_by('date_debut')

    for item in credit_info:
        montant_credit = format(item['montant_credit'], ".2f")  # Format the value with 2 decimal places
        montant_rembourser = format(item['montant_rembourser'], ".2f")  # Format the value with 2 decimal places
        interet_total_credit = format(item['interet_total_credit'], ".2f")  # Format the value with 2 decimal places
        writer.writerow([
            item['numero'],
            montant_credit,
            montant_rembourser,
            interet_total_credit,
            item['date_debut']
        ])
        
    return response

def dernier_samedi(date):
        while date.weekday() != 5:
            date = date + timedelta(days=1)

        while True:
            dernier_jour = date.replace(day=1) + timedelta(days=32)
            dernier_jour = dernier_jour - timedelta(days=dernier_jour.day)
            while dernier_jour.weekday() != 5:
                dernier_jour = dernier_jour - timedelta(days=1)

            if dernier_jour >= date:
                yield dernier_jour
            date = dernier_jour + timedelta(days=7)

def CalculateurPretView(request):
    current_user = request.user
    compagnie_id = current_user.compagnie_id
     
    code_pret = request.POST.get('code_pret')
    montant_pret = request.POST.get('montant_credit')
    
    nombre_mois = request.POST.get('nombre_mois')
    date_deb = request.POST.get('date_debut')
    if date_deb is not None:
        date_debut = datetime.strptime(date_deb, "%d/%m/%Y")
    else:
        date_debut = "27/05/2023"
    
    generateur_samedis = dernier_samedi(date_debut)
        # Vérifiez si l'intérêt est fixe ou variable
    if request.POST.get('choix_interet') == "Fixe":
        taux_interet = request.POST.get('taux_interet')
        montant_interet = float(montant_pret) * float(taux_interet) / 100
        montant_total = float(montant_pret) + float(montant_interet)
            
    else:
        montant_interet_ = 0.0
        montant_pret = 0.0
        #montant_interet_ = request.POST.get('montant_interet')
        montant_total = float(montant_pret) + float(montant_interet_)
    # Calculez les paiements mensuels
    montant_restant = float(montant_total)
       
    count = 0
    if nombre_mois is not None:
        while count < int(nombre_mois):
            # Trouver le dernier samedi du mois pour la date de début
            derniersam = next(generateur_samedis)
            capital = float(montant_pret) / float(nombre_mois)
            interet = float(montant_interet)
            total = capital + interet
            montant_restant -= capital
            count += 1

            # Insérez les données dans la table
            tbdetailcredit.objects.create(date_pret=derniersam, montant_pret=montant_pret, montant_capital=capital, montant_interet=interet, total_montant_jr=total, total_montant_rest=montant_restant,codecredit_id=code_pret)
    else: 
        nombre_mois = 1
   
    paiements = tbdetailcredit.objects.filter(Q(codecredit_id__in=tbcredit.objects.filter( code_membre_id__in=Membre.objects.filter(admin_id__in=CustomUser.objects.filter(compagnie_id=compagnie_id))).values('numero')))

    # Return the appropriate HttpResponse
    return render(request, "hod_template/frmcalculateur_credit.html", { "paiements":paiements })
    #return render(request, self.template_name, {'paiements': paiements})

def get_credit_data(request):
    code_credit = request.GET.get('code_credit')
    credit = tbcredit.objects.get(numero=code_credit)
    #format(number, ".2f")
    capital_credit = credit.montant_credit / credit.nbre_de_mois
    montant_interet = credit.interet_credit * credit.montant_credit
    montant_a_rembourser = capital_credit + montant_interet
    data = {
        'montant_credit': format(montant_a_rembourser,".2f"),
        'capital_credit':  format(capital_credit,".2f"),
        'interet_credit': format(montant_interet,".2f"),
    }
    return JsonResponse(data)

def get_credit_info(request):
    code_credit = request.GET.get('code_credit')
    credit = tbcredit.objects.get(numero=code_credit)

    montant_credit = credit.montant_credit
    taux_interet = credit.interet_credit *100
    date_debut = credit.date_debut
    duree = credit.nbre_de_mois
    data = {

        'montant_credit': montant_credit,
        'taux_interet': taux_interet,
        'date_debut': date_debut.strftime('%d/%m/%Y'),
        'duree': duree
    }
    return JsonResponse(data)

def add_comments_save(request):
    current_user = request.user
    compagnie_id = current_user.compagnie
    membres = Membre.objects.filter(admin_id=request.user.id).values('id')
    if membres.exists():
        code_membre = membres[0]['id']

    if request.method !="POST":
        return HttpResponse("Method Not Allowed")
    else:
        #current_user = request.user
        text_comment = request.POST.get("content")
        try:
            comment=Comment(text=text_comment, author_id=code_membre, compagnie_id=compagnie_id)
            comment.save()
            return HttpResponseRedirect(reverse("profile_view")) 
        except Exception as e:
            traceback.print_exc() 
            #messages.error(request.traceback.format_exc())
            return HttpResponseRedirect(reverse("profile_view"))
        
def profile_view(request):
    current_user = request.user
    compagnie_id = current_user.compagnie
    # Logic for the profile view
    comments = Comment.objects.filter(author_id=F('author_id__id'), compagnie_id_id=compagnie_id).order_by('-created_at').values('id', 'text', 'created_at','author_id__profile_pic', 'author_id__nomp', 'author_id__prenomp')
    #comments = Comment.objects.annotate(champ_concatene=ExpressionWrapper(F('author_id__nomp') + ' ' + F('author_id__prenomp'),output_field=CharField())).values('id', 'text', 'created_at', 'champ_concatene')
    #comments = Comment.objects.filter(compagnie_id=compagnie_id).order_by('-created_at')
    today_date = datetime.now().date()

    # Ajouter une clé 'difference_in_days' à chaque commentaire contenant la différence en jours
    for comment in comments:
        created_at_date = comment['created_at'].date()
        difference = today_date - created_at_date
        comment['difference_in_days'] = difference.days

    return render(request, 'hod_template/commentaire.html', {'comments': comments})

#@login_required
def user_info(request):
    # Récupérer l'ID de l'utilisateur connecté
    user_id = request.user.id
    
    # Récupérer le type d'utilisateur (par exemple, nom d'utilisateur ou email)
    user_type = request.user.username  # Vous pouvez utiliser d'autres attributs tels que 'email'
    
    # Récupérer l'ID du groupe de l'utilisateur
    group_id = request.user.groups.first().id if request.user.groups.exists() else None
    
    # Récupérer les permissions de l'utilisateur
    permissions = request.user.get_all_permissions()
    
    # Passer les valeurs récupérées au contexte de rendu
    context = {
        'user_id': user_id,
        'user_type': user_type,
        'group_id': group_id,
        'permissions': permissions
    }
    
    return render(request, 'hod_template/user_info.html', context)

#@login_required
def user_access(request):
 
    user_permissions = Permission.objects.all()
    # Passer les accès au contexte de rendu
    context = {
        'user_permissions': user_permissions
    }
    
    return render(request, 'hod_template/user_access.html', context)

def user_groups(request):

    user_groups = AbstractBaseUser.objects.all()
    #
    # Passer les groupes d'utilisateurs au contexte de rendu
    context = {
        'user_groups': user_groups
    }
    return render(request, 'hod_template/user_groups.html', context)

#################### gestion User ##################
def GUtilisateur(request):
    current_user = request.user
    compagnie_id = current_user.compagnie_id

    membre_info = Membre.objects.filter(admin__compagnie=current_user.compagnie, membre_actif='True')
    membres = CustomUser.objects.filter(user_type=2, compagnie=current_user.compagnie)
    initial_data = Permission.objects.filter(name="Can add tbcotisation") | Permission.objects.filter(name="Can add tbcredit") | Permission.objects.filter(name="Can add tbremboursement") | Permission.objects.filter(name="Can add membre") | Permission.objects.filter(name="Can add tbdepense")

    query = """
        SELECT a.id, c.id, c.first_name, c.last_name, b.id, b.name 
        FROM psp_cash_app_customuser_user_permissions a
        JOIN auth_permission b ON a.permission_id = b.id 
        JOIN psp_cash_app_customuser c ON a.customuser_id = c.id 
        WHERE c.compagnie_id = %s
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, [int(compagnie_id)])
            permission_info = cursor.fetchall()
    except Exception as e:
        # Handle exceptions here
        # For example: log the exception or return an error response
        return render(request, "error_template.html", {"error_message": str(e)})
    return render(request, 'hod_template/add_access_user_template.html', {'initial_data': initial_data, 'membre_info':membre_info, 'membres':membres, 'permission_info':permission_info })

def add_access_rightss(request):
    if request.method == 'POST':
        code_membres = request.POST.get("membre")
        code_membre = Membre.objects.get(id=code_membres)
        selected_permissions = request.POST.getlist('permiss')
        
        try:
            for permission_id in selected_permissions:
                permission = Permission.objects.get(id=permission_id)
                # Créez une nouvelle instance de CustomUserPermission pour associer l'utilisateur à la permission
                permission_ajouter = CustomUserPermission.objects.create(customer_id=code_membre, permission_id=permission)
                permission_ajouter.save()
                
            messages.success(request, "Successfully Access Add")
            return HttpResponseRedirect(reverse("GUtilisateur")) 
        except Exception as e:
            messages.error(request, traceback.format_exc())
            return HttpResponseRedirect(reverse("GUtilisateur"))

def add_access_rightee(request):
    if request.method == 'POST':
        code_membres = request.POST.get("membre")
        #code_membre = Membre.objects.get(id=code_membres)
        selected_permissions = request.POST.getlist('permissions')
    
        try:
            for permission_id in selected_permissions:
                permission_id = Permission.objects.get(id=permission_id)
                # Identifiez l'ID de la permission que vous souhaitez ajouter
                #permission_id = 42  # Remplacez 42 par l'ID de la permission que vous souhaitez ajouter

                # Récupérez l'utilisateur auquel vous souhaitez ajouter la permission
                user_instance = Membre.objects.get(id=code_membres)

                # Vérifiez si l'utilisateur a déjà cette permission
                if not user_instance.user_permissions.filter(id=permission_id).exists():
                    # Récupérez l'objet Permission correspondant à l'ID donné
                    permission = Permission.objects.get(id=permission_id)
                    
                    # Ajoutez la permission à l'utilisateur
                    user_instance.user_permissions.add(permission)

                    # Enregistrez les modifications dans la base de données
                    user_instance.save()

                    # Optionnel : message de succès ou autre logique de traitement
                    add_permission_success = True
                else:
                    # Optionnel : message d'erreur ou autre logique de traitement
                    add_permission_success = False
            messages.success(request, "Access successfully added")
            return HttpResponseRedirect(reverse("GUtilisateur")) 
        except Exception as e:
            messages.error(request, traceback.format_exc())
            return HttpResponseRedirect(reverse("GUtilisateur"))

def add_access_rightkk(request):
    if request.method == 'POST':
        code_membres = request.POST.get("membre")
        code_membre = Membre.objects.get(id=code_membres)
        selected_permissions = request.POST.getlist('permis_info[]')
    
        try:
            for permission_id in selected_permissions:
                permission_id = Permission.objects.get(id=permission_id)
                # Créer une nouvelle instance
                permission_instance = CustomUserPermission.objects.create(customuser_id=code_membre, permission_id=permission_id)

                # Récupérer des instances
                permissions = CustomUserPermission.objects.filter(customuser_id=code_membre)

                # Mettre à jour une instance
                permission_instance.customuser = permissions
                permission_instance.save()

            messages.success(request, "Access successfully added")
            return HttpResponseRedirect(reverse("GUtilisateur")) 
        except Exception as e:
            messages.error(request, traceback.format_exc())
            return HttpResponseRedirect(reverse("GUtilisateur"))

def add_access_right(request):
    if request.method == 'POST':
        code_membres = request.POST.get("membre")
        code_membre = Membre.objects.get(admin_id=code_membres)
        selected_permissions = request.POST.getlist('permis_info[]')
    
        try:
            for permission_id in selected_permissions:
                permission_id = Permission.objects.get(id=permission_id)
                # Créer une nouvelle instance
                permission_instance = CustomUserPermission.objects.create(customuser_id=code_membre.admin_id, permission_id=permission_id.id)

            messages.success(request, "Access successfully added")
            return HttpResponseRedirect(reverse("GUtilisateur")) 
        except Exception as e:
            messages.error(request, str(e))
            return HttpResponseRedirect(reverse("GUtilisateur"))

def afficher_listePermission(request):
    current_user = request.user
    compagnie_id = current_user.compagnie_id

    query = """
        SELECT a.id, c.first_name, c.last_name, b.name 
        FROM psp_cash_app_customuser_user_permissions a
        JOIN auth_permission b ON a.permission_id = b.id 
        JOIN psp_cash_app_customuser c ON a.customuser_id = c.id 
        WHERE c.compagnie_id = %s
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, [int(compagnie_id)])
            permission_info = cursor.fetchall()
    except Exception as e:
        # Handle exceptions here
        # For example: log the exception or return an error response
        return render(request, "error_template.html", {"error_message": str(e)})

    return render(request, "hod_template/edit_access_user_template.html", {"permission_info": permission_info})

def delete_permission(request):
    pass

def supprimer_permissionok(request, permission_id):
    if request.method == 'POST':
        try:
            # Récupérer l'instance de permission à supprimer
            permission_instance = get_object_or_404(CustomUserPermission, id=permission_id)
            
            # Supprimer l'instance de permission
            permission_instance.delete()

            messages.success(request, "Permission successfully removed")
            return HttpResponseRedirect(reverse("GUtilisateur")) 
        except Exception as e:
            messages.error(request, str(e))
            return HttpResponseRedirect(reverse("GUtilisateur"))

def supprimer_permissionbon(request, permission_id):
    if request.method == 'POST':
        try:
            # Récupérer l'instance de permission à supprimer
            permission_instance = get_object_or_404(CustomUserPermission, id=permission_id)
            
            # Supprimer l'instance de permission
            permission_instance.delete()

            messages.success(request, "Permission successfully removed")
            return HttpResponseRedirect(reverse("GUtilisateur")) 
        except Exception as e:
            
            messages.error(request, f"Failed to remove permission: {str(e)}")
            return HttpResponseRedirect(reverse("GUtilisateur"))

def supprimer_permissionnnnn(request, permission_id):
    if request.method == 'POST':
        try:
            # Récupérer l'instance de permission à supprimer
            permission_instance = get_object_or_404(CustomUserPermission, id=permission_id)
            
            # Supprimer l'instance de permission
            permission_instance.delete()

            messages.success(request, "Permission successfully removed")
            return redirect("GUtilisateur") 
        except Exception as e:
            messages.error(request, f"Failed to remove permission: {str(e)}")
            return redirect("GUtilisateur")
      
def supprimer_permissionoo(request, permission_id):
    if request.method == 'POST':
        try:
            # Récupérer l'instance de permission à supprimer
            permission_instance = get_object_or_404(CustomUserPermission, id=permission_id)
            
            # Supprimer l'instance de permission
            permission_instance.delete()

            return JsonResponse({'success': True, 'message': 'Permission successfully removed'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    elif request.method == 'GET':
        return HttpResponseNotAllowed(['POST'])  # Refuser les requêtes GET
    else:
        return HttpResponseNotAllowed([])
    
def supprimer_permission(request, permission_id, customer_id):
    if request.method == 'POST':
        try:
            # Récupérer l'instance de permission à supprimer
            permission_instance = get_object_or_404(CustomUserPermission, permission_id=permission_id, customuser_id=customer_id)
            
            # Supprimer l'instance de permission
            permission_instance.delete()

            messages.success(request, "Permission successfully removed")
            return redirect("GUtilisateur") 
        except Exception as e:
            messages.error(request, f"Failed to remove permission: {str(e)}")
            return redirect("GUtilisateur")