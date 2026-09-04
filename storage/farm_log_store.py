import json
from utils.exceptions import StorageError

FARM_PLOTS_FILE = 'data/farm_plots.json'


def load_plots():
    try:
        f = open(FARM_PLOTS_FILE, 'r', encoding='utf-8')
    except FileNotFoundError:
        return []

    try:
        plots = json.load(f)
    except json.JSONDecodeError:
        f.close()
        raise StorageError(f'{FARM_PLOTS_FILE} is corrupted and could not be read')

    f.close()
    return plots


def save_plots(plots):
    try:
        f = open(FARM_PLOTS_FILE, 'w', encoding='utf-8')
    except OSError as e:
        raise StorageError(f'could not write to {FARM_PLOTS_FILE}: {e}')

    json.dump(plots, f, indent=2)
    f.close()


def add_plot(crop_name, state_name, latitude, longitude, planting_date):
    plots = load_plots()

    new_id = 1
    if plots:
        new_id = max(p['id'] for p in plots) + 1

    plot = {
        'id': new_id,
        'crop': crop_name,
        'state': state_name,
        'latitude': latitude,
        'longitude': longitude,
        'planting_date': planting_date,
    }

    plots.append(plot)
    save_plots(plots)
    return plot


def delete_plot(plot_id):
    plots = load_plots()
    remaining = [p for p in plots if p['id'] != plot_id]

    if len(remaining) == len(plots):
        raise StorageError(f'no plot found with id {plot_id}')

    save_plots(remaining)


PLANTING_LOGS_FILE = 'data/planting_logs.json'

ACTIVITY_TYPES = [
    'Land preparation',
    'Planting',
    'Watering/Irrigation',
    'Fertilizer application',
    'Weeding',
    'Pest control',
    'Disease treatment',
    'Harvesting',
    'General notes',
]


def load_logs():
    try:
        f = open(PLANTING_LOGS_FILE, 'r', encoding='utf-8')
    except FileNotFoundError:
        return []

    try:
        logs = json.load(f)
    except json.JSONDecodeError:
        f.close()
        raise StorageError(f'{PLANTING_LOGS_FILE} is corrupted and could not be read')

    f.close()
    return logs


def save_logs(logs):
    try:
        f = open(PLANTING_LOGS_FILE, 'w', encoding='utf-8')
    except OSError as e:
        raise StorageError(f'could not write to {PLANTING_LOGS_FILE}: {e}')

    json.dump(logs, f, indent=2)
    f.close()


def add_log(plot_id, activity, log_date, notes=''):
    # a log entry must belong to a plot that actually exists
    plots = load_plots()
    if not any(p['id'] == plot_id for p in plots):
        raise StorageError(f'no plot found with id {plot_id}')

    logs = load_logs()

    new_id = 1
    if logs:
        new_id = max(l['id'] for l in logs) + 1

    log_entry = {
        'id': new_id,
        'plot_id': plot_id,
        'date': log_date,
        'activity': activity,
        'notes': notes,
    }

    logs.append(log_entry)
    save_logs(logs)
    return log_entry


def get_logs_for_plot(plot_id):
    logs = load_logs()
    return [l for l in logs if l['plot_id'] == plot_id]


def delete_log(log_id):
    logs = load_logs()
    remaining = [l for l in logs if l['id'] != log_id]

    if len(remaining) == len(logs):
        raise StorageError(f'no log found with id {log_id}')

    save_logs(remaining)


SEASON_CALENDARS_FILE = 'data/season_calendars.json'


def load_calendars():
    try:
        f = open(SEASON_CALENDARS_FILE, 'r', encoding='utf-8')
    except FileNotFoundError:
        return []

    try:
        calendars = json.load(f)
    except json.JSONDecodeError:
        f.close()
        raise StorageError(f'{SEASON_CALENDARS_FILE} is corrupted and could not be read')

    f.close()
    return calendars


def save_calendars(calendars):
    try:
        f = open(SEASON_CALENDARS_FILE, 'w', encoding='utf-8')
    except OSError as e:
        raise StorageError(f'could not write to {SEASON_CALENDARS_FILE}: {e}')

    json.dump(calendars, f, indent=2)
    f.close()


def save_calendar_for_plot(plot_id, events):
    plots = load_plots()
    if not any(p['id'] == plot_id for p in plots):
        raise StorageError(f'no plot found with id {plot_id}')

    calendars = load_calendars()
    # replace any existing calendar for this plot, so re-generating stays up to date
    calendars = [c for c in calendars if c['plot_id'] != plot_id]
    calendars.append({'plot_id': plot_id, 'events': events})
    save_calendars(calendars)


def get_calendar_for_plot(plot_id):
    calendars = load_calendars()
    for c in calendars:
        if c['plot_id'] == plot_id:
            return c['events']
    return None
