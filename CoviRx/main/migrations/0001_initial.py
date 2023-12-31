# Generated by Django 3.2.6 on 2021-09-21 18:28

from django.db import migrations, models
import main.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('date_uploaded', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=158)),
                ('email', models.EmailField(max_length=254)),
                ('subject', models.CharField(max_length=158)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('organisation', models.CharField(blank=True, max_length=158, null=True)),
                ('message', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustomFields',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(help_text='Enter the name of this field exactly as in the Excel sheet.', unique=True)),
                ('verbose_name', models.TextField(blank=True, help_text='Enter the name of this field in the format in which you want the user to view the field.', null=True, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Custom fields',
            },
        ),
        migrations.CreateModel(
            name='Drug',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.TextField(unique=True)),
                ('formula', models.TextField(blank=True, null=True)),
                ('smiles', models.TextField(blank=True, null=True, unique=True)),
                ('inchi', models.TextField(blank=True, null=True, unique=True)),
                ('synonyms', models.TextField(blank=True, null=True, unique=True)),
                ('cas', models.TextField(blank=True, null=True, unique=True)),
                ('chebl', models.TextField(blank=True, null=True, unique=True)),
                ('chembl', models.TextField(blank=True, null=True)),
                ('pubchem', models.TextField(blank=True, null=True, unique=True)),
                ('chembank', models.TextField(blank=True, null=True)),
                ('drugbank', models.TextField(blank=True, null=True)),
                ('indication_class', models.TextField(blank=True, null=True, verbose_name='indication_class/category')),
                ('label', models.CharField(choices=[('1', 'White'), ('2', 'Green'), ('3', 'Red'), ('4', 'Amber')], default='1', max_length=1)),
                ('custom_fields', models.JSONField(blank=True, default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='DrugBulkUpload',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('date_uploaded', models.DateTimeField(auto_now=True)),
                ('csv_file', models.FileField(upload_to=main.models.storage_path)),
                ('invalid_drugs', models.TextField(blank=True, null=True)),
                ('valid_count', models.IntegerField(default=0)),
                ('invalid_count', models.IntegerField(default=0)),
                ('total_count', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddIndex(
            model_name='drug',
            index=models.Index(fields=['name'], name='main_drug_name_bffea9_idx'),
        ),
        migrations.AddIndex(
            model_name='drug',
            index=models.Index(fields=['smiles'], name='main_drug_smiles_710c01_idx'),
        ),
        migrations.AddIndex(
            model_name='drug',
            index=models.Index(fields=['inchi'], name='main_drug_inchi_9e34a5_idx'),
        ),
        migrations.AddIndex(
            model_name='drug',
            index=models.Index(fields=['synonyms'], name='main_drug_synonym_81f090_idx'),
        ),
        migrations.AddIndex(
            model_name='drug',
            index=models.Index(fields=['cas'], name='main_drug_cas_ee2b0f_idx'),
        ),
        migrations.AddIndex(
            model_name='drug',
            index=models.Index(fields=['chebl'], name='main_drug_chebl_a8f84c_idx'),
        ),
        migrations.AddIndex(
            model_name='drug',
            index=models.Index(fields=['pubchem'], name='main_drug_pubchem_dcb991_idx'),
        ),
    ]
