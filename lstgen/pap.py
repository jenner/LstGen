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
    ('2006', PapResource(
        '/interface/2006.jsp',
        '/pruefdaten/Lohnsteuer2006Big.xml'
    )),
    ('2007', PapResource(
        '/interface/2007.jsp',
        '/pruefdaten/Lohnsteuer2007Big.xml'
    )),
    ('2008', PapResource(
        '/interface/2008.jsp',
        '/pruefdaten/Lohnsteuer2008Big.xml'
    )),
    ('2009', PapResource(
        '/interface/2009.jsp',
        '/pruefdaten/Lohnsteuer2009Big.xml'
    )),
    ('2010', PapResource(
        '/interface/2010.jsp',
        '/pruefdaten/Lohnsteuer2010Big.xml'
    )),
    ('2011bisNov', PapResource(
        '/interface/2011bisNov.jsp',
        '/pruefdaten/Lohnsteuer2011BisNovember.xml'
    )),
    ('2011Dez', PapResource(
        '/interface/2011Dez.jsp',
        '/pruefdaten/Lohnsteuer2011Dezember.xml'
    )),
    ('2012', PapResource(
        '/interface/2012.jsp',
        '/pruefdaten/Lohnsteuer2012.xml'
    )),
    ('2013', PapResource(
        '/interface/2013.jsp',
        '/pruefdaten/Lohnsteuer2013_2.xml'
    )),
    ('2014', PapResource(
        '/interface/2014.jsp',
        '/pruefdaten/Lohnsteuer2014.xml'
    )),
    ('2015bisNov', PapResource(
        '/interface/2015bisNov.jsp',
        '/pruefdaten/Lohnsteuer2015BisNovember.xml'
    )),
    ('2015Dez', PapResource(
        '/interface/2015Dez.jsp',
        '/pruefdaten/Lohnsteuer2015Dezember.xml'
    )),
    ('2016', PapResource(
        '/interface/2016V1.jsp',
        '/pruefdaten/Lohnsteuer2016.xml'
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
