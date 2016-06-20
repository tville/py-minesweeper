# P-Uppgift: Minröjning
# Jerker Ersare
# 2015-09-07
#
# Denna fil innehåller allt relaterat till high score-listan.

import Config
import csv
from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import showinfo

 
class HighScoreManager:
    """ Denna klass hanterar high score-data samt ser till att det som mest finns ett 
    high score-fönster öppet. """
    def __init__(self):
        """ Konstruktor. """
        # hsw står för HighScoreWindow
        self.hsw = None
        csv.register_dialect("custom", delimiter=Config.HIGH_SCORE_DELIMITER, skipinitialspace=True)
        
    def show_hsw(self, event = None):
        """ Visar High Score-fönstret. 
        param event:  Skickas av tk om funktionen anropas via menyn, används ej.
        """
        if not self.hsw:
            self.hsw = HighScoreWindow(self)
            self.hsw.set_list(self.read_file())
    
    def win_round(self, score):
        """ Anropas vid vinst, kollar om poängen platsar på high score-listan. Därefter visas
        i såna fall inmatningsruta för namn, annars bara en kort text om att man vunnit.
        param score:  Antal poäng för den vunna rundan. 
        """
        if self.is_high_score(score):
            NameEntryDialog(self, score, "You won!", "Congratulations, you won! Score: " +
                    str(score) + "\nPlease enter your name for the high score list:")
        else:
            showinfo("You won!", "Congratulations, you won! Score: " + str(score))
    
    def is_high_score(self, score):
        """ Kollar om poängen platsar på topplistan.
        param score:  Antal poäng. 
        returns:  boolean motsvarande frågeställningen. 
        """
        # Läs in nuvarande high score-lista
        hs_list = self.read_file()        
        if len(hs_list) >= 10:
            # Kolla om score är högre än poängen i någon tupel i listan
            return any(score > current_tuple[1] for current_tuple in hs_list)
        else:
            # Listan har färre än 10 element - man kommer med så länge poängen är över 0.
            return score > 0
    
    def read_file(self):
        """ Läser in high score från fil.
        returns:  En lista med high score i form av tupler med namn och poäng. 
        """
        hs_list =  []
        try:
            with open(Config.HIGH_SCORE_FILENAME, "r") as hs_file:
                reader = csv.reader(hs_file, dialect="custom")
                for current_row in reader:
                    # Ignorera tomma rader
                    if current_row: 
                        hs_list.append((current_row[0], int(current_row[1])))
        except FileNotFoundError:
            pass
        return hs_list
    
    def update_high_score(self, score, name):
        """ Lägger till nytt namn-poäng-par i high score-listan. 
        param score:  Poäng för den nya posten.
        param name:  Namn för den nya posten.
        """
        # Läs in nuvarande lista och lägg till ny rad
        hs_list = self.read_file()
        hs_list.append((name, score))
        
        # Sortera listan, fallande. Behåll bara de första 10 tuplerna.
        hs_list.sort(key = lambda hs_tuple : hs_tuple[1], reverse = True)
        hs_list = hs_list[:10]
                    
        # Spara den nya listan
        self.save_file(hs_list)    
    
    def save_file(self, hs_list):
        """ Sparar high score till fil. """
        with open(Config.HIGH_SCORE_FILENAME, "w") as hs_file:            
            writer = csv.writer(hs_file, dialect="custom")
            writer.writerows(hs_list)
    
    def reset_high_score(self):
        """ Nollställer high score. (Skriver tom lista till filen) """        
        self.save_file([]);
    
class NameEntryDialog:
    """ Den här dialogrutan visas när man har kommit med på High Score-listan. Den uppmanar
    användaren att skriva in sitt namn. 
    """
    
    def __init__(self, hsm, score, title, text):
        """ Konstruktor. 
        param hsm:  HighScoreManager-objekt.
        param score:  Antal poäng uppnådda under den vunna rundan.
        param title:  Dialogrutans titel.
        param text:  Dialogrutans text.
        """
        self.hsm = hsm
        self.score = score
        
        # Skapa dialogruta med text och textinmatning
        self.dialog = Toplevel()
        self.dialog.title(title)
        self.dialog.configure(padx = 40, pady = 10)        
        self.label = Label(self.dialog, text = text)
        self.label.pack(pady = 8)
        
        # Textfält. Vid ändringar i textfältet anropas validate_name 
        self.name = StringVar()
        self.name.trace("w", self.validate_name)        
        self.entry = Entry(self.dialog, textvariable = self.name, width = 25)
        self.entry.bind("<Return>", self.submit_name)
        self.entry.pack(pady = 8)
        
        # Grupperar knapparna i en egen gui för enkelhetens skull, vill ha dem sida vid sida i mitten.
        self.button_panel = Frame(self.dialog)
        self.button_panel.pack()        
        self.cancel_button = Button(self.button_panel, text = "Cancel", command = self.dialog.destroy)
        self.cancel_button.pack(pady = 5, padx = 3, side = "left")                
        self.ok_button = Button(self.button_panel, text = "OK", command = self.submit_name, 
                state = "disabled")        
        self.ok_button.pack(pady = 5, padx = 3, side = "right")
    
    def validate_name(self, *bundle):
        """ Anropas vid ändrad text i textfältet. Ser till så att det går att gå vidare bara om
        textfältet innehåller rimlig inmatning. 
        param *bundle:  Flera variabler skickas vid trace, används ej.
        """     
        value = self.name.get()
        
        # Eliminera eventuell förekomst av den delimiter som används när high score lagras till fil
        value = value.replace(Config.HIGH_SCORE_DELIMITER, "")    
        self.name.set(value)
        
        if len(value) == 0 or len(value) > 25:
            self.ok_button.configure(state = "disabled")
        else:
            self.ok_button.configure(state = "enabled")
        
    def submit_name(self, event = NONE):
        """ Skickar namn och poäng till HighScoreManager. Stänger denna dialogruta,
        High Score-fönstret visas. """
        self.hsm.update_high_score(self.score, self.entry.get())             
        self.hsm.show_hsw()   
        self.dialog.destroy()
        

class HighScoreWindow:
    """ Visar high score-fönstret """
    def __init__(self, hsm):
        """ Konstruktor.
        param hsm:  HighScoreManager-objekt.
        """
        self.hsm = hsm 
        self.hs_list = []
        
        # Skapa fönster
        self.window = Toplevel()
        self.window.title("MineSweeper High Scores")
        
        # Bind en metod till stängning av det här fönstret för att hinna registrera att det inte längre finns
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        self.window.bind("<Destroy>", self.close_window)
                               
        # Skapa tree view med kolumner
        Style().configure("Treeview", font=("Helvetica", 20), rowheight = 40)
        Style().configure("Treeview.Heading", font=("Helvetica", 24, "bold"), align = "left" )
        
        self.treeview = Treeview(self.window, style="Treeview", columns = ('Name', 'Score'), 
                show = "headings", height="10")
        self.treeview.pack(side = 'top', fill = 'both', expand = 1)        
        self.treeview.column("Name", minwidth=250)
        self.treeview.column("Score", minwidth=100)
        self.treeview.heading("Name", text = "Name", anchor = W)
        self.treeview.heading("Score", text = "Score", anchor = W)

        # Knapp för att stänga
        self.close_button = Button(self.window, text = 'Close', command=self.close_window)
        self.close_button.pack(side = 'bottom', pady=8)
        self.close_button.focus()
        self.close_button.bind("<Return>", self.close_window)
        
        # Knapp för att nollställa
        self.reset_button = Button(self.window, text = 'Reset', command=self.reset)
        self.reset_button.pack(side = 'bottom', pady=8)
          
        self.window.minsize(370, 500)
        
    def reset(self):
        """ Låter High Score Manager nollställa filen och uppdaterar treeview """
        self.hsm.reset_high_score()
        self.set_list([])
    
    def set_list(self, hs_list):
        """ Uppdaterar Treeview-komponenten med en ny High Score-lista. 
        param hs_list:  En lista med tupler med namn och poäng. 
        """
        self.hs_list = hs_list

        # Töm listan
        for item in self.treeview.get_children(""):
            self.treeview.delete(item)
        
        # Lägg till alla element från hs_list
        for item in hs_list:
            self.treeview.insert("", "end", values = item)
            
    def close_window(self, event = None):
        """ Avregistrerar fönstret från High Score Manager.
        param event:  Skickas av tk, används ej. 
        """
        self.hsm.hsw = None
        try:
            if self.window:
                self.window.destroy()
        except TclError:
            pass

    
    