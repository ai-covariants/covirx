from collections import OrderedDict
import logging
import csv

from django.conf import settings
from django.core.mail import EmailMessage
from premailer import transform

from .models import Drug

# Used for auto-versioning of static files
# Changing below version would force browsers to reload static files
static_version = '0.0.8'

# The suggestions that is to be returned for autocomplete
# We are adding a backend check to prevent misuse of API
MAX_SUGGESTIONS = 20

# Fields to be used to search on home page
search_fields = ['name', 'smiles', 'inchi', 'synonyms', 'cas_number', 'chebi', 'pubchemcid']

# Fields which have been name differently in excel sheet and in our Drug model
# It should be in lowercase with spaces replaced by underscore
verbose_names = {
    'indication_(1)': 'indication_class'
}

# Fields that need to be stored during a bulk drug upload
ignore_fields = ['id'] + list(verbose_names.values())
store_fields = [f.name for f in Drug._meta.get_fields() if f.name not in ignore_fields]

# Dictionary contains the list of all invalidated drugs during drug upload
invalid_drugs = OrderedDict()

target_model_names = [
    'Caco2 Ellinger',
    'Vero-E6 Zaliani',
    'Vero-E6 Touret',
    'HRCE Heiser',
    '3CLPro Kuzikov',
    'Vero-E6 Riva',
    'Bakowski',
    'SARS-CoV Pseudotyped particle entry Vero E6 - NCATS and PubChem (AID:1479145)',
    'SARS-CoV Pseudotyped particle entry Vero E6 (Tox counterscreen)- NCATS and PubChem (AID:1479150)',
    'MERS Pseudotyped particle entry Huh7 - NCATS and PubChem (AID:1479149)',
    'MERS Pseudotyped particle entry Huh7 (Tox counterscreen) - NCATS and PubChem (AID:1479147)',
    'SARS-CoV-2 cytopathic effect (CPE)(Tox counterscreen) - NCATS, PubChem (AID:1508605) and Chen',
    'SARS-CoV-2 cytopathic effect (CPE) - NCATS, PubChem (AID:1508606) and Chen',
]

special_drugs = {
    'lopinavir': 'The NIH COVID-19 treatment guideline <b>recommends against</b> the use of lopinavir/ritonavir and other protease inhibitors for the treatment of COVID-19 in hospitalized and non-hospitalized patients. <a target="_blank" href="https://www.covid19treatmentguidelines.nih.gov/therapies/antiviral-therapy/lopinavir-ritonavir-and-other-hiv-protease-inhibitors">Link</a>',
    'nitazoxanide': 'The NIH COVID-19 treatment guideline <b>recommends against</b> the use of nitazoxanide for the treatment of COVID-19, except in clinical trials. <a target="_blank" href="https://www.covid19treatmentguidelines.nih.gov/therapies/antiviral-therapy/nitazoxanide/">Link</a>',
    'chloroquine phosphate': 'The NIH COVID-19 treatment guideline <b>recommends against</b> the use of chloroquine for the treatment of COVID-19 in hospitalized and non-hospitalized patients. <a target="_blank" href="https://www.covid19treatmentguidelines.nih.gov/therapies/antiviral-therapy/chloroquine-or-hydroxychloroquine-and-or-azithromycin/">Link</a>',
    'hydroxychloroquine sulfate': 'The NIH COVID-19 treatment guideline <b>recommends against</b> the use of hydroxychloroquine for the treatment of COVID-19 in hospitalized and non-hospitalized patients. <a target="_blank" href="https://www.covid19treatmentguidelines.nih.gov/therapies/antiviral-therapy/chloroquine-or-hydroxychloroquine-and-or-azithromycin/">Link</a>',
    'doxycycline hydrochloride': 'The Australian National COVID-19 Clinical Evidence Taskforce <b>recommends against</b> the use of doxycycline or doxycycline/ivermectin combination for the treatment of COVID-19 except under randomized clinical trials (with appropriate ethical approval). <a target="_blank" href="https://app.magicapp.org/#/guideline/L4Q5An/section/nygMxj">Link</a>',
    'telmisartan': 'The Australian National COVID-19 Clinical Evidence Taskforce <b>recommends against</b> the use of telmisartan for the treatment of COVID-19 except under randomized clinical trials (with appropriate ethical approval). <a target="_blank" href="https://app.magicapp.org/#/guideline/L4Q5An/section/nygMxj">Link</a>',
    'darunavir': 'The Australian National COVID-19 Clinical Evidence Taskforce <b>recommends against</b> the use of darunavir-cobicistat for the treatment of COVID-19 except under randomized clinical trials (with appropriate ethical approval). <a target="_blank" href="https://app.magicapp.org/#/guideline/L4Q5An/section/nygMxj">Link</a>',
    'favipiravir': 'The Australian National COVID-19 Clinical Evidence Taskforce <b>recommends against</b> the use of favipiravir for the treatment of COVID-19 except under randomized clinical trials (with appropriate ethical approval). <a target="_blank" href="https://app.magicapp.org/#/guideline/L4Q5An/section/nygMxj">Link</a>',
    'sofosbuvir': 'The Australian National COVID-19 Clinical Evidence Taskforce <b>recommends against</b> the use of sofosbuvir-daclatasvir for the treatment of COVID-19 except under randomized clinical trials (with appropriate ethical approval). <a target="_blank" href="https://app.magicapp.org/#/guideline/L4Q5An/section/nygMxj">Link</a>',
    'triazavirin': 'The Australian National COVID-19 Clinical Evidence Taskforce <b>recommends against</b> the use of triazavirin for the treatment of COVID-19 except under randomized clinical trials (with appropriate ethical approval). <a target="_blank" href="https://app.magicapp.org/#/guideline/L4Q5An/section/nygMxj">Link</a>',
    'umifenovir (hydrochloride)': 'The Australian National COVID-19 Clinical Evidence Taskforce <b>recommends against</b> the use of umifenovir for the treatment of COVID-19 except under randomized clinical trials (with appropriate ethical approval). <a target="_blank" href="https://app.magicapp.org/#/guideline/L4Q5An/section/nygMxj">Link</a>',
    'ruxolitinib (incb018424)': 'The Australian National COVID-19 Clinical Evidence Taskforce <b>recommends against</b> the use of ruxolitinib for the treatment of COVID-19 except under randomized clinical trials (with appropriate ethical approval). <a target="_blank" href="https://app.magicapp.org/#/guideline/L4Q5An/section/nygMxj">Link</a>',
    'tofacitinib (cp-690550 or tasocitinib)': 'The Australian National COVID-19 Clinical Evidence Taskforce <b>recommends against</b> the use of tofacitinib for the treatment of COVID-19 except under randomized clinical trials (with appropriate ethical approval). <a target="_blank" href="https://app.magicapp.org/#/guideline/L4Q5An/section/nygMxj">Link</a>',
    'tofacitinib (cp-690550) citrate': 'The Australian National COVID-19 Clinical Evidence Taskforce <b>recommends against</b> the use of tofacitinib for the treatment of COVID-19 except under randomized clinical trials (with appropriate ethical approval). <a target="_blank" href="https://app.magicapp.org/#/guideline/L4Q5An/section/nygMxj">Link</a>',
    'aprepitant': 'The Australian National COVID-19 Clinical Evidence Taskforce <b>recommends against</b> the use of aprepitant for the treatment of COVID-19 except under randomized clinical trials (with appropriate ethical approval). <a target="_blank" href="https://app.magicapp.org/#/guideline/L4Q5An/section/nygMxj">Link</a>',
    'bromhexine hydrochloride': 'The Australian National COVID-19 Clinical Evidence Taskforce <b>recommends against</b> the use of bromhexine for the treatment of COVID-19 except under randomized clinical trials (with appropriate ethical approval). <a target="_blank" href="https://app.magicapp.org/#/guideline/L4Q5An/section/nygMxj">Link</a>',
    'fluvoxamine maleate': 'The Australian National COVID-19 Clinical Evidence Taskforce <b>recommends against</b> the use of fluvoxamine for the treatment of COVID-19 except under randomized clinical trials (with appropriate ethical approval). <a target="_blank" href="https://app.magicapp.org/#/guideline/L4Q5An/section/nygMxj">Link</a>',
    'metformin hydrochloride': 'The Australian National COVID-19 Clinical Evidence Taskforce <b>recommends against</b> the use of metformin for the treatment of COVID-19 except under randomized clinical trials (with appropriate ethical approval). <a target="_blank" href="https://app.magicapp.org/#/guideline/L4Q5An/section/nygMxj">Link</a>',
}

extra_references = [
    'Probst, Daniel, Reymond, Jean-Louis. SmilesDrawer: Parsing and Drawing SMILES-Encoded Molecular Structures Using Client-Side JavaScript. J. Chem. Inf. Model. 2018, 58, 1, 1–7',
    'Therapeutic Goods Administration (TGA). 2022. Search the TGA website. [online] Available at: <https://tga-search.clients.funnelback.com/s/search.html?query=&collection=tga-artg> [Accessed 20 January 2022].',
    'Accessdata.fda.gov. 2022. Drugs@FDA: FDA-Approved Drugs. [online] Available at: <https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm> [Accessed 20 January 2022].',
    'Drugs.ncats.io. 2022. NCATS Inxight Drugs. [online] Available at: <https://drugs.ncats.io/> [Accessed 20 January 2022].'
]

def _get_clinical_trials():
    clinical_trials = dict()
    file_path = f'{settings.BASE_DIR}/clinical_trial_links.csv'
    with open(file_path, 'r', encoding='UTF-8') as fp:
        rows = list(csv.reader(fp, delimiter=','))
        for row in rows[1:]:
            row = [s.strip() for s in row]
            if row[2] in ['-', '']:
                continue
            clinical_trials[row[0]] = row[2]
    return clinical_trials

clinical_trial_links = _get_clinical_trials()


def sendmail(html, subject, recepients, bcc=list(), log=None):
    """
    Utility function to send emails. Currently being used for:-
    1) Contact form emails
    2) Sharing invalid drugs during drug upload
    3) Inviting members to the admin panel
    Args:
        html (string/template): Pass on the html template which needs to be sent as message
        subject (string): Subject of the email
        recepients (list): The individuals who need to be sent email
        bcc ([list], optional): If any individuals need to be sent email without them finding
                                out any other member in the mailing list.
        log ([string], optional): If anything needs to be logged on successful email,
                                  can be passed here.
    """
    message = transform(
        html,
        allow_insecure_ssl=True,
        disable_leftover_css=True,
        strip_important=False,
        disable_validation=True,
    )
    msg = EmailMessage(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        recepients,
    )
    msg.content_subtype = "html"
    if recepients:
        msg.send(fail_silently=False)
    if bcc: # Useful to send emails when we don't want recipient to know others in email list
        msg.to = []
        msg.bcc = bcc
        msg.send(fail_silently=False)
    if log:
        logging.getLogger('info_logger').info(log)
