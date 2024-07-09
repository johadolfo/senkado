from django.contrib.auth.models import AbstractUser
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
import datetime
import os
from django.contrib.auth.models import Permission
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission

def filepath(request, filename):
    old_filename=filename
    timenow = datetime.datetime.now().strftime('%Y%m%d%H:%M:%S')
    filename = "%s%s" % (timeNow, old_filename)
    return os.path.join('uploads/', filename)

# Create your models here.
gender_choice = {
    ('M', 'Masculin'),
    ('F', 'Feminin'),
}

typecotisation_choice = {
    ('Fonds de Credit', 'Fonds de Credit'),
    ('Fonds Urgences', 'Fonds Urgences'),
    ('Fonds de Fonctionnement', 'Fonds de Fonctionnement'),
}

class SessionYearModel(models.Model):
    id=models.AutoField(primary_key=True)
    session_start_year=models.DateField()
    session_end_year=models.DateField()
    objects = models.Manager()

############################# gestion commande ###############################
class tbcompagnie(models.Model):
    code_compagnie =  models.CharField("CODE COMPAGNIE ",max_length=50, blank=True)
    compagnie = models.CharField("COMPAGNIE ",max_length=50, blank=True)
    adresse =  models.CharField("ADRESSE ",max_length=50, blank=True)
    adresse2 =  models.CharField("ADRESSE ",max_length=50, blank=True)
    phone =  models.CharField("TELEPHONE ",max_length=50, blank=True)
    phone2 =  models.CharField("TELEPHONE ",max_length=50, blank=True)
    phone3 =  models.CharField("TELEPHONE ",max_length=50, blank=True)
    logoPath = models.FileField(upload_to=filepath, null=True, blank=True)
    email = models.CharField("EMAIL ",max_length=50, blank=True)
    siteweb = models.CharField("SITE ",max_length=50, blank=True)
    couleur_preferee = models.CharField("Couleur Preferee ", default='#2471A3',max_length=50, blank=True)
    statut = models.CharField("Status Compagnie",max_length=50, blank=True, default="Enable", null=True)
    couleur_text_menu = models.CharField("Couleur Preferee ", default='#2471A3',max_length=50, blank=True)

class tbdepartement(models.Model):
    code_departement =  models.CharField("CODE DEPARTEMENT ",max_length=50, blank=True)
    departement = models.CharField("DEPARTEMENT ",max_length=50, blank=True)
    print_in_kitchen =  models.CharField("PRINT IN KITCHEN ",max_length=50, blank=True)
    print_bar =  models.CharField("PRINT BAR ",max_length=50, blank=True)
    compagnie = models.ForeignKey(tbcompagnie, on_delete=models.CASCADE)

class tbunitemesure(models.Model):
    unite_mesure = models.CharField("UNITE DE MESURE ",max_length=50, blank=True)
    compagnie = models.ForeignKey(tbcompagnie, on_delete=models.CASCADE)

class tbarticle(models.Model):
    code_articl = models.CharField("CODE ARTICLE ",max_length=50, blank=True)
    code_departement= models.ForeignKey(tbdepartement, on_delete=models.CASCADE)
    description = models.CharField("DESCRIPTION ",max_length=50, blank=True)
    description2 = models.CharField("DESCRIPTION ",max_length=50, blank=True)
    unite_mesure= models.ForeignKey(tbunitemesure, on_delete=models.CASCADE)
    cout_unit = models.FloatField("COUT",default='0.0', blank=True, null=True)
    quantite = models.FloatField("QUANTITE",default='0.0', blank=True, null=True)
    prix = models.FloatField("PRICE",default='0.0', blank=True, null=True)
    reoderpoint = models.FloatField("REODERPOINT",default='0.0', blank=True, null=True)
    date_expiration = models.DateTimeField("Date Expiration (YYYY-MM-DD)",auto_now_add=False, auto_now=False)
    compagnie = models.ForeignKey(tbcompagnie, on_delete=models.CASCADE)
    objects=models.Manager()

class tbajustement(models.Model):
    date_ajustement = models.DateTimeField("Date Ajustement (YYYY-MM-DD)",auto_now_add=False, auto_now=False)
    memo = models.TextField()
    recu_par = models.CharField("Recu Par",max_length=50, blank=True, null=True)
    objects=models.Manager()

class tbajustementarticle(models.Model):
    code_ajustement = models.ForeignKey(tbajustement, on_delete=models.CASCADE)
    code_article = models.ForeignKey(tbarticle, on_delete=models.CASCADE)
    anc_quantite = models.FloatField("Ancienne Quantite",default='0.0', blank=True, null=True)
    nouv_quantite = models.FloatField("Nouvelle Quantite",default='0.0', blank=True, null=True)
    anc_cout = models.FloatField("Ancien Cout",default='0.0', blank=True, null=True)
    nouv_cout = models.FloatField("Nouveau Cout",default='0.0', blank=True, null=True)
    anc_prix = models.FloatField("Ancien Prix",default='0.0', blank=True, null=True)
    nouv_prix = models.FloatField("Nouveau Prix",default='0.0', blank=True, null=True)
    memo = models.TextField()
    objects=models.Manager()

class CustomUser(AbstractUser):
    user_type_data = ((1,"HOD"), (2, "Membre"), (3, "SUPHOD"))
    user_type= models.CharField(default=1, choices=user_type_data, max_length=10)
    compagnie = models.ForeignKey(tbcompagnie, default=1, on_delete=models.CASCADE)

class Membre(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    codep =  models.CharField("CODE MEMBRE ",max_length=50, blank=True)
    nomp =  models.CharField("NOM MEMBRE ",max_length=50, blank=True, null=True)
    prenomp =  models.CharField("PRENOM MEMBRE ",max_length=50, blank=True, null=True)
    sexep =  models.CharField("SEXE MEMBRE ",max_length=50, blank=True, null=True, choices=gender_choice)
    cin =  models.CharField("CIN ",max_length=50, blank=True, null=True)
    nif =  models.CharField("NIF ",max_length=50, blank=True, null=True)
    tel_mob =  models.CharField("TELEPHONE MOBILE ",max_length=50, blank=True, null=True)
    tel_house =  models.CharField("TELEPHONE HOUSE ",max_length=50, blank=True, null=True)
    adresse =  models.CharField("ADRESSE EMPLOYE ",max_length=50, blank=True, null=True)
    dateajout =  models.DateTimeField(auto_now_add=False, auto_now=True, null=True)
    profile_pic=models.FileField(upload_to=filepath, null=True, blank=True)
    credit_limit = models.FloatField("CREDIT LIMIT",default='0.0', blank=True, null=True)
    account = models.FloatField("ACCOUNT",default='0.0', blank=True, null=True)
    membre_actif = models.BooleanField(default = True)
    objects=models.Manager()

class tbreceipt(models.Model):
    num_receipt = models.AutoField(primary_key=True)
    num_bath = models.CharField("Numero batch", max_length=50, blank=True, null=True)
    client = models.CharField("Client", max_length=50, blank=True, null=True)
    date_receipt = models.DateTimeField(auto_now_add=False, auto_now=True, null=True)
    total_article = models.FloatField("Total Article", default=0.0, blank=True, null=True)
    tax = models.FloatField("Tax", default=0.0, blank=True, null=True)
    total_cost = models.FloatField("Total Cost", default=0.0, blank=True, null=True)
    total_price = models.FloatField("Total Price", default=0.0, blank=True, null=True)
    receipt_discount = models.FloatField("Receipt Discount", default=0.0, blank=True, null=True)
    balance = models.FloatField("Balance", default=0.0, blank=True, null=True)
    observation = models.CharField("Observation", max_length=50, blank=True, null=True)
    statut = models.CharField("Statut", max_length=50, blank=True, null=True)
    deposit = models.FloatField("Deposit", default=0.0, blank=True, null=True)
    service_charge = models.FloatField("Service Charge", default=0.0, blank=True, null=True)
    type_receipt = models.CharField("Type Receipt", max_length=50, blank=True, null=True)
    user_receipt = models.CharField("User", max_length=50, blank=True, null=True)
    date_close = models.DateTimeField("Date Close (YYYY-MM-DD)", auto_now_add=False, auto_now=False)
    close_by = models.CharField("Close By", max_length=50, blank=True, null=True)
    compagnie = models.ForeignKey(tbcompagnie,default='1', on_delete=models.CASCADE)
    objects = models.Manager()

class tbreceiptarticle(models.Model):
    num_ligne = models.BigIntegerField("Numero batch", default=1, blank=True, null=True)
    receipt = models.ForeignKey(tbreceipt, on_delete=models.CASCADE)
    article = models.ForeignKey(tbarticle, on_delete=models.CASCADE)
    quantite = models.FloatField("Total Article", default=0.0, blank=True, null=True)
    cout = models.FloatField("Tax", default=0.0, blank=True, null=True)
    prix = models.FloatField("Total Cost", default=0.0, blank=True, null=True)
    discount_article = models.FloatField("Total Price", default=0.0, blank=True, null=True)
    receipt_discount = models.FloatField("Receipt Discount", default=0.0, blank=True, null=True)
    observation = models.CharField("Observation", max_length=50, blank=True, null=True)
    statut = models.CharField("Statut", max_length=50, blank=True, null=True)
    user_added_byreceipt = models.CharField("User", max_length=50, blank=True, null=True)
    date_added = models.DateTimeField("Date Added (YYYY-MM-DD)", auto_now_add=False, auto_now=False)
    objects = models.Manager()

class tbpaiement(models.Model):
    num_paiement = models.AutoField(primary_key=True)
    receipt =  models.ForeignKey(tbreceipt, on_delete=models.CASCADE)
    date_paiement =models.DateTimeField("Date Paiement (YYYY-MM-DD)",auto_now_add=True, auto_now=False)
    type_paiement =  models.CharField("Type de Paiement ",max_length=50, blank=True, null=True)
    montant =  models.FloatField("Montant Paie",default='0.0', blank=True, null=True)
    tender = models.FloatField("Tender",default='0.0', blank=True, null=True)
    day_rate =  models.FloatField("Total Cost",default='0.0', blank=True, null=True)
    user_paie =models.CharField("User ",max_length=50, blank=True, null=True)   
    objects=models.Manager()

class tbconfiguration(models.Model):
    id_conf = models.AutoField(primary_key=True)
    orther_curr_name = models.CharField("Other Current Name ",max_length=50, blank=True, null=True)
    other_curr_symb = models.CharField("Other Current Symbole ",max_length=50, blank=True, null=True)
    other_curr_rate =  models.FloatField("Other Current Rate ",default='0.0', blank=True, null=True)
    taxname =  models.CharField("Tax Name 1 ",max_length=50, blank=True, null=True)
    tax_rate1 =  models.FloatField("Tax Rate 1 ",default='0.0', blank=True, null=True)
    taxname2 =  models.CharField("Tax Name 2 ",max_length=50, blank=True, null=True)
    tax_rate2 =  models.FloatField("Tax Rate 2 ",default='0.0', blank=True, null=True)
    taxname3 =  models.CharField("Tax Name 3 ",max_length=50, blank=True, null=True)
    tax_rate3 =  models.FloatField("Tax Rate 3 ",default='0.0', blank=True, null=True)
    use_batch_num = models.CharField("Use Batch Number",max_length=50, blank=True, null=True)
    curr_batch_num =  models.IntegerField("Current Batch Number",default='0', blank=True, null=True)
    nbctoprintonhold =  models.IntegerField("Nb C to Print on Hold",default='0', blank=True, null=True)
    nbctoprintonpayment =  models.IntegerField("Nb C to Print on Payment",default='0', blank=True, null=True)
    compagnie = models.ForeignKey(tbcompagnie,default='1', on_delete=models.CASCADE)
    objects=models.Manager()


class Comment(models.Model):
    author = models.ForeignKey(Membre, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    compagnie_id = models.ForeignKey(tbcompagnie, default=1, on_delete=models.CASCADE)

class tbpayout(models.Model):
    code_payout = models.AutoField(primary_key=True)
    payout =   models.FloatField("Payout ",default='0.0', blank=True, null=True)
    date_payout =models.DateTimeField("Date Payout (YYYY-MM-DD)",auto_now_add=True, auto_now=False)
    payout_comment = models.CharField("Observation", max_length=50, blank=True, null=True)
    userAdded =models.CharField("User ",max_length=50, blank=True, null=True)  
    compagnie = models.ForeignKey(tbcompagnie,default='1', on_delete=models.CASCADE) 
    objects=models.Manager()

########################### fin ##################################################

class tbmuso(models.Model):
    codemuso =  models.CharField("CODE MUSO ",max_length=50, blank=True)
    sigle =  models.CharField("SIGLE ",max_length=50, blank=True)
    nom_muso =  models.CharField("NOM ",max_length=50, blank=True)
    adresse_muso =  models.CharField("ADRESSE ",max_length=50, blank=True)
    telephone_muso =  models.CharField("TELEPHONE ",max_length=50, blank=True)
    email_muso = models.CharField("EMAIL ",max_length=50, blank=True)
    site_muso = models.CharField("SITE ",max_length=50, blank=True)
    logo_muso = models.FileField(upload_to=filepath, null=True, blank=True)
    couleur_preferee = models.CharField("Couleur Preferee ", default='#2471A3',max_length=50, blank=True)
    taux_interet = models.FloatField("Taux Interet",default='0.0', blank=True, null=True)
    couleur_text_menu = models.CharField("Couleur Preferee ", default='#2471A3',max_length=50, blank=True)
    date_creation =  models.DateTimeField("Date Creation",auto_now_add=False, auto_now=False)

    #def __str__(self):
    #return self.nom_muso

class tbtypecotisation(models.Model):
    nom_cotisation = models.CharField("Libelle ",max_length=50, blank=True)
    cotisation_muso = models.ForeignKey(tbmuso, on_delete=models.CASCADE)
    reference = models.CharField("Reference Caisse ",max_length=50, blank=True)


class CustomUserPermission(models.Model):
    customuser = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'g_muso_app_customuser_user_permissions'

class AdminHOD(models.Model):
    id = models.AutoField(primary_key=True)
    admin=models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class tbcotisation(models.Model):
    typecotisation = models.CharField("Type de Cotisation",max_length=50, blank=True, null=True, choices=typecotisation_choice)
    montant = models.FloatField("Montant",default='0.0', blank=True, null=True)
    interet = models.FloatField("Interet",default='0.0', blank=True, null=True)
    balance = models.FloatField("Balance",default='0.0', blank=True, null=True)
    date_fait = models.DateTimeField("Date Cotisation (YYYY-MM-DD)",auto_now_add=False, auto_now=False)
    code_membre = models.ForeignKey(Membre, on_delete=models.CASCADE)
    penalite = models.FloatField("Penalite",default='0.0', blank=True, null=True)
    recu_par = models.CharField("Recu Par",max_length=50, blank=True, null=True)
    objects=models.Manager()

class tbcredit(models.Model):
    numero = models.CharField("Numero Credit",max_length=50, blank=True, primary_key=True)
    date_credit =  models.DateTimeField("Date Credit (YYYY-MM-DD)",auto_now_add=False, auto_now=False)
    nbre_de_mois = models.FloatField("Nombre de Mois",default='0.0', blank=True, null=True)
    date_debut =  models.DateTimeField("Date debut (YYYY-MM-DD)",auto_now_add=False, auto_now=False)
    date_fin = models.DateTimeField("Date Fin (YYYY-MM-DD)",auto_now_add=False, auto_now=False)
    montant_credit = models.FloatField("Montant Credit",default='0.0', blank=True, null=True)
    interet_credit = models.FloatField("Interet Credit",default='0.0', blank=True, null=True)
    code_membre = models.ForeignKey(Membre, on_delete=models.CASCADE)
    commentaire = models.TextField()
    valider_par = models.CharField("Valider Par",max_length=50, blank=True, null=True)
    credit_status = models.CharField("Status Credit",max_length=50, blank=True, default="En cour", null=True)
    objects=models.Manager()

class tbdetailcredit(models.Model):
    codecredit=models.ForeignKey(tbcredit, on_delete=models.CASCADE,  blank=True)
    date_pret =  models.DateField("Date (YYYY-MM-DD)",auto_now_add=False, auto_now=False, blank=True)
    montant_pret = models.FloatField("Montant Credit",default='0.0', blank=True, null=True)
    montant_capital =  models.FloatField("Capital ",default='0.0', blank=True, null=True)
    montant_interet = models.FloatField("Montant Interet",default='0.0', blank=True, null=True)
    total_montant_jr = models.FloatField("Total Montant journalier",default='0.0', blank=True, null=True)
    total_montant_rest = models.FloatField("Total Montant Reste",default='0.0', blank=True, null=True)
    objects=models.Manager()

class tbremboursement(models.Model):
    date_remb =  models.DateField("Date Remboursement (YYYY-MM-DD)",auto_now_add=False, auto_now=False, blank=True)
    codecredit=models.ForeignKey(tbcredit, on_delete=models.CASCADE,  blank=True)
    montant_a_remb = models.FloatField("Montant Credit",default='0.0', blank=True, null=True)
    capital_remb =  models.FloatField("Capital Remboursement",default='0.0', blank=True, null=True)
    interet_remb = models.FloatField("Interet Remboursement",default='0.0', blank=True, null=True)
    balance = models.FloatField("Balance",default='0.0', blank=True, null=True)
    penalite = models.FloatField("Penalite",default='0.0', blank=True, null=True)
    commentaire = models.TextField()
    faites_par = models.ForeignKey(Membre, on_delete=models.CASCADE)
    recu_par = models.CharField("Recu Par",max_length=50, blank=True, null=True)
    objects=models.Manager()

class tbdetailproduit(models.Model):
    no = models.AutoField(primary_key=True)
    codecredit=models.ForeignKey(tbcredit, on_delete=models.CASCADE,  blank=True)
    description =  models.CharField("Nom Produit ",max_length=50, blank=True, null=True)
    quantite_prod = models.FloatField("Quantite ",default='0.0', blank=True, null=True)
    unite= models.CharField("Unite ",max_length=50, blank=True, null=True)
    prix_unitaire = models.FloatField("Prix Unitaire",default='0.0', blank=True, null=True)
    prix_total = models.FloatField("Prix Total",default='0.0', blank=True, null=True)
    frais_transport = models.FloatField("Montant transporter",default='0.0', blank=True, null=True)
    prix_de_revient = models.FloatField("Prix de Revient",default='0.0', blank=True, null=True)
    prix_de_vente = models.FloatField("Prix de Vente",default='0.0', blank=True, null=True)

class tbdepense(models.Model):
    date_depense =  models.DateField("Date Depense (YYYY-MM-DD)",auto_now_add=False, auto_now=False, blank=True)
    description = models.TextField()
    depense_unit = models.FloatField("Prix Unit",default='0.0', blank=True, null=True)
    quantite_dep =  models.FloatField("Quantite",default='0.0', blank=True, null=True)
    muso_id = models.ForeignKey(tbmuso, default=1, on_delete=models.CASCADE)
    objects=models.Manager()

class LeaveReportMembre(models.Model):
    id=models.AutoField(primary_key=True)
    code_membre=models.ForeignKey(Membre, on_delete=models.CASCADE)
    leave_date=models.CharField(max_length=255)
    leave_message=models.TextField()
    leave_status = models.IntegerField(default=0)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    objects=models.Manager()

class FeedBackMembre(models.Model):
    id=models.AutoField(primary_key=True)
    code_membre=models.ForeignKey(Membre, on_delete=models.CASCADE)
    feedback=models.TextField()
    feedback_reply=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    objects=models.Manager()

class NotificationMembre(models.Model):
    id=models.AutoField(primary_key=True)
    code_membre=models.ForeignKey(Membre, on_delete=models.CASCADE)
    message=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    objects=models.Manager()

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created,**kwargs):
    if created:
        if instance.user_type==1:
            AdminHOD.objects.create(admin=instance)
        if instance.user_type==2:
            Membre.objects.create(admin=instance)
       
@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, created,**kwargs):
    if created:
        if instance.user_type==1:
            instance.adminhod.save()
        if instance.user_type==2:
            instance.membre.save()





