"""
A weather app practicing Secret APIs. 


Geocoding location name
http://api.openweathermap.org/geo/1.0/direct?q=Minneapolis&limit=1&appid={API_KEY}  # This limits to the first match.   This is for simplicity right now. 

http://api.openweathermap.org/geo/1.0/direct?q={city name},{state code},{country code}&limit={limit}&appid={API key} 


Using coordinates to get weather: 
https://api.openweathermap.org/data/2.5/weather?lat=82&lon=56&units=imperial&appid={API_KEY}




"""
from pprint import pprint
from datetime import datetime
import requests, os, logging

logging.basicConfig(level=logging.WARNING, format=f'%(asctime)s - %(name)s - %(levelname)s - %(message)s')

key = os.environ.get('WEATHER_KEY')

url = 'http://api.openweathermap.org/geo/1.0/direct?'
query = {'q': 'Minneapolis', 'limit':1, 'appid':key}

data = requests.get(url, params=query).json()

# pprint(data)

def main():
    while True:
        city = get_user_city()
        lat_long, api_place, value_error, other_error = get_latitude_longitude(city)

        if value_error:
            pass # Loop back
        elif other_error:
            print(other_error)
            print('\tExiting program....')
            return
        else: 
            break

    
    units = get_user_units_preference()
    weather, error = get_weather(lat_long, units)

    if error:
        # TODO error handling
        return
    
    forecasts = process_weather(weather)

    display_forecast_list_to_user(forecasts, api_place, units)
    # pprint(forecast)

    
def get_user_city():
    city = input("Please enter the city you want to get weather for: ")
    return city.capitalize()  # API seems to like capitalized cities

def get_user_units_preference():
    unit_prefs = None
    while True:
        while True:
            try: units_choice = int(input(f'Units preference? -- Input (1) for Metric, or (2) for Imperial: '))
            except ValueError: 
                print('\tPlease try again.')
            else:  # Executes with no error in "try"
                break
        
        if units_choice == 1:
            unit_prefs = 'metric'
            break
        elif units_choice == 2:
            unit_prefs = 'imperial'
            break
        else:
            print('\tPlease try again.')
            pass
    
    return unit_prefs

def get_latitude_longitude(city):
    try:
        url = 'http://api.openweathermap.org/geo/1.0/direct?'
        query = {'q': city, 'limit':1, 'appid':key} # Return only first result

        data = requests.get(url, params=query).json()  
        logging.debug(data) 
        if data == []: # API Returns [] if no city could be found. 
            raise ValueError
    except ValueError as ve:
        print(f'\tCity search for "{city}" returned no results. Please try again')
        logging.info(f'Invalid search query "{city}", should loop back. -- {ve}')
        return None, None, True, None
    except Exception as e:
        error = f'An exception has occurred - {e}'
        logging.exception(e)
        logging.error('An exception has occurred') 
        return None, None, None, error
    else:
        latitude = data[0]['lat']
        longitude = data[0]['lon']
        lat_long = [latitude, longitude]
        api_city = data[0]['name']
        api_state = data[0]['state']
        api_country = data[0]['country']
        api_place = f'{api_city}, {api_state}; located in {api_country}'
        logging.debug(lat_long)
        return lat_long, api_place, None, None

def get_weather(lat_long, units):
    latitude = lat_long[0]
    longitude = lat_long[1]

    try: 
        url = 'https://api.openweathermap.org/data/2.5/forecast?'
        query =  {'lat': latitude, 'lon': longitude, 'units':units, 'appid':key}
        data = requests.get(url, params=query).json() # 40 3-hour periods in 5 days
        logging.debug(data)
        return data, None
    except Exception as e:
        logging.exception(e)
        logging.error('An exception has occurred')
        error = 'An exception has occurred'
        return None, error

def process_weather(weather):
    """
    This method iterates over the weather dictionary to get the following in a list 
    for every 3 hours in a 5 day period:
      - temperature (˚C or ˚F)
      - Weather Description
      - Wind Speed (km/h or mi/h)
    param: weather - dictionary of weather forecast from API
    returns: forecast - a dictionary of above relevant data
    """
    forecasts = weather['list']
    compiled_weather_forecast = []

    # Build a list of lists with the following format to display to user later
    # [[date, temperature, description, wind_speed], [...]]
    for forecast in forecasts:
        this_weather_forecast = []

        this_weather_forecast.append(forecast['dt_txt'])
        this_weather_forecast.append(forecast['main']['temp'])

        #  Sample data for 'weather': [{'description': 'scattered clouds',
            #   'icon': '03d',
            #   'id': 802,
            #   'main': 'Clouds'}],
        this_weather_forecast.append(forecast['weather'][0]['description'])
        this_weather_forecast.append(forecast['wind']['speed'])
        
        compiled_weather_forecast.append(this_weather_forecast)
    return compiled_weather_forecast

def print_title_bar(message):
    title = f'*   {message}   *' 
    stars = '*' * len(title)
    print(f'\n{stars}\n{title}\n{stars}')

def print_four_column_row(c1, c2, c3, c4):
    print (f'{c1}  ---  {c2}  ---  {c3}  --  {c4}')

def display_forecast_list_to_user(forecast_list, city, units):
    print_title_bar(f'The 5 Day forecast for the city of {city}')
    print_four_column_row('Date and Time   ', 'Temperature', 'Description', 'Wind Speed')

    wind_units = ''
    temperature_units = ''
    if units == 'metric':
        wind_units = 'km/h'
        temperature_units = '˚C'
    elif units == 'imperial':
        wind_units = 'mi/h'
        temperature_units = '˚F'

    for forecast in forecast_list:
        date_and_time_of_forecast = forecast[0]
        temperature = str(forecast[1]) + ' ' + temperature_units
        description = forecast[2]
        wind_speed = str(forecast[3]) + ' ' + wind_units

        print_four_column_row(date_and_time_of_forecast, temperature, description, wind_speed)




main()

