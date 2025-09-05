import threading
import time
import requests
import customtkinter as ctk
from urllib.parse import urlparse
import statistics
import random
import socket
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from collections import deque

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ModernSpeedTestApp:
    def __init__(self):
        self.results_available = False
        self.test_in_progress = False
        self.test_duration = 15
        self.active_threads = 0
        self.download_speeds = []
        self.upload_speeds = []
        self.ping_results = []
        self.test_start_time = 0

        self.graph_data = {
            'time': deque(maxlen=100),
            'download': deque(maxlen=100),
            'upload': deque(maxlen=100)
        }
        
        self.root = ctk.CTk()
        self.root.title("Network SpeedTest Pro")
        self.root.geometry("700x750")
        self.root.minsize(650, 700)

        self.create_widgets()

        self.update_ui()
        
    def create_widgets(self):
        self.main_frame = ctk.CTkScrollableFrame(self.root, width=650, height=700)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.title_frame.pack(pady=(10, 20), fill="x")
        
        self.title_label = ctk.CTkLabel(
            self.title_frame, 
            text="🌐 Network SpeedTest Pro",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=5)
        
        self.subtitle_label = ctk.CTkLabel(
            self.title_frame,
            text="Измерение скорости интернета с максимальной точностью",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.subtitle_label.pack()

        self.control_frame = ctk.CTkFrame(self.main_frame, height=80)
        self.control_frame.pack(pady=(0, 15), fill="x")

        self.duration_frame = ctk.CTkFrame(self.control_frame, fg_color="transparent")
        self.duration_frame.pack(side="left", padx=20, pady=15)
        
        ctk.CTkLabel(self.duration_frame, text="Длительность теста:", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.duration_slider = ctk.CTkSlider(
            self.duration_frame, 
            from_=5, to=30, 
            number_of_steps=25,
            width=150,
            command=self.update_duration_label
        )
        self.duration_slider.set(self.test_duration)
        self.duration_slider.pack(pady=(5, 0))
        
        self.duration_label = ctk.CTkLabel(
            self.duration_frame, 
            text=f"{self.test_duration} сек",
            font=ctk.CTkFont(size=11)
        )
        self.duration_label.pack()

        self.button_frame = ctk.CTkFrame(self.control_frame, fg_color="transparent")
        self.button_frame.pack(side="right", padx=20, pady=15)
        
        self.test_button = ctk.CTkButton(
            self.button_frame,
            text="🚀 Начать тест",
            command=self.start_test,
            width=120,
            height=35,
            fg_color="#2AA876",
            hover_color="#22865F"
        )
        self.test_button.pack(side="left", padx=5)
        
        self.stop_button = ctk.CTkButton(
            self.button_frame,
            text="⏹️ Остановить",
            command=self.stop_test,
            width=120,
            height=35,
            fg_color="#D9534F",
            hover_color="#C9302C",
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=5)

        self.progress_frame = ctk.CTkFrame(self.main_frame)
        self.progress_frame.pack(pady=(0, 20), fill="x", padx=5)
        
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="Готов к тестированию",
            font=ctk.CTkFont(size=14),
            text_color="lightblue"
        )
        self.progress_label.pack(pady=(15, 10))
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, height=20)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(0, 10), padx=20, fill="x")
        
        self.stats_frame = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
        self.stats_frame.pack(pady=(0, 15), fill="x", padx=20)
        
        self.time_label = ctk.CTkLabel(
            self.stats_frame,
            text="Осталось: -/- сек",
            font=ctk.CTkFont(size=12)
        )
        self.time_label.pack(side="left")
        
        self.threads_label = ctk.CTkLabel(
            self.stats_frame,
            text="Потоков: 0",
            font=ctk.CTkFont(size=12)
        )
        self.threads_label.pack(side="right")

        self.results_frame = ctk.CTkFrame(self.main_frame)
        self.results_frame.pack(pady=(0, 20), fill="x", padx=5)
        
        ctk.CTkLabel(
            self.results_frame, 
            text="Результаты теста",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=15)

        self.results_grid = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        self.results_grid.pack(pady=(0, 15), fill="x", padx=20)

        self.download_card = ctk.CTkFrame(self.results_grid, width=180, height=120)
        self.download_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(
            self.download_card, 
            text="📥 Скачивание",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 5))
        
        self.download_value = ctk.CTkLabel(
            self.download_card,
            text="- Мбит/с",
            font=ctk.CTkFont(size=18)
        )
        self.download_value.pack(pady=5)
        
        self.download_status = ctk.CTkLabel(
            self.download_card,
            text="ожидание",
            font=ctk.CTkFont(size=12)
        )
        self.download_status.pack(pady=(0, 10))

        self.upload_card = ctk.CTkFrame(self.results_grid, width=180, height=120)
        self.upload_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(
            self.upload_card, 
            text="📤 Загрузка",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 5))
        
        self.upload_value = ctk.CTkLabel(
            self.upload_card,
            text="- Мбит/с",
            font=ctk.CTkFont(size=18)
        )
        self.upload_value.pack(pady=5)
        
        self.upload_status = ctk.CTkLabel(
            self.upload_card,
            text="ожидание",
            font=ctk.CTkFont(size=12)
        )
        self.upload_status.pack(pady=(0, 10))

        self.ping_card = ctk.CTkFrame(self.results_grid, width=180, height=120)
        self.ping_card.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(
            self.ping_card, 
            text="📶 Пинг",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 5))
        
        self.ping_value = ctk.CTkLabel(
            self.ping_card,
            text="- мс",
            font=ctk.CTkFont(size=18)
        )
        self.ping_value.pack(pady=5)
        
        self.ping_status = ctk.CTkLabel(
            self.ping_card,
            text="ожидание",
            font=ctk.CTkFont(size=12)
        )
        self.ping_status.pack(pady=(0, 10))

        self.results_grid.grid_columnconfigure(0, weight=1)
        self.results_grid.grid_columnconfigure(1, weight=1)
        self.results_grid.grid_columnconfigure(2, weight=1)

        self.graph_frame = ctk.CTkFrame(self.main_frame, height=200)
        self.graph_frame.pack(pady=(0, 20), fill="x", padx=5)
        
        ctk.CTkLabel(
            self.graph_frame, 
            text="График скорости в реальном времени",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)

        self.fig = Figure(figsize=(6, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#2B2B2B')
        self.fig.patch.set_facecolor('#2B2B2B')
        self.ax.tick_params(colors='white')
        for spine in self.ax.spines.values():
            spine.set_color('#444444')

        self.line_download, = self.ax.plot([], [], label='Скачивание', color='#4CC9F0')
        self.line_upload, = self.ax.plot([], [], label='Загрузка', color='#F72585')
        self.ax.legend(facecolor='#2B2B2B', edgecolor='#444444', labelcolor='white')
        self.ax.set_ylabel('Мбит/с', color='white')
        self.ax.set_xlabel('Время (сек)', color='white')
        self.ax.set_ylim(0, 100)
        
        self.canvas = FigureCanvasTkAgg(self.fig, self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.assessment_frame = ctk.CTkFrame(self.main_frame)
        self.assessment_frame.pack(pady=(0, 20), fill="x", padx=5)
        
        ctk.CTkLabel(
            self.assessment_frame, 
            text="Общая оценка качества соединения",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=15)
        
        self.assessment_label = ctk.CTkLabel(
            self.assessment_frame,
            text="Ожидание результатов...",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        self.assessment_label.pack(pady=(0, 15))

        self.history_frame = ctk.CTkFrame(self.main_frame)
        self.history_frame.pack(pady=(0, 20), fill="x", padx=5)
        
        ctk.CTkLabel(
            self.history_frame, 
            text="История тестов",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=15)
        
        self.history_text = ctk.CTkTextbox(
            self.history_frame, 
            height=80,
            font=ctk.CTkFont(size=12)
        )
        self.history_text.pack(pady=(0, 15), padx=15, fill="x")
        self.history_text.insert("1.0", "Дата и время\tСкачивание\tЗагрузка\tПинг\n")
        self.history_text.configure(state="disabled")
        
        self.footer_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.footer_frame.pack(pady=20)
        
        ctk.CTkLabel(
            self.footer_frame,
            text="Network SpeedTest Pro v2.0 • © 2025",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack()

        ctk.CTkLabel(
            self.footer_frame,
            text="Разработано: StalsCat",
            font=ctk.CTkFont(size=10),
            text_color="lightblue"
        ).pack(pady=(5, 0))
        
    def update_duration_label(self, value):
        self.test_duration = int(value)
        self.duration_label.configure(text=f"{self.test_duration} сек")
        
    def update_ui(self):
        """Обновление элементов UI"""
        if self.test_in_progress:
            elapsed = time.time() - self.test_start_time
            remaining = max(0, self.test_duration - elapsed)
            self.time_label.configure(text=f"Осталось: {remaining:.1f}/{self.test_duration} сек")
            self.progress_bar.set(elapsed / self.test_duration)
            self.threads_label.configure(text=f"Потоков: {threading.active_count() - 1}")

            if self.graph_data['time']:
                self.line_download.set_data(self.graph_data['time'], self.graph_data['download'])
                self.line_upload.set_data(self.graph_data['time'], self.graph_data['upload'])

                if self.graph_data['download'] or self.graph_data['upload']:
                    all_speeds = list(self.graph_data['download']) + list(self.graph_data['upload'])
                    max_speed = max(all_speeds) if all_speeds else 100
                    self.ax.set_ylim(0, max_speed * 1.1)
                
                if self.graph_data['time']:
                    self.ax.set_xlim(min(self.graph_data['time']), max(self.graph_data['time']))
                
                self.canvas.draw()
        
        self.root.after(100, self.update_ui)
        
    def get_speed_color(self, speed_mbps, is_download=True):
        """Определяет цвет в зависимости от скорости"""
        if is_download:
            if speed_mbps > 50: return "#4CC9F0"
            elif speed_mbps > 20: return "#F9C74F"
            else: return "#F94144"
        else:
            if speed_mbps > 10: return "#4CC9F0"
            elif speed_mbps > 5: return "#F9C74F"
            else: return "#F94144"
    
    def get_ping_color(self, ping_ms):
        """Определяет цвет в зависимости от пинга"""
        if ping_ms < 50: return "#4CC9F0"
        elif ping_ms < 100: return "#F9C74F"
        else: return "#F94144"
    
    def get_quality_assessment(self, download_speed, upload_speed, ping):
        """Определяет общую оценку качества соединения"""
        score = 0

        if download_speed > 50: score += 3
        elif download_speed > 20: score += 2
        elif download_speed > 5: score += 1

        if upload_speed > 10: score += 3
        elif upload_speed > 5: score += 2
        elif upload_speed > 2: score += 1

        if ping < 100: score += 3
        elif ping < 175: score += 2
        elif ping < 250: score += 1

        if score >= 7: return ("Отлично 🌟", "#4CC9F0")
        elif score >= 4: return ("Нормально 👍", "#F9C74F")
        else: return ("Плохо 👎", "#F94144")
    
    def update_results(self):
        if not self.results_available:
            return
            
        download_speed = statistics.mean(self.download_speeds) / 10**6
        upload_speed = statistics.mean(self.upload_speeds) / 10**6
        ping = statistics.mean(self.ping_results)

        download_color = self.get_speed_color(download_speed, True)
        upload_color = self.get_speed_color(upload_speed, False)
        ping_color = self.get_ping_color(ping)

        self.download_value.configure(
            text=f"{download_speed:.1f} Мбит/с", 
            text_color=download_color
        )
        self.upload_value.configure(
            text=f"{upload_speed:.1f} Мбит/с", 
            text_color=upload_color
        )
        self.ping_value.configure(
            text=f"{ping:.1f} мс", 
            text_color=ping_color
        )

        self.download_status.configure(
            text="✓ завершено" if download_speed > 0 else "✗ ошибка",
            text_color=download_color
        )
        self.upload_status.configure(
            text="✓ завершено" if upload_speed > 0 else "✗ ошибка",
            text_color=upload_color
        )
        self.ping_status.configure(
            text="✓ завершено" if ping > 0 else "✗ ошибка",
            text_color=ping_color
        )

        quality_text, quality_color = self.get_quality_assessment(download_speed, upload_speed, ping)
        self.assessment_label.configure(
            text=quality_text, 
            text_color=quality_color
        )

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.history_text.configure(state="normal")
        self.history_text.insert("2.0", 
            f"{timestamp}\t{download_speed:.1f} Мбит/с\t{upload_speed:.1f} Мбит/с\t{ping:.1f} мс\n")
        self.history_text.configure(state="disabled")
        
        self.progress_label.configure(text="Тест завершен!", text_color="#4CC9F0")
        self.test_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.progress_bar.set(1.0)
        
    def measure_ping(self, url):
        try:
            domain = urlparse(url).netloc
            if not domain:
                domain = url
                
            start_time = time.time()
            try:
                ip = socket.gethostbyname(domain)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)
                s.connect((ip, 80))
                s.close()
            except:
                socket.gethostbyname(domain)
                
            return (time.time() - start_time) * 1000
        except:
            return None
            
    def download_worker(self, url, results_list, start_time, duration):
        """Поток для скачивания данных"""
        try:
            while time.time() - start_time < duration and self.test_in_progress:
                try:
                    chunk_start_time = time.time()
                    response = requests.get(url, stream=True, timeout=10)
                    response.raise_for_status()
                    
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if not self.test_in_progress or time.time() - start_time >= duration:
                            break
                            
                        downloaded += len(chunk)
                        chunk_elapsed_time = time.time() - chunk_start_time
                        
                        if chunk_elapsed_time > 0.5:
                            speed = downloaded / chunk_elapsed_time
                            speed_bits = speed * 8
                            results_list.append(speed_bits)
                            
                            elapsed = time.time() - self.test_start_time
                            speed_mbps = speed_bits / 10**6
                            
                            self.root.after(0, self.add_graph_point, elapsed, speed_mbps, 'download')
                            break
                        
                except Exception as e:
                    time.sleep(0.5)
                    continue
                    
        except Exception as e:
            pass
            
    def upload_worker(self, url, results_list, start_time, duration):
        """Поток для загрузки данных"""
        try:
            data_size = random.randint(512 * 1024, 2048 * 1024)
            test_data = b"0" * data_size
            
            while time.time() - start_time < duration and self.test_in_progress:
                try:
                    upload_start_time = time.time()
                    response = requests.post(url, data=test_data, timeout=10)
                    response.raise_for_status()
                    
                    upload_elapsed_time = time.time() - upload_start_time
                    if upload_elapsed_time > 0:
                        speed = len(test_data) / upload_elapsed_time
                        speed_bits = speed * 8
                        results_list.append(speed_bits)

                        elapsed = time.time() - self.test_start_time
                        speed_mbps = speed_bits / 10**6

                        self.root.after(0, self.add_graph_point, elapsed, speed_mbps, 'upload')
                        
                    time.sleep(0.2)
                        
                except Exception as e:
                    time.sleep(0.5)
                    continue
                    
        except Exception as e:
            pass
            
    def add_graph_point(self, time_val, speed_val, graph_type):
        """Добавляет точку на график (вызывается из главного потока)"""
        self.graph_data['time'].append(time_val)
        if graph_type == 'download':
            self.graph_data['download'].append(speed_val)
            self.graph_data['upload'].append(0)
        else:
            self.graph_data['upload'].append(speed_val)
            self.graph_data['download'].append(0)
            
    def ping_worker(self, urls, results_list, start_time, duration):
        """Поток для измерения пинга"""
        try:
            while time.time() - start_time < duration and self.test_in_progress:
                for url in urls:
                    if not self.test_in_progress or time.time() - start_time >= duration:
                        break
                        
                    ping = self.measure_ping(url)
                    if ping is not None:
                        results_list.append(ping)
                        
                    time.sleep(1)
                    
        except Exception as e:
            pass
        
    def run_test(self):
        try:
            self.test_in_progress = True
            self.test_start_time = time.time()

            self.graph_data['time'].clear()
            self.graph_data['download'].clear()
            self.graph_data['upload'].clear()

            self.download_speeds = []
            self.upload_speeds = []
            self.ping_results = []

            download_urls = [
                "https://proof.ovh.net/files/10Mb.dat",
                "http://ipv4.download.thinkbroadband.com/10MB.zip",
                "http://speedtest.tele2.net/10MB.zip",
                "http://test.download.net/10MB.zip",
            ]
            
            upload_urls = [
                "https://httpbin.org/post",
                "https://postman-echo.com/post",
                "https://ptsv2.com/t/post",
            ]
            
            ping_urls = [
                "https://www.google.com",
                "https://www.yandex.ru",
                "https://www.cloudflare.com",
            ]

            threads = []

            for i in range(3):
                url = download_urls[i % len(download_urls)]
                thread = threading.Thread(
                    target=self.download_worker, 
                    args=(url, self.download_speeds, self.test_start_time, self.test_duration)
                )
                thread.daemon = True
                thread.start()
                threads.append(thread)

            for i in range(2):
                url = upload_urls[i % len(upload_urls)]
                thread = threading.Thread(
                    target=self.upload_worker, 
                    args=(url, self.upload_speeds, self.test_start_time, self.test_duration)
                )
                thread.daemon = True
                thread.start()
                threads.append(thread)

            for i in range(1):
                thread = threading.Thread(
                    target=self.ping_worker, 
                    args=(ping_urls, self.ping_results, self.test_start_time, self.test_duration)
                )
                thread.daemon = True
                thread.start()
                threads.append(thread)

            while time.time() - self.test_start_time < self.test_duration and self.test_in_progress:
                time.sleep(0.1)

            for thread in threads:
                thread.join(timeout=2)

            if not self.download_speeds:
                self.download_speeds = [0]
            if not self.upload_speeds:
                self.upload_speeds = [0]
            if not self.ping_results:
                self.ping_results = [0]
                
            self.results_available = True
            self.root.after(0, self.update_results)
            
        except Exception as e:
            self.root.after(0, lambda: self.progress_label.configure(text=f"Ошибка: {str(e)}", text_color="#F94144"))
        finally:
            self.test_in_progress = False
        
    def start_test(self):
        self.results_available = False
        self.test_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.progress_label.configure(text="Подготовка к тесту...", text_color="lightblue")
        self.progress_bar.set(0)

        self.download_value.configure(text="- Мбит/с", text_color="white")
        self.upload_value.configure(text="- Мбит/с", text_color="white")
        self.ping_value.configure(text="- мс", text_color="white")
        
        self.download_status.configure(text="ожидание", text_color="white")
        self.upload_status.configure(text="ожидание", text_color="white")
        self.ping_status.configure(text="ожидание", text_color="white")
        
        self.assessment_label.configure(text="Ожидание результатов...", text_color="gray")
        
        self.test_thread = threading.Thread(target=self.run_test)
        self.test_thread.daemon = True
        self.test_thread.start()
        
    def stop_test(self):
        self.test_in_progress = False
        self.progress_label.configure(text="Тест остановлен", text_color="#F9C74F")
        self.test_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

if __name__ == "__main__":
    app = ModernSpeedTestApp()
    app.root.mainloop()