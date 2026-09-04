from datetime import datetime, timedelta

# Basic recommended action shown alongside each threat type, per project rule 17
# (kept centralized and configurable) and rule 4's "give basic recommended actions".
RECOMMENDED_ACTIONS = {
    'Heavy Rain': 'Consider delaying planting and ensuring good field drainage to prevent waterlogging.',
    'Heatwave': 'Consider providing shade or mulching, and watering more frequently to reduce heat stress.',
    'Dry Spell': 'Plan for supplemental irrigation if available, and consider delaying planting until rain resumes.',
    'Extreme Cold': 'Consider delaying planting, and protect young seedlings from cold stress where possible.',
}


def detect_heavy_rain(daily_forecast, crop):
    warnings = []
    dates = daily_forecast['time']
    rain = daily_forecast['precipitation_sum']

    for i in range(len(dates)):
        if rain[i] >= crop.heavy_rain_mm:
            warnings.append({
                'type': 'Heavy Rain',
                'date': dates[i],
                'message': f'{rain[i]}mm of rain expected on {dates[i]}, which exceeds the {crop.heavy_rain_mm}mm threshold for {crop.name}',
                'recommended_action': RECOMMENDED_ACTIONS['Heavy Rain'],
            })

    return warnings


def detect_heatwave(daily_forecast, crop):
    warnings = []
    dates = daily_forecast['time']
    temp_max = daily_forecast['temp_max']

    for i in range(len(dates)):
        if temp_max[i] >= crop.heatwave_temp_c:
            warnings.append({
                'type': 'Heatwave',
                'date': dates[i],
                'message': f'Temperature expected to reach {temp_max[i]}C on {dates[i]}, at or above the {crop.heatwave_temp_c}C heatwave threshold for {crop.name}',
                'recommended_action': RECOMMENDED_ACTIONS['Heatwave'],
            })

    return warnings


def detect_cold_snap(daily_forecast, crop):
    warnings = []
    dates = daily_forecast['time']
    temp_min = daily_forecast['temp_min']

    for i in range(len(dates)):
        if temp_min[i] <= crop.cold_temp_c:
            warnings.append({
                'type': 'Extreme Cold',
                'date': dates[i],
                'message': f'Temperature expected to drop to {temp_min[i]}C on {dates[i]}, at or below the {crop.cold_temp_c}C cold-risk threshold for {crop.name}',
                'recommended_action': RECOMMENDED_ACTIONS['Extreme Cold'],
            })

    return warnings


def detect_dry_spell(daily_forecast, crop):
    warnings = []
    dates = daily_forecast['time']
    rain = daily_forecast['precipitation_sum']

    consecutive_dry_days = 0

    for i in range(len(dates)):
        if rain[i] < crop.dry_spell_rain_mm:
            consecutive_dry_days += 1
        else:
            consecutive_dry_days = 0

        if consecutive_dry_days >= crop.dry_spell_days:
            warnings.append({
                'type': 'Dry Spell',
                'date': dates[i],
                'message': f'{consecutive_dry_days} consecutive dry days expected by {dates[i]}, at or above the {crop.dry_spell_days}-day dry spell threshold for {crop.name}',
                'recommended_action': RECOMMENDED_ACTIONS['Dry Spell'],
            })

    return warnings


def detect_weather_threats(daily_forecast, crop):
    warnings = []
    warnings.extend(detect_heavy_rain(daily_forecast, crop))
    warnings.extend(detect_heatwave(daily_forecast, crop))
    warnings.extend(detect_cold_snap(daily_forecast, crop))
    warnings.extend(detect_dry_spell(daily_forecast, crop))
    return warnings


# How many upcoming days count as "the next few days" for planting suitability checks.
# Kept as one named constant so it stays easy to find/tune (rule 17 style).
NEAR_TERM_DAYS = 5


def _slice_daily_forecast(daily_forecast, days):
    return {
        'time': daily_forecast['time'][:days],
        'temp_max': daily_forecast['temp_max'][:days],
        'temp_min': daily_forecast['temp_min'][:days],
        'precipitation_sum': daily_forecast['precipitation_sum'][:days],
    }


def analyze_planting_suitability(daily_forecast, crop, days=NEAR_TERM_DAYS):
    window = _slice_daily_forecast(daily_forecast, days)
    total_days = len(window['time'])

    if total_days == 0:
        return {
            'verdict': 'UNKNOWN',
            'reason': 'No forecast data is available to evaluate planting suitability.'
        }

    # near-term suitability only checks immediate risks (heavy rain / heatwave / extreme cold)
    # that can occur within a short window. Longer dry-spell trends are covered separately by
    # the full-window weather threat warnings, since a short window cannot detect them.
    threats = detect_heavy_rain(window, crop) + detect_heatwave(window, crop) + detect_cold_snap(window, crop)

    suitable_days = 0
    for i in range(total_days):
        if crop.temp_in_range(window['temp_max'][i]) or crop.temp_in_range(window['temp_min'][i]):
            suitable_days += 1

    suitable_ratio = suitable_days / total_days

    if threats:
        threat_types = ', '.join(sorted(set(t['type'] for t in threats)))
        return {
            'verdict': 'NOT RECOMMENDED RIGHT NOW',
            'reason': f'Based on the available weather data, {threat_types} is expected in the next {total_days} days, which poses a risk to {crop.name}. Consider waiting until conditions stabilize.'
        }

    if suitable_ratio >= 0.6:
        return {
            'verdict': 'GOOD TIME TO PLANT',
            'reason': f'Based on the available weather data, temperatures over the next {total_days} days appear suitable for {crop.name} ({crop.min_temp}-{crop.max_temp}C ideal) and no immediate weather threats were detected.'
        }

    return {
        'verdict': 'NOT RECOMMENDED RIGHT NOW',
        'reason': f'Based on the available weather data, temperatures over the next {total_days} days fall outside the suitable range ({crop.min_temp}-{crop.max_temp}C) for {crop.name} on most days.'
    }


def find_planting_window(daily_forecast, crop, days=NEAR_TERM_DAYS):
    window = _slice_daily_forecast(daily_forecast, days)
    threat_dates = set(t['date'] for t in detect_heavy_rain(window, crop) + detect_heatwave(window, crop) + detect_cold_snap(window, crop))

    best_start = None
    best_end = None
    best_length = 0
    current_start = None
    current_length = 0

    for i in range(len(window['time'])):
        date = window['time'][i]
        temp_ok = crop.temp_in_range(window['temp_max'][i]) or crop.temp_in_range(window['temp_min'][i])
        no_threat = date not in threat_dates

        if temp_ok and no_threat:
            if current_start is None:
                current_start = date
            current_length += 1
            if current_length > best_length:
                best_length = current_length
                best_start = current_start
                best_end = date
        else:
            current_start = None
            current_length = 0

    if best_start is None:
        return None

    return {'start': best_start, 'end': best_end}


def estimate_irrigation_need(daily_forecast, crop, days=NEAR_TERM_DAYS):
    window = _slice_daily_forecast(daily_forecast, days)
    total_days = len(window['time'])

    if total_days == 0:
        return {'level': 'UNKNOWN', 'reason': 'No forecast data is available to estimate irrigation need.'}

    # ASSUMPTION: crop.min_rainfall_mm is a whole-season total requirement (see models/crop.py),
    # not a daily figure. We derive a rough average daily need from it as a simplification.
    # This is intentionally a category-level estimate, not a precise irrigation quantity
    # (see project rule 15).
    daily_need_mm = crop.min_rainfall_mm / crop.growth_days
    avg_daily_rain = sum(window['precipitation_sum']) / total_days

    if avg_daily_rain >= daily_need_mm:
        level = 'unnecessary'
    elif avg_daily_rain >= daily_need_mm * 0.5:
        level = 'low'
    elif avg_daily_rain >= daily_need_mm * 0.2:
        level = 'moderate'
    else:
        level = 'high'

    return {
        'level': level,
        'reason': f'Based on the available weather data, {crop.name} needs roughly {daily_need_mm:.1f}mm/day on average, and the forecast shows about {avg_daily_rain:.1f}mm/day of rain over the next {total_days} days.'
    }


# ASSUMPTION (rule 31): these calendar-event offsets, expressed as a fraction of the crop's
# total growth_days, are not defined anywhere in the provided reference files or instructions.
# They are a reasonable general-purpose spread of farming activities across a growing season
# and MUST be reviewed against real agronomic guidance later. Kept simple per rule 20 (a
# straightforward timeline, not a complicated calendar system).
CALENDAR_EVENT_OFFSETS = [
    ('Planting', 0.0),
    ('First weeding', 0.15),
    ('Fertilizer application', 0.25),
    ('Second weeding', 0.4),
    ('Irrigation reminder', 0.5),
    ('Expected harvest', 1.0),
]


def generate_season_calendar(planting_date_str, crop):
    planting_date = datetime.strptime(planting_date_str, '%Y-%m-%d')

    events = []
    for label, fraction in CALENDAR_EVENT_OFFSETS:
        offset_days = round(crop.growth_days * fraction)
        event_date = planting_date + timedelta(days=offset_days)
        events.append({
            'event': label,
            'date': event_date.strftime('%Y-%m-%d'),
        })

    return events
