# coding: utf-8
from lxml import etree
import datetime


class ZoneAlerte(object):
    """Une classe pour décrire les alertes météo d'un département Français.

    Les informations sont récupérée du site vigilance.meteofrance.com.

    L'objet ZoneAlerte est définit par les attributs:
    - _departement : le département surveillé
    - _dateMiseAJour : la date et l'heure de mise à jour de la prévision par
                       MétéoFrance
    - _listeAlertes : le dictionnaire comportant les alertes. L'indice du
                      dictionnaire correspond au type de l'alerte et la valeur
                      associée à la gravité de l'alerte représenté par une
                      couleur.

    La méthode suivante est disponibles:
    - miseAJourEtat() : pour mettre à jour la liste des alertes en prenant la
                        dernière prévision de MétéoFrance

    Les propriétés suivantes sont disponibles:
    - syntheseCouleur : retourne la couleur correspondant à la criticité
                        maximum du département
    - urlPourEnSavoirPlus : retourne l'URL correspondant à la page web
                            détaillant les alertes en cours dans le département
    - messageDeSynthese : retourne une chaine de caractère faisant la synthèse
                          des alertes en cours dans le département.

    Exemple:
    >>>import vigilancemeteo
    >>>zone = vigilancemeteo.ZoneAlerte('92')
    >>>zone.syntheseCouleur
    'Vert'
    >>>zone.urlPourEnSavoirPlus
    'http://vigilance.meteofrance.com/Bulletin_sans.html?a=dept75&b=1&c='
    >>>zone.messageDeSynthese
    'Aucune alerte en cours.'
    """
    # TODO: Définir comportement si problème d'accès au réseau
    # TODO: Vérfier les problèmatique d'encodate.

    # enums utilisées par cette classe. Attention premier indice est 0
    LISTE_COULEUR_ALERTE = ['Vert', 'Jaune', 'Orange', 'Rouge']
    LISTE_TYPE_ALERTE = ['Vent violent', 'Pluie-innodation', 'Orages',
                         'Inondation', 'Neige-verglas', 'Canicule',
                         'Grand-froid', 'Avalanches', 'Vagues-submersion']
    LISTE_DEPARTEMENT_LITTORAL = [
        '06', '11', '13', '14', '17', '22', '29', '2A', '2B', '30', '33', '34',
        '35', '40', '44', '50', '56', '59', '62', '64', '66', '76', '80', '83',
        '85']
    LISTE_DEPARTEMENT_VALIDE = [
        '01', '02', '03', '04', '05', '06', '07', '08', '09',
        '10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
        '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '2A', '2B',
        '30', '31', '32', '33', '34', '35', '36', '37', '38', '39',
        '40', '41', '42', '43', '44', '45', '46', '47', '48', '49',
        '50', '51', '52', '53', '54', '55', '56', '57', '58', '59',
        '60', '61', '62', '63', '64', '65', '66', '67', '68', '69',
        '70', '71', '72', '73', '74', '75', '76', '77', '78', '79',
        '80', '81', '82', '83', '84', '85', '86', '87', '88', '89',
        '90', '91', '92', '93', '94', '95', '99']

    # URL utilisée pour récupérer les informations sur le site de Météo France
    URL_VIGILANCE_METEO = "http://vigilance.meteofrance.com"\
                          "/data/NXFR33_LFPW_.xml"
    # URL_VIGILANCE_METEO = "./tests/NXFR33_LFPW_.xml"

    def __init__(self, departement):
        """Constructeur de la classe.

        Prend le département en paramètre sous forme du chaine de caractère
        sur deux caractères. Peut prendre les valeurs de 01 à 95, 2A, 2B
        et 99 (pour Andorre).
        """

        # Initialisation des attributs
        self._dateMiseAJour = None
        self._listeAlertes = {}

        # Validation de l'attribut _departement via la propriété.
        # Attention le setter lance automatiquement la méthode miseAJourEtat()
        self.departement = departement

    def miseAJourEtat(self):
        """Récupère les alertes météo en cours pour le département.

        Récupère la couleur de l'alerte pour les 9 types de vigilance sur le
        site de météofrance et met à jour l'attribut 'listeAlertes'.
        Récupère la date et l'heure de mise à jour du buletin sur le site de
        météofrance et met à jour l'attribut '_dateMiseAJour'.
        """

        # vide la liste des alertes
        self._listeAlertes = {}

        # Récupère les information sur le site de météofrance
        tree = etree.parse(ZoneAlerte.URL_VIGILANCE_METEO)

        # Récupère les alertes pour un département donné
        alertesStandards = tree.xpath("/CV/DV[attribute::dep='" +
                                      self._departement + "']")
        # Ajout des alertes supplémentaires pour les département du littoral
        if self._departement in ZoneAlerte.LISTE_DEPARTEMENT_LITTORAL:
            alertesStandards.extend(tree.xpath("/CV/DV[attribute::dep='" +
                                    self._departement + "10']"))

        # Récupère les alertes du département.
        # Elles sont regroupées par niveau (couleur)
        for alertesDuDepartement in alertesStandards:
            # On récupère la couleur du groupe d'alertes
            couleur = int(alertesDuDepartement.get('coul'))

            # Récupère la liste des alertes en cours dans le département pour
            # ce niveau d'alerte (couleur)
            for risque in list(alertesDuDepartement):
                type = int(risque.get('val'))
                # On met à jour la liste des alertes du département.
                self._miseAJourAlerte(ZoneAlerte.LISTE_TYPE_ALERTE[type - 1],
                                      ZoneAlerte.LISTE_COULEUR_ALERTE[couleur
                                                                      - 1])

        # Recupere la date de mise a jour de la prévision
        elementDate = tree.xpath("/CV/EV")
        stringDate = elementDate[0].get('dateinsert')

        # On la converti en date et heure
        annee = int(stringDate[0:4])
        mois = int(stringDate[4:6])
        jour = int(stringDate[6:8])
        heure = int(stringDate[8:10])
        minute = int(stringDate[10:12])
        seconde = int(stringDate[12:14])
        self._dateMiseAJour = datetime.datetime(annee, mois, jour, heure,
                                                minute, seconde)

    def _miseAJourAlerte(self, type, couleur):
        """Met à jour un type d'alerte."""
        self._listeAlertes[type] = couleur

    def __repr__(self):
        """"Représenation de l'instance"""
        # Tri des clés du dictionnaires car avant python 3.6 elles ne sont
        # pas ordonnées
        listeAlertesOrdonnee = ""
        for key in sorted(self.listeAlertes.keys()):
            listeAlertesOrdonnee = listeAlertesOrdonnee +\
                                  "'{}': '{}', ".\
                                  format(key, self.listeAlertes[key])
        return "ZoneAlerte: \n - departement: '{}'\n - dateMiseAJour: '{}'"\
               "\n - listeAlertes: {{{}}}".format(self._departement,
                                                  self._dateMiseAJour,
                                                  listeAlertesOrdonnee[:-2])

    @property
    def syntheseCouleur(self):
        """Retourne la couleur du département.

        Elle correspond à la couleur de l'alerte la plus critique.
        """
        if any(alerte == 'Rouge' for alerte in self.listeAlertes.values()):
            synthese = 'Rouge'
        elif any(alerte == 'Orange' for alerte in self.listeAlertes.values()):
            synthese = 'Orange'
        elif any(alerte == 'Jaune' for alerte in self.listeAlertes.values()):
            synthese = 'Jaune'
        else:
            synthese = 'Vert'
        return synthese

    @property
    def urlPourEnSavoirPlus(self):
        """Pour en savoir plus sur les alertes du département.

        Retourne l'url du site vigilance.meteofrance.com pour connaitre le
        détail des alertes en cours dans le departement.
        """
        return "http://vigilance.meteofrance.com/"\
               "Bulletin_sans.html?a=dept{}&b=1&c=".format(self._departement)

    @property
    def messageDeSynthese(self):
        """Message expliquant la liste des alertes en cours du département."""
        if self.syntheseCouleur == 'Vert':
            message = "Aucune alerte en cours."
        else:
            message = "Alerte {} en cours :".format(self.syntheseCouleur)
            # Tri des clés du dictionnaires car avant python 3.6 elles ne sont
            # pas ordonnées
            for type in sorted(self.listeAlertes.keys()):
                message = message + "\n - {}: {}"\
                          .format(type, self.listeAlertes[type])

        return message

    @property
    def dateMiseAJour(self):
        return self._dateMiseAJour

    @property
    def listeAlertes(self):
        return self._listeAlertes

    @property
    def departement(self):
        return self._departement

    @departement.setter
    def departement(self, departement):
        """Setter avec vérification de la valeur 'departement'.

        Il faut rentrer le département sous forme de chaine de 2 caractères.
        Dans le fichier XML source, les départements 92, 93 et 94 n'existent
        pas. Dans ce cas, il faut utiliser le département 75 à la place.
        Le setter lance la méthode miseAJourEtat() de manière systématique.
        """
        # Vérfie les valeurs valide pour departement
        if departement not in ZoneAlerte.LISTE_DEPARTEMENT_VALIDE:
            raise ValueError("Le département doit être une chaine de 2 "
                             "caractères compris entre '01' et '95' ou '2A' "
                             "ou '2B' ou '99'")

        # Liste des équivalences
        equivalence75 = ['92', '93', '94']
        departementValide = departement

        # Remplace les départements qui n'existent pas dans le XML par leur
        # équivalence.
        if departement in equivalence75:
            departementValide = '75'

        # Affect l'attribut
        self._departement = departementValide

        # Lance la première mise à jour de l'état
        self.miseAJourEtat()
