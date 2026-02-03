import os
import sys
import threading
import queue
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText


ROOT = Path(__file__).resolve().parent  # folder containing manage.py


class RunnerGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("MPE Website Tools (Local / Deploy)")
        self.root.geometry("980x650")

        # Process handles (so we can stop runserver)
        self.current_proc: subprocess.Popen | None = None
        self.worker_thread: threading.Thread | None = None
        self.log_q: queue.Queue[str] = queue.Queue()

        # UI state
        self.mode_var = tk.StringVar(value="dev")  # dev or prod
        self.host_var = tk.StringVar(value="127.0.0.1")
        self.port_var = tk.StringVar(value="8000")
        self.commit_var = tk.StringVar(value="Update website")
        self.debug_var = tk.BooleanVar(value=True)

        self._build_ui()
        self._poll_logs()

        self._log(f"Project root: {ROOT}")
        self._log(f"Python: {sys.executable}")

    # ---------------- UI ----------------
    def _build_ui(self):
        pad = {"padx": 10, "pady": 8}

        top = ttk.Frame(self.root)
        top.pack(fill="x", **pad)

        # Mode
        mode_frame = ttk.LabelFrame(top, text="Local Run Settings")
        mode_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ttk.Radiobutton(mode_frame, text="Dev (DEBUG=True)", value="dev", variable=self.mode_var).grid(row=0, column=0, sticky="w", padx=10, pady=6)
        ttk.Radiobutton(mode_frame, text="Prod-like (DEBUG=False)", value="prod", variable=self.mode_var).grid(row=0, column=1, sticky="w", padx=10, pady=6)

        ttk.Label(mode_frame, text="Host").grid(row=1, column=0, sticky="w", padx=10)
        ttk.Entry(mode_frame, textvariable=self.host_var, width=20).grid(row=1, column=1, sticky="w", padx=10)

        ttk.Label(mode_frame, text="Port").grid(row=2, column=0, sticky="w", padx=10, pady=(0, 10))
        ttk.Entry(mode_frame, textvariable=self.port_var, width=20).grid(row=2, column=1, sticky="w", padx=10, pady=(0, 10))

        ttk.Checkbutton(mode_frame, text="Debug output (show env + commands)", variable=self.debug_var).grid(
            row=3, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 10)
        )

        # Actions
        act_frame = ttk.LabelFrame(top, text="Actions")
        act_frame.pack(side="right", fill="y")

        self.btn_run = ttk.Button(act_frame, text="▶ Run Local", command=self.run_local_clicked)
        self.btn_run.grid(row=0, column=0, padx=10, pady=(10, 6), sticky="ew")

        self.btn_stop = ttk.Button(act_frame, text="■ Stop Server", command=self.stop_clicked, state="disabled")
        self.btn_stop.grid(row=1, column=0, padx=10, pady=6, sticky="ew")

        ttk.Separator(act_frame, orient="horizontal").grid(row=2, column=0, sticky="ew", padx=10, pady=10)

        ttk.Label(act_frame, text="Deploy commit message:").grid(row=3, column=0, sticky="w", padx=10)
        ttk.Entry(act_frame, textvariable=self.commit_var, width=32).grid(row=4, column=0, padx=10, pady=(0, 8), sticky="ew")

        self.btn_deploy = ttk.Button(act_frame, text="⬆ Deploy (git push)", command=self.deploy_clicked)
        self.btn_deploy.grid(row=5, column=0, padx=10, pady=(0, 10), sticky="ew")

        # Log console
        log_frame = ttk.LabelFrame(self.root, text="Console (live logs)")
        log_frame.pack(fill="both", expand=True, **pad)

        self.log = ScrolledText(log_frame, height=20, wrap="word")
        self.log.pack(fill="both", expand=True, padx=10, pady=10)
        self.log.configure(font=("Consolas", 10))
        self.log.configure(state="disabled")

        # Bottom bar
        bottom = ttk.Frame(self.root)
        bottom.pack(fill="x", padx=10, pady=(0, 10))

        ttk.Button(bottom, text="Clear Log", command=self.clear_log).pack(side="left")
        ttk.Button(bottom, text="Open Site in Browser", command=self.open_browser).pack(side="left", padx=(10, 0))

        self.status_var = tk.StringVar(value="Idle")
        ttk.Label(bottom, textvariable=self.status_var).pack(side="right")

    # ---------------- Helpers ----------------
    def _set_busy(self, busy: bool, status: str):
        self.status_var.set(status)
        state = "disabled" if busy else "normal"
        self.btn_run.configure(state=state)
        self.btn_deploy.configure(state=state)

    def _log(self, text: str):
        self.log_q.put(text)

    def _poll_logs(self):
        try:
            while True:
                line = self.log_q.get_nowait()
                self.log.configure(state="normal")
                self.log.insert("end", line + "\n")
                self.log.see("end")
                self.log.configure(state="disabled")
        except queue.Empty:
            pass
        self.root.after(80, self._poll_logs)

    def clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def open_browser(self):
        import webbrowser
        host = self.host_var.get().strip() or "127.0.0.1"
        port = self.port_var.get().strip() or "8000"
        url = f"http://{host}:{port}/"
        webbrowser.open(url)

    def _make_env(self, mode: str) -> dict:
        env = os.environ.copy()
        if mode == "dev":
            env["DEBUG"] = "True"
            env["ALLOWED_HOSTS"] = "127.0.0.1,localhost"
        else:
            env["DEBUG"] = "False"
            env["ALLOWED_HOSTS"] = "127.0.0.1,localhost"
        return env

    def _run_cmd_stream(self, cmd: list[str], *, env: dict | None = None, keep_process: bool = False) -> subprocess.Popen | None:
        """
        Run a command, streaming output to log.
        If keep_process is True, returns the Popen handle (caller must manage it).
        Otherwise waits for completion and returns None.
        """
        if self.debug_var.get():
            self._log("$ " + " ".join(cmd))
            if env:
                self._log(f"ENV DEBUG={env.get('DEBUG')} ALLOWED_HOSTS={env.get('ALLOWED_HOSTS')}")

        proc = subprocess.Popen(
            cmd,
            cwd=ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        def reader():
            assert proc.stdout is not None
            for line in proc.stdout:
                self._log(line.rstrip("\n"))
            proc.wait()

        t = threading.Thread(target=reader, daemon=True)
        t.start()

        if keep_process:
            return proc

        # Wait for completion (but keep GUI responsive by polling)
        while proc.poll() is None:
            self.root.update_idletasks()
            self.root.update()

        if proc.returncode != 0:
            raise subprocess.CalledProcessError(proc.returncode, cmd)

        return None

    def _manage(self, *args: str, env: dict | None = None, keep_process: bool = False) -> subprocess.Popen | None:
        cmd = [sys.executable, "manage.py", *args]
        return self._run_cmd_stream(cmd, env=env, keep_process=keep_process)

    def _git(self, *args: str) -> None:
        self._run_cmd_stream(["git", *args])

    def _get_git_branch_name(self):
        try:
            # Attempt to get current branch name
            p = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if p.returncode == 0:
                return p.stdout.strip()
        except Exception:
            pass
        return "unknown"

    # ---------------- Actions ----------------
    def run_local_clicked(self):
        if self.worker_thread and self.worker_thread.is_alive():
            messagebox.showwarning("Busy", "A task is already running.")
            return

        mode = self.mode_var.get()
        host = self.host_var.get().strip() or "127.0.0.1"
        port = self.port_var.get().strip() or "8000"

        # validate port
        try:
            port_i = int(port)
            if not (1 <= port_i <= 65535):
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Port", "Port must be an integer between 1 and 65535.")
            return

        env = self._make_env(mode)

        def work():
            try:
                self._set_busy(True, f"Running locally ({mode})...")
                self._log("---- Django check ----")
                self._manage("check", env=env)

                self._log("---- Migrate ----")
                self._manage("migrate", env=env)

                self._log("---- Collectstatic (strict) ----")
                self._manage("collectstatic", "--noinput", env=env)

                self._log("---- Runserver ----")
                self._log(f"Opening: http://{host}:{port_i}/")
                proc = self._manage("runserver", f"{host}:{port_i}", env=env, keep_process=True)
                self.current_proc = proc

                # enable stop button
                self.root.after(0, lambda: self.btn_stop.configure(state="normal"))
                self.root.after(0, lambda: self._set_busy(True, f"Server running on {host}:{port_i} (click Stop to end)"))

                # Wait until server stops
                if proc is not None:
                    proc.wait()
                self._log("---- Server stopped ----")
            except subprocess.CalledProcessError as e:
                self._log(f"❌ Command failed: {e}")
                self.root.after(0, lambda: messagebox.showerror("Error", "A command failed. Check the console output."))
            except Exception as e:
                self._log(f"❌ Error: {e}")
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            finally:
                self.current_proc = None
                self.root.after(0, lambda: self.btn_stop.configure(state="disabled"))
                self.root.after(0, lambda: self._set_busy(False, "Idle"))

        self.worker_thread = threading.Thread(target=work, daemon=True)
        self.worker_thread.start()

    def stop_clicked(self):
        if self.current_proc and self.current_proc.poll() is None:
            self._log("Stopping server...")
            try:
                self.current_proc.terminate()
            except Exception as e:
                self._log(f"Terminate failed: {e}")
        else:
            self._log("No running server process found.")
        self.btn_stop.configure(state="disabled")

    def deploy_clicked(self):
        if self.worker_thread and self.worker_thread.is_alive():
            messagebox.showwarning("Busy", "A task is already running.")
            return

        msg = self.commit_var.get().strip() or "Update website"

        def work():
            try:
                branch = self._get_git_branch_name()
                self._set_busy(True, f"Deploying from branch '{branch}'...")
                self._log(f"---- Current Git Branch: {branch} ----")

                self._log("---- Django check ----")
                self._manage("check")

                self._log("---- Collectstatic (strict, catches missing assets) ----")
                self._manage("collectstatic", "--noinput")

                self._log("---- Git add ----")
                self._git("add", "-A")

                self._log("---- Git status ----")
                self._git("status")

                self._log(f"---- Git commit: {msg} ----")
                try:
                    self._git("commit", "-m", msg)
                except subprocess.CalledProcessError:
                    self._log("(No changes to commit)")

                self._log("---- Git push (origin HEAD:main) ----")
                self._git("push", "origin", "HEAD:main")

                self._log("✅ Pushed to GitHub. Railway should deploy automatically (if linked).")
                self.root.after(0, lambda: messagebox.showinfo("Deploy", "Pushed to GitHub. Railway should deploy automatically."))
            except subprocess.CalledProcessError as e:
                self._log(f"❌ Deploy failed: {e}")
                self.root.after(0, lambda: messagebox.showerror("Deploy Failed", "A command failed. Check the console output."))
            except Exception as e:
                self._log(f"❌ Error: {e}")
                self.root.after(0, lambda: messagebox.showerror("Deploy Failed", str(e)))
            finally:
                self.root.after(0, lambda: self._set_busy(False, "Idle"))

        self.worker_thread = threading.Thread(target=work, daemon=True)
        self.worker_thread.start()


def main():
    root = tk.Tk()
    try:
        # nicer defaults on Windows
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
    except Exception:
        pass

    RunnerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
