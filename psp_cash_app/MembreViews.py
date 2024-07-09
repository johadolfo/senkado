from django.shortcuts import render

from django.http import HttpResponseRedirect, HttpResponse,HttpResponseRedirect, HttpResponse, HttpResponseServerError
import traceback
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from psp_cash_app.models import CustomUser, Membre, tbarticle, tbconfiguration, tbcotisation, tbcredit, tbdepartement, tbpaiement, tbreceipt, tbreceiptarticle,tbremboursement,FeedBackMembre,LeaveReportMembre,CustomUser, tbdepense, Comment, tbcompagnie, tbtypecotisation
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.core.paginator import Paginator
from django.db.models import Sum, Count,  F
from django.db import connection
import csv

from django.db.models import F

import datetime 

from django.shortcuts import redirect
from django.db.models.functions import Coalesce
from datetime import datetime, timedelta, date
from calendar import monthrange
from django.http import JsonResponse

from django.db.models import F, ExpressionWrapper
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, FloatField
from django.db.models import F, ExpressionWrapper, FloatField, Subquery, OuterRef
from django.shortcuts import render, get_object_or_404

from django.utils import timezone
import sqlite3
from django.db.models import Q
from django.core.paginator import Paginator
from django.db.models import Sum, Count,  F
from django.db import connection
import csv
from django.db.models import F
import datetime 
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.db.models.functions import Coalesce
from datetime import datetime, timedelta, date
from calendar import monthrange
from django.http import JsonResponse

from django.db.models import F, ExpressionWrapper
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

from django.db.models import F, ExpressionWrapper
from django.db.models import Sum, FloatField
from django.db.models import F, ExpressionWrapper, FloatField, Subquery, OuterRef
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
import sqlite3
import json
from django.db.models import Sum,  F
from django.db.models import Sum,  F, FloatField
from django.db.models import  Q
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def membre_home(request):
    has_permission = request.user.has_perm('psp_cash_app.add_depense')
    current_user = request.user

    # modification gestion commande
    #modification psp cash
    receipt = tbreceipt.objects.filter(user_receipt=request.user.username, compagnie=current_user.compagnie, statut='CLOSED')
    
    montant_total_receipt = receipt.aggregate(Sum('total_price'))['total_price__sum']

    receipt1 = tbreceipt.objects.filter(user_receipt=request.user.username, compagnie=current_user.compagnie, statut='OPENNED')
    
    montant_total_openreceipt = receipt1.aggregate(Sum('total_price'))['total_price__sum']

    nbre_receipt_open = tbreceipt.objects.filter(user_receipt=request.user.username, compagnie=current_user.compagnie, statut='OPENNED').count()
   
    nbre_receipt = tbreceipt.objects.filter(user_receipt=request.user.username, compagnie=current_user.compagnie).count()

    paiements = tbpaiement.objects.filter(user_paie=request.user.username)
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

    result = tbreceiptarticle.objects.filter(user_added_byreceipt=request.user.username).values('article__description').annotate(quantity=Sum('quantite')).order_by()  # Pour éviter le group_by automatique

    stock_article = tbarticle.objects.filter(compagnie=current_user.compagnie)

    ####################### fin ##########################################

    #compagnie_id = current_user.compagnie
    membre_count=Membre.objects.filter(membre_actif='True', admin__compagnie=current_user.compagnie).count()
    membre_obj=Membre.objects.get(admin_id=request.user.id)

    valeur2 = tbremboursement.objects.filter(faites_par__admin__compagnie=current_user.compagnie).values('date_remb').order_by('date_remb').annotate(sum=Sum('interet_remb'))
 
    credit_info = tbcredit.objects.filter(credit_status__icontains="En cour", code_membre__admin__compagnie=current_user.compagnie)
    montant_credit = sum(credit_info.values_list('montant_credit', flat=True))
    #remb_info = tbremboursement.objects.all()
    remb_info = tbremboursement.objects.filter(faites_par__admin__compagnie=current_user.compagnie,codecredit_id__credit_status__icontains="En cour").values('codecredit_id').order_by('codecredit_id').annotate(capital_remb=Sum('capital_remb'))
    montant_rembourse = format(sum(remb_info.values_list('capital_remb', flat=True)),'.2f')
    
 
    montant_rembourse = format(sum(remb_info.values_list('capital_remb', flat=True)),'.2f')

     #modificatio apporter
    creditsmt = tbcredit.objects.filter(code_membre__admin_id__compagnie_id=current_user.compagnie)
    
    montant_total_credit = creditsmt.aggregate(Sum('montant_credit'))['montant_credit__sum']
    
    creditsit = creditsmt.annotate(
        interet_montant=F('montant_credit') * F('interet_credit') * F('nbre_de_mois')
    )
    
    interet_total = creditsit.aggregate(Sum('interet_montant'))['interet_montant__sum']
    
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

    return render(request, "membre_template/membre_home_template.html",{"receipt1":receipt1,"stock_article":stock_article,"result":result,"total_cash":total_cash, "total_us_cash":total_us_cash, "total_dollarcard":total_dollarcard, "total_segracrte":total_sogecarte, "total_unicarte":total_unicarte, "total_zelle":total_zelle, "total_cashapp":total_cashapp, "total_complementary":total_complementary, "total_check":total_check,"nbre_receipt_open":nbre_receipt_open, "montant_total_openreceipt":montant_total_openreceipt,"nbre_receipt":nbre_receipt, "montant_total_receipt":montant_total_receipt, "credit_info":credit_info,"remb_info":remb_info, "montant_credit":montant_credit,"valeur2":valeur2, "montant_rembourse":montant_rembourse, "interet_anticipe":interet_anticipe, "Total_interet_restant":Total_interet_restant, "montant_total_restant":montant_total_restant, "montant_total_credit":montant_total_credit, "interet_total":interet_total, "montant_total_credit_encour":montant_total_credit_encour, "interet_total_encour":interet_total_encour, "remboursements_info":remboursements_info, "membre_count":membre_count, "penalite_total":penalite_total, "membre_obj": membre_obj })

def get_articlem(request):
    if request.method == 'GET' and 'receipt_id' in request.GET:
        receipt_id = request.GET.get('receipt_id')
        articles = tbreceiptarticle.objects.filter(receipt_id=receipt_id).values(
            'article_id', 'article__description', 'quantite', 'prix', 'cout'
        )
        return JsonResponse(list(articles), safe=False)
    else:
        return JsonResponse({'error': 'Invalid request'})

def manage_receiptm(request):
    current_user = request.user
    membre_obj=Membre.objects.get(admin=request.user.id, admin__compagnie=current_user.compagnie)
    receipt_info = tbreceipt.objects.filter(user_receipt=request.user.username, compagnie_id=current_user.compagnie).order_by('num_receipt')

    if 'q' in request.GET:
        q = request.GET['q']
        
        all_receipt_list = tbreceipt.objects.filter(user_receipt=request.user.username, compagnie_id=current_user.compagnie).order_by('num_receipt')
    else:
        all_receipt_list = tbreceipt.objects.filter(user_receipt=request.user.username, compagnie_id=current_user.compagnie).order_by('num_receipt')
    paginator = Paginator(all_receipt_list,250,orphans=5)
    page = request.GET.get('page')
    receipt_info = paginator.get_page(page)
    return render(request, "membre_template/manage_receiptm_template.html", { "membre_obj":membre_obj,"receipt_info": receipt_info })

def add_receiptemp(request):
    current_user = request.user
    compagnie_id = current_user.compagnie
    membre_obj=Membre.objects.get(admin=request.user.id,admin__compagnie=current_user.compagnie)
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
        'configuration_info': configuration_info,
        'membre_obj':membre_obj
    }
    #print(opentap)
    return render(request, "membre_template/add_receiptm_template.html", context)

def payer_panieremp(request):
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
                        user_receipt =request.user.username,
                        date_close=date_now,
                        close_by=request.user.username
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
                            user_paie=request.user.username
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
                            user_paie=request.user.username
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
                            user_added_byreceipt=request.user.username,
                            date_added=date_now
                        )
                    return redirect('add_receiptemp')
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
            supprimer_receiptholdemp(request, receipt_id)
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
                        user_receipt =request.user.username,
                        date_close=date_now,
                        close_by=request.user.username
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
                            user_added_byreceipt=request.user.username,
                            date_added=date_now
                        )
                    return redirect('add_receiptemp')
            except Exception as e:
                # Capturer l'exception et afficher un message d'erreur (ou journaliser l'erreur)
                print("Une erreur s'est produite lors du traitement du panier :", str(e))
                return HttpResponseServerError("Une erreur s'est produite lors du traitement du panier. Veuillez contacter l'administrateur.")
                
        return redirect('add_receiptemp')

def supprimer_receiptholdemp(request, receipt_id):
    try:
        receipt_del = tbreceipt.objects.get(num_receipt=receipt_id)
        receipt_del.delete()
    except ObjectDoesNotExist:
        # Gérer le cas où le tbreceipt avec num_receipt spécifié n'existe pas
        # Vous pouvez journaliser un avertissement ou effectuer toute autre action nécessaire
        print(f"tbreceipt avec num_receipt {receipt_id} n'existe pas.")

def hold_receiptemp(request):
    
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
                        user_receipt =request.user.username,
                        date_close=date_now,
                        close_by=request.user.username
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
                            user_added_byreceipt=request.user.username,
                            date_added=date_now
                        )
                    return redirect('add_receiptemp')
            except Exception as e:
                # Capturer l'exception et afficher un message d'erreur (ou journaliser l'erreur)
                print("Une erreur s'est produite lors du traitement du panier :", str(e))
                return HttpResponseServerError("Une erreur s'est produite lors du traitement du panier. Veuillez contacter l'administrateur.")
                
        #la table est ouverte
        else:
            receipt_id = request.POST.get('receipt_id_holdtab')
            
            supprimer_receiptholdemp(request, receipt_id)
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
                        user_receipt =request.user.username,
                        date_close=date_now,
                        close_by=request.user.username
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
                            user_added_byreceipt=request.user.username,
                            date_added=date_now
                        )
                    return redirect('add_receiptemp')
            except Exception as e:
                # Capturer l'exception et afficher un message d'erreur (ou journaliser l'erreur)
                print("Une erreur s'est produite lors du traitement du panier :", str(e))
                return HttpResponseServerError("Une erreur s'est produite lors du traitement du panier. Veuillez contacter l'administrateur.")       
        return redirect('add_receiptemp')

def tab_openemp(request):
    current_user = request.user
    compagnie_id = current_user.compagnie
    membre_obj=Membre.objects.get(admin=request.user.id,admin__compagnie=current_user.compagnie)
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
        'configuration_info': configuration_info,
        'membre_obj':membre_obj
    }
    #print(opentap)
    return render(request, "membre_template/liste_tabopen.html", context)





















def manage_membres(request):

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
    membre_obj=Membre.objects.get(admin_id=request.user.id)
    return render(request, "membre_template/manage_membres_template.html", { "membres": membres, "membre_obj" :membre_obj})

def liste_credits_encour(request):
    current_user = request.user
    compagnie_id = current_user.compagnie_id

    query = """
     SELECT 
    psp_cash_app_tbcredit.numero AS codecredit_id,
    COUNT(psp_cash_app_tbremboursement.id) AS quantite_remboursement,
    (psp_cash_app_tbcredit.nbre_de_mois - COUNT(psp_cash_app_tbremboursement.id)) AS Qtee_restant,
    IFNULL(SUM(psp_cash_app_tbremboursement.capital_remb), 0) + IFNULL(SUM(psp_cash_app_tbremboursement.interet_remb), 0) AS montant_total_rembourse,
    ((IFNULL(SUM(psp_cash_app_tbremboursement.capital_remb), 0) + (IFNULL(SUM(psp_cash_app_tbremboursement.interet_remb), 0)) * nbre_de_mois) - IFNULL(SUM(psp_cash_app_tbremboursement.capital_remb), 0) + IFNULL(SUM(psp_cash_app_tbremboursement.interet_remb), 0)) AS montant_total_Restant,
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
        AND psp_cash_app_CustomUser.compagnie_id = %s
        
    GROUP BY
        psp_cash_app_tbcredit.numero, psp_cash_app_tbcredit.nbre_de_mois, psp_cash_app_tbcredit.interet_credit, psp_cash_app_tbcredit.montant_credit,
        psp_cash_app_tbcredit.date_debut, psp_cash_app_tbcredit.date_fin,
        psp_cash_app_Membre.profile_pic, psp_cash_app_Membre.prenomp, psp_cash_app_Membre.nomp
    ORDER BY
        codecredit_id ASC;
        """

    with connection.cursor() as cursor:
        cursor.execute(query, [int(compagnie_id)])
        remboursement_info = cursor.fetchall()

    if 'q' in request.GET:
        q = request.GET['q']
        queryparametre = """
            SELECT 
    psp_cash_app_tbcredit.numero AS codecredit_id,
    COUNT(psp_cash_app_tbremboursement.id) AS quantite_remboursement,
    (psp_cash_app_tbcredit.nbre_de_mois - COUNT(psp_cash_app_tbremboursement.id)) AS Qtee_restant,
    IFNULL(SUM(psp_cash_app_tbremboursement.capital_remb), 0) + IFNULL(SUM(psp_cash_app_tbremboursement.interet_remb), 0) AS montant_total_rembourse,
    ((IFNULL(SUM(psp_cash_app_tbremboursement.capital_remb), 0) + (IFNULL(SUM(psp_cash_app_tbremboursement.interet_remb), 0)) * nbre_de_mois) - IFNULL(SUM(psp_cash_app_tbremboursement.capital_remb), 0) + IFNULL(SUM(psp_cash_app_tbremboursement.interet_remb), 0)) AS montant_total_Restant,
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
        AND psp_cash_app_CustomUser.compagnie_id = %s
        
    GROUP BY
        psp_cash_app_tbcredit.numero, psp_cash_app_tbcredit.nbre_de_mois, psp_cash_app_tbcredit.interet_credit, psp_cash_app_tbcredit.montant_credit,
        psp_cash_app_tbcredit.date_debut, psp_cash_app_tbcredit.date_fin,
        psp_cash_app_Membre.profile_pic, psp_cash_app_Membre.prenomp, psp_cash_app_Membre.nomp
    ORDER BY
        codecredit_id ASC;
        """

        with connection.cursor() as cursor:
            cursor.execute(queryparametre, [int(compagnie_id), q])
            all_remboursement_info = cursor.fetchall()

        #all_remboursement_info = tbremboursement.objects.filter(  Q(codecredit_id=q) ).values('codecredit_id').annotate(total=Count('codecredit_id'),faites_par__admin__compagnie = compagnie_id, sum=Sum('capital_remb')).order_by('-date_remb')
    else:
        #all_remboursement_info = tbremboursement.objects.filter(faites_par__admin__compagnie = compagnie_id).select_related("tbcredit").values('codecredit_id').annotate(total=Count('codecredit_id'), sum=Sum('capital_remb')).order_by('-date_remb')
        all_remboursement_info = remboursement_info
    paginator = Paginator(all_remboursement_info,15)
    page = request.GET.get('page')
    credits = paginator.get_page(page)
    qte_credit =tbcredit.objects.filter(credit_status='En cour',code_membre__admin__compagnie = compagnie_id).count()
    today = timezone.now()
    montant_total_interet = tbcredit.objects.filter(credit_status='En cour',code_membre__admin__compagnie_id=1,).filter(Q(date_debut__lte=today, date_fin__gte=today) |Q(date_debut__gte=today)).aggregate(total_interet=Sum(F('interet_credit') * F('montant_credit')))['total_interet']
    membre_obj=Membre.objects.get(admin_id=request.user.id)
    return render(request, "membre_template/liste_creditencours_template.html", { "credits":credits, "qte_credit":qte_credit, "montant_total_interet":montant_total_interet, "membre_obj":membre_obj  })

def liste_credits_encours(request):
    current_user = request.user
    compagnie_id = current_user.compagnie_id
    credits = tbcredit.objects.filter(credit_status='En cour', code_membre__admin__compagnie = compagnie_id).order_by('-date_credit')

    if 'q' in request.GET:
        q = request.GET['q']
        all_credit_list = tbcredit.objects.filter(  Q(numero__icontains=q)  | Q(date_credit__icontains=q) ).order_by('-date_credit')
    else:
        all_credit_list = tbcredit.objects.filter(credit_status='En cour', code_membre__admin__compagnie = compagnie_id).order_by('-date_credit')
    paginator = Paginator(all_credit_list,25)
    page = request.GET.get('page')
    credits = paginator.get_page(page)
    qte_credit =tbcredit.objects.filter(credit_status='En cour',code_membre__admin__compagnie = compagnie_id).count()
    
    return render(request, "membre_template/liste_creditencours_template.html", { "credits":credits, "qte_credit":qte_credit  })

def interet_ajoute(request):
    current_user = request.user
    compagnie_id = current_user.compagnie
    qte_membre=Membre.objects.filter(membre_actif='True',admin__compagnie=current_user.compagnie).count()
    membre_obj=Membre.objects.get(admin_id=request.user.id)
    valeur2 = tbremboursement.objects.filter(faites_par__admin__compagnie=current_user.compagnie).values('date_remb').order_by('date_remb').annotate(sum=Sum('interet_remb'), sum2=Count('interet_remb')).order_by('-date_remb')
    return render(request, "membre_template/interets_ajoutes.html", { "valeur2":valeur2, "qte_membre":qte_membre, "membre_obj":membre_obj })

def membre_cotisation(request):
    current_user = request.user
    membre_obj=Membre.objects.get(admin=request.user.id ,admin__compagnie=current_user.compagnie)
    caisseverte = tbtypecotisation.objects.get(reference='cr', cotisation_compagnie=current_user.compagnie)
    caisserouge = tbtypecotisation.objects.get(reference='cv', cotisation_compagnie=current_user.compagnie)
    caissebleue = tbtypecotisation.objects.get(reference='cb', cotisation_compagnie=current_user.compagnie)
    
    if caisseverte:
        _credit  =tbcotisation.objects.filter(code_membre_id=membre_obj, typecotisation=caisseverte.nom_cotisation, code_membre__admin__compagnie=current_user.compagnie)
        qtite_cotcredit = (_credit.values_list('montant', flat=True)).count()
    else:
        qtite_cotcredit =0
    
    if caissebleue:
        _ijans  =tbcotisation.objects.filter(code_membre_id=membre_obj,typecotisation=caissebleue.nom_cotisation, code_membre__admin__compagnie=current_user.compagnie)
        qtite_cotijans = (_ijans.values_list('montant', flat=True)).count()
    else:
        qtite_cotijans =0
    
    if caisserouge:
        _fonctionnement  =tbcotisation.objects.filter(code_membre_id=membre_obj,typecotisation=caisserouge.nom_cotisation, code_membre__admin__compagnie=current_user.compagnie)
        qtite_cotfonk = (_fonctionnement.values_list('montant', flat=True)).count()
    else:
        qtite_cotfonk =0
 
    cotisations = tbcotisation.objects.filter(code_membre_id=membre_obj, code_membre__admin__compagnie=current_user.compagnie).order_by('-date_fait')

    ###########mise a jour 10-03-2024###########
    
    #add_cotisation_permission = False

    ###### add permission cotisation
    permission_depense = 61
    if CustomUser.objects.filter(id=current_user.id, user_permissions__id=int(permission_depense)).exists(): 
        add_depense_permission = True
    else:
        add_depense_permission = False

    ###### add permission cotisation
    permission_membre = 25
    if CustomUser.objects.filter(id=current_user.id, user_permissions__id=int(permission_membre)).exists(): 
        add_membre_permission = True
    else:
        add_membre_permission = False

    ###### add permission cotisation
    permission_id = 41
    if CustomUser.objects.filter(id=current_user.id, user_permissions__id=int(permission_id)).exists(): 
        add_cotisation_permission = True
    else:
        add_cotisation_permission = False
    ####fini mise a jour #########
    return render(request, "membre_template/membre_cotisation.html", {"add_membre_permission":add_membre_permission, "add_depense_permission": add_depense_permission, "add_cotisation_permission":add_cotisation_permission, "membre_obj":membre_obj,  "cotisations":cotisations, "qtite_cotcredit":qtite_cotcredit, "qtite_cotijans":qtite_cotijans, "qtite_cotfonk":qtite_cotfonk })

def membre_credit(request):
    current_user = request.user
    membre_obj=Membre.objects.get(admin=request.user.id,admin__compagnie=current_user.compagnie)
    credits = tbcredit.objects.filter(code_membre_id=membre_obj, code_membre__admin__compagnie=current_user.compagnie).order_by('-date_credit')
    
    #add_cotisation_permission = False
    permission_id = 33
    if CustomUser.objects.filter(id=current_user.id, user_permissions__id=int(permission_id)).exists(): 
        add_credit_permission = True
    else:
        add_credit_permission = False
    return render(request, "membre_template/membre_credit.html", {"membre_obj":membre_obj, "credits":credits, "add_credit_permission":add_credit_permission })

def add_creditM(request):
    current_user = request.user
    compagnie_id = current_user.compagnie_id
    credits = tbcredit.objects.filter(code_membre__admin__compagnie=current_user.compagnie_id)
    membre_info = Membre.objects.filter(admin__compagnie=current_user.compagnie_id, membre_actif='True')
    membres = CustomUser.objects.filter(user_type=2, compagnie=current_user.compagnie_id)
    compagnie_idd = str(compagnie_id)
    interet_compagnie = tbcompagnie.objects.get(id=compagnie_idd)
    return render(request, "membre_template/add_creditM_template.html", {"membres":membres, "credits":credits, "membre_info":membre_info, "interet_compagnie":interet_compagnie})

def add_creditM_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    
    credit_exist = tbcredit.objects.filter(numero=request.POST.get("numero_credit")).first()
    code_membres = request.POST.get("membre")
    code_membre = Membre.objects.get(id=code_membres)
    
    numero_credit = request.POST.get("numero_credit")
    date_credit = request.POST.get("date_credit")
    date_debut = request.POST.get("date_debut")
    date_fin = request.POST.get("date_fin")
    nbre_de_mois = request.POST.get("nbre_mois")
    montant_recu = request.POST.get("montant_credit")
    interet_recu = request.POST.get("interet_credit")
    commentaire = request.POST.get("commentaire")
    valider_par = request.POST.get("valider_par")
    
    try:
        if credit_exist:
            messages.error(request, "Ce numero de Credit Existe Deja!")
            return HttpResponseRedirect(reverse("add_creditM")) 
        else:
            credit = tbcredit.objects.create(
                numero=numero_credit,
                date_credit=date_credit,
                nbre_de_mois=nbre_de_mois,
                date_debut=date_debut,
                date_fin=date_fin,
                montant_credit=float(montant_recu),
                interet_credit=float(interet_recu),
                code_membre=code_membre,
                commentaire=commentaire,
                valider_par=valider_par
            )
            messages.success(request, "Successfully Added credit")
            return HttpResponseRedirect(reverse("add_creditM"))
    except Exception as e:
        messages.error(request, str(e))
        return HttpResponseRedirect(reverse("add_creditM"))
    
def membre_remboursement(request):
    current_user = request.user
    membre_obj=Membre.objects.get(admin=request.user.id, admin__compagnie=current_user.compagnie)
    rembous = tbremboursement.objects.filter(faites_par_id=membre_obj, faites_par__admin__compagnie=current_user.compagnie).order_by('-date_remb')
    ####add_remboursement_permission = False
    permission_id = 37
    if CustomUser.objects.filter(id=current_user.id, user_permissions__id=int(permission_id)).exists(): 
        add_remboursement_permission = True
    else:
        add_remboursement_permission = False
    return render(request, "membre_template/membre_remboursement.html", { "add_remboursement_permission":add_remboursement_permission,"membre_obj":membre_obj, "rembous":rembous })

def add_membreM(request):
    #form = AddMembreForm()
    return render(request, "membre_template/add_membreM_templates.html")

def add_membreM_save(request):
    if request.method !="POST":
        return HttpResponse("Method Not Allowed")
    else:
        current_user = request.user
        compagnie_id = current_user.compagnie
        prenomp = request.POST.get("prenomp")
        nomp = request.POST.get("nomp")
        codep = request.POST.get("codep")
        email = request.POST.get("emailp")
        password = request.POST.get("passwordp")
        adressep = request.POST.get("adressep")
        sexep = request.POST.get("sexep")

        #datenaissancep = form.cleaned_data["datenaissancep"]
        villep = request.POST.get("villep")
        communep = request.POST.get("communep")
        departementp = request.POST.get("departementp")
        paysp = request.POST.get("paysp")
        nifp = request.POST.get("nifp")
        
        telephone1p = request.POST.get("telephone1p")
        telephone2p = request.POST.get("telephone2p")
        activiteprofessionp = request.POST.get("activiteprofessionp")
        referencep = request.POST.get("referencep")
        lieunaissancep = request.POST.get("lieunaissancep")
        #compagnie = form.cleaned_data["compagnie"]
        
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
            #user.membre.datenaissancep = datenaissancep
            user.membre.lieunaissancep=lieunaissancep
            user.membre.adressep=adressep
            user.membre.villep=villep
            user.membre.communep = communep
            user.membre.departementp=departementp
            user.membre.paysp = paysp
            user.membre.nifp=nifp
            user.membre.telephone1p = telephone1p
            user.membre.telephone2p=telephone2p
            user.membre.activiteprofessionp = activiteprofessionp
            user.membre.referencep = referencep
            user.membre.profile_pic=profile_pic_url
            #user.membre.compagnie = compagnie=compagnie_id
            user.membre.save()
           
            messages.success(request,"Successfully Added membre")
            return HttpResponseRedirect(reverse("add_membreM")) 
        except Exception as e:
            messages.error(request,traceback.format_exc())
            return HttpResponseRedirect(reverse("add_membreM"))
        
def add_remboursementM(request):
    current_user = request.user
    compagnie_id = current_user.compagnie
    remboursements = tbremboursement.objects.all()
    credits=tbcredit.objects.all()
    membre_info = Membre.objects.filter(admin__compagnie=current_user.compagnie, membre_actif='True')
    membres = CustomUser.objects.filter(user_type=2,compagnie=current_user.compagnie)
    return render(request, "membre_template/add_remboursementM_template.html", {"membres":membres, "remboursements":remboursements, "membre_info":membre_info, "credits":credits})

def add_remboursementM_save(request):
 
    if request.method !="POST":
        return HttpResponse("Method Not Allowed")
    else:
        code_membres = request.POST.get("membre")
        code_membre=Membre.objects.get(id=code_membres)
        date_remboursement = request.POST.get("date_remboursement")
        numero_credit = request.POST.get("numero_credit")
        code_credit=tbcredit.objects.get(numero=numero_credit)
        montant_recu = request.POST.get("montant_a_rembourser")
        capital_recu = request.POST.get("capital_a_rembourser")
        interet_recu = request.POST.get("interet_a_rembourser")
        balance_recu = request.POST.get("balance_remb")
        penalite_recu = request.POST.get("penalite_remb")
        commentaire = request.POST.get("commentaire")
        valider_par = request.POST.get("recu_par")

        try:
            remboursement=tbremboursement(date_remb=date_remboursement,  montant_a_remb=float(montant_recu),capital_remb=float(capital_recu), interet_remb=float(interet_recu), balance=float(balance_recu), penalite=float(penalite_recu), commentaire=commentaire, recu_par=valider_par, codecredit=code_credit, faites_par=code_membre)
            remboursement.save()
            # editer status_credit, si la qtite de remboursement arrive a sa fin
            nbre_remb = tbremboursement.objects.filter(codecredit_id = code_credit).count()
            nbreM = tbcredit.objects.get(numero = request.POST.get("numero_credit"))
            if (nbre_remb == nbreM.nbre_de_mois ):
                credit=tbcredit.objects.get(numero=request.POST.get("numero_credit"))
                credit.credit_status = 'Termine'
                credit.save()
        
            messages.success(request,"Successfully Added remboursement")
            return HttpResponseRedirect(reverse("add_remboursement")) 
        except Exception as e:
            messages.error(request,traceback.format_exc())
            return HttpResponseRedirect(reverse("add_remboursement"))

def add_depenseM(request):
    depenses = tbdepense.objects.all()
    return render(request, "membre_template/add_depenseM_template.html", {"depenses":depenses})

def add_depenseM_save(request):
    current_user = request.user
    compagnie_id = current_user.compagnie
 
    if request.method !="POST":
        return HttpResponse("Method Not Allowed")
    else:
        date_depense = request.POST.get("date_depense")
        description = request.POST.get("description")
        depense_unit = request.POST.get("depense_unit")
        quantite_dep = request.POST.get("quantite_dep")

        try:
            depense=tbdepense(date_depense=date_depense,  description=description, depense_unit=float(depense_unit), quantite_dep=float(quantite_dep), compagnie_id=compagnie_id)
            depense.save()
        
            messages.success(request,"Successfully Added Depense")
            return HttpResponseRedirect(reverse("add_depenseM")) 
        except Exception as e:
            messages.error(request,traceback.format_exc())
            return HttpResponseRedirect(reverse("add_depenseM"))
        
def Lesinterets_membre_ajoutes(request):
    current_user = request.user
    #compagnie_id = current_user.compagnie
    qte_membre=Membre.objects.filter(membre_actif=1, admin__compagnie=current_user.compagnie).count()
    valeur2 = tbremboursement.objects.filter( faites_par__admin__compagnie=current_user.compagnie).values('date_remb').order_by('date_remb').annotate(sum=Sum('interet_remb')/qte_membre, sum2=Count('interet_remb')).order_by('-date_remb')
 
    if 'q' in request.GET:
        q = request.GET['q']
        qte_membre=Membre.objects.filter(membre_actif=1, admin__compagnie=current_user.compagnie).count()
        valeur2 = tbremboursement.objects.filter(  Q(date_remb__year=q) | Q(codecredit=q), Q(faites_par__admin__compagnie=current_user.compagnie) ).values('date_remb').order_by('-date_remb').annotate(sum=Sum('interet_remb')/qte_membre, sum2=Count('interet_remb'))
    else:
        qte_membre=Membre.objects.filter(membre_actif=1, admin__compagnie=current_user.compagnie).count()
        valeur2 = tbremboursement.objects.filter( faites_par__admin__compagnie=current_user.compagnie).values('date_remb').order_by('-date_remb').annotate(sum=Sum('interet_remb')/qte_membre, sum2=Count('interet_remb'))
       
    paginator = Paginator(valeur2,15)
    page = request.GET.get('page')
    rembs = paginator.get_page(page)
    membre_obj=Membre.objects.get(admin=request.user.id, admin__compagnie=current_user.compagnie)
    
    return render(request, "membre_template/Lesinterets_membre_ajoutes.html", {"membre_obj":membre_obj, "valeur2":valeur2, "qte_membre":qte_membre })

def statistique_remboursements(request):
    current_user = request.user
    compagnie_id = current_user.compagnie_id

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
        cursor.execute(query, [int(compagnie_id)])
        remboursement_info = cursor.fetchall()

    if 'q' in request.GET:
        q = request.GET['q']
        queryparametre = """
            SELECT 
        codecredit_id,
        COUNT(psp_cash_app_tbremboursement.id) AS quantite_remboursement,
        (psp_cash_app_tbcredit.nbre_de_mois- COUNT(psp_cash_app_tbremboursement.id)) as Qtee_restant,
        SUM(capital_remb) + SUM(interet_remb) AS montant_total_rembourse,
        ((montant_a_remb*nbre_de_mois) - (SUM(capital_remb) + SUM(interet_remb))) AS montant_total_Restant,
        SUM(interet_remb) AS total_interet,
        (interet_remb*nbre_de_mois) - SUM(interet_remb) AS total_interet_restant,
        SUM(penalite) AS total_penalite
        FROM
            psp_cash_app_tbremboursement,psp_cash_app_membre ,psp_cash_app_customuser, psp_cash_app_tbcredit
        WHERE
            psp_cash_app_tbremboursement.faites_par_id = psp_cash_app_membre.id and psp_cash_app_membre.admin_id = psp_cash_app_customuser.id and psp_cash_app_tbremboursement.codecredit_id = psp_cash_app_tbcredit.numero and psp_cash_app_customuser.compagnie_id = %s and psp_cash_app_tbcredit.numero=%s
        GROUP BY
            codecredit_id
        ORDER BY
            codecredit_id ASC
        """

        with connection.cursor() as cursor:
            cursor.execute(queryparametre, [int(compagnie_id), q])
            all_remboursement_info = cursor.fetchall()

        #all_remboursement_info = tbremboursement.objects.filter(  Q(codecredit_id=q) ).values('codecredit_id').annotate(total=Count('codecredit_id'),faites_par__admin__compagnie = compagnie_id, sum=Sum('capital_remb')).order_by('-date_remb')
    else:
        #all_remboursement_info = tbremboursement.objects.filter(faites_par__admin__compagnie = compagnie_id).select_related("tbcredit").values('codecredit_id').annotate(total=Count('codecredit_id'), sum=Sum('capital_remb')).order_by('-date_remb')
        all_remboursement_info = remboursement_info
    paginator = Paginator(all_remboursement_info,15)
    page = request.GET.get('page')
    remboursement_info = paginator.get_page(page)
    membre_obj=Membre.objects.get(admin_id=request.user.id)
    return render(request, "membre_template/statistique_remboursements_template.html", { "remboursement_info":remboursement_info, "membre_obj":membre_obj })

def statistique_credits(request):
    current_user = request.user
    compagnie_id = current_user.compagnie_id
    
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
    
    
    #--------------modification------------------------
    db_path = "db.sqlite3"
    query = """
        SELECT
        SUM(montant_credit) AS sum_montant_credit,
        SUM((montant_credit * interet_credit * nbre_de_mois) + montant_credit) AS montant_rembourser,
        SUM(((montant_credit * interet_credit * nbre_de_mois) + montant_credit) - montant_credit) AS interet_total_credit
        FROM
            psp_cash_app_tbcredit 
        LEFT JOIN
        
            psp_cash_app_Membre  ON psp_cash_app_tbcredit.code_membre_id = psp_cash_app_Membre.id
        JOIN
            psp_cash_app_CustomUser  ON psp_cash_app_Membre.admin_id = psp_cash_app_CustomUser.id
        WHERE
            psp_cash_app_CustomUser.compagnie_id = ?
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    current_users = request.user
   
    # Exécutez la requête
    cursor.execute(query, (current_users.compagnie_id,))

    # Parcourez les résultats pour calculer la somme du montant_total_Restant
    montant_total_credit = 0
    montant_total_remboursement = 0
    montant_total_interet = 0
    for row in cursor.fetchall():
        montant_total_credit = row[0]
        montant_total_remboursement = row[1]
        montant_total_interet = row[2]

    #---------------fin-modification---------------------

    
    query = """
        SELECT SUM(a.montant_credit * a.interet_credit) AS interet_anticipe
        FROM psp_cash_app_tbcredit a
        INNER JOIN psp_cash_app_tbremboursement b ON a.numero = b.codecredit_id
        INNER JOIN psp_cash_app_membre c ON a.code_membre_id = c.id
        INNER JOIN psp_cash_app_customuser d ON c.admin_id = d.id
        WHERE b.interet_remb = 0 AND d.compagnie_id = %s
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [int(compagnie_id)])
        result = cursor.fetchone()
    interet_anticipe = result[0] if result else 0

    if 'q' in request.GET:
        q = request.GET['q']
        subquery = tbremboursement.objects.filter(codecredit_id=OuterRef('numero')).values('codecredit_id')
        all_credit_info = tbcredit.objects.annotate(
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
            numero=q,
            pk__in=Subquery(subquery)
        ).values(
            'numero',
            'montant_credit',
            'date_debut',
            'montant_rembourser',
            'interet_total_credit'
        ).order_by('date_debut')
        #///////////////////////////////////
        query = """
            SELECT SUM(a.montant_credit * a.interet_credit) AS interet_anticipe
            FROM psp_cash_app_tbcredit a
            INNER JOIN psp_cash_app_tbremboursement b ON a.numero = b.codecredit_id
            INNER JOIN psp_cash_app_membre c ON a.code_membre_id = c.id
            INNER JOIN psp_cash_app_customuser d ON c.admin_id = d.id
            WHERE b.interet_remb = 0 AND d.compagnie_id = %s and a.numero=%s
        """

        with connection.cursor() as cursor:
            cursor.execute(query, [int(compagnie_id), q])
            result = cursor.fetchone()
        interet_anticipe = result[0] if result else 0
        #/////////////////////////////////////////////
        result_tot = 0
    else:
        all_credit_info = credit_info
    paginator = Paginator(all_credit_info,15)
    page = request.GET.get('page')
    credit_info = paginator.get_page(page)
    membre_obj=Membre.objects.get(admin_id=request.user.id)
    return render(request, "membre_template/statistique_credit_template.html", {"membre_obj":membre_obj, "montant_total_credit":montant_total_credit, "montant_total_remboursement":montant_total_remboursement, "montant_total_interet":montant_total_interet,  "credit_info":credit_info, "interet_anticipe":interet_anticipe })

def statistique_cotisations(request):
    current_user = request.user
    compagnie_id = current_user.compagnie_id

    caisseverte = tbtypecotisation.objects.get(reference='cv', cotisation_compagnie=current_user.compagnie)
    caisserouge = tbtypecotisation.objects.get(reference='cr', cotisation_compagnie=current_user.compagnie)
    caissebleue = tbtypecotisation.objects.get(reference='cb', cotisation_compagnie=current_user.compagnie)

    query = """
        select a.id, codep,  nomp || ' ' || prenomp AS nom_membre, sum(case when typecotisation = %s then montant else 0 END) as Montantcredit, sum(case when typecotisation = %s then montant END) as MontantFonct, sum(case when typecotisation = %s then montant else 0 END) as MontantUrgence, sum(interet) as MontantInteret,sum(penalite) as penalite, (sum(interet)+ sum(case when typecotisation = %s then montant else 0 END)+sum(case when typecotisation = %s then montant else 0 END)) as Montanttotal, membre_actif  from psp_cash_app_membre a, psp_cash_app_tbcotisation b, psp_cash_app_customuser c where code_membre_id=a.id and a.admin_id=c.id and c.compagnie_id = %s group by code_membre_id 
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [caisseverte.nom_cotisation, caisserouge.nom_cotisation, caissebleue.nom_cotisation, caisseverte.nom_cotisation, caissebleue.nom_cotisation, int(compagnie_id)])
        cotisation_info = cursor.fetchall()

    if 'q' in request.GET:
        q = request.GET['q']
        queryparametre = """
            select a.id, codep,  nomp || ' ' || prenomp AS nom_membre, sum(case when typecotisation = "Fond de Credit" then montant else 0 END) as Montantcredit, sum(case when typecotisation = "Fond de Fonctionnement" then montant END) as MontantFonct, sum(case when typecotisation = "Fond d'Urgence" then montant else 0 END) as MontantUrgence, sum(interet) as MontantInteret,sum(penalite) as penalite, (sum(interet)+ sum(case when typecotisation = "Fond de Credit" then montant else 0 END)+sum(case when typecotisation = "Fond d'Urgence" then montant else 0 END)) as Montanttotal  from psp_cash_app_membre a, psp_cash_app_tbcotisation b, psp_cash_app_customuser c where code_membre_id=a.id and a.admin_id=c.id and c.compagnie_id = %s and a.codep=%s group by code_membre_id 
        """
        with connection.cursor() as cursor:
            cursor.execute(queryparametre, [int(compagnie_id), q])
            all_remboursement_info = cursor.fetchall()

        #all_remboursement_info = tbremboursement.objects.filter(  Q(codecredit_id=q) ).values('codecredit_id').annotate(total=Count('codecredit_id'),faites_par__admin__compagnie = compagnie_id, sum=Sum('capital_remb')).order_by('-date_remb')
    else:
        #all_remboursement_info = tbremboursement.objects.filter(faites_par__admin__compagnie = compagnie_id).select_related("tbcredit").values('codecredit_id').annotate(total=Count('codecredit_id'), sum=Sum('capital_remb')).order_by('-date_remb')
        all_remboursement_info = cotisation_info
    paginator = Paginator(all_remboursement_info,15)
    page = request.GET.get('page')
    cotisation_info = paginator.get_page(page)
    return render(request, "membre_template/statistique_cotisation_template.html", { "cotisation_info":cotisation_info })

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

def membre_apply_leave(request):
    current_user = request.user
    membre_obj=Membre.objects.get(admin=request.user.id, admin__compagnie=current_user.compagnie)
    leave_data=LeaveReportMembre.objects.filter(code_membre=membre_obj)
    return render(request, "membre_template/membre_apply_leave.html", {"membre_obj":membre_obj, "leave_data":leave_data})

def membre_apply_leave_save(request):
    
    if request.method!="POST":
        return HttpResponseRedirect(reverse("membre_apply_leave"))
    else:
        leave_date=request.POST.get("leave_date")
        leave_msg=request.POST.get("leave_msg")

        membre_obj=Membre.objects.get(admin=request.user.id)
        try:
            leave_report=LeaveReportMembre(code_membre=membre_obj, leave_date=leave_date,leave_message=leave_msg,leave_status=0)
            leave_report.save()
            messages.success(request,"Successfully Applied for Leave")
            return HttpResponseRedirect(reverse("membre_apply_leave")) 
        except Exception as e:
            messages.error(request,traceback.format_exc())
            return HttpResponseRedirect(reverse("membre_apply_leave"))

def membre_feedback(request):
    current_user = request.user
    membre_id=Membre.objects.get(admin=request.user.id)
    feedback_data=FeedBackMembre.objects.filter(code_membre=membre_id)
    membre_obj=Membre.objects.get(admin=request.user.id, admin__compagnie=current_user.compagnie)
    return render(request, "membre_template/membre_feedback.html", {"membre_obj":membre_obj, "membre_data":feedback_data})

def membre_feedback_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("membre_feedback_save"))
    else:
        feedback_msg=request.POST.get("feedback_msg")
        membre_obj=Membre.objects.get(admin=request.user.id)
        try:
            feedback=FeedBackMembre(code_membre=membre_obj, feedback=feedback_msg, feedback_reply="")
            feedback.save()
            messages.success(request,"Successfully Sent Feedback")
            return HttpResponseRedirect(reverse("membre_feedback")) 
        except Exception as e:
            messages.error(request,traceback.format_exc())
            return HttpResponseRedirect(reverse("membre_feedback"))

def membre_profile(request):
    current_user = request.user
    user=CustomUser.objects.get(id=request.user.id)
    membre=Membre.objects.get(admin=user)
    membre_obj=Membre.objects.get(admin=request.user.id, admin__compagnie=current_user.compagnie)
    return render(request,"membre_template/membre_profile.html",{"membre_obj":membre_obj, "user":user, "membre":membre})

def membre_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("membre_profile"))
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

        membre=Membre.objects.get(admin=customuser.id)
        membre.save()
        messages.success(request,"Successfully Update Profile")
        return HttpResponseRedirect(reverse("membre_profile"))
    except:
        messages.success(request,"Failed Update Profile")
        return HttpResponseRedirect(reverse("membre_profile"))

def add_mcomments_save(request):
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
            return HttpResponseRedirect(reverse("profile_mview")) 
        except Exception as e:
            traceback.print_exc() 
            return HttpResponseRedirect(reverse("profile_mview"))
        
def profile_mview(request):
    current_user = request.user
    compagnie_id = current_user.compagnie
    # Logic for the profile view
    comments = Comment.objects.filter(author_id=F('author_id__id'), compagnie_id_id=compagnie_id).order_by('-created_at').values('id', 'text', 'created_at', 'author_id__profile_pic', 'author_id__nomp', 'author_id__prenomp')
    membre_obj=Membre.objects.get(admin=request.user.id, admin__compagnie=current_user.compagnie)
    today_date = datetime.now().date()

    for comment in comments:
        created_at_date = comment['created_at'].date()
        difference = today_date - created_at_date
        comment['difference_in_days'] = difference.days

    return render(request, 'membre_template/commentaire.html', {"membre_obj":membre_obj, 'comments': comments})

def user_info(request):
    # Récupérer l'ID de l'utilisateur connecté
    user_id = request.user.id
   
    user_type = request.user.username  
    
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
    
    return render(request, 'membre_template/user_info.html', context)

##################################### Authorisation si possible #########################################

@login_required
def add_more_cotisation_correctionMss(request):
    # Vérifiez si l'utilisateur a la permission d'ajouter une cotisation
    if not request.user.has_perm('add_tbcotisation'):
        # Si l'utilisateur n'a pas la permission, renvoyez un message d'erreur
        return HttpResponseForbidden("Vous n'avez pas la permission d'ajouter une cotisation.")
    
    # Si l'utilisateur a la permission, continuez avec le reste de votre logique
    current_user = request.user
    compagnie_id = current_user.compagnie_id
    type_cotisation = tbtypecotisation.objects.filter(cotisation_compagnie=compagnie_id)
    membre_info = Membre.objects.filter(admin__compagnie=current_user.compagnie, membre_actif='True')
    
    return render(request, "membre_template/add_more_cotisation_correctionM.html", {"membre_info":membre_info, "type_cotisation":type_cotisation})

@login_required
def add_more_cotisation_correctionMff(request):
    # Récupérez l'instance de l'utilisateur connecté
    user_instance = request.user
    user_has_permission
    # Récupérez l'ID de la permission spécifique que vous souhaitez vérifier (ID 41 dans ce cas)
    permission_id = 41

    # Vérifiez si l'utilisateur a cette permission dans la table de liaison psp_cash_app_customuser_user_permissions
    if CustomUser.objects.filter(id=user_instance.id, user_permissions__id=int(permission_id)).exists():
        user_has_permission = True
        current_user = request.user
        compagnie_id = current_user.compagnie_id
        type_cotisation = tbtypecotisation.objects.filter(cotisation_compagnie=compagnie_id)
        membre_info = Membre.objects.filter(admin__compagnie=current_user.compagnie, membre_actif='True')
        return render(request, "membre_template/add_more_cotisation_correctionM.html", {"membre_info":membre_info, "type_cotisation":type_cotisation})
    else:
        user_has_permission = False
        #return HttpResponseForbidden("Vous n'avez pas la permission d'ajouter une cotisation.")
    
@login_required
def add_more_cotisation_correctionM(request):
    # Récupérez l'instance de l'utilisateur connecté
    user_instance = request.user

    # Récupérez l'ID de la permission spécifique que vous souhaitez vérifier (ID 41 dans ce cas)
    permission_id = 41

    # Vérifiez si l'utilisateur a cette permission dans la table de liaison psp_cash_app_customuser_user_permissions
    if CustomUser.objects.filter(id=user_instance.id, user_permissions__id=int(permission_id)).exists(): 
        add_cotisation_permission = True  # Indique que l'utilisateur a la permission
    else:
        add_cotisation_permission = False  # Indique que l'utilisateur n'a pas la permission
       #return render(request, "membre_template/add_more_cotisation_correctionM.html", {"user_has_permission": user_has_permission})
    current_user = request.user
    compagnie_id = current_user.compagnie_id
    type_cotisation = tbtypecotisation.objects.filter(cotisation_compagnie=compagnie_id)
    membre_info = Membre.objects.filter(admin__compagnie=current_user.compagnie, membre_actif='True')
    print(add_cotisation_permission)
    return render(request, "membre_template/add_more_cotisation_correctionM.html", {"membre_info":membre_info, "type_cotisation":type_cotisation, "add_cotisation_permission": add_cotisation_permission})

def add_more_cotisation_correctionM_save(request):
     if request.method == 'POST':
        try:
            date_cotisation = request.POST.get('date_cotisation')
            type_cotisation = request.POST.getlist('type_cotisation[]')
            montant = request.POST.getlist('montant[]')
            interet = request.POST.getlist('interet[]')
            penalite = request.POST.getlist('penalite[]')
            membres = request.POST.getlist('membre_info[]')

            # Insérez vos opérations de traitement des données ici, par exemple :
            for i in range(len(type_cotisation)):
                for membre_id in membres:
                    membre = Membre.objects.get(id=membre_id)
                    cotisation = tbcotisation.objects.create(typecotisation=type_cotisation[i], montant=montant[i], interet=interet[i], penalite=penalite[i], date_fait=date_cotisation, code_membre_id=membre.id)

            # Redirigez l'utilisateur vers une autre page une fois le traitement terminé
            messages.success(request,"Successfully ")
            return HttpResponseRedirect(reverse("add_more_cotisation_correctionM")) 
        except Exception as e:
            messages.error(request,traceback.format_exc())
            return HttpResponseRedirect(reverse("add_more_cotisation_correctionM"))
        
def get_creditM_data(request):
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