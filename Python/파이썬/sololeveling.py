# tkinter: 파이썬 기본 GUI 라이브러리
import tkinter as tk
from tkinter import ttk, messagebox  # ttk: 좀 더 예쁜 위젯 / messagebox: 팝업창

import time  # 시간 측정용
import json  # 데이터 저장/불러오기용
from datetime import datetime  # 현재 날짜/시간
import calendar  # 달력 생성

import matplotlib.pyplot as plt  # 그래프 출력
import numpy as np  # 숫자 계산
import mplcursors  # 그래프에 마우스 올리면 정보 표시

# 한글 폰트 설정 (그래프에서 한글 깨짐 방지)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


class StudyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("자기주도 학습 관리 프로그램")
        self.root.geometry("900x850")

        # 달력 시작 요일을 일요일로 설정
        calendar.setfirstweekday(calendar.SUNDAY)

        # 타이머 관련 변수
        self.start_time = 0     # 시작 시간
        self.elapsed_time = 0   # 경과 시간
        self.running = False    # 타이머 실행 여부

        # 데이터 저장용
        self.study_log = {}  # 공부 기록
        self.plan_log = {}   # 날짜별 계획
        self.goal_hours = {} # (현재 코드에서는 사용 안됨)

        # 현재 연도/월
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month

        # 기본 과목 목록
        self.subjects = ["Python", "SQLD", "Linux"]

        # UI 생성
        self.create_ui()

        # 저장된 데이터 불러오기
        self.load_data()

        # 기존 기록 리스트에 표시
        self.load_records()

        # 타이머 계속 업데이트
        self.update_timer()

    def create_ui(self):
        # 제목 라벨
        tk.Label(self.root, text="자기주도 학습 관리 프로그램",
                 font=("맑은고딕", 18, "bold")).pack(pady=10)

        # 과목 선택 콤보박스
        self.combo = ttk.Combobox(self.root, values=self.subjects, width=20)
        self.combo.pack()

        # 과목 추가 영역
        subject_frame = tk.Frame(self.root)
        subject_frame.pack(pady=5)

        self.subject_entry = tk.Entry(subject_frame)
        self.subject_entry.grid(row=0, column=0)

        ttk.Button(subject_frame, text="과목 추가",
                   command=self.add_subject).grid(row=0, column=1)

        # 타이머 표시 라벨
        self.timer_label = tk.Label(self.root, text="00:00:00",
                                    font=("Arial", 30))
        self.timer_label.pack(pady=10)

        # 버튼 영역
        btn_frame = tk.Frame(self.root)
        btn_frame.pack()

        ttk.Button(btn_frame, text="시작", command=self.start_timer).grid(row=0, column=0)
        ttk.Button(btn_frame, text="일시정지", command=self.pause_timer).grid(row=0, column=1)
        ttk.Button(btn_frame, text="종료", command=self.stop_timer).grid(row=0, column=2)
        ttk.Button(btn_frame, text="그래프", command=self.show_graph).grid(row=0, column=3)

        # 기록 리스트 출력
        self.listbox = tk.Listbox(self.root, width=100, height=15)
        self.listbox.pack(pady=10)

        # 달력 상단 버튼
        cal_frame = tk.Frame(self.root)
        cal_frame.pack()

        ttk.Button(cal_frame, text="<", command=self.prev_month).grid(row=0, column=0)

        self.month_label = tk.Label(cal_frame)
        self.month_label.grid(row=0, column=1)

        ttk.Button(cal_frame, text=">", command=self.next_month).grid(row=0, column=2)

        # 달력 영역
        self.calendar_frame = tk.Frame(self.root)
        self.calendar_frame.pack(pady=10)

        self.update_calendar()

    def add_subject(self):
        # 입력값 가져오기
        subject = self.subject_entry.get().strip()

        # 중복 방지 + 빈 값 방지
        if subject and subject not in self.subjects:
            self.subjects.append(subject)
            self.combo["values"] = self.subjects
            messagebox.showinfo("추가 완료", f"{subject} 과목 추가")

        # 입력창 초기화
        self.subject_entry.delete(0, tk.END)

    def start_timer(self):
        # 타이머 시작
        if not self.running:
            self.start_time = time.time() - self.elapsed_time
            self.running = True

    def pause_timer(self):
        # 일시정지
        if self.running:
            self.elapsed_time = time.time() - self.start_time
            self.running = False

    def stop_timer(self):
        # 종료 (기록 저장)
        if self.running:
            self.elapsed_time = time.time() - self.start_time
            self.running = False

        subject = self.combo.get()

        # 과목 선택 안 했을 경우 경고
        if not subject:
            messagebox.showwarning("경고", "과목을 선택하세요.")
            return

        # 오늘 날짜
        date = datetime.now().strftime("%Y-%m-%d")

        # 기록 저장
        self.study_log.setdefault(date, []).append({
            "subject": subject,
            "time": self.elapsed_time
        })

        # 리스트박스에 추가
        self.listbox.insert(
            0,
            f"{date} | {subject} | {self.format_time(int(self.elapsed_time))}"
        )

        # 타이머 초기화
        self.elapsed_time = 0
        self.timer_label.config(text="00:00:00")

        # 파일 저장
        self.save_data()

    def update_timer(self):
        # 1초마다 타이머 갱신
        if self.running:
            self.elapsed_time = time.time() - self.start_time
            self.timer_label.config(text=self.format_time(int(self.elapsed_time)))

        self.root.after(1000, self.update_timer)

    def format_time(self, sec):
        # 초 → 시:분:초 변환
        h = sec // 3600
        m = (sec % 3600) // 60
        s = sec % 60
        return f"{h:02}:{m:02}:{s:02}"

    def update_calendar(self):
        # 기존 달력 삭제
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        self.month_label.config(text=f"{self.current_year}년 {self.current_month}월")

        # 요일 표시
        days = ["일", "월", "화", "수", "목", "금", "토"]
        for col, day_name in enumerate(days):
            tk.Label(self.calendar_frame, text=day_name,
                     width=5, font=("맑은고딕", 10, "bold")).grid(row=0, column=col)

        cal = calendar.monthcalendar(self.current_year, self.current_month)
        today = datetime.now()

        # 날짜 버튼 생성
        for row, week in enumerate(cal, start=1):
            for col, day in enumerate(week):
                if day == 0:
                    tk.Label(self.calendar_frame, text="", width=5).grid(row=row, column=col)
                else:
                    # 오늘 날짜 색상 표시
                    color = "lightblue" if (
                        today.year == self.current_year and
                        today.month == self.current_month and
                        today.day == day
                    ) else "SystemButtonFace"

                    tk.Button(self.calendar_frame, text=str(day),
                              width=5, bg=color,
                              command=lambda d=day: self.show_day_detail(d)
                              ).grid(row=row, column=col, padx=2, pady=2)

    def prev_month(self):
        # 이전 달
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self.update_calendar()

    def next_month(self):
        # 다음 달
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        self.update_calendar()

    def show_day_detail(self, day):
        # 날짜별 계획 입력 창
        date = f"{self.current_year}-{self.current_month:02}-{day:02}"

        top = tk.Toplevel(self.root)
        top.title(f"{date} 계획")
        top.geometry("400x350")

        tk.Label(top, text=date, font=("맑은고딕", 12, "bold")).pack(pady=10)

        text = tk.Text(top, width=40, height=10)
        text.pack(pady=10)

        # 기존 계획 불러오기
        if date in self.plan_log:
            text.insert(tk.END, self.plan_log[date])

        def save_plan():
            self.plan_log[date] = text.get("1.0", tk.END).strip()
            self.save_data()
            messagebox.showinfo("저장", "완료")
            top.destroy()

        ttk.Button(top, text="저장", command=save_plan).pack()

    def show_graph(self):
        # 과목별 시간 합산
        subject_time = {}
        for logs in self.study_log.values():
            for item in logs:
                subject_time[item["subject"]] = subject_time.get(item["subject"], 0) + float(item["time"])

        subjects = list(subject_time.keys())
        total_seconds = list(subject_time.values())

        # 데이터 없으면 종료
        if not subjects:
            messagebox.showwarning("알림", "학습 데이터가 없습니다.")
            return

        # 시간 표시 형식
        def format_to_hm(sec):
            h = int(sec // 3600)
            m = int((sec % 3600) // 60)
            return f"{h}시간 {m}분"

        # 시간 → 시간 단위 변환
        hours_for_plot = [s / 3600 for s in total_seconds]

        # 라벨 생성
        labels = [f"{sub}\n({format_to_hm(s)})" for sub, s in zip(subjects, total_seconds)]

        # 그래프 생성
        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(labels, hours_for_plot)

        # 마우스 올리면 정보 표시
        cursor = mplcursors.cursor(bars, hover=True)
        @cursor.connect("add")
        def on_add(sel):
            idx = sel.index
            sel.annotation.set_text(f"{subjects[idx]}\n{format_to_hm(total_seconds[idx])}")

        # y축 설정 (30분 단위)
        max_val = max(hours_for_plot)
        y_ticks = np.arange(0, max_val + 0.5, 0.5)
        ax.set_yticks(y_ticks)
        ax.set_yticklabels([f"{int(y)}시간" if y.is_integer() else f"{int(y)}시간 30분" for y in y_ticks])

        ax.set_title("과목별 학습 시간")

        plt.tight_layout()
        plt.show()

    def load_records(self):
        # 기존 기록 리스트에 표시
        all_records = []
        for date, logs in self.study_log.items():
            for item in logs:
                all_records.append((date, item))

        all_records.sort(key=lambda x: x[0])

        for date, item in all_records:
            self.listbox.insert(
                tk.END,
                f"{date} | {item['subject']} | {self.format_time(int(item['time']))}"
            )

    def save_data(self):
        # JSON 파일 저장
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump({
                "study": self.study_log,
                "plan": self.plan_log
            }, f, ensure_ascii=False, indent=4)

    def load_data(self):
        # JSON 파일 불러오기
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.study_log = data.get("study", {})
                self.plan_log = data.get("plan", {})
        except:
            pass


# 프로그램 실행
root = tk.Tk()
app = StudyApp(root)
root.mainloop()