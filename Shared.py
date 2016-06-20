# P-Uppgift: Minröjning
# Jerker Ersare
# 2015-09-07
#
# Denna fil samlar klasser som behövs av flera andra filer. 
# Lägger dem här för att undvika circular dependencies.


class MapSize():
    """ Denna klass används för kartstorlekar. """ 
    def __init__(self, name, width, height, max_time):
        """ Konstruktor. 
        param name:  Storleksklassens namn.
        param width:  Bredd i antal celler.
        param height:  Höjd i antal celler.
        param max_time:  Tid i minuter som måste understigas för att man ska få några poäng
                när man har vunnit.
        """
        self.name = name
        self.width = width
        self.height = height
        self.max_time = max_time

class Level():
    """ Används för svårighetsnivåer. """
    def __init__(self, name, mines_rate, score_multi):
        """ Konstruktor. 
        param name:  Svårighetsgradens namn.
        param mines_rate:  Andel minor, anges i %.
        param score_multi: "Multiplier" som avgör hur många poäng man får för varje kvarvarande
                sekund av rundan om man vinner. 
        """
        self.name = name
        self.mines_rate = mines_rate
        self.score_multi = score_multi

class GameState():
    """ Används för att veta spelets status efter varje drag. """
    NORMAL = 0
    WON = 1
    LOST = 2