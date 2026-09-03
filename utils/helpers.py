NIGERIA_STATES = [
    'Abia', 'Adamawa', 'Akwa Ibom', 'Anambra', 'Bauchi', 'Bayelsa', 'Benue', 'Borno',
    'Cross River', 'Delta', 'Ebonyi', 'Edo', 'Ekiti', 'Enugu', 'FCT (Abuja)', 'Gombe',
    'Imo', 'Jigawa', 'Kaduna', 'Kano', 'Katsina', 'Kebbi', 'Kogi', 'Kwara', 'Lagos',
    'Nasarawa', 'Niger', 'Ogun', 'Ondo', 'Osun', 'Oyo', 'Plateau', 'Rivers', 'Sokoto',
    'Taraba', 'Yobe', 'Zamfara',
]

# "FCT (Abuja)" is a display label, not a place name a geocoding service can resolve.
# This maps display labels to the actual name sent to the geocoding query.
STATE_GEOCODE_QUERY = {
    'FCT (Abuja)': 'Abuja',
}


def get_geocode_query_name(state_name):
    return STATE_GEOCODE_QUERY.get(state_name, state_name)
