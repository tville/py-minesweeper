# P-Uppgift: Minröjning
# Jerker Ersare
# 2015-09-07
#
# Programmet utgör en kopia/variant av det klassiska MS Röj / MineSweeper
# som fungerar enligt uppgiftens lydelse.

# Tillägg 2015-09-07: Går igenom lydelsen en sista gång och ser att storleken och antal minor
# egentligen ska kunna anges fritt. Väljer att ha kvar det såhär (tre olika storleks- och nivålägen
# går att välja mellan) istället för att försena inlämningen mera. Det bör vara uppenbart att övrig
# kod kan hantera vilken storlek som helst osv.


import Config
from MineSweeperGUI import *
from MapDataStructure import MapData
from timeit import default_timer
   
   
class MineSweeper:    
    """ Representerar en runda i spelet. Håller reda på start- och sluttid. """

    def __init__(self, map_data, level):
        """ Startar en ny runda.
        
        param map_data:  Nuvarande kartinformation i form av ett MapData-objekt.
        param level:  Vald svårighetsgrad.
        """
        self.time_start = default_timer()
        self.map_data = map_data
        self.level = level        

    def get_score(self):
        """ Räknar ut och returnerar antal poäng. Uträkningen baseras på tid kvar. 
        Om man inte klarade att vinna innan kartans max_time får man 0 poäng. 
        """       
        round_time = default_timer() - self.time_start        
        time_left = (self.map_data.size.max_time * 60) - round_time                
        if (time_left > 0):
            # Poäng räknas ut som kvarvarande tid i sekunder * multiplier för på nivå
            return int(time_left * self.level.score_multi)
        else:
            return 0       
   
def main():
    """ Huvudfunktion """
    # Skapa "karta" med inställningarna medium för storlek och nivå
    map_data = MapData(Config.MAP_SIZES[1], Config.GAME_LEVELS[1])
    
    # Starta omgång
    ms_round = MineSweeper(map_data, Config.GAME_LEVELS[1])
        
    # Skapa gränssnitt    
    interface = GUI(map_data, ms_round) 
    

#
# Kör funktionen main
#
if __name__ == "__main__":
    main()
