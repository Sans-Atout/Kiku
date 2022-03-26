from sniffer.sniffer_base import getSniffer
from configparser import ConfigParser
from python_tracer.Logger import VerboseLevel,Logger
from datetime import datetime, timezone, timedelta
from time import mktime
from dateutil.relativedelta import relativedelta
import dateparser

# ignore warnings from the dateparser library
import warnings
warnings.filterwarnings(
    "ignore",
    message="The localize method is no longer necessary, as this time zone supports the fold attribute",
)


# url template
base = "https://www.manga-sanctuary.com/planning/?&pays_edition=%5B77%5D&deb="
datetime_string_converter = "%d %b %Y"

# initialization of logs
config = ConfigParser()
config.read("kiku.ini")
log_level       = int(config.get("log", "prod_env"))
log_path        = config.get("log", "path")
log_extension   = config.get("log", "extension")

log = Logger(log_path,log_level,service_name="manga-sanctuary", log_extension=log_extension)

def getMSNewManga():
    """
        Function that retrieves all the manga releases from the manga-sanctuary
        website for the following month and returns them as a JSON table
        (param) null
    """
    # Récupération des données
    log.info("Récupération du temps Unix pour le moi suivant")
    tzinfo = timezone(timedelta(hours=+1))
    dt = datetime.now(tzinfo).replace(hour=0, minute=0,second=0,day=1) + relativedelta(months=1)
    unixTime = int(mktime(dt.timetuple()))
    log.done("the unix time is : %s " % unixTime)
    # Recrustruction de l'url
    log.info("récupération des données sur manga sanctuary")
    url = base + str(unixTime)
    result, status, sniffer = getSniffer(url,30,60,10)

    if result:
        log.done("the response status is "+str(status))
        sorties = sniffer.find("div", id = "liste-sorties")
        _allManga = getAllMangaAsJSON(sorties.find_all("div"))
        log.info("We found %s manga for the month %s." % (len(_allManga),dt.month))
    else:
        log.error("the response status is "+str(status))
    #return url

def getAllMangaAsJSON(all_sortie):
    """
        Retrieves all the manga outputs displayed in the page retrieved on
        manga-sanctuary.
        (param) all_sortie: a div with id "liste-sortie". This div is
                            the main div in which the schedule of the releases
        (return) all_manga: an array containing manga in JSON format
    """
    publicationDate = ""
    _allManga = []
    for ligne in all_sortie:
        # Récupération de la date de sortie
        if "sortie-date" in str(ligne["class"]):
            publicationDate = dateparser.parse(ligne.text).date()
        # Récupération des sorties
        if "sorties-liste" in str(ligne["class"]):
            img = ligne.find("img").src
            editeur = ligne.find("a",class_="sortie-editeur").text
            type = ligne.find("span",class_="type-fiche").text
            serie,number = getSerieAndNumber(ligne.find("h2",class_="post-title").text)
            mangaInfo = { "date" : publicationDate,"type":type,"editeur" : editeur}
            mangaInfo["serie"] = serie
            mangaInfo["number"] = number
            try:
                prix = str(ligne.find("span",class_="btn-primary").find("span").find("span").text)
                prix = float(prix[:len(prix)-1].replace(",",'.'))
                prix = None if prix == 0.0 else prix
                mangaInfo["prix"] = prix
            except Exception as e:
                mangaInfo["prix"] = None
            _allManga.append(mangaInfo)

    return _allManga

def getSerieAndNumber(base):
    """
        Function that from a manga name with the volume number returns the name
        of the series and its volume number. In the case where no number is
        available then the value -1 is returned.
        (param) base    :   a line containing the name of the series and its
                            volume number
        (return) number :   the number of the volume in the series
        (return) serie  :   the name of the manga series
    """
    array = base[:len(base)-1].split(" ")
    serie = ""
    for id in range(len(array)-1):
        serie = serie +" "+array[id]
    serie = serie[1:]
    number = -1
    try:
        number = int(array[len(array)-1])
    except Exception as e:
        pass

    return serie,number
getMSNewManga()
