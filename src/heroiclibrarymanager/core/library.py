from heroiclibrarymanager.models.game import HeroicGame
from rapidfuzz import fuzz, process, utils

class GameLibrary:
    def __init__(self, games: list[HeroicGame]):
        self._all_games = games

    def __iter__(self):
        return iter(self._all_games)
    
    def __len__(self):
        return len(self._all_games)
    
    def __getitem__(self, index):
        return self._all_games[index]
    
    @property
    def games(self) -> list[HeroicGame]:
        return self._all_games
    
    def find(self, title: str, platform: str) -> HeroicGame | None:
        for game in self._all_games:
            if game.title == title and game.platform == platform:
                return game
        return None
    
    def get_game(self, app_name: str) -> HeroicGame | None:
        for game in self._all_games:
            if game.app_name == app_name:
                return game
        return None

    def filter_platform(self, platform: str) -> list[HeroicGame]:
        return [g for g in self._all_games if g.platform == platform]
    
    def get_visible(self) -> list[HeroicGame]:
        return [g for g in self._all_games if not g.is_hidden]
    
    def toggle_hidden(self, game: HeroicGame):
        if game not in self._all_games: return
        game.is_hidden = not game.is_hidden
    
    def get_duplicates(self, threshold=95) -> list[list[HeroicGame]]:
        """
            Gets duplicates.
        """
        platforms = {game.platform for game in self._all_games} # get all unique platforms
        platform_games = {} # dict of lists wrt platform e. g. {"GOG": [...], "Epic Games Store": [...]}
        anchor_platform = None # this is the base list which will be compared to everything else

        for p in platforms:
            platform_games[p] = self.filter_platform(p)
        # print(platform_games.keys())

        duplicates = []
        while platform_games:
            if not anchor_platform:
                if platforms: anchor_platform = platforms.pop() # get the anchor platform, remove it from the set of platforms
                if not platforms: break # means there's nothing left to compare
            other_platforms = list(platforms) # everything that's not an anchor

            if platform_games[anchor_platform]: 
                game: HeroicGame = platform_games[anchor_platform].pop() # game to check
            else: 
                anchor_platform = None # nothing left on this platform, reset anchor
                continue

            if game.is_dlc: continue # don't care for DLCs
            if game.is_hidden: continue # hidden is already duplicated, so skip
            game_duplicates = [] # list of duplicates for this game, if any

            while other_platforms:
                test_platform = other_platforms.pop()
                other_titles = [g.title for g in platform_games[test_platform]] # get titles of the other platform's games

                # fuzzy match the game title against the other platform's titles
                match = process.extractOne( 
                    game.title,
                    other_titles,
                    scorer=fuzz.ratio,
                    processor=utils.default_process
                )

                # check if match is above threshold, if so, we have a duplicate
                if match and match[1] >= threshold:
                    matched_game = platform_games[test_platform].pop(match[2]) # remove the matched game from the other platform's list
                    if not matched_game.is_hidden: 
                        if not game_duplicates: game_duplicates.append(game)
                        game_duplicates.append(matched_game)
            if game_duplicates: duplicates.append(game_duplicates)
        return duplicates # ez ez

# for testing only! prints dups to terminal if you run this file
if __name__ == "__main__":
    from heroiclibrarymanager.core.scanner import HeroicScanner
    
    # make sure this exists. dump test configs from your heroic config dir
    # DON'T POINT TO ACTUAL CONFIG DIR (it's not writing anything, but just in case)
    games = HeroicScanner("/workspaces/heroiclibrarymanager/tests/test_configs").scan()
    library = GameLibrary(games)
    duplicates = library.get_duplicates()
    print(duplicates)
