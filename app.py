import streamlit as st
from datetime import datetime
from models.crop import get_crop, SUPPORTED_CROPS
from utils.helpers import NIGERIA_STATES, get_geocode_query_name
from utils.validators import validate_coordinates, validate_date_format
from utils.exceptions import InvalidDateError, InvalidCoordinateError, WeatherAPIError, GeminiAPIError, StorageError, GeocodingError
from services.weather_client import WeatherClient
from services.geocoding_client import GeocodingClient
from services.planting_advisor import detect_weather_threats, analyze_planting_suitability, find_planting_window, estimate_irrigation_need, generate_season_calendar
from services.gemini_client import GeminiClient
from storage.farm_log_store import load_plots, add_plot, delete_plot, ACTIVITY_TYPES, add_log, get_logs_for_plot, delete_log, save_calendar_for_plot, get_calendar_for_plot

st.set_page_config(page_title='Crop & Farm Advisory', layout='wide')

st.title('AI Crop & Farm Advisory System')


def geocode_state(state_name):
    # cache per state in this session so re-selecting the same state doesn't re-hit the API
    cache = st.session_state.setdefault('geocode_cache', {})

    if state_name in cache:
        return cache[state_name]

    query_name = get_geocode_query_name(state_name)
    result = GeocodingClient().geocode(query_name)

    # sanity-check whatever the geocoding service handed back before trusting it (rule 9)
    validate_coordinates(str(result['latitude']), str(result['longitude']))

    cache[state_name] = result
    return result


def plot_label(plot):
    location = plot.get('state', f"{plot['latitude']}, {plot['longitude']}")
    return f"#{plot['id']} - {plot['crop']} ({location})"


def generic_crop_notice(crop):
    if crop is not None and crop.is_generic:
        st.info(f"No specific agronomic data for '{crop.name}' — using generic estimates that may be less accurate than for a known crop.")


def get_plot_by_id(plots, plot_id):
    for plot in plots:
        if plot['id'] == plot_id:
            return plot
    return None


def generate_plot_advice(plot, crop, forecast_data, daily, threats):
    weather_client = WeatherClient(plot['latitude'], plot['longitude'])
    current = weather_client.get_current_conditions(forecast_data)

    suitability = analyze_planting_suitability(daily, crop)
    window = find_planting_window(daily, crop)
    irrigation = estimate_irrigation_need(daily, crop)

    threat_summary = '; '.join(t['message'] for t in threats) if threats else 'none detected'
    window_text = f"{window['start']} to {window['end']}" if window else 'no clear window found'

    advisory_data = {
        'crop_name': crop.name,
        'latitude': plot['latitude'],
        'longitude': plot['longitude'],
        'current_conditions': f"temperature {current['temperature']}C, precipitation {current['precipitation']}mm, humidity {current['humidity']}%",
        'suitability_verdict': suitability['verdict'],
        'suitability_reason': suitability['reason'],
        'planting_window': window_text,
        'irrigation_level': irrigation['level'],
        'irrigation_reason': irrigation['reason'],
        'threats': threat_summary,
        'common_pests': ', '.join(crop.common_pests),
        'common_diseases': ', '.join(crop.common_diseases),
    }

    gemini_client = GeminiClient()
    return gemini_client.generate_advice(advisory_data)


def load_plot_context(plot, crop, regenerate_advice=False):
    # Fetches weather, computes threats, caches everything for this plot, and makes it the
    # active plot. Only called from explicit actions (Home's save, Saved Plots' Load, or a
    # manual Refresh) - never unconditionally on every render, since Streamlit reruns the
    # whole script on any interaction anywhere in the app.
    weather_client = WeatherClient(plot['latitude'], plot['longitude'])
    forecast_data = weather_client.get_forecast()
    daily = weather_client.get_daily_forecast(forecast_data)
    threats = detect_weather_threats(daily, crop)

    st.session_state['last_forecast'] = forecast_data
    st.session_state['crop_name'] = plot['crop']
    st.session_state['state_name'] = plot.get('state')
    st.session_state['latitude'] = plot['latitude']
    st.session_state['longitude'] = plot['longitude']
    st.session_state['active_plot_id'] = plot['id']

    plot_advice_cache = st.session_state.setdefault('plot_advice', {})
    if regenerate_advice or plot['id'] not in plot_advice_cache:
        try:
            advice_text = generate_plot_advice(plot, crop, forecast_data, daily, threats)
            plot_advice_cache[plot['id']] = {
                'text': advice_text,
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
            }
        except GeminiAPIError as e:
            st.warning(f'AI advisory could not be generated: {e}')

    return forecast_data, daily, threats


def build_calendar_log_timeline(calendar_events, logs):
    # merges season-calendar reminders and logged activities into one chronological list,
    # each row clearly tagged so it's obvious which is which
    timeline = []
    for event in calendar_events:
        timeline.append({'date': event['date'], 'type': 'Calendar', 'details': event['event']})
    for log in logs:
        note_text = f" - {log['notes']}" if log.get('notes') else ''
        timeline.append({'date': log['date'], 'type': 'Log', 'details': f"{log['activity']}{note_text}"})
    timeline.sort(key=lambda row: row['date'])
    return timeline


def format_plot_report(plot, crop, calendar_events, logs, threats, advice_data):
    location = plot.get('state', f"{plot['latitude']}, {plot['longitude']}")
    lines = [f"Farm Plot Report - Plot #{plot['id']}", '=' * 50, '']

    lines.append('PLOT DETAILS')
    lines.append('-' * 50)
    lines.append(f"Crop: {plot['crop']}")
    lines.append(f"Location: {location}")
    lines.append(f"Planting date: {plot['planting_date']}")
    if crop is not None and crop.is_generic:
        lines.append(f"Note: '{plot['crop']}' isn't in the known-crop database, so thresholds used here are generic estimates.")
    lines.append('')

    lines.append('SEASON CALENDAR')
    lines.append('-' * 50)
    if calendar_events:
        for event in calendar_events:
            lines.append(f"  {event['date']} - {event['event']}")
    else:
        lines.append('  No season calendar available for this plot.')
    lines.append('')

    lines.append('WEATHER THREATS (at time of report)')
    lines.append('-' * 50)
    if threats:
        for t in threats:
            lines.append(f"  {t['type']} ({t['date']}): {t['message']}")
            lines.append(f"    Recommended action: {t['recommended_action']}")
    else:
        lines.append('  No weather threats detected in the forecast window at the time this report was generated.')
    lines.append('')

    lines.append('AI ADVISORY')
    lines.append('-' * 50)
    if advice_data:
        lines.append(f"Generated: {advice_data['generated_at']}")
        lines.append(advice_data['text'])
    else:
        lines.append('  No AI advisory generated yet for this plot. Visit the Information tab, then regenerate this report.')
    lines.append('')

    lines.append('ACTIVITY LOG')
    lines.append('-' * 50)
    if logs:
        for log in logs:
            note_text = f" - {log['notes']}" if log.get('notes') else ''
            lines.append(f"  {log['date']}: {log['activity']}{note_text}")
    else:
        lines.append('  No activities logged yet for this plot.')
    lines.append('')

    return '\n'.join(lines)


# ---------- Home: crop + location + planting date -> automatically creates a farm plot ----------
st.header('Set your crop and location')
st.caption('Confirming below automatically creates a saved farm plot with its season calendar.')

home_col1, home_col2, home_col3 = st.columns(3)
crop_name_selected = home_col1.selectbox('Crop', list(SUPPORTED_CROPS.keys()))
state_name = home_col2.selectbox('State', NIGERIA_STATES)
planting_date_picked = home_col3.date_input('Planting date', value=datetime.now().date())

if st.button('Confirm & create farm plot'):
    try:
        planting_date_input = planting_date_picked.strftime('%Y-%m-%d')
        validate_date_format(planting_date_input)
        geocoded = geocode_state(state_name)

        new_plot = add_plot(crop_name_selected, state_name, geocoded['latitude'], geocoded['longitude'], planting_date_input)

        crop = get_crop(crop_name_selected)
        calendar_events = generate_season_calendar(new_plot['planting_date'], crop)
        save_calendar_for_plot(new_plot['id'], calendar_events)

        st.success(f"Saved plot #{new_plot['id']}: {crop_name_selected} in {state_name}, planting {planting_date_input}.")

        try:
            load_plot_context(new_plot, crop, regenerate_advice=True)
            st.success('Weather and AI advisory pulled automatically. View everything together on the Information tab.')
        except WeatherAPIError as e:
            st.warning(f'Plot and calendar were saved, but weather and AI advisory could not be pulled automatically: {e}. You can fetch them from the Information tab.')

    except InvalidDateError as e:
        st.error(f'an error occurred: {e}')
    except (GeocodingError, InvalidCoordinateError) as e:
        st.error(f'an error occurred: {e}')
    except StorageError as e:
        st.error(f'an error occurred: {e}')

if 'crop_name' in st.session_state and 'state_name' in st.session_state:
    st.caption(f"Currently set: {st.session_state['crop_name']} in {st.session_state['state_name']}")

st.divider()

tab_info, tab_log, tab_saved_plots = st.tabs(['Information', 'Activity Logs', 'Saved Plots'])

# ---------- Information ----------
with tab_info:
    st.header('Information')
    st.caption('Everything about a saved plot in one place: weather, AI advice, weather threats, season calendar, and activity logs.')

    try:
        plots = load_plots()
    except StorageError as e:
        plots = []
        st.error(f'an error occurred: {e}')

    if not plots:
        st.warning('No farm plots saved yet. Add your crop, location, and date above to create one.')
    else:
        plot_options = {plot_label(p): p for p in plots}
        labels = list(plot_options.keys())

        default_index = 0
        active_id = st.session_state.get('active_plot_id')
        if active_id is not None:
            for i, p in enumerate(plots):
                if p['id'] == active_id:
                    default_index = i
                    break

        selected_label = st.selectbox('Farm plot', labels, index=default_index, key='info_plot_select')
        selected_plot = plot_options[selected_label]
        crop = get_crop(selected_plot['crop'])
        generic_crop_notice(crop)

        if st.button('Fetch / refresh all information', key=f"refresh_info_{selected_plot['id']}"):
            try:
                load_plot_context(selected_plot, crop, regenerate_advice=True)
                st.rerun()
            except WeatherAPIError as e:
                st.error(f'an error occurred: {e}')

        is_active_plot = st.session_state.get('active_plot_id') == selected_plot['id']
        cached_forecast = st.session_state.get('last_forecast') if is_active_plot else None

        if cached_forecast is None:
            st.info('Click "Fetch / refresh all information" above to pull weather, weather threats, and AI advice for this plot.')
        else:
            weather_client = WeatherClient(selected_plot['latitude'], selected_plot['longitude'])
            current = weather_client.get_current_conditions(cached_forecast)
            daily = weather_client.get_daily_forecast(cached_forecast)
            threats = detect_weather_threats(daily, crop)

            st.subheader('Weather details')
            w1, w2, w3, w4 = st.columns(4)
            w1.metric('Condition', current['condition'])
            w2.metric('Temperature', f"{current['temperature']} C")
            w3.metric('Precipitation', f"{current['precipitation']} mm")
            w4.metric('Humidity', f"{current['humidity']} %")

            daily_rows = []
            for i in range(len(daily['time'])):
                daily_rows.append({
                    'date': daily['time'][i],
                    'condition': daily['condition'][i],
                    'temp_max_C': daily['temp_max'][i],
                    'temp_min_C': daily['temp_min'][i],
                    'precipitation_sum_mm': daily['precipitation_sum'][i],
                })
            st.table(daily_rows)

            st.subheader('Weather threats')
            if not threats:
                st.success(f'No weather threats detected for {crop.name} in the forecast window.')
            else:
                for threat in threats:
                    st.warning(f"{threat['type']}: {threat['message']}")
                    st.caption(f"Recommended action: {threat['recommended_action']}")

            st.subheader('AI advisory')
            cached_advice = st.session_state.get('plot_advice', {}).get(selected_plot['id'])
            if cached_advice:
                st.write(cached_advice['text'])
                st.caption(f"Generated: {cached_advice['generated_at']}")
            else:
                st.info('No AI advisory generated yet for this plot. Click "Fetch / refresh all information" above.')
            st.caption('This is guidance based on available weather data, not a guarantee. It does not replace professional agricultural expertise.')

        st.divider()
        st.subheader('Season calendar & activity log')
        st.caption('Calendar reminders and logged activities are shown together, tagged, and sorted by date.')

        try:
            events = get_calendar_for_plot(selected_plot['id'])

            if events is None:
                st.info('No calendar found for this plot yet (it may have been created before this feature was added).')
                if st.button('Generate calendar now', key=f"gen_cal_{selected_plot['id']}"):
                    events = generate_season_calendar(selected_plot['planting_date'], crop)
                    save_calendar_for_plot(selected_plot['id'], events)
                    st.rerun()
            else:
                logs = get_logs_for_plot(selected_plot['id'])
                timeline = build_calendar_log_timeline(events, logs)

                if not timeline:
                    st.write('Nothing to show yet.')
                else:
                    st.table(timeline)

        except StorageError as e:
            st.error(f'an error occurred: {e}')

        st.divider()
        st.subheader('Download')
        st.caption('One file with everything above: plot details, season calendar, weather threats, AI advisory, and activity log.')

        if st.button('Generate full report', key=f"gen_report_{selected_plot['id']}"):
            try:
                report_weather_client = WeatherClient(selected_plot['latitude'], selected_plot['longitude'])
                report_daily = report_weather_client.get_daily_forecast()
                report_threats = detect_weather_threats(report_daily, crop)
                report_calendar = get_calendar_for_plot(selected_plot['id']) or []
                report_logs = get_logs_for_plot(selected_plot['id'])
                report_advice = st.session_state.get('plot_advice', {}).get(selected_plot['id'])

                report_text = format_plot_report(selected_plot, crop, report_calendar, report_logs, report_threats, report_advice)
                st.session_state[f"plot_report_{selected_plot['id']}"] = report_text
            except WeatherAPIError as e:
                st.error(f'an error occurred: {e}')

        report_key = f"plot_report_{selected_plot['id']}"
        if report_key in st.session_state:
            st.download_button(
                label=f"Download plot #{selected_plot['id']} full report (.txt)",
                data=st.session_state[report_key],
                file_name=f"plot_{selected_plot['id']}_report.txt",
                mime='text/plain',
                key=f"download_report_{selected_plot['id']}",
            )


# ---------- Activity Logs ----------
with tab_log:
    st.header('Activity Logs')

    try:
        plots = load_plots()
    except StorageError as e:
        plots = []
        st.error(f'an error occurred: {e}')

    if not plots:
        st.warning('No farm plots saved yet. Create one using the form above.')
    else:
        plot_options = {plot_label(p): p['id'] for p in plots}
        selected_label = st.selectbox('Farm plot', list(plot_options.keys()), key='log_plot_select')
        selected_plot_id = plot_options[selected_label]

        st.subheader('Log an activity')
        activity = st.selectbox('Activity', ACTIVITY_TYPES)
        log_date_picked = st.date_input('Date', value=datetime.now().date(), key='log_date')
        notes = st.text_area('Notes (optional)', key='log_notes')

        if st.button('Save activity'):
            try:
                log_date = log_date_picked.strftime('%Y-%m-%d')
                validate_date_format(log_date)
                new_log = add_log(selected_plot_id, activity, log_date, notes)
                st.toast(f"Logged: {new_log['activity']} on {new_log['date']}")
                st.rerun()
            except InvalidDateError as e:
                st.error(f'an error occurred: {e}')
            except StorageError as e:
                st.error(f'an error occurred: {e}')

        st.divider()
        st.subheader('Season calendar & activity log')
        st.caption('Calendar reminders and logged activities together, tagged, and sorted by date.')

        try:
            calendar_events = get_calendar_for_plot(selected_plot_id)
        except StorageError as e:
            calendar_events = None
            st.error(f'an error occurred: {e}')

        logs = get_logs_for_plot(selected_plot_id)

        if calendar_events is None:
            st.info('No calendar found for this plot yet. Visit the Information tab to generate one.')
        else:
            timeline = build_calendar_log_timeline(calendar_events, logs)
            if not timeline:
                st.write('Nothing to show yet.')
            else:
                st.table(timeline)

        st.divider()
        st.subheader(f'Manage logged activities for {selected_label}')

        if not logs:
            st.write('No activities logged for this plot yet.')
        else:
            for log in logs:
                col1, col2 = st.columns([4, 1])
                note_text = f" - {log['notes']}" if log['notes'] else ''
                col1.write(f"{log['date']}: {log['activity']}{note_text}")
                if col2.button('Delete', key=f"delete_log_{log['id']}"):
                    try:
                        delete_log(log['id'])
                        st.rerun()
                    except StorageError as e:
                        st.error(f'an error occurred: {e}')

# ---------- Saved Plots ----------
with tab_saved_plots:
    st.header('Saved Plots')
    st.caption('Load a plot to make it active — its weather, AI advisory, and calendar will be ready on the Information tab.')

    try:
        plots = load_plots()
    except StorageError as e:
        plots = []
        st.error(f'an error occurred: {e}')

    if not plots:
        st.write('No farm plots saved yet. Add your crop, location, and date above to create one.')
    else:
        for plot in plots:
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.write(f"{plot_label(plot)}, planting {plot['planting_date']}")

            if col2.button('Load', key=f"load_{plot['id']}"):
                try:
                    plot_crop = get_crop(plot['crop'])
                    load_plot_context(plot, plot_crop, regenerate_advice=False)
                    st.toast(f"Loaded plot #{plot['id']}")
                    st.rerun()
                except WeatherAPIError as e:
                    st.error(f'an error occurred: {e}')

            if col3.button('Delete', key=f"delete_{plot['id']}"):
                try:
                    delete_plot(plot['id'])
                    st.rerun()
                except StorageError as e:
                    st.error(f'an error occurred: {e}')
