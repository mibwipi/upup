#본 브로젝트는 사용자의 학습 시간을 기록하고 분석하여 자기주도 학습 능력을 향상시키기 위한 프로그램이다. 
#현대 학생들은 학습 시간을 체계적으로 관리하지 못하고 자신의 학습 패턴을 객관적으로 파악하기 어려운 문제가 있다.
#이를 해결하기 위해 타이머를 활용한 학습 시간 측정, 달력 기반 계획 관리, 그리고 그래프를 통한 데이터 시각화 기능을 구현하였다.
#python과 tkinter를 활용해 GUI를 구성하고, JSON으로 데이터를 저장하며, matplotlib을 통해 과목별 학습 시간을 분석할 수 있도록 하였다.
#특히 날짜별 학습 기록을 딕셔너리와 리스트 구조로 관리하고, 시간 변환 및 과목별 합산 알고리즘을 적용하여 
#단순 기록을 의미 있는 데이터로 변환하였다.

#개발 과정에서는 AI를 활용하여 코드 오류를 수정하고 기능 구현 아이디어를 확장했으며, 달력 기능 개선, 그래프 추가,
#데이터 저장 방식 수정 등 지속적인 개선을 통해 완성도를 높였다.
#본 프로그램은 사용자가 직접 입력한 실제 학습 데이터를 기반으로 하여 일정 수준의 오차는 존재하지만 장기적인 학습 패턴 
#분석에는 충분한 타당성을 가진다
#결과적으로 사용자는 과목별 학습 시간과 편중 여부를 파악하고, 이를 바탕으로 학습 습관을 개선할 수 있다.
#따라서 이 프로그램은 단순한 기록 도구를 넘어 데이터 기반 자기주도 학습을 지원하는 시스템으로서 의미를 가지며,
#향후 AI 기반 분석 기능 등을 추가하여 더욱 발전할 수 있다.


###느낀점###

#처음 프로젝트를 시작했을 때는 무엇부터 해야 할지 막막하게 느껴졌다.
#프로그램 구조를 설계하는 것부터 기능을 하나씩 구현하는 과정까지 쉽지 않았고, 오류가 발생할 때마다 해결하는 데 많은 시간이 필요했다. 
#하지만 하나씩 문제를 해결해 나가면서 점점 프로그램의 형태가 갖춰지는 것을 보며 성취감을 느낄 수 있었다.
#특히 이전에는 단순히 코드를 따라 작성하는 수준이었다면, 이번 프로젝트를 통해 직접 문제를 정의하고 
#기능을 설계하는 경험을 할 수 있었다는 점에서 의미가 있었다.
#또한 친한 친구와 팀을 이루어 진행했기 때문에 서로 부담 없이 의견을 나누고 협력할 수 있었던 점도 큰 도움이 되었다.
#완성된 결과물이 완벽하다고 보기는 어렵지만, 끝까지 포기하지 않고 하나의 프로그램을 완성했다는 점에 큰 의의를 두고 있다.
#이번 경험을 통해 개발 과정의 어려움과 동시에 재미를 느낄 수 있었으며, 
#앞으로는 더 완성도 높은 프로그램을 만들고 싶다는 목표도 가지게 되었다.


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
