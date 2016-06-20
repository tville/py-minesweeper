# P-Uppgift: Minröjning
# Jerker Ersare
# 2015-09-07
#
# Denna fil definierar klasser som hanterar datastrukturen kring kartan

import Shared
import Config
from random import randint


class CellData:
    """ En klass som representerar en ruta (datatypen, inte grafiskt). """
    
    def __init__(self, x, y):
        """ Skapar en ny cell. 
        param x: Cellens X-koordinat.
        param y: Cellens Y-koordinat.
        """        
        # Det blir viss redundans att lagra dessa både här och i kartans dictionary men 
        # det underlättar. 
        self.x = x
        self.y = y
        
        # Flaggor för olika lägen cellen kan vara i
        self.is_unknown = True;
        self.is_mine = False;
        self.is_flagged = False;
        
        # Antal närliggande minor (används om detta ej är en mina)
        self.nearby_mines = 0;        


class MapData:
    """ En klass som representerar kartans information. Varje ruta/cell på kartan representeras
    av ett CellData-objekt. Dessa lagras i en dictionary med en x, y-tupel som nyckel.
    """    
    
    def __init__(self, map_size, level):
        """ Skapar en karta med given storlek och svårighetsgrad. 
        param map_size:  Storlek, anges som ett MapSize-objekt.
        param level:  Svårighetsgrad, anges som ett Level-objekt.
        """        
        # Map size innehåller dels bredd och höjd, dels maxtid (för att få poäng) för kartan
        self.size = map_size                 
        # Spelet börjar i läget NORMAL, dvs man har ej vunnit eller förlorat än
        self.state = Shared.GameState.NORMAL
        
        # Initiera celler        
        self.cells = {}
        for x in range(0, self.size.width):            
            for y in range(0, self.size.height):
                self.cells[(x, y)] = CellData(x, y)
                
        # Räkna ut antal minor (procent av antal rutor)
        if (Config.QUICK_TEST):
            mines = 2
        else:
            mines = (self.size.width * self.size.height) * (level.mines_rate / 100)
            
        # Placera ut minor 
        mines_placed = 0
        while mines_placed < mines:
            # Slumpa position
            mine_x = randint(0, self.size.width - 1)
            mine_y = randint(0, self.size.height - 1)
            
            # Fortsätt bara om det inte är en mina redan;
            if not self.cells[(mine_x, mine_y)].is_mine:
                self.cells[(mine_x, mine_y)].is_mine = True
                mines_placed += 1
                
                # Öka siffrorna hos angränsande celler                
                self.increase_adjacent(mine_x, mine_y)
            
                      
    def get_neighbors(self, x, y):
        """ Returnerar närliggande celler (normalt 8 st såvida ej vid en kant eller ett hörn).
        param x: X-koordinat.
        param y: Y-koordinat.
        returns:  En lista med närliggande celler.
        """
        neighbors = []
        for x_offset in [-1, 0, 1]:
            for y_offset in [-1, 0, 1]:
                # Kolla så koordinaterna inte hamnar utanför kartan. Returnera ej cellen vid x, y.            
                if (x + x_offset, y + y_offset) in self.cells \
                        and not (x_offset == 0 and y_offset == 0): 
                    neighbors.append(self.cells[(x + x_offset, y + y_offset)])
        return neighbors
                            
    def increase_adjacent(self, mine_x, mine_y):
        """ Ökar siffrorna i angränsande celler. Anropas efter att en mina lagts till.
        param mine_x:  X-koordinat för den nya minan.
        param mine_y:  Y-koordinat för den nya minan.
        """
        for neighbor in self.get_neighbors(mine_x, mine_y):
            if not neighbor.is_mine:
                neighbor.nearby_mines += 1

    def sweep(self, x, y):
        """ Försöker röja cellen vid x, y. Leder till sprängning eller röjning, där det senare
        också innebär att man kan ha vunnit.
        param x: X-koordinat.
        param y: Y-koordinat.
        returns:  Rundans nya status, i form av ett GameStatus-värde.
        """
        # Ändra status till visad
        self.cells[(x, y)].is_unknown = False
        # Ta bort ev flaggstatus, en flagga vid röjt område gör ändå ingen nytta
        self.cells[(x, y)].is_flagged = False
        
        # Kolla om man har klickat på ett tomt område så att fler celler ska svepas rekursivt
        if not self.cells[(x, y)].is_mine and self.cells[(x, y)].nearby_mines == 0:
            self.sweep_recursively(x, y)
            
        # Returnera status
        if self.cells[(x, y)].is_mine:
            self.state = Shared.GameState.LOST
        elif self.check_sweep_win() or self.check_flag_win():
            self.state = Shared.GameState.WON                
        else:
            self.state = Shared.GameState.NORMAL                       
        return self.state
        
    def sweep_recursively(self, x, y):
        """ Används när man har röjt en tom cell (med nearby_mines == 0) och alla närliggande 
        tomma celler ska röjas.
        param x: X-koordinat för nuvarande cell.
        param y: Y-koordinat för nuvarande cell.
        """        
        # Cellen som metoden har kallats på kan alltid röjas.        
        self.cells[(x, y)].is_unknown = False
        self.cells[(x, y)].is_flagged = False
            
        # ...men röj bara grannar om detta är en nolla
        if self.cells[(x, y)].nearby_mines == 0:                        
            for neighbor in self.get_neighbors(x, y):
                # Kör detta rekursivt på ej röjda grannar
                if neighbor.is_unknown:                    
                    self.sweep_recursively(neighbor.x, neighbor.y)
                
    def check_sweep_win(self):
        """ Hjälpmetod för att kolla om man vunnit genom vanlig röjning - enklast formulerar vi det
        som att man INTE vunnit så länge det finns minst en okänd ruta kvar som inte är en mina 
        returns:  Boolean motsvarande frågeställningen.
        """        
        for xy in self.cells:
            if self.cells[xy].is_unknown and not self.cells[xy].is_mine:
                return False
        return True
    
    def check_flag_win(self):
        """ Hjälpmetod för att kolla om man vunnit genom att flagga alla (och endast) minor.
        Precis som i metoden check_sweep_win är det enkelt att kolla om man inte vunnit än.
        returns:  Boolean motsvarande frågeställningen. 
        """
        for xy in self.cells:
            # Om det finns en oflaggad mina, returnera false
            if self.cells[xy].is_mine and not self.cells[xy].is_flagged:
                return False         
            
            # Om det finns en flagga utan en mina under, returnera false
            if self.cells[xy].is_flagged and not self.cells[xy].is_mine:
                return False         
        # Annars har man flaggat alla (och endast) minor, dvs vunnit rundan.
        return True
    
    def flag(self, x, y):
        """ Växlar status för om cellen är flaggad eller inte. 
        returns:  Rundans nya status, i form av ett GameStatus-värde.
        """
        self.cells[(x, y)].is_flagged = not self.cells[(x, y)].is_flagged
        
        # Kolla om man vunnit genom att flagga alla
        if self.check_flag_win():
            self.state = Shared.GameState.WON                
        else:
            self.state = Shared.GameState.NORMAL
        return self.state
        