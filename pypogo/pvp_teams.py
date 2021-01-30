"""
Hacky team builder notes and code
"""
import ubelt as ub
from pypogo.pokemon import Pokemon
from pypogo.pogo_api import api
# azumarill,BUBBLE,ICE_BEAM,PLAY_ROUGH,38,12,15,13

# https://pvpoke.com/custom-rankings/
great_meta = """
abomasnow,POWDER_SNOW,WEATHER_BALL_ICE,ENERGY_BALL
altaria,DRAGON_BREATH,SKY_ATTACK,DRAGON_PULSE
azumarill,BUBBLE,ICE_BEAM,HYDRO_PUMP
bastiodon,SMACK_DOWN,STONE_EDGE,FLAMETHROWER
clefable,CHARM,METEOR_MASH,PSYCHIC
cresselia,PSYCHO_CUT,GRASS_KNOT,MOONBLAST
deoxys_defense,COUNTER,THUNDERBOLT,ROCK_SLIDE
drifblim,HEX,ICY_WIND,SHADOW_BALL
ferrothorn,BULLET_SEED,POWER_WHIP,THUNDER
galvantula,VOLT_SWITCH,DISCHARGE,LUNGE
haunter,SHADOW_CLAW,SHADOW_PUNCH,SHADOW_BALL
hypno,CONFUSION,THUNDER_PUNCH,SHADOW_BALL
hypno_shadow-shadow,CONFUSION,ICE_PUNCH,THUNDER_PUNCH
lapras,ICE_SHARD,SURF,SKULL_BASH
machamp_shadow-shadow,COUNTER,CROSS_CHOP,ROCK_SLIDE
marowak_alolan,FIRE_SPIN,SHADOW_BALL,BONE_CLUB
melmetal,THUNDER_SHOCK,ROCK_SLIDE,SUPER_POWER
munchlax,LICK,BODY_SLAM,BULLDOZE
raichu_alolan,VOLT_SWITCH,THUNDER_PUNCH,WILD_CHARGE
registeel,LOCK_ON,FLASH_CANNON,FOCUS_BLAST
sableye,SHADOW_CLAW,FOUL_PLAY,POWER_GEM
scrafty,COUNTER,POWER_UP_PUNCH,FOUL_PLAY
shiftry,SNARL,LEAF_BLADE,FOUL_PLAY
skarmory,AIR_SLASH,SKY_ATTACK,BRAVE_BIRD
stunfisk,THUNDER_SHOCK,MUD_BOMB,DISCHARGE
stunfisk_galarian,MUD_SHOT,ROCK_SLIDE,EARTHQUAKE
swampert,MUD_SHOT,HYDRO_CANNON,SLUDGE_WAVE
swampert,MUD_SHOT,HYDRO_CANNON,EARTHQUAKE
toxicroak,COUNTER,MUD_BOMB,SLUDGE_BOMB
umbreon,SNARL,FOUL_PLAY,LAST_RESORT
venusaur,VINE_WHIP,FRENZY_PLANT,SLUDGE_BOMB
victreebel_shadow-shadow,RAZOR_LEAF,LEAF_BLADE,SLUDGE_BOMB
vigoroth,COUNTER,BODY_SLAM,BULLDOZE
whiscash,MUD_SHOT,MUD_BOMB,BLIZZARD
wigglytuff,CHARM,ICE_BEAM,PLAY_ROUGH
"""

less_encountered = """
dewgong,ICE_SHARD,ICY_WIND,WATER_PULSE
froslass,POWDER_SNOW,AVALANCHE,SHADOW_BALL
mantine,BUBBLE,BUBBLE_BEAM,ICE_BEAM
medicham,COUNTER,DYNAMIC_PUNCH,ICE_PUNCH
meganium,VINE_WHIP,FRENZY_PLANT,EARTHQUAKE
pelipper,WING_ATTACK,WEATHER_BALL_WATER,HURRICANE
tropius,AIR_SLASH,LEAF_BLADE,AERIAL_ACE
tropius,RAZOR_LEAF,LEAF_BLADE,AERIAL_ACE
zweilous,DRAGON_BREATH,BODY_SLAM,DARK_PULSE
"""


def main():
    candidates = None
    mode = 'ultra'
    if mode == 'great':
        candidate_csv_text = ub.codeblock(
            '''
            registeel,LOCK_ON,FLASH_CANNON,FOCUS_BLAST,22,10,14,15
            stunfisk_galarian,MUD_SHOT,ROCK_SLIDE,EARTHQUAKE,25,11,14,14
            # altaria,DRAGON_BREATH,SKY_ATTACK,DRAGON_PULSE,26.5,14,12,13

            skarmory,AIR_SLASH,SKY_ATTACK,FLASH_CANNON,26,11,13,10

            azumarill,BUBBLE,ICE_BEAM,HYDRO_PUMP,38,12,15,13
            dewgong,ICE_SHARD,ICY_WIND,WATER_PULSE,26.5,15,08,15

            # umbreon,SNARL,FOUL_PLAY,LAST_RESORT,24.5,15,10,15
            # farfetchd_galarian,FURY_CUTTER,LEAF_BLADE,BRAVE_BIRD,33.5,12,15,15

            hypno,CONFUSION,SHADOW_BALL,THUNDER_PUNCH,25.5,13,15,14
            # hypno,CONFUSION,SHADOW_BALL,FOCUS_BLAST,25.5,13,15,14

            # machamp-shadow,COUNTER,ROCK_SLIDE,CROSS_CHOP,18,5,11,10
            victreebel_shadow-shadow,RAZOR_LEAF,LEAF_BLADE,FRUSTRATION,22.5,4,14,14
            ''')

        candidate_explicit = [
            Pokemon('medicham', ivs=[7, 15, 14], level=41.5),
            Pokemon('medicham', ivs=[7, 15, 14], level=43.0),
            Pokemon('medicham', ivs=[7, 15, 14]).maximize(1500),
            Pokemon('machamp', [1, 15, 6], cp=1493),
            Pokemon('altaria', [1, 11, 8], cp=1496),
            Pokemon('skarmory', [0, 15, 13], cp=1495),
            Pokemon('umbreon', [1, 8, 8], cp=1495),
            Pokemon('registeel', [10, 14, 15], cp=1487),
            Pokemon('stunfisk', [11, 14, 14], form='Galarian', cp=1498),
            Pokemon('cresselia', [7, 14, 8], cp=1493),
            Pokemon('vigoroth', [0, 10, 9], cp=1495),
            Pokemon('drifblim', [4, 14, 13], cp=1498),
            Pokemon('haunter', [6, 13, 15], cp=1498),
            Pokemon('mantine', [6, 13, 14], cp=1497),
            Pokemon('politoed', [3, 5, 13], cp=1493),
            Pokemon('charizard', [3, 15, 14], cp=1485),
            Pokemon('gengar', [5, 11, 14], cp=1483),
            Pokemon('mew', [15, 12, 11], cp=1470),
            Pokemon('dewgong', [15, 8, 15]).maximize(1500),
            Pokemon('azumarill', [12, 15, 13]).maximize(1500),
            Pokemon('hypno', [13, 15, 14]).maximize(1500),
        ]
        for cand in candidate_explicit:
            cand.populate_cp()
        stat_products = [cand.stat_product for cand in candidate_explicit]
        sortx = ub.argsort(stat_products)
        candidate_explicit = list(ub.take(candidate_explicit, sortx))
        stat_products = list(ub.take(stat_products, sortx))
        print('stat_products = {}'.format(ub.repr2(stat_products, nl=1)))
        print('candidate_explicit = {}'.format(ub.repr2(candidate_explicit, nl=1)))

        for cand in candidate_explicit:
            print('cand.adjusted = {}, {:.2f}, {}'.format(ub.repr2(cand.adjusted, nl=0, precision=2), cand.stat_product, cand))

    if mode == 'ultra':
        candidate_csv_text = ub.codeblock(
            '''
            cresselia,PSYCHO_CUT,MOONBLAST,FUTURE_SIGHT
            togekiss,CHARM,FLAMETHROWER,ANCIENT_POWER
            articuno,ICE_SHARD,ICY_WIND,HURRICANE
            swampert,MUD_SHOT,MUDDY_WATER,EARTHQUAKE
            venusaur,VINE_WHIP,FRENZY_PLANT,SLUDGE_BOMB
            ''')

        candidates = [
            Pokemon('Gengar', (7, 14, 14), cp=2500, moves=['SHADOW_CLAW', 'SHADOW_PUNCH', 'SHADOW_BALL']),
            Pokemon('Togekiss', (15, 15, 14), cp=2469, moves=['CHARM', 'FLAMETHROWER', 'AERIAL_ACE']),
            Pokemon('Venusaur', (15, 13, 13), cp=2482, moves=['VINE_WHIP', 'FRENZY_PLANT', 'SLUDGE_BOMB']),
            Pokemon('Muk', (9, 7, 4), cp=2486, form='Alola', moves=['SNARL', 'DARK_PULSE', 'SLUDGE_WAVE']),
            Pokemon('Swampert', (0, 2, 14), cp=2500, moves=['WATER_GUN', 'HYDRO_CANNON', 'SLUDGE_WAVE']),
            Pokemon('Empoleon', (0, 10, 14), cp=2495, moves=['WATERFALL', 'HYDRO_CANNON', 'DRILL_PECK']),
            Pokemon('sirfetch’d', (4, 11, 12), cp=2485, form='Galarian', moves=['COUNTER', 'CLOSE_COMBAT', 'LEAF_BLADE']),
        ]
    # else:
    #     raise KeyError(mode)

    if candidates is None:
        candidates = []
        for line in candidate_csv_text.split('\n'):
            line = line.strip()
            if line.startswith('#'):
                continue
            if line:
                row = line.split(',')
                cand = Pokemon.from_pvpoke_row(row)
                candidates.append(cand)

    print(ub.repr2(api.learnable))

    if mode == 'ultra':
        base = 'https://pvpoke.com/team-builder/all/2500'
        base = 'https://pvpoke.com/team-builder/premier/2500'
    elif mode == 'great':
        base = 'https://pvpoke.com/team-builder/all/1500'
    sep = '%2C'
    import itertools as it
    print('candidates = {!r}'.format(candidates))
    for team in it.combinations(candidates, 3):
        # if not any('registeel' in p.name for p in team):
        #     continue
        # if not any('victree' in p.name for p in team):
        #     continue
        # if len(set(p.name for p in team)) != 3:
        #     continue
        suffix = sep.join([p.to_pvpoke_url() for p in team])
        url = base + '/' + suffix
        print(url)

    # altaria-26.5-14-12-13-4-4-1-m-0-3-2%2Cskarmory-26-11-13-10-4-4-1-m-0-3-2%2Cazumarill-38-12-15-13-4-4-1-m-0-2-1

    # !pip install beautifulsoup4

    # from bs4 import BeautifulSoup
    # import requests
    # got = requests.request('get', url)
    # print(got.text)
    # soup = BeautifulSoup(got.text, 'html.parser')
    # for div in soup.find_all(name='div'):
    #     if 'grade' in div.attrs:
    #         print('div = {!r}'.format(div))
