import urllib2
from urlparse import urlparse
from utils.preprocessing_helper import index_of_discrete_bin
import re
from bs4 import Comment
from scanner_attribute import ScannerAttribute

"""Parse CMS system for a website"""

# The various CMS systems
DOTNETNUKE = 'DOTNETNUKE'
UMBRACO = 'UMBRACO'
EPISERVER = 'EPISERVER'
SHAREPOINT = 'SHAREPOINT'
SITECORE = 'SITECORE'
DYNAMICWEB = 'DYNAMICWEB'
WORDPRESS = 'WORDPRESS'
TYPO3 = 'TYPO3'
PHPNUKE = 'PHPNUKE'
DRUPAL = 'DRUPAL'
JOOMLA = 'JOOMLA'
UNKNOWN = 'UNKNOWN'

# The bins
def bins():
    return [
        DOTNETNUKE,
        UMBRACO,
        EPISERVER,
        SHAREPOINT,
        SITECORE,
        DYNAMICWEB,
        WORDPRESS,
        TYPO3,
        PHPNUKE,
        DRUPAL,
        JOOMLA,
        UNKNOWN
    ]


def found(cms):
    """Utility method which returns which CMS was found."""
    return ScannerAttribute('cms', cms, index_of_discrete_bin(bins(), cms), bins())


def cms_scanner(website):
    """Find out whether or not the website uses a CMS (and which)."""

    soup = website.soup

    try:
        if website is None:
            print 'CMS scanner. Website was: ', website

        # Assert that data is there
        if soup is None or soup.get_text().isspace():
            print 'CMS scanner. soup was: ', soup
            raise Exception()

        # See if some cms is simply mentioned in the header
        drupal = 'drupal'
        umbraco = 'umbraco'
        for key in website.headers.keys():

            # Drupal
            if drupal in website.headers[key].lower() or drupal in key.lower():
                return found(DRUPAL)

            # Umbraco
            if umbraco in website.headers[key].lower() or umbraco in key.lower():
                return found(UMBRACO)

        # See if a certain path name occurs
        # DotNetNuke
        dnn_path = '/Portals/_default/'
        if dnn_path in soup.get_text():
            return found(DOTNETNUKE)

        # Umbraco
        umbraco_path = '/umbraco/'
        if umbraco_path in soup.get_text():
            return found(UMBRACO)

        # Drupal
        if 'var Drupal = Drupal' in soup.get_text():
            return found(DRUPAL)

        # Sitecore
        sitecore_content_path = 'sitecore/content/'
        sitecore_util_path = 'http://www.sitecore.net/webutil'
        if sitecore_content_path in soup.get_text() or sitecore_util_path in soup.get_text():
            return found(SITECORE)

        # Wordpress url in any href or src
        if soup.find_all(href=re.compile('wp-content', re.IGNORECASE))
                or soup.find_all(href=re.compile('wp-include', re.IGNORECASE)):
            return found(WORDPRESS)

        # Type3 in script source
        if soup.find_all('script', src=re.compile('typo3', re.IGNORECASE)):
            return found(TYPO3)

        # Joomla in script source
        if soup.find_all('script', src=re.compile('joomla', re.IGNORECASE)):
            return found(JOOMLA)

        # DotNetNuke in script source
        if soup.find_all('script', src=re.compile('(dnn\\.js|dnncore\\.js)', re.IGNORECASE)):
            return found(DOTNETNUKE)

        # SharePoint in script source
        if soup.find_all('script', src=re.compile('(core\\.js|msstring\\.js)', re.IGNORECASE)):
            return found(SHAREPOINT)

        comments = soup.find_all(text=lambda text: isinstance(text, Comment))

        # Check for Typo3 in comment text
        txt = ['This website is powered by TYPO3',
               'TYPO3 is a free open source Content Management Framework']
        if any(txt[0].lower() in x.lower() or txt[1].lower() in x.lower() for x in comments):
            return found(TYPO3)

        # Meta tags
        # PHP-Nuke
        if soup.find_all('meta', attrs={
                'name': re.compile('generator', re.IGNORECASE), 
                'content': re.compile('PHP-Nuke', re.IGNORECASE)}):
            return found(PHPNUKE)

        # EpiServer
        if soup.find_all('meta', attrs={
                'name': re.compile('generator', re.IGNORECASE), 
                'content': re.compile('episerver', re.IGNORECASE)}):
            return found(EPISERVER)

        # SharePoint
        if soup.find_all('meta', attrs={
                'name': re.compile('generator', re.IGNORECASE), 
                'content': re.compile('microsoft sharepoint', re.IGNORECASE)}):
            return found(SHAREPOINT)

        # Dynamic web
        if soup.find_all('meta', attrs={
                'name': re.compile('generator', re.IGNORECASE), 
                'content': re.compile('dynamicweb', re.IGNORECASE)}):
            return found(DYNAMICWEB)

    except Exception as e:
        print 'Exception: ', e
        print 'site: ', website.url
        if hasattr(e, 'read'):
            print e.read()

    return found(UNKNOWN)
