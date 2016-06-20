# P-Uppgift: Minröjning
# Jerker Ersare
# 2015-09-07
#
# Denna fil innehåller allt relaterat till det grafiska interfacet (förutom high score-listan).
from Shared import GameState

HELP = "You can use the S and F keys to switch between the Sweep and Flag modes.\n\n" \
        "Legend:\n:(\t\tExploded mine\nX\t\tMine\nGreen \"F\"\t\tCorrectly flagged mine\n" \
        "Red \"F\"\t\tFalse flag"
BUTTON_WIDTH = 25
BUTTON_HEIGHT = 25

import Config
import Shared
from MineSweeper import MineSweeper
from MapDataStructure import MapData
from HighScore import HighScoreManager

from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import showinfo, askokcancel


class GUI:
    """ Denna klass hanterar spelets huvudfönster. """
    def __init__(self, map_data, ms_round):
        """ Initierar huvudfönstret. 
        param map_data:  MapData-objekt vars information kommer att representeras grafiskt.
        param ms_round:  Aktuell spelomgång (objekt av klassen MineSweeper).
        """
        self.ms_round = ms_round
        self.map_data = map_data
        self.hsm = HighScoreManager()
        
        # Skapa fönster
        self.gui = Tk()        
        self.gui.title("MineSweeper")               
            
        # Radiobuttons för val av röjverktyg / flaggverktyg, grupperade i en frame
        self.button_frame = Frame(self.gui)       
        self.button_frame.grid(row = 0, column = 0, sticky = W, padx = 5, pady = 5)
        self.selected_tool = StringVar()
        self.selected_tool.set("sweep")
        # Sweep
        self.sweep_button = Radiobutton(self.button_frame, text = "Sweep", value = "sweep",
                variable = self.selected_tool, underline = 0)
        self.gui.bind_all("s", lambda e : self.selected_tool.set("sweep"))        
        self.sweep_button.pack(side = LEFT)
        # Flag 
        self.flag_button = Radiobutton(self.button_frame, text = "Flag", value = "flag",
                variable = self.selected_tool, underline = 0)
        self.gui.bind_all("f", lambda e : self.selected_tool.set("flag"))        
        self.flag_button.pack(side = LEFT, padx = 8)
    
        # Spelplanen är en map_component, ett rutnät av knappar
        self.gui.columnconfigure(0, weight = 1)
        self.gui.rowconfigure(1, weight = 1)
        self.map_component = MapComponent(self.gui, self, map_data, ms_round)                        
        
        # Lägg till menyrad
        self.build_menus()
                                        
        self.gui.mainloop()        
        
    
    def build_menus(self):
        """ Hjälpmetod för att sätta ihop och lägga till menyraden """
        self.menubar = Menu(self.gui)
        self.gui.config(menu = self.menubar)
        
        # Menyn "Game"
        self.game_menu = Menu(self.menubar, tearoff = 0)
        self.menubar.add_cascade(label = "Game", menu = self.game_menu)
        self.game_menu.add_command(label = "New game", command = self.new_game, accelerator = "F2")
        self.gui.bind_all("<F2>", self.new_game)        
        self.game_menu.add_command(label = "Show high score", command = self.hsm.show_hsw, 
                accelerator = "F3")
        self.gui.bind_all("<F3>", self.hsm.show_hsw)
        self.game_menu.add_command(label = "Help", command = self.show_help, 
                accelerator = "F1")
        self.gui.bind_all("<F1>", self.show_help)
        self.game_menu.add_command(label = "Quit", command = self.gui.quit, accelerator = "Alt+F4")
        self.gui.bind_all("<Alt-F4>", lambda event : self.gui.quit())           
           
        # Storleksmeny. Metoden change_size anropas vid ändring. Denna och menyn nedan använder en
        # IntVar som representerar index i listorna av möjliga alternativ definierade i Config.
        self.size_menu = Menu(self.menubar, tearoff = 0)
        self.menubar.add_cascade(label = "Size", menu = self.size_menu)
        self.selected_size = IntVar()
        self.selected_size.set(1)
        self.selected_size.trace('w', self.change_size)
        for i, size in enumerate(Config.MAP_SIZES):
            self.size_menu.add_radiobutton(label = size.name, value = i, 
                    variable = self.selected_size)        

        # Nivåmeny. Metoden change_level anropas vid ändring.
        self.level_menu = Menu(self.menubar, tearoff = 0)
        self.menubar.add_cascade(label = "Level", menu = self.level_menu)                
        self.selected_level = IntVar()
        self.selected_level.set(1)
        self.selected_level.trace('w', self.change_level)
        for i, level in enumerate(Config.GAME_LEVELS):
            self.level_menu.add_radiobutton(label = level.name, value = i,
                    variable = self.selected_level)
            
    def change_size(self, *bundle):
        """ Anropas när man byter storlek i menyn. Startar en ny runda efter storleksbyte.
        param *bundle: Flera variabler skickas vid trace av IntVar, används ej.
        """
        if not self.map_data.size == Config.MAP_SIZES[self.selected_size.get()]:
            # Visa bara dialogrutan om inte spelrundan är slut (LOST eller WON)
            if self.map_data.state == GameState.LOST or self.map_data.state == GameState.WON or \
                    askokcancel("Change Size?", "This will abort your current game! Continue?"):                    
                self.new_game(map_size = Config.MAP_SIZES[self.selected_size.get()])
       
    def change_level(self, *bundle):
        """ Anropas när man byter nivå i menyn. Startar en ny runda efter nivåbyte. 
        param *bundle: Skickas vid trace av IntVar, används ej.
        """
        if not self.ms_round.level == Config.GAME_LEVELS[self.selected_level.get()]:
            if self.map_data.state == GameState.LOST or self.map_data.state == GameState.WON or \
                    askokcancel("Change Level?", "This will abort your current game! Continue?"):
                self.new_game(game_level = Config.GAME_LEVELS[self.selected_level.get()]) 
    
    def new_game(self, event = None, map_size = None, game_level = None):
        """ Starta en ny runda. Anropas av alternativet New Game eller när storlek eller nivå ändras. 
        param event:  Skickas vid menyval, används ej.
        param map_size:  Kartstorlek för nästa runda, i form av ett MapSize-objekt.
        param game_level:  Svårighetsgrad för nästa runda, Level-objekt.
        """
        # Hämta valda inställningar om ej angivet i funktionsanropet
        if not map_size:
            map_size = Config.MAP_SIZES[self.selected_size.get()]
        if not game_level:
            game_level = Config.GAME_LEVELS[self.selected_level.get()]
        
        # Initiera karta och runda med rätt storlek och nivå
        self.map_data = MapData(map_size, game_level)        
        self.ms_round = MineSweeper(self.map_data, game_level)
        
        # Bygg ny kartkomponent för denna karta och runda. 
        # Den gamla måste tas bort den gamla för korrekt storleksuppdatering om den nya är mindre.
        self.map_component.panel.grid_remove()
        self.map_component = MapComponent(self.gui, self, self.map_data, self.ms_round)        
    
    def show_help(self, event = None):
        """ Visar en dialogruta med en kort hjälptext. """
        showinfo("Help", HELP)
        
class MapComponent:
    """ Denna klass hanterar visningen av minfältet och interagerar med den underliggande
    datastrukturen som har implementerats i klasserna MapData och CellData. 
    """    
    def __init__(self, master, gui, map_data, ms_round):
        """ Konstruktor.
        param master:  Förälderkomponent.
        param gui:  Instansen av klassen GUI (som representerar huvudfönstret).
        param map_data:  MapData-objekt vars information renderas av MapComponent.
        param ms_round:  MineSweeper-objekt, information om nuvarande runda.
        """
        self.map_data = map_data
        self.ms_round = ms_round
        self.gui = gui
        
        # Konfigurera utseende
        Style().map("TButton", background=[("disabled", "gray"), ("!disabled", "white")])
        Style().map("Red.TButton", foreground = [("disabled", "red")])
        Style().configure("Red.TButton", foreground = "red")
        Style().map("Green.TButton", foreground = [("disabled", "green")])
        Style().configure("Green.TButton", foreground = "green")
        
        # Panel för knappar
        self.panel = Frame(master)
        # Lägg till denna i master. Detta ansvar kanske borde ligga i den användande klassen,
        # men här tyckte jag det var smidigt att den lägger till sej själv.
        self.panel.grid(column = 0, row = 1, columnspan = 2, sticky = (N, E, S, W))
        self.panel.columnconfigure(0, weight = 1)
        self.panel.rowconfigure(0, weight = 1)                
        self.panel.master.minsize(BUTTON_WIDTH * map_data.size.width, 
                BUTTON_HEIGHT * map_data.size.height)
        
        # Skapa alla knappar
        self.buttons = {}                
        for xy in map_data.cells:
            # x och y är kombinerade till en tupel som är nyckel i map_data.cells
            # för tydlighet använder jag temporära variabler här
            x, y = xy

            # Default values krävs för att anropet ska ha rätt värden för x och y
            self.buttons[xy] = Button(self.panel, style = "TButton", width = 1, 
                                      command = (lambda x2 = x, y2 = y: self.cell_click(x2, y2)))
            
            # Konfigurera grid layout
            self.buttons[xy].grid(column = x, row = y, sticky = (N, E, S, W))
            Grid.columnconfigure(self.panel, index = x, weight = 1)
            Grid.rowconfigure(self.panel, index = y, weight = 1)        
        
            if Config.CHEAT: 
                self.show_all_info(xy)
            
    def show_all_info(self, xy):
        """ Används i fuskläget - Visar info för en oröjd cell.
        param xy:  Tupel med koordinater för vald cell. 
        """            
        if self.map_data.cells[xy].is_mine:
            self.buttons[xy].config(text = str("X"))
        elif self.map_data.cells[xy].nearby_mines > 0:
            self.buttons[xy].config(text = str(self.map_data.cells[xy].nearby_mines))
                    
    def cell_click(self, x, y):
        """ Röj eller flagga, beroede på valt verktyg, (self.gui.selected_tool (StringVar) sätts av 
        fönstrets radiobuttons).        
        param x:  X-koordinat för vald cell.
        param y:  Y-koordinat för vald cell. 
        """        
        # Om vi vet sedan tidigare att spelomgången är slut, gör inget
        if not (self.map_data.state == Shared.GameState.LOST or self.map_data.state == Shared.GameState.WON):             
            state = self.map_data.state
            if self.gui.selected_tool.get() == "sweep":
                # Anropa sweep på den underliggande datastrukturen
                state = self.map_data.sweep(x, y)
            
            else:
                # Flagga
                state = self.map_data.flag(x, y)        
                
            # Uppdatera alla knappar nu när kartan är ändrad
            self.update_buttons(x, y, state)
                
            # Om man har vunnit efter detta drag, uppdatera ev highscore
            if (self.map_data.state == Shared.GameState.WON):                
                self.gui.hsm.win_round(self.ms_round.get_score())
        
    def update_buttons(self, last_x = None, last_y = None, state = None):
        """ Uppdaterar alla knappar till att reflektera läget i varje cell.
        param last_x:  X-koordinat för senast klickade knapp.
        param last_y:  Y-koordinat för senast klickade knapp.
        param state:  Spelets nuvarande status, en av möjliga konstanter i GameState. 
        """                                              
        for xy in self.map_data.cells:                
            # Text för ej röjda celler, dvs knappar som fortfarande är "enabled":
            # "F", fuskinfo eller ingenting.
            if self.map_data.cells[xy].is_flagged:
                self.buttons[xy].config(text = "F")
            elif Config.CHEAT:
                # Om fuskläge, skriv ut alla siffror och X
                self.show_all_info(xy)
            else:
                self.buttons[xy].config(text = "")                       
                    
            # Om inte längre okänd - sätt till disabled
            if (not self.map_data.cells[xy].is_unknown):          
                self.buttons[xy].config(state = DISABLED)
            
                # Visa siffra om ej mina
                if not self.map_data.cells[xy].is_mine and self.map_data.cells[xy].nearby_mines > 0:
                    self.buttons[xy].config(text = str(self.map_data.cells[xy].nearby_mines))             
                
            # Om spelet slut, ändra färger på flaggorna
            if state == Shared.GameState.LOST or state == Shared.GameState.WON:
                # Om flaggad mina, gör flaggan grön eftersom den var rätt
                if self.map_data.cells[xy].is_mine and self.map_data.cells[xy].is_flagged:
                    self.buttons[xy].config(style = "Green.TButton")
                        
                # Om flaggad men ej mina, gör flaggan röd
                if self.map_data.cells[xy].is_flagged and not self.map_data.cells[xy].is_mine:                    
                    self.buttons[xy].config(text = "F", style = "Red.TButton")                
            
            # Om man förlorade, visa alla minor     
            if state == Shared.GameState.LOST:
                # Visa ej flaggade minor som X
                if self.map_data.cells[xy].is_mine and not self.map_data.cells[xy].is_flagged:
                    self.buttons[xy].config(text = "X")

                # Senast klickade ruta och man förlorade = sprängd mina
                if xy[0] == last_x and xy[1] == last_y:                                         
                    self.buttons[xy].config(text = ":(", style = "Red.TButton")           
                
                