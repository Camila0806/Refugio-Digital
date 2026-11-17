"""
Interfaz sencilla de escritorio para consultar Gemini con Tkinter.

Requisitos:
  py -m pip install requests

Uso:
  1. Ejecuta: py consulta_gemini_tkinter.py
  2. Pega tu clave de API de Google AI Studio en la ventana.
  3. Escribe una pregunta y pulsa "Consultar Gemini".

Nota: para uso personal/de pruebas. No compartas la clave ni la guardes en el código.
"""

import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

import requests

API_URL = (
    
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-3.6-flash:generateContent"
)


class GeminiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Consultas a Gemini")
        self.root.geometry("760x620")
        self.root.minsize(600, 480)
        self.root.configure(bg="#f3f5fb")

        self.api_key = tk.StringVar()
        self.status = tk.StringVar(value="Listo para consultar.")

        main = tk.Frame(root, bg="white", padx=22, pady=20)
        main.pack(fill="both", expand=True, padx=18, pady=18)

        tk.Label(
            main, text="Consulta a Gemini", font=("Segoe UI", 20, "bold"),
            fg="#4057c8", bg="white"
        ).pack(anchor="w")

        tk.Label(
            main, text="Escribe una pregunta y consulta el modelo de Google.",
            font=("Segoe UI", 10), fg="#555555", bg="white"
        ).pack(anchor="w", pady=(4, 16))

        tk.Label(
            main, text="Clave de API", font=("Segoe UI", 10, "bold"),
            bg="white", fg="#202124"
        ).pack(anchor="w")

        key_row = tk.Frame(main, bg="white")
        key_row.pack(fill="x", pady=(6, 14))

        self.key_entry = tk.Entry(
            key_row, textvariable=self.api_key, show="•",
            font=("Segoe UI", 10), relief="solid", bd=1
        )
        self.key_entry.pack(side="left", fill="x", expand=True, ipady=7)

        self.show_key = tk.BooleanVar(value=False)
        tk.Checkbutton(
            key_row, text="Mostrar", variable=self.show_key,
            command=self.toggle_key, bg="white", activebackground="white"
        ).pack(side="left", padx=(8, 0))

        tk.Label(
            main, text="Tu pregunta", font=("Segoe UI", 10, "bold"),
            bg="white", fg="#202124"
        ).pack(anchor="w")

        self.question = scrolledtext.ScrolledText(
            main, height=5, wrap="word", font=("Segoe UI", 10),
            relief="solid", bd=1, padx=8, pady=8
        )
        self.question.pack(fill="x", pady=(6, 12))
        self.question.insert(
            "1.0", "Explícame qué es una API con palabras sencillas."
        )

        button_row = tk.Frame(main, bg="white")
        button_row.pack(fill="x")

        self.ask_button = tk.Button(
            button_row, text="Consultar Gemini", command=self.ask,
            bg="#4057c8", fg="white", activebackground="#3246aa",
            activeforeground="white", font=("Segoe UI", 10, "bold"),
            relief="flat", padx=16, pady=9, cursor="hand2"
        )
        self.ask_button.pack(side="left")

        tk.Button(
            button_row, text="Limpiar respuesta", command=self.clear_answer,
            font=("Segoe UI", 10), relief="groove", padx=10, pady=8
        ).pack(side="left", padx=8)

        tk.Label(
            main, text="Respuesta", font=("Segoe UI", 10, "bold"),
            bg="white", fg="#202124"
        ).pack(anchor="w", pady=(16, 6))

        self.answer = scrolledtext.ScrolledText(
            main, wrap="word", font=("Segoe UI", 10), relief="solid",
            bd=1, padx=10, pady=10, state="disabled"
        )
        self.answer.pack(fill="both", expand=True)

        tk.Label(
            main, textvariable=self.status, anchor="w",
            font=("Segoe UI", 9), fg="#555555", bg="white"
        ).pack(fill="x", pady=(8, 0))

        tk.Label(
            root,
            text="No compartas tu clave de API ni la incluyas en código público.",
            font=("Segoe UI", 9), fg="#6b5a24", bg="#fff3cd",
            padx=12, pady=8
        ).pack(fill="x", side="bottom")

    def toggle_key(self):
        self.key_entry.configure(show="" if self.show_key.get() else "•")

    def set_answer(self, text):
        self.answer.configure(state="normal")
        self.answer.delete("1.0", "end")
        self.answer.insert("1.0", text)
        self.answer.configure(state="disabled")

    def clear_answer(self):
        self.set_answer("")
        self.status.set("Respuesta limpiada.")

    def ask(self):
        key = self.api_key.get().strip()
        question = self.question.get("1.0", "end").strip()

        if not key:
            messagebox.showwarning(
                "Falta la clave", "Pega tu clave de API de Gemini."
            )
            return
        if not question:
            messagebox.showwarning(
                "Falta la pregunta", "Escribe una pregunta antes de consultar."
            )
            return

        self.ask_button.configure(state="disabled")
        self.status.set("Consultando a Gemini…")
        self.set_answer("Esperando respuesta…")

        thread = threading.Thread(
            target=self._request_gemini,
            args=(key, question),
            daemon=True
        )
        thread.start()

    def _request_gemini(self, key, question):
        try:
            response = requests.post(
                API_URL,
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": key,
                },
                json={
                    "contents": [
                        {"parts": [{"text": question}]}
                    ]
                },
                timeout=60,
            )

            try:
                data = response.json()
            except ValueError:
                data = {}

            if not response.ok:
                detail = data.get("error", {}).get(
                    "message", f"Error HTTP {response.status_code}"
                )
                raise RuntimeError(detail)

            parts = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [])
            )
            answer = "\n".join(
                part.get("text", "") for part in parts if part.get("text")
            ).strip()

            if not answer:
                answer = (
                    "Gemini no devolvió texto. Intenta reformular la pregunta."
                )

            self.root.after(0, self._finish, answer, "Consulta completada.")
        except requests.RequestException as exc:
            self.root.after(
                0, self._finish,
                f"No se pudo conectar con Gemini: {exc}",
                "Error de conexión."
            )
        except RuntimeError as exc:
            self.root.after(
                0, self._finish,
                f"Gemini devolvió un error:\n{exc}\n\n"
                "Verifica la clave, el acceso a la API y el modelo disponible.",
                "La consulta falló."
            )

    def _finish(self, answer, status):
        self.set_answer(answer)
        self.status.set(status)
        self.ask_button.configure(state="normal")


def main():
    root = tk.Tk()
    GeminiApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
