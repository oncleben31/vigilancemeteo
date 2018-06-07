# coding: utf-8


class SurveillancePluie1h(object):
    """Une class pour avoir les prévisions de pluie dans l'heure.
    """
    URL_API_PLUIE1H = "http://www.meteofrance.com/mf3-rpc-portlet/rest/pluie/"
    URL_API_CHERCHE_ID_VILLE = ""
    # Auradé: 320160

    def __init__(self, idVille):
        """Constructeur de la classe.

        Prend en entrée l'ID de la ville.
        """
        # TODO: ajouter comment on trouve l'ID de la ville.
        self.idVille = idVille
        self._datePrevision = None
        self._previsionTexte = None
        self._tableauPluie1h = None

    def miseAJourPrevision(self):
        """Mise à jour de la prévision."""

    def __repr__(self):
        """Representation de l'instance."""

    @property
    def idVille(self):
        """Accesseur à l'attribut idVille"""

    @idVille.setter
    def idVille(self, idVille):
        """Setter avec vérification du format de l'entrée"""

    @property
    def datePrevision(self):
        """Proporiété pour accéder à la date de mise à jour de la prévision."""

    @property
    def previsionTexte(self):
        """Propriété pour accéder à la prévision en version texte."""

    @property
    def heureDeLaProchainePluie(self):
        """Donne l'heure du début de la prochaine pluie."""


def chercheIdVille(nomVille):
    """Helper pour chercher l'ID d'une ville à partir du nom de la commune"""
