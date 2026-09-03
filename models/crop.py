class Crop:
    def __init__(self, name, min_temp, max_temp, min_rainfall_mm, max_rainfall_mm, growth_days,
                 common_pests, common_diseases, heavy_rain_mm, heatwave_temp_c, dry_spell_days,
                 dry_spell_rain_mm, cold_temp_c, is_generic=False):
        self.name = name
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.min_rainfall_mm = min_rainfall_mm
        self.max_rainfall_mm = max_rainfall_mm
        self.growth_days = growth_days
        self.common_pests = common_pests
        self.common_diseases = common_diseases
        # weather threat thresholds, per crop 
        self.heavy_rain_mm = heavy_rain_mm            # daily rainfall (mm) that counts as "heavy rain" for this crop
        self.heatwave_temp_c = heatwave_temp_c        # daily max temp (C) that counts as a "heatwave" for this crop
        self.dry_spell_days = dry_spell_days           # consecutive dry days needed to flag a "dry spell"
        self.dry_spell_rain_mm = dry_spell_rain_mm      # daily rainfall (mm) below which a day counts as "dry"
        self.cold_temp_c = cold_temp_c                  # daily min temp (C) at or below which counts as an extreme-cold risk for this crop
     
        self.is_generic = is_generic

    def temp_in_range(self, temp):
        return self.min_temp <= temp <= self.max_temp


maize = Crop('Maize', 18, 32, 500, 800, 90,
              ['fall armyworm', 'stem borer'], ['maize streak virus', 'leaf blight'],
              heavy_rain_mm=40, heatwave_temp_c=36, dry_spell_days=10, dry_spell_rain_mm=1, cold_temp_c=12)

cassava = Crop('Cassava', 20, 35, 750, 1500, 300,
                ['cassava mealybug', 'whitefly'], ['cassava mosaic disease', 'root rot'],
                heavy_rain_mm=50, heatwave_temp_c=38, dry_spell_days=14, dry_spell_rain_mm=1, cold_temp_c=14)

tomato = Crop('Tomato', 18, 27, 400, 600, 80,
               ['whitefly', 'tomato fruitworm'], ['fungal disease', 'bacterial wilt'],
               heavy_rain_mm=30, heatwave_temp_c=32, dry_spell_days=5, dry_spell_rain_mm=1, cold_temp_c=12)

rice = Crop('Rice', 20, 35, 1000, 2000, 120,
             ['stem borer', 'rice bug'], ['rice blast', 'bacterial leaf blight'],
             heavy_rain_mm=60, heatwave_temp_c=38, dry_spell_days=7, dry_spell_rain_mm=1, cold_temp_c=14)

yam = Crop('Yam', 20, 30, 1000, 1500, 270,
            ['yam beetle', 'nematodes'], ['yam anthracnose', 'dry rot'],
            heavy_rain_mm=45, heatwave_temp_c=35, dry_spell_days=12, dry_spell_rain_mm=1, cold_temp_c=14)

sorghum = Crop('Sorghum', 20, 35, 400, 800, 120,
                ['sorghum midge', 'stem borer'], ['anthracnose', 'grain mold'],
                heavy_rain_mm=45, heatwave_temp_c=38, dry_spell_days=12, dry_spell_rain_mm=1, cold_temp_c=14)

millet = Crop('Millet', 20, 35, 300, 600, 90,
               ['millet head miner', 'stem borer'], ['downy mildew', 'ergot'],
               heavy_rain_mm=40, heatwave_temp_c=40, dry_spell_days=14, dry_spell_rain_mm=1, cold_temp_c=13)

groundnut = Crop('Groundnut', 20, 30, 500, 1000, 110,
                  ['aphids', 'groundnut rosette vector'], ['groundnut rosette', 'leaf spot'],
                  heavy_rain_mm=40, heatwave_temp_c=34, dry_spell_days=10, dry_spell_rain_mm=1, cold_temp_c=14)

cowpea = Crop('Cowpea', 20, 30, 400, 700, 70,
               ['pod borer', 'aphids'], ['cowpea mosaic virus', 'bacterial blight'],
               heavy_rain_mm=35, heatwave_temp_c=34, dry_spell_days=7, dry_spell_rain_mm=1, cold_temp_c=14)

sweet_potato = Crop('Sweet Potato', 20, 30, 500, 1000, 120,
                     ['sweet potato weevil'], ['sweet potato virus disease', 'root rot'],
                     heavy_rain_mm=45, heatwave_temp_c=34, dry_spell_days=10, dry_spell_rain_mm=1, cold_temp_c=14)

pepper = Crop('Pepper', 18, 27, 600, 1200, 90,
               ['aphids', 'fruit borer'], ['bacterial wilt', 'anthracnose'],
               heavy_rain_mm=35, heatwave_temp_c=33, dry_spell_days=6, dry_spell_rain_mm=1, cold_temp_c=12)

onion = Crop('Onion', 13, 28, 350, 600, 110,
              ['onion thrips'], ['purple blotch', 'downy mildew'],
              heavy_rain_mm=35, heatwave_temp_c=32, dry_spell_days=10, dry_spell_rain_mm=1, cold_temp_c=8)

okra = Crop('Okra', 20, 32, 400, 800, 60,
             ['aphids', 'pod borer'], ['okra mosaic virus', 'powdery mildew'],
             heavy_rain_mm=35, heatwave_temp_c=35, dry_spell_days=6, dry_spell_rain_mm=1, cold_temp_c=14)

watermelon = Crop('Watermelon', 20, 30, 400, 600, 80,
                   ['aphids', 'fruit fly'], ['fusarium wilt', 'anthracnose'],
                   heavy_rain_mm=35, heatwave_temp_c=34, dry_spell_days=7, dry_spell_rain_mm=1, cold_temp_c=14)

garden_egg = Crop('Garden Egg', 20, 30, 600, 1200, 100,
                   ['flea beetle', 'fruit borer'], ['bacterial wilt', 'leaf spot'],
                   heavy_rain_mm=35, heatwave_temp_c=33, dry_spell_days=6, dry_spell_rain_mm=1, cold_temp_c=14)

cucumber = Crop('Cucumber', 18, 28, 400, 700, 60,
                 ['aphids', 'cucumber beetle'], ['powdery mildew', 'downy mildew'],
                 heavy_rain_mm=30, heatwave_temp_c=32, dry_spell_days=5, dry_spell_rain_mm=1, cold_temp_c=12)

cabbage = Crop('Cabbage', 15, 25, 400, 600, 90,
                ['diamondback moth', 'aphids'], ['black rot', 'clubroot'],
                heavy_rain_mm=35, heatwave_temp_c=28, dry_spell_days=8, dry_spell_rain_mm=1, cold_temp_c=8)

carrot = Crop('Carrot', 15, 25, 350, 600, 90,
               ['carrot fly', 'aphids'], ['leaf blight', 'root rot'],
               heavy_rain_mm=30, heatwave_temp_c=28, dry_spell_days=8, dry_spell_rain_mm=1, cold_temp_c=8)

soybean = Crop('Soybean', 20, 30, 500, 900, 100,
                ['pod borer', 'aphids'], ['rust', 'bacterial blight'],
                heavy_rain_mm=40, heatwave_temp_c=34, dry_spell_days=9, dry_spell_rain_mm=1, cold_temp_c=14)

sesame = Crop('Sesame', 25, 35, 350, 650, 90,
               ['gall midge', 'leaf webber'], ['leaf spot', 'phyllody'],
               heavy_rain_mm=35, heatwave_temp_c=38, dry_spell_days=10, dry_spell_rain_mm=1, cold_temp_c=16)

bambara_nut = Crop('Bambara Nut', 20, 30, 400, 800, 120,
                    ['aphids', 'pod borer'], ['leaf spot', 'rosette'],
                    heavy_rain_mm=40, heatwave_temp_c=34, dry_spell_days=12, dry_spell_rain_mm=1, cold_temp_c=14)

ginger = Crop('Ginger', 20, 30, 1500, 2500, 240,
               ['shoot borer', 'root knot nematode'], ['rhizome rot', 'bacterial wilt'],
               heavy_rain_mm=55, heatwave_temp_c=34, dry_spell_days=10, dry_spell_rain_mm=1, cold_temp_c=14)

garlic = Crop('Garlic', 12, 25, 350, 600, 150,
               ['thrips', 'nematodes'], ['white rot', 'purple blotch'],
               heavy_rain_mm=30, heatwave_temp_c=28, dry_spell_days=10, dry_spell_rain_mm=1, cold_temp_c=6)

hibiscus = Crop('Hibiscus', 20, 32, 500, 900, 120,
                 ['aphids', 'flea beetle'], ['leaf spot', 'root rot'],
                 heavy_rain_mm=40, heatwave_temp_c=35, dry_spell_days=10, dry_spell_rain_mm=1, cold_temp_c=14)

cotton = Crop('Cotton', 20, 32, 600, 1200, 180,
               ['bollworm', 'aphids'], ['bacterial blight', 'fusarium wilt'],
               heavy_rain_mm=45, heatwave_temp_c=36, dry_spell_days=12, dry_spell_rain_mm=1, cold_temp_c=14)

wheat = Crop('Wheat', 15, 25, 350, 650, 120,
              ['aphids', 'armyworm'], ['rust', 'powdery mildew'],
              heavy_rain_mm=35, heatwave_temp_c=28, dry_spell_days=10, dry_spell_rain_mm=1, cold_temp_c=6)

lettuce = Crop('Lettuce', 15, 24, 350, 500, 50,
                ['aphids', 'leaf miner'], ['downy mildew', 'leaf rot'],
                heavy_rain_mm=25, heatwave_temp_c=27, dry_spell_days=4, dry_spell_rain_mm=1, cold_temp_c=8)

spinach = Crop('Spinach', 15, 27, 350, 600, 45,
                ['aphids', 'leaf miner'], ['downy mildew', 'leaf spot'],
                heavy_rain_mm=30, heatwave_temp_c=30, dry_spell_days=5, dry_spell_rain_mm=1, cold_temp_c=8)

SUPPORTED_CROPS = {
    'Maize': maize,
    'Cassava': cassava,
    'Tomato': tomato,
    'Rice': rice,
    'Yam': yam,
    'Sorghum': sorghum,
    'Millet': millet,
    'Groundnut': groundnut,
    'Cowpea': cowpea,
    'Sweet Potato': sweet_potato,
    'Pepper': pepper,
    'Onion': onion,
    'Okra': okra,
    'Watermelon': watermelon,
    'Garden Egg': garden_egg,
    'Cucumber': cucumber,
    'Cabbage': cabbage,
    'Carrot': carrot,
    'Soybean': soybean,
    'Sesame': sesame,
    'Bambara Nut': bambara_nut,
    'Ginger': ginger,
    'Garlic': garlic,
    'Hibiscus': hibiscus,
    'Cotton': cotton,
    'Wheat': wheat,
    'Lettuce': lettuce,
    'Spinach': spinach,
}

# Common alternate/local names for some crops above, so typing them still resolves to the
# known-crop entry instead of falling back to generic estimates.
CROP_ALIASES = {
    'beans': 'Cowpea',
    'peanut': 'Groundnut',
    'peanuts': 'Groundnut',
    'sweet potatoes': 'Sweet Potato',
}

# generic fallback thresholds used for any crop name that isn't in
# SUPPORTED_CROPS above. These are broad, rough-average values across common tropical food
# crops, deliberately not tuned to any specific crop. Any advice generated using them is less
# reliable than advice for a known crop, and the UI flags this via Crop.is_generic.
GENERIC_CROP_DEFAULTS = {
    'min_temp': 18,
    'max_temp': 34,
    'min_rainfall_mm': 500,
    'max_rainfall_mm': 1200,
    'growth_days': 90,
    'heavy_rain_mm': 40,
    'heatwave_temp_c': 36,
    'dry_spell_days': 10,
    'dry_spell_rain_mm': 1,
    'cold_temp_c': 12,
}


def get_crop(name):
    if not name or not name.strip():
        return None

    typed_name = name.strip()

    # match known crops case-insensitively, so "maize" / "MAIZE" / "Maize" all resolve
    for known_name, crop in SUPPORTED_CROPS.items():
        if known_name.lower() == typed_name.lower():
            return crop

    # match common local aliases (e.g. "Beans" -> Cowpea) before falling back to generic
    alias_target = CROP_ALIASES.get(typed_name.lower())
    if alias_target:
        return SUPPORTED_CROPS[alias_target]

    # unknown crop: return a generic crop rather than None, so the rest of the app
    # (weather threats, planting advisor, season calendar) still works for any crop name
    defaults = GENERIC_CROP_DEFAULTS
    return Crop(
        name=typed_name,
        min_temp=defaults['min_temp'],
        max_temp=defaults['max_temp'],
        min_rainfall_mm=defaults['min_rainfall_mm'],
        max_rainfall_mm=defaults['max_rainfall_mm'],
        growth_days=defaults['growth_days'],
        common_pests=[],
        common_diseases=[],
        heavy_rain_mm=defaults['heavy_rain_mm'],
        heatwave_temp_c=defaults['heatwave_temp_c'],
        dry_spell_days=defaults['dry_spell_days'],
        dry_spell_rain_mm=defaults['dry_spell_rain_mm'],
        cold_temp_c=defaults['cold_temp_c'],
        is_generic=True,
    )
