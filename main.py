import requests

class WeatherDataService:
    API_KEY = "b7db408cc6fda8096048b104720f2f90"
    BASE_URL = "http://api.openweathermap.org/data/2.5/"

    def get_current_weather(self, city: str):
        url = f"{self.BASE_URL}weather?q={city}&appid={self.API_KEY}&units=metric&lang=zh_cn"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json()}

    def get_forecast(self, city: str):
        url = f"{self.BASE_URL}forecast?q={city}&appid={self.API_KEY}&units=metric&lang=zh_cn"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data["list"][:2]
        else:
            return {"error": response.json()}

class UserInterface:
    def display_weather(self, weather_data):

        if "error" in weather_data:
            print("获取天气信息失败：", weather_data["error"]["message"])
        else:
            print(f"城市：{weather_data['name']}")
            print(f"天气：{weather_data['weather'][0]['description']}")
            print(f"温度：{weather_data['main']['temp']}°C")
            print(f"湿度：{weather_data['main']['humidity']}%")

    def display_forecast(self, forecast_data):

        if "error" in forecast_data:
            print("获取天气预测失败：", forecast_data["error"]["message"])
        else:
            print("未来2小时天气预测：")
            for item in forecast_data:
                print(f"时间：{item['dt_txt']}, 天气：{item['weather'][0]['description']}, 温度：{item['main']['temp']}°C")

    def get_user_input(self):

        return input("请输入城市名称：")

class NotificationService:
    def send_weather_alert(self, alert: str):

        print(f"天气警报：{alert}")

class RecommendationService:
    def generate_recommendations(self, weather_data):

        if "error" in weather_data:
            return "无法提供建议，请检查天气信息。"
        weather = weather_data["weather"][0]["main"]
        if weather == "Rain":
            return "建议带伞，避免被雨淋。"
        elif weather == "Clear":
            return "天气晴朗，适合外出。"
        elif weather == "Snow":
            return "建议穿戴保暖衣物，注意道路结冰。"
        else:
            return "天气多变，请注意安全。"

if __name__ == "__main__":
    weather_service = WeatherDataService()
    ui = UserInterface()
    notification_service = NotificationService()
    recommendation_service = RecommendationService()

    city = ui.get_user_input()

    current_weather = weather_service.get_current_weather(city)
    ui.display_weather(current_weather)

    forecast_data = weather_service.get_forecast(city)
    ui.display_forecast(forecast_data)

    recommendation = recommendation_service.generate_recommendations(current_weather)
    notification_service.send_weather_alert(recommendation)
