
import tkinter as tk
from tkinter import ttk, messagebox
import time
import json
from datetime import datetime, timedelta
import calendar
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


class StudyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("자기주도 학습 관리 프로그램")
        self.root.geometry("900x850")

        self.start_time = 0
        self.elapsed_time = 0
        self.running = False

        self.study_log = {}
        self.plan_log = {}
        self.goal_hours = {}

        self.current_year = datetime.now().year
        self.current_month = datetime.now().month

        self.subjects = ["Python", "SQLD", "Linux", "AWS", "파이썬", ""]

        self.create_ui()
        self.load_data()
        self.load_records()
        self.update_timer()

    def create_ui(self):
        tk.Label(
            self.root,
            text="자기주도 학습 관리 프로그램",
            font=("맑은고딕", 18, "bold")
        ).pack(pady=10)

        self.combo = ttk.Combobox(self.root, values=self.subjects, width=20)
        self.combo.pack()

        subject_frame = tk.Frame(self.root)
        subject_frame.pack(pady=5)

        self.subject_entry = tk.Entry(subject_frame)
        self.subject_entry.grid(row=0, column=0)

        ttk.Button(
            subject_frame,
            text="과목 추가",
            command=self.add_subject
        ).grid(row=0, column=1)

        self.timer_label = tk.Label(
            self.root,
            text="00:00:00",
            font=("Arial", 30)
        )
        self.timer_label.pack(pady=10)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack()

        ttk.Button(btn_frame, text="시작", command=self.start_timer).grid(row=0, column=0)
        ttk.Button(btn_frame, text="일시정지", command=self.pause_timer).grid(row=0, column=1)
        ttk.Button(btn_frame, text="종료", command=self.stop_timer).grid(row=0, column=2)
        ttk.Button(btn_frame, text="그래프", command=self.show_graph).grid(row=0, column=3)

        goal_frame = tk.Frame(self.root)
        goal_frame.pack(pady=10)

        tk.Label(goal_frame, text="목표 시간(시간)").grid(row=0, column=0)

        self.goal_entry = tk.Entry(goal_frame, width=10)
        self.goal_entry.grid(row=0, column=1)

        ttk.Button(goal_frame, text="목표 설정", command=self.set_goal).grid(row=0, column=2)

        stat_frame = tk.Frame(self.root)
        stat_frame.pack(pady=5)

        ttk.Button(stat_frame, text="주간 통계", command=self.show_weekly_stats).grid(row=0, column=0)
        ttk.Button(stat_frame, text="월간 통계", command=self.show_monthly_stats).grid(row=0, column=1)

        self.listbox = tk.Listbox(self.root, width=100, height=15)
        self.listbox.pack(pady=10)

        cal_frame = tk.Frame(self.root)
        cal_frame.pack()

        ttk.Button(cal_frame, text="<", command=self.prev_month).grid(row=0, column=0)

        self.month_label = tk.Label(cal_frame)
        self.month_label.grid(row=0, column=1)

        ttk.Button(cal_frame, text=">", command=self.next_month).grid(row=0, column=2)

        self.calendar_frame = tk.Frame(self.root)
        self.calendar_frame.pack(pady=10)

        self.plan_entry = tk.Entry(self.root, width=50)
        self.plan_entry.pack(pady=5)

        ttk.Button(self.root, text="계획 저장", command=self.save_plan).pack()

        self.update_calendar()

    def add_subject(self):
        subject = self.subject_entry.get().strip()
        if subject and subject not in self.subjects:
            self.subjects.append(subject)
            self.combo["values"] = self.subjects
            messagebox.showinfo("추가 완료", f"{subject} 과목 추가")
        self.subject_entry.delete(0, tk.END)

    def set_goal(self):
        subject = self.combo.get()
        if not subject:
            return
        try:
            self.goal_hours[subject] = float(self.goal_entry.get())
            self.save_data()
            messagebox.showinfo("저장", f"{subject} 목표 설정 완료")
        except ValueError:
            messagebox.showwarning("오류", "숫자를 입력하세요.")

    def start_timer(self):
        if not self.running:
            self.start_time = time.time() - self.elapsed_time
            self.running = True

    def pause_timer(self):
        if self.running:
            self.elapsed_time = time.time() - self.start_time
            self.running = False

    def stop_timer(self):
        if self.running:
            self.elapsed_time = time.time() - self.start_time
            self.running = False

        subject = self.combo.get()
        if not subject:
            messagebox.showwarning("경고", "과목을 선택하세요.")
            return

        date = datetime.now().strftime("%Y-%m-%d")

        self.study_log.setdefault(date, []).append({
            "subject": subject,
            "time": self.elapsed_time
        })

        self.listbox.insert(
            tk.END,
            f"{date} | {subject} | {self.format_time(int(self.elapsed_time))}"
        )

        self.elapsed_time = 0
        self.timer_label.config(text="00:00:00")
        self.save_data()

    def update_timer(self):
        if self.running:
            self.elapsed_time = time.time() - self.start_time
            self.timer_label.config(text=self.format_time(int(self.elapsed_time)))
        self.root.after(1000, self.update_timer)

    def format_time(self, sec):
        h = sec // 3600
        m = (sec % 3600) // 60
        s = sec % 60
        return f"{h:02}:{m:02}:{s:02}"

    def update_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        self.month_label.config(text=f"{self.current_year}년 {self.current_month}월")

        days = ["일", "월", "화", "수", "목", "금", "토"]
        for col, day_name in enumerate(days):
            tk.Label(
                self.calendar_frame,
                text=day_name,
                width=5,
                font=("맑은고딕", 10, "bold")
            ).grid(row=0, column=col)

        cal = calendar.monthcalendar(self.current_year, self.current_month)
        today = datetime.now()

        for row, week in enumerate(cal, start=1):
            for col, day in enumerate(week):
                if day == 0:
                    tk.Label(self.calendar_frame, text="", width=5).grid(row=row, column=col)
                else:
                    color = "lightblue" if (
                        today.year == self.current_year and
                        today.month == self.current_month and
                        today.day == day
                    ) else "SystemButtonFace"

                    tk.Button(
                        self.calendar_frame,
                        text=str(day),
                        width=5,
                        bg=color,
                        command=lambda d=day: self.show_day_detail(d)
                    ).grid(row=row, column=col, padx=2, pady=2)

    def prev_month(self):
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self.update_calendar()

    def next_month(self):
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        self.update_calendar()

    def show_day_detail(self, day):
        date = f"{self.current_year}-{self.current_month:02}-{day:02}"

        self.listbox.insert(tk.END, f"📅 {date}")

        if date in self.study_log:
            for item in self.study_log[date]:
                study_time = item["time"]
                if isinstance(study_time, str):
                    display_time = study_time
                else:
                    display_time = self.format_time(int(study_time))

                self.listbox.insert(
                    tk.END,
                    f"• {item['subject']} | {display_time}"
                )
        else:
            self.listbox.insert(tk.END, "공부 기록 없음")

        if date in self.plan_log:
            self.listbox.insert(tk.END, f"계획 : {self.plan_log[date]}")

    def save_plan(self):
        date = datetime.now().strftime("%Y-%m-%d")
        self.plan_log[date] = self.plan_entry.get()
        self.plan_entry.delete(0, tk.END)
        self.save_data()
        messagebox.showinfo("저장", "계획 저장 완료")

    def show_graph(self):
        subject_time = {}
        for logs in self.study_log.values():
            for item in logs:
                subject_time[item["subject"]] = subject_time.get(item["subject"], 0) + float(item["time"])

        plt.figure(figsize=(8, 5))
        plt.bar(subject_time.keys(), [v / 3600 for v in subject_time.values()])
        plt.title("과목별 학습 시간")
        plt.ylabel("시간")
        plt.show()

    def show_weekly_stats(self):
        total = 0
        week_ago = datetime.now() - timedelta(days=7)

        for date, logs in self.study_log.items():
            d = datetime.strptime(date, "%Y-%m-%d")
            if d >= week_ago:
                for item in logs:
                    total += float(item["time"])

        messagebox.showinfo("주간 통계", f"{total / 3600:.2f} 시간")

    def show_monthly_stats(self):
        total = 0
        now = datetime.now()

        for date, logs in self.study_log.items():
            d = datetime.strptime(date, "%Y-%m-%d")
            if d.year == now.year and d.month == now.month:
                for item in logs:
                    total += float(item["time"])

        messagebox.showinfo("월간 통계", f"{total / 3600:.2f} 시간")

    def load_records(self):
        for date, logs in self.study_log.items():
            for item in logs:
                study_time = item["time"]
                if isinstance(study_time, str):
                    display_time = study_time
                else:
                    display_time = self.format_time(int(study_time))

                self.listbox.insert(
                    tk.END,
                    f"{date} | {item['subject']} | {display_time}"
                )

    def save_data(self):
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump({
                "study": self.study_log,
                "plan": self.plan_log,
                "goal": self.goal_hours
            }, f, ensure_ascii=False, indent=4)

    def load_data(self):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.study_log = data.get("study", {})
                self.plan_log = data.get("plan", {})
                self.goal_hours = data.get("goal", {})
        except FileNotFoundError:
            pass


root = tk.Tk()
app = StudyApp(root)
root.mainloop()

### 파이썬 기말과제