import tkinter as tk
from tkinter import messagebox
import requests
from io import BytesIO
from PIL import Image, ImageTk
import pyperclip
from datetime import datetime
import pytz
  
 



class WeatherDataService:
    """
    选择openweathermap的免费api获取天气数据
    """
    API_KEY = "b7db408cc6fda8096048b104720f2f90"
    BASE_URL = "http://api.openweathermap.org/data/2.5/"

    def get_current_weather(self, city: str):
        """
        获取指定城市的当前天气。
        返回包含天气数据或错误消息的字典。
        """
        url = (f"{self.BASE_URL}weather?q={city}&appid={self.API_KEY}"
               "&units=metric&lang=en")
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json()}

    def get_forecast(self, city: str):
        """
        获取指定城市未来两小时内的天气预报。
        返回预报数据列表或错误消息。
        """
        url = (f"{self.BASE_URL}forecast?q={city}&appid={self.API_KEY}"
               "&units=metric&lang=en")
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data["list"][:2]
        else:
            return {"error": response.json()}




class WeatherApp:
    """
    使用Tkinter 根窗口初始化 WeatherApp。
    设置应用程序的所有 UI 元素，包括搜索栏、按钮和标签。
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Weather App")
        self.followed_window = None
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        self.weather_service = WeatherDataService()
        self.followed_cities = []
        self.weather_icon = None
        self.history = []

        #设置主页面背景颜色
        self.root.configure(bg="#f7f7f7")

        self.title_label = tk.Label(
            root, text="Weather App", font=("Arial", 20, "bold"),
            bg="#4CAF50", fg="white"
        )
        self.title_label.pack(pady=10, fill="x")

        # 城市输入框框架
        self.city_frame = tk.Frame(root, bg="#f7f7f7")
        self.city_frame.pack(pady=15)

        self.city_label = tk.Label(
            self.city_frame, text="City:", font=("Arial", 12),
            bg="#f7f7f7", fg="#333333"
        )
        self.city_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")

        self.city_entry = tk.Entry(
            self.city_frame, font=("Arial", 14), width=20,
            justify="center"
        )
        self.city_entry.grid(row=0, column=1, padx=10, pady=5)

        #搜索按钮
        self.search_button = tk.Button(
            self.city_frame, text="Search", font=("Arial", 12),
            bg="#4CAF50", fg="white", command=self.search_weather
        )
        self.search_button.grid(row=0, column=2, padx=10, pady=5)

        #查询结果框架
        self.result_frame = tk.Frame(
            root, bg="#ffffff", bd=2, relief="groove"
        )
        self.result_frame.pack(pady=15, padx=10, fill="both", expand=True)

        self.icon_label = tk.Label(self.result_frame, bg="#f7f7f7")
        self.icon_label.pack(pady=5, anchor="center")  # 修改为 anchor="center"

        self.weather_label = tk.Label(
            self.result_frame, font=("Arial", 12), bg="#ffffff", fg="#333333",
            text="Weather Information", anchor="center", justify="center"
        )
        self.weather_label.pack(padx=10, pady=10, fill="both", expand=True)

        self.weather_label.config(justify="center", state="normal")

        self.advice_label = tk.Label(
            self.result_frame, text="", font=("Arial", 12),
            wraplength=500, bg="#ffffff", fg="red", anchor="center"
        )
        self.advice_label.pack(fill="x", pady=5)

        self.button_frame = tk.Frame(root, bg="#f7f7f7")
        self.button_frame.pack(pady=10, fill="x")

        # 为每一列设置权重，使按钮居中
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)
        self.button_frame.grid_columnconfigure(2, weight=1)
        self.button_frame.grid_columnconfigure(3, weight=1)

        # 第1行：Follow 和 View Followed List 按钮
        self.follow_button = tk.Button(
            self.button_frame, text="Follow", font=("Arial", 12),
            bg="#4CAF50", fg="white", command=self.add_to_followed
        )
        self.follow_button.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        self.view_followed_button = tk.Button(
            self.button_frame, text="View Followed List",
            font=("Arial", 12), bg="#2196F3", fg="white",
            command=self.show_followed_window
        )
        self.view_followed_button.grid(row=0, column=2, padx=10, pady=5, sticky="ew")

        # 第2行：Share 和 Theme 按钮
        self.share_button = tk.Button(
            self.button_frame, text="Share", font=("Arial", 12),
            bg="#FF9800", fg="white", command=self.share_weather
        )
        self.share_button.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        self.theme_button = tk.Button(
            self.button_frame, text="Toggle Theme", font=("Arial", 12),
            bg="#FF5722", fg="white", command=self.toggle_theme
        )
        self.theme_button.grid(row=1, column=2, padx=10, pady=5, sticky="ew")

        # 第3行：History 按钮
        self.history_button = tk.Button(
            self.button_frame, text="History", font=("Arial", 12),
            bg="#607D8B", fg="white", command=self.show_history
        )
        self.history_button.grid(row=2, column=1, columnspan=2, pady=5, sticky="ew")

        # 第4行：Help 按钮
        self.help_button = tk.Button(
            self.button_frame, text="Help", font=("Arial", 12),
            bg="#8BC34A", fg="white", command=self.show_help
        )
        self.help_button.grid(row=3, column=1, columnspan=2, pady=5, sticky="ew")

    def toggle_like(self, city_data):
        """切换城市的 'liked' 状态"""
        # 如果城市已经被喜欢，取消喜欢状态；如果未被喜欢，则设置为喜欢
        city_data["liked"] = not city_data["liked"]

        # 更新已关注窗口中的喜欢状态
        if self.followed_window and self.followed_window.winfo_exists():
            self.update_followed_window()

    def show_help(self):
        help_window = tk.Toplevel(self.root)
        help_window.title("Help")
        help_window.geometry("500x300")
        tk.Label(
            help_window, text="How to use Weather App:",
            font=("Arial", 14, "bold")
        ).pack(pady=10)

        instructions = (
            "1. Enter a city name and click 'Search' to get weather data.\n"
            "2. Use 'Follow' to add a city to your followed list.\n"
            "3. View history of searched cities with 'History'.\n"
            "4. Use 'Toggle Theme' to switch between light and dark modes.\n"
            "5. Use 'Toggle Mode' to switch between simple and detailed views."
        )
        tk.Label(help_window, text=instructions, font=("Arial", 12), wraplength=400).pack(pady=10)

    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Weather Search History")
        history_window.geometry("400x300")

        for record in self.history:
            tk.Label(
                history_window,
                text=f"City: {record['city']} | Time: {record['timestamp']}",
                font=("Arial", 10)
            ).pack(pady=5)


    def toggle_theme(self):
        if self.root["bg"] == "#f7f7f7":
            self.root.configure(bg="#333333")
            self.title_label.configure(bg="#444444", fg="white")
            self.result_frame.configure(bg="#444444")
            self.weather_label.configure(bg="#333333", fg="white")
            self.advice_label.configure(bg="#444444", fg="lightgreen")
        else:
            self.root.configure(bg="#f7f7f7")
            self.title_label.configure(bg="#4CAF50", fg="white")
            self.result_frame.configure(bg="#ffffff")
            self.weather_label.configure(bg="#f7f7f7", fg="#333333")
            self.advice_label.configure(bg="#f7f7f7", fg="red")

    def search_weather(self):
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showerror("Error", "Please enter a city name!")
            return

        # 获取当前天气数据
        current_weather = self.weather_service.get_current_weather(city)
        if "error" in current_weather:
            messagebox.showerror(
                "Error",
                f"Failed to get weather: {current_weather['error']['message']}"
            )
            return

        # 获取天气预报数据
        forecast_data = self.weather_service.get_forecast(city)
        if "error" in forecast_data:
            messagebox.showerror(
                "Error",
                f"Failed to get forecast: {forecast_data['error']['message']}"
            )
            return

        # 格式化天气信息
        weather_info, icon_url, advice = self.format_weather_info(
            current_weather, forecast_data
        )

        # 更新天气信息标签
        self.weather_label.config(text=weather_info)

        # 更新出行建议标签
        self.advice_label.config(text=advice)

        # 获取并更新天气图标
        icon_data = requests.get(icon_url).content
        image = Image.open(BytesIO(icon_data))
        image = image.resize((100, 100), Image.Resampling.LANCZOS)
        self.weather_icon = ImageTk.PhotoImage(image)
        self.icon_label.config(image=self.weather_icon)

        # 添加到历史记录
        self.add_to_history(city)



    def add_to_history(self, city):
        """
        将搜索的城市及其时间戳添加到搜索历史记录中。
        参数：
        city (str)：要添加到历史记录的城市名称。
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append({"city": city, "timestamp": timestamp})



    def format_weather_info(self, current_weather, forecast_data):
        """
        将当前天气和预报数据格式化为人类可读的字符串。
        参数：
        current_weather (dict)：从 API 获取的当前天气数据。
        Forecast_data (list)：从 API 获取的未来 2 小时的预报数据。

        返回：
        tuple：包含以下内容的元组：
        - current_info (str)：包含当前天气信息的字符串。
        - icon_url (str)：天气图标的 URL。
        - Advice (str)：基于天气的旅行建议。
        """



        def convert_utc_to_beijing(utc_time_str):
            """
            将 UTC 时间字符串转换为北京时间。
            参数：
            utc_time_str (str)：UTC 时间字符串，格式为“YYYY-MM-DD HH:MM:SS”。
            返回：
            str：转换后的北京时间，格式为“YYYY-MM-DD HH:MM:SS”。
            """
            utc_zone = pytz.utc
            beijing_zone = pytz.timezone('Asia/Shanghai')
            utc_time = datetime.strptime(
                utc_time_str, "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=utc_zone)
            beijing_time = utc_time.astimezone(beijing_zone)
            return beijing_time.strftime("%Y-%m-%d %H:%M:%S")

        weather_desc = current_weather["weather"][0]["description"]
        temp = current_weather["main"]["temp"]
        humidity = current_weather["main"]["humidity"]
        icon_code = current_weather["weather"][0]["icon"]
        city = current_weather["name"]

        current_info = (
            f"City: {city}\nCurrent Weather: {weather_desc}\n"
            f"Temperature: {temp}°C\nHumidity: {humidity}%\n"
        )

        forecast_info = "2-Hour Forecast:\n"
        for item in forecast_data:
            time = convert_utc_to_beijing(item["dt_txt"])
            desc = item["weather"][0]["description"]
            temp = item["main"]["temp"]
            forecast_info += (
                f"- Time: {time}, Weather: {desc}, "
                f"Temperature: {temp}°C\n"
            )

        advice = "Travel Advice:\n"
        if "rain" in weather_desc.lower():
            advice += "- Bring an umbrella.\n"
        if temp < 10:
            advice += "- Wear warm clothes.\n"
        elif temp > 30:
            advice += "- Stay hydrated.\n"

        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

        return current_info + forecast_info, icon_url, advice




    def share_weather(self):
        """
        将当前查询到的天气信息复制到剪贴板，以便用户在社交媒体上分享。
        如果没有可用的天气信息，则显示错误消息。
        """
        weather_text = self.weather_label.cget("text").strip()

        if weather_text:
            pyperclip.copy(f"Check out the weather: \n{weather_text}")
            messagebox.showinfo(
                "Share", "Weather information has been copied to your clipboard,"
                         "You can paste it to social media!"
            )
        else:
            messagebox.showerror("Error", "No weather information to share!")




    def add_to_followed(self):
        """
        将查询的城市添加到关注的城市列表中。
        如果该城市已在列表中，则弹出提示框。
        """
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showerror("Error", "Please enter a city name!")
            return

        for followed in self.followed_cities:
            if followed["name"] == city:
                messagebox.showinfo(
                    "Info", f"{city} is already in the followed list!"
                )
                return

        self.followed_cities.append({"name": city, "liked": False})
        messagebox.showinfo("Success", f"{city} has been added to the followed list!")

        if self.followed_window and self.followed_window.winfo_exists():
            self.update_followed_window()




    def remove_from_followed(self, city_data):
        """
        从关注的城市列表中删除一个城市。
        参数：
        city_data (dict)：要从关注的城市列表中删除的城市数据。
        """
        response = messagebox.askyesno(
            "Confirm", f"Are you sure you want to remove {city_data['name']} from the followed list?"
        )
        if response:
            self.followed_cities.remove(city_data)
            messagebox.showinfo("Success", f"{city_data['name']} has been removed from the followed list.")
            self.update_followed_window()




    def show_followed_window(self):
        """
        显示关注城市列表的窗口。
        如果窗口已打开，则将其置于最前。
        """
        if self.followed_window and self.followed_window.winfo_exists():
            self.followed_window.lift()
            return

        self.followed_window = tk.Toplevel(self.root)
        self.followed_window.title("Followed Cities")
        self.followed_window.geometry("400x500")
        self.update_followed_window()





    def show_city_weather(self, city):
        """
        点击对应城市名显示该城市的天气信息。
        """
        current_weather = self.weather_service.get_current_weather(city)
        if "error" in current_weather:
            messagebox.showerror(
                "Error",
                f"Failed to get weather: {current_weather['error']['message']}"
            )
            return

        forecast_data = self.weather_service.get_forecast(city)
        if "error" in forecast_data:
            messagebox.showerror(
                "Error",
                f"Failed to get forecast: {forecast_data['error']['message']}"
            )
            return

        weather_info, icon_url, advice = self.format_weather_info(
            current_weather, forecast_data
        )

        self.weather_label.config(text=weather_info)

        self.advice_label.config(text=advice)

        icon_data = requests.get(icon_url).content
        image = Image.open(BytesIO(icon_data))
        image = image.resize((100, 100), Image.Resampling.LANCZOS)
        self.weather_icon = ImageTk.PhotoImage(image)
        self.icon_label.config(image=self.weather_icon)

        self.add_to_history(city)





    def update_followed_window(self):
        """
        更新已打开的关注城市列表窗口。
        每个城市都有查看天气、喜欢或删除的选项。
        """
        for widget in self.followed_window.winfo_children():
            widget.destroy()

        label = tk.Label(
            self.followed_window, text="Followed Cities:",
            font=("Arial", 14, "bold")
        )
        label.pack(pady=10)

        for city_data in self.followed_cities:
            frame = tk.Frame(self.followed_window)
            frame.pack(pady=5, fill="x")

            city_name = f"{city_data['name']} {'❤️' if city_data['liked'] else ''}"
            city_button = tk.Button(
                frame, text=city_name, font=("Arial", 12), width=20,
                command=lambda c=city_data['name']: self.show_city_weather(c)
            )
            city_button.pack(side="left", padx=5)

            like_button = tk.Button(
                frame, text="Like", font=("Arial", 10), width=8,
                command=lambda c=city_data: self.toggle_like(c)
            )
            like_button.pack(side="left", padx=5)

            remove_button = tk.Button(
                frame, text="Remove", font=("Arial", 10), width=8,
                command=lambda c=city_data: self.remove_from_followed(c)
            )
            remove_button.pack(side="left", padx=5)



if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
