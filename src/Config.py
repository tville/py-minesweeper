# P-Uppgift: Minröjning
# Jerker Ersare
# 2015-09-07
#
# Denna fil samlar inställningar. Jag är lite ovan vid att dela upp saker i olika filer i Python,
# detta är i alla fall en möjlighet att dela konstanter utan circular dependencies.  

import Shared


# Sätt till true för att göra spelet väldigt enkelt att vinna
QUICK_TEST = False
# Sätt till true för att se vad som finns i varje cell
CHEAT = False

# Filnamn för high score
HIGH_SCORE_FILENAME = "highscore.csv"
HIGH_SCORE_DELIMITER = "|"

# Kartstorlekar och svårighetsnivåer. Hade kunnat ange dessa som listor/dictionaries av tupler 
# till exempel, men känner att det blir lite tydligare vad siffrorna står för med egna klasser
MAP_SIZES = []
MAP_SIZES.append(Shared.MapSize("Small", 12, 12, 3))
MAP_SIZES.append(Shared.MapSize("Medium", 18, 18, 5))
MAP_SIZES.append(Shared.MapSize("Large", 24, 24, 8))

GAME_LEVELS = []
GAME_LEVELS.append(Shared.Level("Easy", 5, 5))
GAME_LEVELS.append(Shared.Level("Medium", 10, 10))
GAME_LEVELS.append(Shared.Level("Hard", 20, 20))   
