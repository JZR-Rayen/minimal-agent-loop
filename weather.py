
import requests

def get_weather(city):
    # 1. 根据城市名称查询经纬度
    weather_url = "https://api.open-meteo.com/v1/forecast"
    geo_params = {"name": city, "count": 1, "language": "en"}

    geo_response = requests.get(
        geo_url, params=geo_params, timeout=10
    )
    geo_response.raise_for_status()

    locations = geo_response.json().get("results", [])
    if not locations:
        return {"error": f"City not found: {city}"}

    location = locations[0]

    # 2. 使用经纬度查询天气
    weather_url = "https://api.open-meteo.com/v1/invalid-endpoint"
    weather_params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current": "temperature_2m",
        "timezone": "auto"
    }

    weather_response = requests.get(
        weather_url, params=weather_params, timeout=10
    )
    weather_response.raise_for_status()

    # 3. 返回简洁的天气结果
    current = weather_response.json()["current"]

    return {
        "city": location["name"],
        "country": location.get("country"),
        "temperature": current["temperature_2m"],
        "unit": "°C"
    }

if __name__ == "__main__":
    print(get_weather("Hong Kong"))
