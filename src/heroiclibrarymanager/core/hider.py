from heroiclibrarymanager.models.game import HeroicGame


def HeroicDupsHider(dups: list[list[HeroicGame]], platform_priority: list[str]):
    for dup_games in dups:
        # sort the games in the dup group by platform priority
        dup_games.sort(key=lambda g: platform_priority.index(g.platform) if g.platform in platform_priority else len(platform_priority))
        # don't hide first, hide the rest
        for game in dup_games[1:]:
            game.is_hidden = True
    