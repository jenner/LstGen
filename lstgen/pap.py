# coding: utf-8
"""
PAP XML and remote API URLs
"""
from collections import (
    namedtuple,
    OrderedDict
)
import requests
from lxml import etree

PAP_BASE_URL = 'https://www.bmf-steuerrechner.de'

PapResource = namedtuple('PapResource', ('remote_service_path', 'pap_xml_path'))

PAP_RESOURCES = OrderedDict((
    ('2006_1', PapResource(
        '/interface/2006Version1.xhtml',
        '/javax.faces.resource/daten/xmls/Lohnsteuer2006Big.xml.xhtml'
    )),
    ('2007_1', PapResource(
        '/interface/2007Version1.xhtml',
        '/javax.faces.resource/daten/xmls/Lohnsteuer2007Big.xml.xhtml'
    )),
    ('2008_1', PapResource(
        '/interface/2008Version1.xhtml',
        '/javax.faces.resource/daten/xmls/Lohnsteuer2008Big.xml.xhtml'
    )),
    ('2009_1', PapResource(
        '/interface/2009Version1.xhtml',
        '/javax.faces.resource/daten/xmls/Lohnsteuer2009Big.xml.xhtml'
    )),
    ('2010_1', PapResource(
        '/interface/2010Version1.xhtml',
        '/javax.faces.resource/daten/xmls/Lohnsteuer2010Big.xml.xhtml'
    )),
    ('2011_1', PapResource(
        '/interface/2011bisNovVersion1.xhtml',
        '/javax.faces.resource/daten/xmls/Lohnsteuer2011BisNovember.xml.xhtml'
    )),
    ('2011_12', PapResource(
        '/interface/2011DezVersion1.xhtml',
        '/javax.faces.resource/daten/xmls/Lohnsteuer2011Dezember.xml.xhtml'
    )),
    ('2012_1', PapResource(
        '/interface/2012Version1.xhtml',
        '/javax.faces.resource/daten/xmls/Lohnsteuer2012.xml.xhtml'
    )),
    ('2013_1', PapResource(
        '/interface/2013Version1.xhtml',
        '/javax.faces.resource/daten/xmls/Lohnsteuer2013.xml.xhtml'
    )),
    ('2014_1', PapResource(
        '/interface/2014Version1.xhtml',
        '/javax.faces.resource/daten/xmls/Lohnsteuer2014.xml.xhtml'
    )),
    ('2015_1', PapResource(
        '/interface/2015bisNovVersion1.xhtml',
        '/javax.faces.resource/daten/xmls/Lohnsteuer2015BisNovember.xml.xhtml'
    )),
    ('2015_12', PapResource(
        '/interface/2015DezVersion1.xhtml',
        '/javax.faces.resource/daten/xmls/Lohnsteuer2015Dezember.xml.xhtml'
    )),
    ('2016_1', PapResource(
        '/interface/2016Version1.xhtml',
        '/javax.faces.resource/daten/xmls/Lohnsteuer2016.xml.xhtml'
    )),
    ('2017_1', PapResource(
        '/interface/2017Version1.xhtml',
        '/javax.faces.resource/daten/xmls/Lohnsteuer2017.xml.xhtml'
    )),
    ('2018_1', PapResource(
        '/interface/2018Version1.xhtml',
        '/javax.faces.resource/daten/xmls/Lohnsteuer2018.xml.xhtml'
    )),
    ('2019_1', PapResource(
        '/interface/2019Version1.xhtml',
        '/javax.faces.resource/daten/xmls/Lohnsteuer2019.xml.xhtml'
    )),
    ('2020_1', PapResource(
        '/interface/2020Version1.xhtml',
        '/javax.faces.resource/daten/xmls/Lohnsteuer2020.xml.xhtml'
    )),
    ('2021_1', PapResource(
        '/interface/2021Version1.xhtml',
        '/javax.faces.resource/daten/xmls/Lohnsteuer2021.xml.xhtml'
    )),
    ('2022_1', PapResource(
        '/interface/2022Version1.xhtml',
        '/javax.faces.resource/daten/xmls/Lohnsteuer2022.xml.xhtml'
    )),
    ('2023_2', PapResource(
        '/interface/2023Version1.xhtml',
        '/javax.faces.resource/daten/xmls/Lohnsteuer2023.xml.xhtml'
    )),
    ('2023_3', PapResource(
        '/interface/2023AbJuliVersion1.xhtml',
        '/javax.faces.resource/daten/xmls/Lohnsteuer2023AbJuli.xml.xhtml'
    )),
    ('2024_1', PapResource(
        '/interface/2024Version1.xhtml',
        '/javax.faces.resource/daten/xmls/Lohnsteuer2024.xml.xhtml'
    )),
    ('2024_2', PapResource(
        '/interface/2024DezemberVersion1.xhtml',
        '/javax.faces.resource/daten/xmls/Lohnsteuer2024Dezember.xml.xhtml'
    )),
    ('2025_1', PapResource(
        '/interface/2025Version1.xhtml',
        '/javax.faces.resource/daten/xmls/Lohnsteuer2025.xml.xhtml'
    )),
))


def get_pap_xml(pap_resource_name):
    """ Fetch PAP XML from bmf-steuerrechner.de and return
        it as a string.
    """
    resource = PAP_RESOURCES.get(pap_resource_name)
    if not resource:
        raise ValueError("Invalid PAP resource name: {}".format(pap_resource_name))
    url = "{}{}".format(PAP_BASE_URL, resource.pap_xml_path)
    response = requests.get(url, verify=False) # FIXME bmf-steuerrechner.de has a weak certificate
    return response.content

def call_pap_service(pap_resource_name, input_vars):
    """ Call PAP remote service (REST XML API) and
        return a dict with results
    """
    resource = PAP_RESOURCES.get(pap_resource_name)
    if not resource:
        raise ValueError("Invalid PAP resource name: {}".format(pap_resource_name))
    url = "{}{}".format(PAP_BASE_URL, resource.remote_service_path)
    response = requests.get(url, input_vars, verify=False)
    tree = etree.fromstring(response.content)
    ret = dict()
    for elm in tree.xpath('/lohnsteuer/ausgaben/ausgabe'):
        ret[elm.get('name')] = elm.get('value')
    return ret
