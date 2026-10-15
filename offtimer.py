"""
Shutdown Timer - a tiny floating window that turns your PC off at a set time
or after a countdown. Needs only Python 3 (tkinter ships with it).

Run:  python shutdown_timer.py
Build .exe (optional):  pip install pyinstaller
                        pyinstaller --onefile --noconsole shutdown_timer.py
"""
import platform
import subprocess
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import messagebox, ttk

IS_WIN = platform.system() == "Windows"
NO_WINDOW = subprocess.CREATE_NO_WINDOW if IS_WIN else 0


def os_schedule(seconds: int, force: bool) -> None:
    """Ask the OS to shut down in `seconds`. Survives closing this app."""
    if IS_WIN:
        cmd = ["shutdown", "/s", "/t", str(seconds)]
        if force:
            cmd.append("/f")
    else:  # Linux / macOS (may need sudo privileges)
        cmd = ["shutdown", "-h", f"+{max(1, -(-seconds // 60))}"]
    subprocess.run(cmd, check=True, creationflags=NO_WINDOW,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def os_cancel() -> None:
    cmd = ["shutdown", "/a"] if IS_WIN else ["shutdown", "-c"]
    subprocess.run(cmd, creationflags=NO_WINDOW,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Shutdown Timer")
        self.resizable(False, False)
        self.attributes("-topmost", True)   # always floats above other windows
        self.attributes("-alpha", 0.95)
        self.target = None

        self.mode = tk.StringVar(value="countdown")
        self.hh = tk.StringVar(value=datetime.now().strftime("%H"))
        self.mm = tk.StringVar(value=datetime.now().strftime("%M"))
        self.minutes = tk.StringVar(value="30")
        self.force = tk.BooleanVar(value=False)

        self._build_setup()
        self._build_running()
        self.setup.pack(padx=14, pady=12)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------- UI ----------
    def _build_setup(self):
        f = self.setup = ttk.Frame(self)

        r1 = ttk.Frame(f); r1.pack(anchor="w", pady=2)
        ttk.Radiobutton(r1, text="Shut down in", variable=self.mode,
                        value="countdown").pack(side="left")
        ttk.Spinbox(r1, from_=1, to=1440, width=5,
                    textvariable=self.minutes).pack(side="left", padx=6)
        ttk.Label(r1, text="min").pack(side="left")

        r2 = ttk.Frame(f); r2.pack(anchor="w", pady=2)
        ttk.Radiobutton(r2, text="Shut down at", variable=self.mode,
                        value="clock").pack(side="left")
        ttk.Spinbox(r2, from_=0, to=23, width=3, format="%02.0f", wrap=True,
                    textvariable=self.hh).pack(side="left", padx=(6, 2))
        ttk.Label(r2, text=":").pack(side="left")
        ttk.Spinbox(r2, from_=0, to=59, width=3, format="%02.0f", wrap=True,
                    textvariable=self.mm).pack(side="left", padx=(2, 0))

        presets = ttk.Frame(f); presets.pack(pady=6)
        for m in (15, 30, 60, 120):
            ttk.Button(presets, text=f"{m}m", width=5,
                       command=lambda m=m: self.set_preset(m)).pack(side="left", padx=2)

        ttk.Checkbutton(f, text="Force-close running apps",
                        variable=self.force).pack(anchor="w", pady=2)
        ttk.Button(f, text="Start", command=self.start).pack(fill="x", pady=(8, 0))

    def _build_running(self):
        f = self.running = ttk.Frame(self)
        self.big = tk.Label(f, text="00:00:00", font=("Segoe UI", 26, "bold"))
        self.big.pack()
        self.info = ttk.Label(f, text="")
        self.info.pack()
        ttk.Button(f, text="Cancel shutdown", command=self.cancel).pack(fill="x", pady=(8, 0))

    # ---------- actions ----------
    def set_preset(self, m):
        self.mode.set("countdown")
        self.minutes.set(str(m))

    def start(self):
        now = datetime.now()
        try:
            if self.mode.get() == "countdown":
                mins = int(self.minutes.get())
                if mins < 1:
                    raise ValueError
                target = now + timedelta(minutes=mins)
            else:
                h, m = int(self.hh.get()), int(self.mm.get())
                if not (0 <= h <= 23 and 0 <= m <= 59):
                    raise ValueError
                target = now.replace(hour=h, minute=m, second=0, microsecond=0)
                if target <= now:               # time already passed -> tomorrow
                    target += timedelta(days=1)
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter a valid time or minutes.")
            return

        seconds = max(1, int((target - now).total_seconds()))
        try:
            os_cancel()                         # clear any earlier schedule
            os_schedule(seconds, self.force.get())
        except Exception as e:
            messagebox.showerror("Could not schedule shutdown", str(e))
            return

        self.target = target
        day = "" if target.date() == now.date() else " (tomorrow)"
        self.info.config(text=f"Shutdown at {target:%H:%M}{day}")
        self.setup.pack_forget()
        self.running.pack(padx=14, pady=10)
        self.geometry("")
        self.tick()

    def tick(self):
        if self.target is None:
            return
        left = int((self.target - datetime.now()).total_seconds())
        if left <= 0:
            self.big.config(text="Shutting down…", font=("Segoe UI", 16, "bold"), fg="red")
            return
        h, rem = divmod(left, 3600)
        m, s = divmod(rem, 60)
        self.big.config(text=f"{h:02d}:{m:02d}:{s:02d}",
                        fg="red" if left <= 60 else "black")
        self.after(500, self.tick)

    def cancel(self):
        os_cancel()
        self.target = None
        self.big.config(font=("Segoe UI", 26, "bold"), fg="black")
        self.running.pack_forget()
        self.setup.pack(padx=14, pady=12)
        self.geometry("")

    def on_close(self):
        if self.target is not None:
            ans = messagebox.askyesnocancel(
                "Shutdown is scheduled",
                "Keep the shutdown scheduled and close this window?\n\n"
                "Yes = keep it   |   No = cancel it   |   Cancel = stay open")
            if ans is None:
                return
            if ans is False:
                os_cancel()
        self.destroy()


if __name__ == "__main__":
    App().mainloop()
