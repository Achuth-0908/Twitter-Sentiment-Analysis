import tkinter as tk
from tkinter import ttk, messagebox
import tweepy
from textblob import TextBlob
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
from datetime import datetime

class TwitterSentimentGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Twitter Sentiment Analysis")
        self.root.geometry("1000x800")
        self.root.configure(bg="#f0f2f5")
        
        self.setup_styles()
        self.create_main_layout()
        self.setup_rate_limit_tracking()
        self.client = self.authenticate_twitter_api()

    def setup_styles(self):
        style = ttk.Style()
        style.configure("Title.TLabel", 
                       font=("Helvetica", 24, "bold"), 
                       foreground="#1DA1F2")
        style.configure("Subtitle.TLabel", 
                       font=("Helvetica", 12),
                       foreground="#657786")
        style.configure("Search.TButton", 
                       font=("Helvetica", 12, "bold"),
                       padding=10)
        style.configure("Status.TLabel",
                       font=("Helvetica", 10),
                       foreground="#657786")

    def create_main_layout(self):
        self.main_frame = ttk.Frame(self.root, padding="30")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Header Section
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = ttk.Label(
            header_frame,
            text="Twitter Sentiment Analysis",
            style="Title.TLabel"
        )
        title_label.pack()

        subtitle_label = ttk.Label(
            header_frame,
            text="Analyze the sentiment of tweets in real-time",
            style="Subtitle.TLabel"
        )
        subtitle_label.pack(pady=(5, 0))

        # Input Section
        self.input_frame = ttk.LabelFrame(
            self.main_frame, 
            text="Search Parameters", 
            padding="20"
        )
        self.input_frame.pack(fill=tk.X, pady=(0, 20))

        # Search Term
        search_frame = ttk.Frame(self.input_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Search Term:").pack(side=tk.LEFT)
        self.search_term = ttk.Entry(search_frame, width=50, font=("Helvetica", 11))
        self.search_term.pack(side=tk.LEFT, padx=(10, 0))

        # Controls Frame
        controls_frame = ttk.Frame(self.input_frame)
        controls_frame.pack(fill=tk.X, pady=(10, 0))

        # Tweet Count
        count_frame = ttk.Frame(controls_frame)
        count_frame.pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(count_frame, text="Number of Tweets:").pack(side=tk.LEFT)
        self.tweet_count = ttk.Spinbox(
            count_frame, 
            from_=1, 
            to=100, 
            width=5,
            font=("Helvetica", 11)
        )
        self.tweet_count.pack(side=tk.LEFT, padx=(10, 0))
        self.tweet_count.set("30")

        # Language Selection
        lang_frame = ttk.Frame(controls_frame)
        lang_frame.pack(side=tk.LEFT)
        ttk.Label(lang_frame, text="Language:").pack(side=tk.LEFT)
        self.language = ttk.Combobox(
            lang_frame,
            values=["English (en)", "Spanish (es)", "French (fr)", "All"],
            width=15,
            font=("Helvetica", 11)
        )
        self.language.pack(side=tk.LEFT, padx=(10, 0))
        self.language.set("English (en)")

        # Search Button
        self.search_button = ttk.Button(
            self.input_frame,
            text="Analyze Tweets",
            command=self.start_analysis,
            style="Search.TButton"
        )
        self.search_button.pack(pady=(20, 0))

        # Status Label
        self.status_label = ttk.Label(
            self.input_frame,
            text="Ready to analyze",
            style="Status.TLabel"
        )
        self.status_label.pack(pady=(5, 0))

        # Results Section
        self.results_frame = ttk.LabelFrame(
            self.main_frame,
            text="Results",
            padding="20"
        )
        self.results_frame.pack(fill=tk.BOTH, expand=True)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.results_frame,
            variable=self.progress_var,
            maximum=100
        )

    def setup_rate_limit_tracking(self):
        self.request_count = 0
        self.last_request_time = None
        self.rate_limit = 180
        self.rate_window = 60  # 15 minutes in seconds

    def check_rate_limit(self):
        current_time = time.time()
        
        if self.last_request_time:
            time_passed = current_time - self.last_request_time
            if time_passed > self.rate_window:
                self.request_count = 0
            elif self.request_count >= self.rate_limit:
                wait_time = self.rate_window - time_passed
                raise Exception(f"Rate limit exceeded. Please wait {int(wait_time/60)} minutes.")

        self.request_count += 1
        self.last_request_time = current_time

    def authenticate_twitter_api(self):
        bearer_token = "AAAAAAAAAAAAAAAAAAAAAFVYzAEAAAAAdPzlCiM4qUxICdZhD%2FpzGBKA9lY%3DQ2rjUV2i2uT17HXGctVXOulo7GSMkwzoqh9ODPQUym6KVAQFf2"
        return tweepy.Client(bearer_token=bearer_token)

    def update_progress(self, value):
        self.progress_var.set(value)
        self.root.update_idletasks()

    def update_status(self, message, is_error=False):
        self.status_label.configure(
            text=message,
            foreground="#E0245E" if is_error else "#657786"
        )

    def start_analysis(self):
        if not self.search_term.get():
            messagebox.showerror("Error", "Please enter a search term")
            return

        try:
            self.check_rate_limit()
        except Exception as e:
            messagebox.showerror("Rate Limit Error", str(e))
            return

        for widget in self.results_frame.winfo_children():
            widget.destroy()

        self.progress_var.set(0)
        self.progress_bar = ttk.Progressbar(
            self.results_frame,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(fill=tk.X, pady=10)

        self.text_widget = tk.Text(
            self.results_frame,
            height=10,
            wrap=tk.WORD,
            font=("Helvetica", 10)
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.search_button.configure(state="disabled")
        self.update_status("Analyzing tweets...")

        thread = threading.Thread(target=self.perform_analysis)
        thread.daemon = True
        thread.start()

    def perform_analysis(self):
        try:
            search_term = self.search_term.get()
            tweet_count = int(self.tweet_count.get())
            language = self.language.get().split(" ")[1].strip("()")

            tweets = self.client.search_recent_tweets(
                query=search_term,
                max_results=min(tweet_count, 100),
                lang=language if language != "All" else None
            )

            if not tweets.data:
                self.root.after(0, self.update_status, "No tweets found", True)
                return

            sentiments = []
            tweet_texts = []

            for i, tweet in enumerate(tweets.data):
                self.root.after(0, self.update_progress, (i + 1) / len(tweets.data) * 100)

                analysis = TextBlob(tweet.text)
                sentiment = analysis.sentiment.polarity
                sentiment_label = "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Neutral"

                self.root.after(0, self.text_widget.insert, tk.END,
                              f"Tweet {i+1}: {tweet.text}\nSentiment: {sentiment_label} (Polarity: {sentiment:.2f})\n\n")

                sentiments.append(sentiment)
                tweet_texts.append(tweet.text)

            self.root.after(0, self.create_pie_chart, sentiments)
            self.root.after(0, self.update_status, f"Analysis completed - {len(tweets.data)} tweets analyzed")

        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", str(e))
            self.root.after(0, self.update_status, "Analysis failed", True)

        finally:
            self.root.after(0, self.search_button.configure, {"state": "normal"})

    def create_pie_chart(self, sentiments):
        if not sentiments:
            return

        positive = len([s for s in sentiments if s > 0])
        negative = len([s for s in sentiments if s < 0])
        neutral = len([s for s in sentiments if s == 0])

        fig, ax = plt.subplots(figsize=(8, 6))
        labels = ['Positive', 'Negative', 'Neutral']
        sizes = [positive, negative, neutral]
        colors = ['#2ecc71', '#e74c3c', '#95a5a6']
        explode = (0.1, 0.1, 0)

        ax.pie(sizes, explode=explode, labels=labels, colors=colors,
               autopct='%1.1f%%', startangle=140)
        ax.axis('equal')

        chart_frame = ttk.Frame(self.results_frame)
        chart_frame.pack(fill=tk.BOTH, expand=True)

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = TwitterSentimentGUI(root)
    root.mainloop()