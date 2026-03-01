from heroiclibrarymanager.models.game import HeroicGame
from rapidfuzz import fuzz, process, utils

class GameLibrary:
    def __init__(self, games: list[HeroicGame]):
        self._all_games = games
        self._duplicates = games

    def __iter__(self):
        return iter(self._all_games)
    
    def __len__(self):
        return len(self._all_games)
    
    @property
    def games(self) -> list[HeroicGame]:
        return self._all_games

    def filter_platform(self, platform: str) -> list[HeroicGame]:
        return [g for g in self._all_games if g.platform == platform]
    
    def get_visible(self) -> list[HeroicGame]:
        return [g for g in self._all_games if not g.is_hidden]
    
    def get_duplicates(self, threshold=90) -> list[list[HeroicGame]]:
        """
            Gets duplicates.
            This code is janky af and could be improved later. Not touching right now!
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
                if platforms: anchor_platform = platforms.pop()
                if not platforms: break
            other_platforms = list(platforms)

            if platform_games[anchor_platform]: 
                game: HeroicGame = platform_games[anchor_platform].pop()
            else: 
                anchor_platform = None
                continue

            game_duplicates = []
            if game.is_dlc: continue
            if game.is_hidden: continue
            while other_platforms:
                other_games = platform_games[other_platforms.pop()]
                other_titles = [g.title for g in other_games]
                match = process.extractOne(
                    game.title,
                    other_titles,
                    scorer=fuzz.token_sort_ratio,
                    processor=utils.default_process
                )
                if match and match[1] >= threshold:
                    matched_game = other_games[match[2]]
                    if not game_duplicates: game_duplicates.append(game)
                    game_duplicates.append(matched_game)
            if game_duplicates: duplicates.append(game_duplicates)
        return duplicates

if __name__ == "__main__":
    from heroiclibrarymanager.core.scanner import HeroicScanner
    
    games = HeroicScanner("/workspaces/heroiclibrarymanager/tests/test_configs").scan()
    library = GameLibrary(games)
    duplicates = library.get_duplicates()
    print(duplicates)
