import os
import uuid
from datetime import datetime
from copy import deepcopy

import reversion
from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from accounts.models import User


class ContributedDrug(models.Model):
    personName = models.CharField('Name of Person',blank=False,unique=True,max_length=50)
    email = models.EmailField('Email',max_length=50,blank=False)
    organisation = models.CharField('Organization',max_length=100, blank=False)
    drugName = models.CharField('Drug Name',blank=False,max_length=100)
    invitro = models.CharField('Invitro',blank = True,max_length=100)
    invivo = models.CharField('Invivo',blank = True,max_length=100)
    exvivo = models.CharField('Exvivo',blank=True,max_length=50)
    results = models.CharField('Activity Results',blank=False,max_length=100)
    inference = models.CharField('Inference',blank=True,max_length=100)
    contributor = models.ForeignKey(User, blank=False, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.drugName

class CustomFields(models.Model):
    name = models.TextField(unique=True, null=False, blank=False, help_text="Enter the name of this field exactly as in the Excel sheet.")
    verbose_name = models.TextField(unique=True, null=True, blank=True, help_text="Enter the name of this field in the format in which you want the user to view the field.")

    def save(self, *args, **kwargs):
        if not self.verbose_name:
            self.verbose_name = self.name
        self.name = self.name.lower().replace(' ', '_')
        super().save(*args, **kwargs)
        cache.set(
            'custom_fields',
            self.__class__.objects.values_list('name', flat=True), None
        )

    def __str__(self):
        return f"{self.verbose_name}"

    class Meta:
        verbose_name_plural = "Custom fields"

@reversion.register()
class Drug(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(blank=False, null=False, unique=True)
    # Drug Structure
    formula = models.TextField(blank=True, null=True)
    smiles = models.TextField(blank=True, null=True, unique=True)
    inchi = models.TextField(blank=True, null=True, unique=True)
    # Drug identifiers
    synonyms = models.TextField(blank=True, null=True, unique=True)
    cas_number = models.TextField(blank=True, null=True, unique=True)
    chebi = models.TextField(blank=True, null=True, unique=True)
    chembl = models.TextField(blank=True, null=True, unique=True)
    pubchemcid = models.TextField(blank=True, null=True, unique=True)
    drugbank = models.TextField(blank=True, null=True)
    indication_class = models.TextField(blank=True, null=True, verbose_name='indication_class/category')
    phase = models.TextField(blank=True, null=True)
    references = models.TextField(blank=True, null=True)
    LABEL_CHOICES = [
        ('1', _('White')),
        ('2', _('Green')),
        ('3', _('Red')),
        ('4', _('Amber')),
    ]
    # Other parameters
    label = models.CharField(max_length=1, choices=LABEL_CHOICES, default='1')
    similar_drugs = models.TextField(blank=True, null=True)
    mw = models.TextField(blank=True, null=True)
    nochiralcentres = models.TextField(blank=True, null=True)
    logp = models.TextField(blank=True, null=True)
    hba = models.TextField(blank=True, null=True)
    hbd = models.TextField(blank=True, null=True)
    psa = models.TextField(blank=True, null=True)
    rotbonds = models.TextField(blank=True, null=True)
    administration_route = models.TextField(blank=True, null=True)
    rank_score = models.TextField(blank=True, null=True)
    # If the 11 filters are run sequentially, the number of filters passed
    filters_passed = models.IntegerField(default=0)
    # the filters the drug will fail at when the filters are ran parallely
    filters_failed = models.JSONField(default=dict, blank=True)
    custom_fields = models.JSONField(default=dict, blank=True)

    @classmethod
    def get_or_create(cls, kwargs):
        kwargs['name'] = kwargs['name'].strip()
        try:
            drug = Drug.objects.get(name=kwargs['name'])
        except:
            # Ensure persistent IDs by storing ID using a SHA-1 hash of a namespace UUID and drug name
            drug = Drug(pk=uuid.uuid5(uuid.NAMESPACE_DNS, kwargs['name']))
        drug.__dict__.update(kwargs)
        if settings.DEBUG:
            print(drug.name)
        drug.full_clean()
        drug.save()
        return drug

    def clean(self):
        if not self.inchi or self.inchi in ['N/A', '|N/A']:
            self.inchi = None
        if not self.smiles or self.smiles in ['N/A', '|N/A']:
            self.smiles = None
        if not self.cas_number or self.cas_number in ['N/A', '|N/A']:
            self.cas_number = None
        if not self.chebi or self.chebi in ['N/A', '|N/A']:
            self.chebi = None
        if not self.chembl or self.chembl in ['N/A', '|N/A']:
            self.chembl = None
        if not self.synonyms or self.synonyms in ['N/A', '|N/A']:
            self.synonyms = None
        if not self.pubchemcid or self.pubchemcid in ['N/A', '|N/A']:
            self.pubchemcid = None

    def related_articles(self, user):
        """returns unverified articles which might contain new assay data for the drug"""
        if user.is_superuser:
            return self.article_set.filter(relevant=None)
        return self.article_set.filter(relevant=None, assigned_to__in=[user, None])

    def update_target_model(self, model_name, data, user):
        custom_fields = dict(self.custom_fields)
        if data is None and model_name in self.custom_fields:
            act = 'Deleted'
            custom_fields.pop(model_name)
        else:
            custom_fields[model_name] = dict()
            for k, v in data.items():
                custom_fields[model_name][k] = v
            act = 'Added' if len(custom_fields)>len(self.custom_fields) else 'Updated'
        with reversion.create_revision():
            # Save previous version to be able to restore in future
            self.save()
            reversion.set_user(user)
            reversion.set_comment(f'{act} target model {model_name} in {self.name}.')
        self.custom_fields = custom_fields
        self.save()

    def __str__(self):
        return f"{self.name}"

    class Meta:
        # indexing a field makes it faster for carrying search on that field in the db
        indexes = [
            models.Index(fields=['name',]),
            models.Index(fields=['smiles',]),
            models.Index(fields=['inchi',]),
            models.Index(fields=['synonyms',]),
            models.Index(fields=['cas_number',]),
            models.Index(fields=['chebi',]),
            models.Index(fields=['pubchemcid',]),
        ]


def storage_path(instance, filename):
    """ file will be uploaded to MEDIA_ROOT/drugs/<datetime>-<filename> """
    return f'drugs/{datetime.now()}-{filename}'


class DrugBulkUpload(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_uploaded = models.DateTimeField(auto_now=True)
    csv_file = models.FileField(upload_to=storage_path)
    invalid_drugs = models.TextField(blank=True, null=True)
    valid_count = models.IntegerField(default=0)
    invalid_count = models.IntegerField(default=0)
    total_count = models.IntegerField(default=0)
    uploaded_by = models.CharField(max_length=100, blank=False, null=False)

    def start_upload(self, total_count, invalid_drugs):
        self.total_count = total_count
        cache.set_many({'total_count': total_count, 'email_recepients': ''}, None)
        cache.set_many({'valid_count': 0, 'invalid_count': 0}, 60)
        self.save()
        invalid_drugs.clear()

    def invalid_drug(self):
        """ Increments the counter for invalid drugs, is useful to display while uploading """
        self.invalid_count+=1
        cache.set('invalid_count', self.invalid_count, 60)

    def valid_drug(self):
        """ Increments the counter for valid drugs, is useful to display while uploading """
        self.valid_count+=1
        cache.set('valid_count', self.valid_count, 60)

    def finish_upload(self, invalid_drugs):
        # Other cache keys have timeout set to 60s
        cache.touch('total_count', 60)
        cache.touch('email_recepients', 60)
        self.invalid_drugs = str(invalid_drugs)
        self.full_clean()
        self.save()
        invalid_drugs.clear()


class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_uploaded = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=158, blank=False, null=False)
    email = models.EmailField(blank=False)
    subject = models.CharField(max_length=158, blank=False, null=False)
    phone = models.CharField(max_length=20, blank=True, null=True)
    organisation = models.CharField(max_length=158, blank=True, null=True)
    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


def REASSIGN(collector, field, sub_objs, using):
    collector.add_field_update(field, None, sub_objs)
    try:
        for count, article in enumerate(Article.objects.filter(assigned_to=None)):
            article.save_and_assign_article(count)
    except:
        pass

class Article(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_mined = models.DateTimeField(auto_now=True)
    title = models.TextField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
    target_model = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(User, on_delete=REASSIGN, null=True, default=None)
    relevant = models.BooleanField(default=None, blank=False, null=True)
    comment = models.TextField(default=None, null=True, blank=True)

    @property
    def verified_by(self):
        return self.assigned_to if self.relevant is not None else None

    def json(self):
        return {
            'title': self.title,
            'url': self.url,
            'date_mined': self.date_mined,
            'target_model': self.target_model,
            'keywords': self.keywords,
            'verified_by': None if not self.verified_by else self.verified_by.get_full_name(),
            'relevant': self.relevant,
            'comment': self.comment,
            'update_drug': reverse(f"admin:{self._meta.app_label}_drug_change", args=(self.drug.id,))
        }

    def mark_verified(self, relevant, comment, verified_by):
        self.relevant = relevant
        self.comment = comment
        self.assigned_to = verified_by
        self.full_clean()
        self.save()

    def save_and_assign_article(self, article_count):
        staff = User.objects.filter(is_staff=True, is_superuser=False, is_active=True).order_by('email')
        if(len(staff) == 0):
            self.save()
            raise Exception('No active staff members to assign article verification job.')
        # sequentially assign article amongst all active non-superuser staff
        self.assigned_to = staff[article_count%len(staff)]
        self.save()

    class Meta:
        ordering = ['date_mined']
        constraints = [
            models.UniqueConstraint(fields=['title', 'drug', 'target_model'], name='Article Uniqueness')
        ]


@receiver(models.signals.post_delete, sender=DrugBulkUpload)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `DrugBulkUpload` object is deleted.
    """
    if instance.csv_file:
        if os.path.isfile(instance.csv_file.path):
            os.remove(instance.csv_file.path)


@receiver(models.signals.post_save, sender=CustomFields)
def auto_add_custom_field(sender, instance, **kwargs):
    """
    Add the custom field with no value to every drug in database
    """
    for drug in Drug.objects.all():
        drug.custom_fields[instance.name] = ''
        drug.save()


@receiver(models.signals.post_delete, sender=CustomFields)
def auto_delete_custom_field(sender, instance, **kwargs):
    """
    Delete the custom field for every drug in database
    """
    for drug in Drug.objects.all():
        drug.custom_fields.pop(instance.name, None)
        drug.save()
