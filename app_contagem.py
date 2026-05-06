import io
import sys
import os

class _SafeStream(io.StringIO):
    def write(self, s):
        try: super().write(s)
        except: pass
    def flush(self): pass
    def fileno(self): raise io.UnsupportedOperation("fileno")

if sys.stdout is None:     sys.stdout     = _SafeStream()
if sys.__stdout__ is None: sys.__stdout__ = sys.stdout
if sys.stderr is None:     sys.stderr     = _SafeStream()
if sys.__stderr__ is None: sys.__stderr__ = sys.stderr

import threading
import math
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image


class StreamRedirector(io.StringIO):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def write(self, text):
        try:
            if text and text.strip():
                self.text_widget.configure(state="normal")
                self.text_widget.insert("end", text + "\n")
                self.text_widget.see("end")
                self.text_widget.configure(state="disabled")
                self.text_widget.update()
        except Exception:
            pass

    def flush(self): pass
    def fileno(self): raise io.UnsupportedOperation("fileno")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("GDCount — GDMAF")
        self.geometry("960x760")
        self.resizable(False, False)

        # Ícone da janela
        if getattr(sys, "frozen", False):
            _base = os.path.dirname(sys.executable)
        else:
            _base = os.path.dirname(os.path.abspath(__file__))
        _ico = os.path.join(_base, "GDcount.ico")
        if os.path.exists(_ico):
            self.iconbitmap(_ico)

        self.selected_files = []
        self.output_dir = ""

        self._build_ui()

    def _build_ui(self):
        # ── CABEÇALHO: logo esquerda + textos ────────────────────────────────
        frame_header = ctk.CTkFrame(self, corner_radius=12)
        frame_header.pack(fill="x", padx=20, pady=(14, 10))

        row_header = ctk.CTkFrame(frame_header, fg_color="transparent")
        row_header.pack(padx=20, pady=12)

        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_gdmaf.png")
        if os.path.exists(logo_path):
            pil_img = Image.open(logo_path).convert("RGBA")
            self._logo_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(68, 68))
            ctk.CTkLabel(row_header, image=self._logo_img, text="").pack(side="left", padx=(0, 18))

        col_texts = ctk.CTkFrame(row_header, fg_color="transparent")
        col_texts.pack(side="left", anchor="center")
        ctk.CTkLabel(col_texts, text="🔬  GDCount",
                     font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(col_texts, text="Segmentação automática com U-Net + SAM",
                     font=ctk.CTkFont(size=12), text_color="gray").pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(col_texts, text="GDMAF — Grupo de Materiais Funcionais, UNIFEI",
                     font=ctk.CTkFont(size=11, weight="bold"), text_color="#4a9eff").pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(col_texts,
                     text="Freire, L.A; Menezes, E.A.F.M; Thomazini, D; Gelfuso, M.V",
                     font=ctk.CTkFont(size=10), text_color="#888888").pack(anchor="w", pady=(2, 0))

        # ── LINHA 1: Imagem entrada (esq) + Pasta saída (dir) ────────────────
        row1 = ctk.CTkFrame(self, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=(0, 8))

        # Imagem entrada
        frame_img = ctk.CTkFrame(row1, corner_radius=10)
        frame_img.pack(side="left", fill="both", expand=True, padx=(0, 6))

        header_img = ctk.CTkFrame(frame_img, fg_color="transparent")
        header_img.pack(fill="x", padx=14, pady=(10, 4))
        ctk.CTkLabel(header_img, text="📁  Imagens de entrada",
                     font=ctk.CTkFont(weight="bold")).pack(side="left")
        self.label_contador = ctk.CTkLabel(header_img, text="", text_color="gray",
                                           font=ctk.CTkFont(size=11))
        self.label_contador.pack(side="right")

        self.listbox = ctk.CTkTextbox(frame_img, height=80, state="disabled",
                                      font=ctk.CTkFont(family="Consolas", size=11))
        self.listbox.pack(fill="x", padx=14, pady=(0, 6))

        row_img_btns = ctk.CTkFrame(frame_img, fg_color="transparent")
        row_img_btns.pack(fill="x", padx=14, pady=(0, 10))
        ctk.CTkButton(row_img_btns, text="Adicionar", width=130,
                      command=self.select_images).pack(side="left")
        ctk.CTkButton(row_img_btns, text="Limpar", width=90,
                      fg_color="transparent", hover_color="#3a3d3e",
                      command=self.clear_images).pack(side="left", padx=(8, 0))

        # Pasta saída
        frame_out = ctk.CTkFrame(row1, corner_radius=10)
        frame_out.pack(side="right", fill="both", expand=True, padx=(6, 0))

        ctk.CTkLabel(frame_out, text="💾  Pasta de saída",
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=14, pady=(10, 4))
        self.label_saida = ctk.CTkLabel(frame_out,
                                        text="Mesma pasta das imagens (padrão)",
                                        text_color="gray", anchor="w", wraplength=360)
        self.label_saida.pack(fill="x", padx=14, pady=(0, 4))

        row_out_btns = ctk.CTkFrame(frame_out, fg_color="transparent")
        row_out_btns.pack(fill="x", padx=14, pady=(0, 10))
        ctk.CTkButton(row_out_btns, text="Alterar", width=130,
                      command=self.select_output_dir).pack(side="left")
        self.btn_abrir_pasta = ctk.CTkButton(
            row_out_btns, text="📂 Abrir pasta", width=120,
            fg_color="transparent", hover_color="#3a3d3e",
            state="disabled", command=self.open_output_folder)
        self.btn_abrir_pasta.pack(side="left", padx=(8, 0))

        # ── LINHA 2: Parâmetros (full width) ─────────────────────────────────
        frame_params = ctk.CTkFrame(self, corner_radius=10)
        frame_params.pack(fill="x", padx=20, pady=(0, 8))

        ctk.CTkLabel(frame_params, text="⚙️  Parâmetros de segmentação",
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=14, pady=(10, 6))

        row_p = ctk.CTkFrame(frame_params, fg_color="transparent")
        row_p.pack(fill="x", padx=14, pady=(0, 4))

        col1 = ctk.CTkFrame(row_p, fg_color="transparent")
        col1.pack(side="left", expand=True, fill="x", padx=(0, 8))
        ctk.CTkLabel(col1, text="Distância mínima entre grãos",
                     font=ctk.CTkFont(size=12)).pack(anchor="w")
        ctk.CTkLabel(col1, text="dbs_max_dist (px)",
                     font=ctk.CTkFont(size=10), text_color="gray").pack(anchor="w")
        self.entry_dbs = ctk.CTkEntry(col1, placeholder_text="Ex: 5.0", width=140)
        self.entry_dbs.insert(0, "5.0")
        self.entry_dbs.pack(anchor="w", pady=(4, 0))

        col2 = ctk.CTkFrame(row_p, fg_color="transparent")
        col2.pack(side="left", expand=True, fill="x", padx=(8, 8))
        ctk.CTkLabel(col2, text="Área mínima de grão",
                     font=ctk.CTkFont(size=12)).pack(anchor="w")
        ctk.CTkLabel(col2, text="min_area (px²)",
                     font=ctk.CTkFont(size=10), text_color="gray").pack(anchor="w")
        self.entry_area = ctk.CTkEntry(col2, placeholder_text="Ex: 150", width=140)
        self.entry_area.insert(0, "150")
        self.entry_area.pack(anchor="w", pady=(4, 0))

        col3 = ctk.CTkFrame(row_p, fg_color="transparent")
        col3.pack(side="right", expand=True, fill="x", padx=(8, 0))
        ctk.CTkLabel(col3, text="Escala da imagem",
                     font=ctk.CTkFont(size=12)).pack(anchor="w")
        ctk.CTkLabel(col3, text="pixels por µm (calibração)",
                     font=ctk.CTkFont(size=10), text_color="gray").pack(anchor="w")
        self.entry_px_um = ctk.CTkEntry(col3, placeholder_text="Ex: 10", width=140)
        self.entry_px_um.pack(anchor="w", pady=(4, 0))

        ctk.CTkLabel(frame_params,
                     text="⚠  Deixe escala em branco para resultados apenas em pixels",
                     font=ctk.CTkFont(size=10), text_color="gray").pack(anchor="w", padx=14, pady=(6, 10))

        # ── BOTÃO INICIAR ─────────────────────────────────────────────────────
        self.btn_run = ctk.CTkButton(
            self, text="▶  Iniciar Contagem",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=44, state="disabled", command=self.run_process)
        self.btn_run.pack(fill="x", padx=20, pady=(0, 8))

        # ── LINHA 3: Log (esq) + Resultados (dir) ────────────────────────────
        row3 = ctk.CTkFrame(self, fg_color="transparent")
        row3.pack(fill="both", expand=True, padx=20, pady=(0, 8))

        frame_log = ctk.CTkFrame(row3, corner_radius=10)
        frame_log.pack(side="left", fill="both", expand=True, padx=(0, 6))
        ctk.CTkLabel(frame_log, text="📋  Log de progresso",
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=14, pady=(10, 4))
        self.log_box = ctk.CTkTextbox(frame_log, height=240, state="disabled",
                                      font=ctk.CTkFont(family="Consolas", size=11))
        self.log_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        frame_results = ctk.CTkFrame(row3, corner_radius=10)
        frame_results.pack(side="right", fill="both", expand=True, padx=(6, 0))
        ctk.CTkLabel(frame_results, text="📊  Resultados",
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=14, pady=(10, 4))
        self.results_box = ctk.CTkTextbox(frame_results, height=240, state="disabled",
                                          font=ctk.CTkFont(family="Consolas", size=11))
        self.results_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # ── STATUS ────────────────────────────────────────────────────────────
        self.status_label = ctk.CTkLabel(self, text="Aguardando seleção de imagens...",
                                         font=ctk.CTkFont(size=12), text_color="gray")
        self.status_label.pack(pady=(0, 10))

    # ── Ações ────────────────────────────────────────────────────────────────
    def select_images(self):
        files = filedialog.askopenfilenames(
            title="Selecionar imagens MEV",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png *.tif *.tiff")])
        if files:
            for f in files:
                if f not in self.selected_files:
                    self.selected_files.append(f)
            self._update_file_list()
            if not self.output_dir:
                self.output_dir = os.path.dirname(self.selected_files[0])
                self.label_saida.configure(text=self.output_dir, text_color="gray")
            self.btn_run.configure(state="normal")

    def clear_images(self):
        self.selected_files = []
        self._update_file_list()
        self.btn_run.configure(state="disabled")
        self.status_label.configure(text="Lista limpa. Adicione imagens para continuar.",
                                    text_color="gray")

    def _update_file_list(self):
        self.listbox.configure(state="normal")
        self.listbox.delete("1.0", "end")
        for f in self.selected_files:
            self.listbox.insert("end", os.path.basename(f) + "\n")
        self.listbox.configure(state="disabled")
        n = len(self.selected_files)
        self.label_contador.configure(
            text=f"{n} imagem{'ns' if n > 1 else ''}" if n else "")

    def select_output_dir(self):
        folder = filedialog.askdirectory(title="Selecionar pasta de saída")
        if folder:
            self.output_dir = folder
            self.label_saida.configure(text=folder, text_color="white")

    def open_output_folder(self):
        if self.output_dir and os.path.isdir(self.output_dir):
            os.startfile(self.output_dir)

    def _log(self, msg):
        try:
            self.log_box.configure(state="normal")
            self.log_box.insert("end", msg + "\n")
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
            self.log_box.update()
        except Exception:
            pass

    def _show_results(self, text):
        try:
            self.results_box.configure(state="normal")
            self.results_box.delete("1.0", "end")
            self.results_box.insert("end", text)
            self.results_box.configure(state="disabled")
        except Exception:
            pass

    def _validate_params(self):
        try:
            dbs = float(self.entry_dbs.get())
            area = float(self.entry_area.get())
            if dbs <= 0 or area <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Parâmetros inválidos",
                                 "Distância mínima e área mínima devem ser números positivos.")
            return None, None, None

        px_um_str = self.entry_px_um.get().strip().replace(",", ".")
        px_um = None
        if px_um_str:
            try:
                px_um = float(px_um_str)
                if px_um <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Escala inválida",
                                     "Pixels por µm deve ser um número positivo.\n"
                                     "Deixe em branco para usar apenas pixels.")
                return None, None, None

        return dbs, area, px_um

    def run_process(self):
        if not self.selected_files:
            messagebox.showwarning("Nenhuma imagem", "Adicione pelo menos uma imagem.")
            return

        dbs_val, area_val, px_um = self._validate_params()
        if dbs_val is None:
            return

        self.btn_run.configure(state="disabled", text="⏳  Processando...")
        self.btn_abrir_pasta.configure(state="disabled")
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")
        self._show_results("Aguardando conclusão do processamento...")

        redirector = StreamRedirector(self.log_box)
        sys.stdout = redirector
        sys.stderr = redirector

        total = len(self.selected_files)
        files = list(self.selected_files)
        output_dir = self.output_dir

        def worker():
            erros = []
            todos_resultados = []

            for i, image_path in enumerate(files, 1):
                nome = os.path.basename(image_path)
                self.after(0, lambda n=nome, i=i, t=total: self.status_label.configure(
                    text=f"Processando {i}/{t}: {n}", text_color="yellow"))
                self.after(0, lambda n=nome, i=i, t=total: self._log(
                    f"\n{'='*46}\n[{i}/{t}] {n}\n{'='*46}"))
                try:
                    import count_grains
                    grain_data = count_grains.count_grains(
                        image_path,
                        output_dir=output_dir,
                        dbs_max_dist=dbs_val,
                        min_area=area_val,
                        px_per_um=px_um)
                    todos_resultados.append((nome, grain_data, px_um))
                except Exception as e:
                    msg = str(e)
                    erros.append((nome, msg))
                    self.after(0, lambda n=nome, m=msg: self._log(f"❌ ERRO em {n}: {m}"))

            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            self.after(0, lambda: self._on_done(total, erros, todos_resultados))

        threading.Thread(target=worker, daemon=True).start()

    def _on_done(self, total, erros, todos_resultados):
        self.btn_run.configure(state="normal", text="▶  Iniciar Contagem")
        self.btn_abrir_pasta.configure(state="normal")
        n_ok = total - len(erros)

        linhas = []
        for nome, grain_data, px_um in todos_resultados:
            n_graos = len(grain_data)
            if px_um is not None:
                um_per_px = 1.0 / px_um
                areas = grain_data['area'] * (um_per_px ** 2)
                unidade_area, unidade_diam = "µm²", "µm"
            else:
                areas = grain_data['area']
                unidade_area, unidade_diam = "px²", "px"

            diametros = areas.apply(lambda a: 2 * math.sqrt(a / math.pi))
            linhas.append(f"{'─'*42}")
            linhas.append(f"📷 {nome}")
            linhas.append(f"   Grãos detectados : {n_graos}")
            linhas.append(f"   Área   — média   : {areas.mean():.2f} {unidade_area}")
            linhas.append(f"   Área   — desvio  : {areas.std():.2f} {unidade_area}")
            linhas.append(f"   Diâm.  — média   : {diametros.mean():.2f} {unidade_diam}")
            linhas.append(f"   Diâm.  — desvio  : {diametros.std():.2f} {unidade_diam}")

        self._show_results("\n".join(linhas) if linhas else "Nenhum resultado disponível.")

        if not erros:
            self.status_label.configure(
                text=f"✅  {total} imagem{'ns' if total > 1 else ''} concluída{'s' if total > 1 else ''} com sucesso!",
                text_color="#4caf50")
            messagebox.showinfo("Concluído!",
                f"Todas as {total} imagens foram processadas!\n\n"
                "Arquivos gerados para cada imagem:\n"
                "  • <nome>_grain_data.csv\n"
                "  • <nome>_grain_mask_all.tif")
        else:
            self.status_label.configure(
                text=f"⚠️  {n_ok}/{total} concluídas. {len(erros)} com erro.",
                text_color="orange")
            detalhes = "\n".join(f"• {n}: {m}" for n, m in erros)
            messagebox.showwarning("Concluído com erros",
                f"{n_ok} de {total} imagens processadas.\n\nErros:\n{detalhes}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
