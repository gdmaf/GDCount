import io
import sys
import os

# ─── DEVE SER O PRIMEIRO CODIGO A RODAR ─────────────────────────────────────
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
import webbrowser
import math
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image

# ─── Traduções ────────────────────────────────────────────────────────────────
STRINGS = {
    "en": {
        "title":            "GDCount — GDMAF",
        "subtitle":         "Automated grain segmentation with U-Net + SAM",
        "group":            "GDMAF — Grupo de Desenvolvimento de Materiais Funcionais, UNIFEI",
        "authors":          "Freire, L.A; Menezes, E.A.F.M; Thomazini, D; Gelfuso, M.V",
        "input_label":      "📁  Input images",
        "output_label":     "💾  Output folder",
        "output_default":   "Same folder as images (default)",
        "params_label":     "⚙️  Segmentation parameters",
        "dbs_label":        "Minimum distance between grains",
        "dbs_sub":          "dbs_max_dist (px)",
        "area_label":       "Minimum grain area",
        "area_sub":         "min_area (px²)",
        "scale_label":      "Image scale",
        "scale_sub":        "pixels per µm (calibration)",
        "scale_hint":       "⚠  Leave scale blank for pixel-only results",
        "max_area_label":   "Maximum grain area",
        "max_area_sub":     "max_area (px²) — leave blank for no limit",
        "max_len_label":    "Maximum grain length",
        "max_len_sub":      "max_length (px) — major axis — leave blank for no limit",
        "ar_min_label":     "Minimum aspect ratio",
        "ar_min_sub":       "major / minor axis — 1.0 = circle — leave blank for no limit",
        "ar_max_label":     "Maximum aspect ratio",
        "ar_max_sub":       "major / minor axis — leave blank for no limit",

        "btn_add":          "Add images",
        "btn_clear":        "Clear list",
        "btn_change":       "Change",
        "btn_open":         "📂 Open folder",
        "btn_run":          "▶  Start Count",
        "btn_running":      "⏳  Processing...",
        "log_label":        "📋  Progress log",
        "results_label":    "📊  Results",
        "status_wait":      "Waiting for image selection...",
        "status_cleared":   "List cleared. Add images to continue.",
        "status_ready":     "Image ready. Adjust parameters and click Start.",
        "n_images":         lambda n: f"{n} image{'s' if n > 1 else ''} selected",
        "processing":       lambda i, t, n: f"Processing {i}/{t}: {n}",
        "done_all":         lambda t: f"✅  {t} image{'s' if t > 1 else ''} completed successfully!",
        "done_partial":     lambda ok, t, e: f"⚠️  {ok}/{t} completed. {e} with error.",
        "error_status":     "❌  Processing error.",
        "awaiting":         "Waiting for processing to complete...",
        "grains":           "Grains detected",
        "area_mean":        "Area    — mean  ",
        "area_std":         "Area    — std   ",
        "diam_mean":        "Diam.   — mean  ",
        "diam_std":         "Diam.   — std   ",
        "no_results":       "No results available.",
        "msg_done_title":   "Completed!",
        "msg_done_body":    lambda t: (
            f"All {t} images processed successfully!\n\n"
            "Files generated for each image:\n"
            "  • <name>_grain_data.csv\n"
            "  • <name>_grain_mask_all.tif\n"
            "  • <name>_grain_overlay.png"
        ),
        "msg_warn_title":   "Completed with errors",
        "msg_warn_body":    lambda ok, t, det: f"{ok} of {t} images processed.\n\nErrors:\n{det}",
        "err_params_title": "Invalid parameters",
        "err_params_body":  "Min. distance and min. area must be positive numbers.",
        "err_scale_title":  "Invalid scale",
        "err_scale_body":   "Pixels per µm must be a positive number.\nLeave blank for pixel-only output.",
        "err_no_img_title": "No image",
        "err_no_img_body":  "Add at least one image.",
        "lang_label":       "Language",
        "csv_label":        "CSV format",
        "csv_en":           "EN  (. decimal, , sep)",
        "csv_br":           "BR  (, decimal, ; sep)",
        "select_title":     "Select SEM images",
        "select_out_title": "Select output folder",
    },
    "pt": {
        "title":            "GDCount — GDMAF",
        "subtitle":         "Segmentação automática com U-Net + SAM",
        "group":            "GDMAF — Grupo de Desenvolvimento de Materiais Funcionais, UNIFEI",
        "authors":          "Freire, L.A; Menezes, E.A.F.M; Thomazini, D; Gelfuso, M.V",
        "input_label":      "📁  Imagens de entrada",
        "output_label":     "💾  Pasta de saída",
        "output_default":   "Mesma pasta das imagens (padrão)",
        "params_label":     "⚙️  Parâmetros de segmentação",
        "dbs_label":        "Distância mínima entre grãos",
        "dbs_sub":          "dbs_max_dist (px)",
        "area_label":       "Área mínima de grão",
        "area_sub":         "min_area (px²)",
        "scale_label":      "Escala da imagem",
        "scale_sub":        "pixels por µm (calibração)",
        "scale_hint":       "⚠  Deixe escala em branco para resultados apenas em pixels",
        "max_area_label":   "Área máxima de grão",
        "max_area_sub":     "max_area (px²) — deixe em branco sem limite",
        "max_len_label":    "Comprimento máximo de grão",
        "max_len_sub":      "max_length (px) — maior eixo — deixe em branco sem limite",
        "ar_min_label":     "Razão de aspecto mínima",
        "ar_min_sub":       "maior / menor eixo — 1,0 = círculo — deixe em branco sem limite",
        "ar_max_label":     "Razão de aspecto máxima",
        "ar_max_sub":       "maior / menor eixo — deixe em branco sem limite",

        "btn_add":          "Adicionar imagens",
        "btn_clear":        "Limpar lista",
        "btn_change":       "Alterar",
        "btn_open":         "📂 Abrir pasta",
        "btn_run":          "▶  Iniciar Contagem",
        "btn_running":      "⏳  Processando...",
        "log_label":        "📋  Log de progresso",
        "results_label":    "📊  Resultados",
        "status_wait":      "Aguardando seleção de imagens...",
        "status_cleared":   "Lista limpa. Adicione imagens para continuar.",
        "status_ready":     "Imagem pronta. Ajuste os parâmetros e clique em Iniciar.",
        "n_images":         lambda n: f"{n} imagem{'ns' if n > 1 else ''} selecionada{'s' if n > 1 else ''}",
        "processing":       lambda i, t, n: f"Processando {i}/{t}: {n}",
        "done_all":         lambda t: f"✅  {t} imagem{'ns' if t > 1 else ''} concluída{'s' if t > 1 else ''} com sucesso!",
        "done_partial":     lambda ok, t, e: f"⚠️  {ok}/{t} concluídas. {e} com erro.",
        "error_status":     "❌  Erro no processamento.",
        "awaiting":         "Aguardando conclusão do processamento...",
        "grains":           "Grãos detectados",
        "area_mean":        "Área   — média  ",
        "area_std":         "Área   — desvio ",
        "diam_mean":        "Diâm.  — média  ",
        "diam_std":         "Diâm.  — desvio ",
        "no_results":       "Nenhum resultado disponível.",
        "msg_done_title":   "Concluído!",
        "msg_done_body":    lambda t: (
            f"Todas as {t} imagens foram processadas!\n\n"
            "Arquivos gerados para cada imagem:\n"
            "  • <nome>_grain_data.csv\n"
            "  • <nome>_grain_mask_all.tif\n"
            "  • <nome>_grain_overlay.png"
        ),
        "msg_warn_title":   "Concluído com erros",
        "msg_warn_body":    lambda ok, t, det: f"{ok} de {t} imagens processadas.\n\nErros:\n{det}",
        "err_params_title": "Parâmetros inválidos",
        "err_params_body":  "Distância mínima e área mínima devem ser números positivos.",
        "err_scale_title":  "Escala inválida",
        "err_scale_body":   "Pixels por µm deve ser um número positivo.\nDeixe em branco para usar apenas pixels.",
        "err_no_img_title": "Nenhuma imagem",
        "err_no_img_body":  "Adicione pelo menos uma imagem.",
        "lang_label":       "Idioma",
        "csv_label":        "Formato CSV",
        "csv_en":           "EN  (. decimal, , sep)",
        "csv_br":           "BR  (, decimal, ; sep)",
        "select_title":     "Selecionar imagens MEV",
        "select_out_title": "Selecionar pasta de saída",
    },
}


# ─── Redireciona prints para a caixa de log ──────────────────────────────────
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


# ─── Janela principal ────────────────────────────────────────────────────────
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.geometry("1100x720")
        self.resizable(False, False)

        # Ícone
        if getattr(sys, "frozen", False):
            _base = os.path.dirname(sys.executable)
        else:
            _base = os.path.dirname(os.path.abspath(__file__))
        _ico = os.path.join(_base, "GDcount.ico")
        if os.path.exists(_ico):
            self.iconbitmap(_ico)

        self.selected_files = []
        self.output_dir = ""

        # Estado de idioma e formato CSV
        self._lang = "en"
        self._csv_fmt = "en"  # "en" ou "br"

        self.log_box     = None
        self.results_box = None
        self._popup      = None

        self._build_ui()
        self._apply_lang()

    # ── Helpers de tradução ───────────────────────────────────────────────────
    def _t(self, key):
        return STRINGS[self._lang][key]

    # ── Construção da UI ──────────────────────────────────────────────────────
    def _build_ui(self):
        # ── CABEÇALHO ────────────────────────────────────────────────────────
        frame_header = ctk.CTkFrame(self, corner_radius=12)
        frame_header.pack(fill="x", padx=20, pady=(14, 10))

        # Linha superior: logo + textos + seletores
        row_top = ctk.CTkFrame(frame_header, fg_color="transparent")
        row_top.pack(fill="x", padx=16, pady=(12, 4))

        # Logo
        if getattr(sys, "frozen", False):
            _base = os.path.dirname(sys.executable)
        else:
            _base = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(_base, "logo_gdmaf.png")
        if os.path.exists(logo_path):
            pil_img = Image.open(logo_path).convert("RGBA")
            self._logo_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(68, 68))
            ctk.CTkLabel(row_top, image=self._logo_img, text="").pack(side="left", padx=(0, 18))

        # Textos
        col_texts = ctk.CTkFrame(row_top, fg_color="transparent")
        col_texts.pack(side="left", anchor="center")
        self.lbl_title    = ctk.CTkLabel(col_texts, text="",
                                          font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"))
        self.lbl_title.pack(anchor="w")
        self.lbl_subtitle = ctk.CTkLabel(col_texts, text="",
                                          font=ctk.CTkFont(size=12), text_color="gray")
        self.lbl_subtitle.pack(anchor="w", pady=(2, 0))
        # Grupo como hyperlink
        self.lbl_group = ctk.CTkLabel(col_texts, text="",
                                       font=ctk.CTkFont(size=11, weight="bold"), text_color="#4a9eff",
                                       cursor="hand2")
        self.lbl_group.pack(anchor="w", pady=(2, 0))
        self.lbl_group.bind("<Button-1>", lambda e: webbrowser.open("http://gdmaf.unifei.edu.br"))
        self.lbl_group.bind("<Enter>", lambda e: self.lbl_group.configure(text_color="#7abfff"))
        self.lbl_group.bind("<Leave>", lambda e: self.lbl_group.configure(text_color="#4a9eff"))

        self.lbl_authors = ctk.CTkLabel(col_texts, text="",
                                         font=ctk.CTkFont(size=10), text_color="#888888")
        self.lbl_authors.pack(anchor="w", pady=(2, 0))

        # Ícones de redes sociais
        row_social = ctk.CTkFrame(col_texts, fg_color="transparent")
        row_social.pack(anchor="w", pady=(4, 0))

        _social_data = [
            ("instagram.png", "https://www.instagram.com/gdmaf_unifei/"),
            ("linkedin.png",  "https://www.linkedin.com/company/grupo-de-desenvolvimento-de-materiais-funcionais/"),
            ("facebook.png",  "https://www.facebook.com/people/Grupo-de-Desenvolvimento-de-Materiais-Funcionais/100092663902474/"),
        ]
        for fname, url in _social_data:
            icon_path = os.path.join(_base, fname)
            if os.path.exists(icon_path):
                pil_icon = Image.open(icon_path).convert("RGBA")
                ctk_icon = ctk.CTkImage(light_image=pil_icon, dark_image=pil_icon, size=(26,26))
                btn = ctk.CTkButton(
                    row_social, text="", image=ctk_icon,
                    width=30, height=30,
                    fg_color="transparent", hover_color="#2a2d2e",
                    corner_radius=6,
                    command=lambda u=url: webbrowser.open(u))
            else:
                btn = ctk.CTkButton(
                    row_social, text=fname[:2],
                    width=30, height=30,
                    corner_radius=6,
                    command=lambda u=url: webbrowser.open(u))
            btn.pack(side="left", padx=(0, 4))

        # Seletores (direita do cabeçalho)
        col_sel = ctk.CTkFrame(row_top, fg_color="transparent")
        col_sel.pack(side="right", anchor="center")

        # Idioma
        self.lbl_lang = ctk.CTkLabel(col_sel, text="", font=ctk.CTkFont(size=11), text_color="gray")
        self.lbl_lang.pack(anchor="e")
        self.opt_lang = ctk.CTkOptionMenu(
            col_sel, values=["English", "Português"],
            width=130, command=self._on_lang_change)
        self.opt_lang.pack(anchor="e", pady=(2, 8))

        # CSV format
        self.lbl_csv = ctk.CTkLabel(col_sel, text="", font=ctk.CTkFont(size=11), text_color="gray")
        self.lbl_csv.pack(anchor="e")
        self.opt_csv = ctk.CTkOptionMenu(
            col_sel, values=["EN  (. decimal, , sep)", "BR  (, decimal, ; sep)"],
            width=180, command=self._on_csv_change)
        self.opt_csv.pack(anchor="e", pady=(2, 0))

        # ── LINHA 1: Imagem (esq) + Pasta saída (dir) ────────────────────────
        row1 = ctk.CTkFrame(self, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=(0, 8))

        # Imagem
        frame_img = ctk.CTkFrame(row1, corner_radius=10)
        frame_img.pack(side="left", fill="both", expand=True, padx=(0, 6))

        header_img = ctk.CTkFrame(frame_img, fg_color="transparent")
        header_img.pack(fill="x", padx=14, pady=(10, 4))
        self.lbl_input = ctk.CTkLabel(header_img, text="", font=ctk.CTkFont(weight="bold"))
        self.lbl_input.pack(side="left")
        self.lbl_contador = ctk.CTkLabel(header_img, text="", text_color="gray",
                                         font=ctk.CTkFont(size=11))
        self.lbl_contador.pack(side="right")

        self.listbox = ctk.CTkTextbox(frame_img, height=80, state="disabled",
                                      font=ctk.CTkFont(family="Consolas", size=11))
        self.listbox.pack(fill="x", padx=14, pady=(0, 6))

        row_img_btns = ctk.CTkFrame(frame_img, fg_color="transparent")
        row_img_btns.pack(fill="x", padx=14, pady=(0, 10))
        self.btn_add = ctk.CTkButton(row_img_btns, text="", width=150, command=self.select_images)
        self.btn_add.pack(side="left")
        self.btn_clear = ctk.CTkButton(row_img_btns, text="", width=100,
                                       fg_color="transparent", hover_color="#3a3d3e",
                                       command=self.clear_images)
        self.btn_clear.pack(side="left", padx=(8, 0))

        # Pasta saída
        frame_out = ctk.CTkFrame(row1, corner_radius=10)
        frame_out.pack(side="right", fill="both", expand=True, padx=(6, 0))

        self.lbl_output = ctk.CTkLabel(frame_out, text="", font=ctk.CTkFont(weight="bold"))
        self.lbl_output.pack(anchor="w", padx=14, pady=(10, 4))
        self.lbl_saida = ctk.CTkLabel(frame_out, text="", text_color="gray",
                                      anchor="w", wraplength=360)
        self.lbl_saida.pack(fill="x", padx=14, pady=(0, 4))

        row_out_btns = ctk.CTkFrame(frame_out, fg_color="transparent")
        row_out_btns.pack(fill="x", padx=14, pady=(0, 10))
        self.btn_change = ctk.CTkButton(row_out_btns, text="", width=130,
                                        command=self.select_output_dir)
        self.btn_change.pack(side="left")
        self.btn_abrir_pasta = ctk.CTkButton(
            row_out_btns, text="", width=130,
            fg_color="transparent", hover_color="#3a3d3e",
            state="disabled", command=self.open_output_folder)
        self.btn_abrir_pasta.pack(side="left", padx=(8, 0))

        # ── LINHA 2: Parâmetros ───────────────────────────────────────────────
        frame_params = ctk.CTkFrame(self, corner_radius=10)
        frame_params.pack(fill="x", padx=20, pady=(0, 8))

        self.lbl_params = ctk.CTkLabel(frame_params, text="", font=ctk.CTkFont(weight="bold"))
        self.lbl_params.pack(anchor="w", padx=14, pady=(10, 6))

        row_p = ctk.CTkFrame(frame_params, fg_color="transparent")
        row_p.pack(fill="x", padx=14, pady=(0, 4))

        col1 = ctk.CTkFrame(row_p, fg_color="transparent")
        col1.pack(side="left", expand=True, fill="x", padx=(0, 8))
        self.lbl_dbs     = ctk.CTkLabel(col1, text="", font=ctk.CTkFont(size=12))
        self.lbl_dbs.pack(anchor="w")
        self.lbl_dbs_sub = ctk.CTkLabel(col1, text="dbs_max_dist (px)",
                                         font=ctk.CTkFont(size=10), text_color="gray")
        self.lbl_dbs_sub.pack(anchor="w")
        self.entry_dbs = ctk.CTkEntry(col1, placeholder_text="Ex: 5.0", width=140)
        self.entry_dbs.insert(0, "5.0")
        self.entry_dbs.pack(anchor="w", pady=(4, 0))

        col2 = ctk.CTkFrame(row_p, fg_color="transparent")
        col2.pack(side="left", expand=True, fill="x", padx=(8, 8))
        self.lbl_area     = ctk.CTkLabel(col2, text="", font=ctk.CTkFont(size=12))
        self.lbl_area.pack(anchor="w")
        self.lbl_area_sub = ctk.CTkLabel(col2, text="min_area (px²)",
                                          font=ctk.CTkFont(size=10), text_color="gray")
        self.lbl_area_sub.pack(anchor="w")
        self.entry_area = ctk.CTkEntry(col2, placeholder_text="Ex: 150", width=140)
        self.entry_area.insert(0, "150")
        self.entry_area.pack(anchor="w", pady=(4, 0))

        col3 = ctk.CTkFrame(row_p, fg_color="transparent")
        col3.pack(side="right", expand=True, fill="x", padx=(8, 0))
        self.lbl_scale     = ctk.CTkLabel(col3, text="", font=ctk.CTkFont(size=12))
        self.lbl_scale.pack(anchor="w")
        self.lbl_scale_sub = ctk.CTkLabel(col3, text="", font=ctk.CTkFont(size=10), text_color="gray")
        self.lbl_scale_sub.pack(anchor="w")
        self.entry_px_um = ctk.CTkEntry(col3, placeholder_text="Ex: 10", width=140)
        self.entry_px_um.pack(anchor="w", pady=(4, 0))

        # Segunda linha: max_area + max_length + ar_min + ar_max (todos na mesma linha)
        row_p2 = ctk.CTkFrame(frame_params, fg_color="transparent")
        row_p2.pack(fill="x", padx=14, pady=(8, 4))

        col4 = ctk.CTkFrame(row_p2, fg_color="transparent")
        col4.pack(side="left", expand=True, fill="x", padx=(0, 6))
        self.lbl_max_area     = ctk.CTkLabel(col4, text="", font=ctk.CTkFont(size=12))
        self.lbl_max_area.pack(anchor="w")
        self.lbl_max_area_sub = ctk.CTkLabel(col4, text="", font=ctk.CTkFont(size=10), text_color="gray")
        self.lbl_max_area_sub.pack(anchor="w")
        self.entry_max_area = ctk.CTkEntry(col4, placeholder_text="—", width=120)
        self.entry_max_area.pack(anchor="w", pady=(4, 0))

        col5 = ctk.CTkFrame(row_p2, fg_color="transparent")
        col5.pack(side="left", expand=True, fill="x", padx=(6, 6))
        self.lbl_max_len     = ctk.CTkLabel(col5, text="", font=ctk.CTkFont(size=12))
        self.lbl_max_len.pack(anchor="w")
        self.lbl_max_len_sub = ctk.CTkLabel(col5, text="", font=ctk.CTkFont(size=10), text_color="gray")
        self.lbl_max_len_sub.pack(anchor="w")
        self.entry_max_len = ctk.CTkEntry(col5, placeholder_text="—", width=120)
        self.entry_max_len.pack(anchor="w", pady=(4, 0))

        col7 = ctk.CTkFrame(row_p2, fg_color="transparent")
        col7.pack(side="left", expand=True, fill="x", padx=(6, 6))
        self.lbl_ar_min     = ctk.CTkLabel(col7, text="", font=ctk.CTkFont(size=12))
        self.lbl_ar_min.pack(anchor="w")
        self.lbl_ar_min_sub = ctk.CTkLabel(col7, text="", font=ctk.CTkFont(size=10), text_color="gray")
        self.lbl_ar_min_sub.pack(anchor="w")
        self.entry_ar_min = ctk.CTkEntry(col7, placeholder_text="—", width=120)
        self.entry_ar_min.pack(anchor="w", pady=(4, 0))

        col8 = ctk.CTkFrame(row_p2, fg_color="transparent")
        col8.pack(side="left", expand=True, fill="x", padx=(6, 6))
        self.lbl_ar_max     = ctk.CTkLabel(col8, text="", font=ctk.CTkFont(size=12))
        self.lbl_ar_max.pack(anchor="w")
        self.lbl_ar_max_sub = ctk.CTkLabel(col8, text="", font=ctk.CTkFont(size=10), text_color="gray")
        self.lbl_ar_max_sub.pack(anchor="w")
        self.entry_ar_max = ctk.CTkEntry(col8, placeholder_text="—", width=120)
        self.entry_ar_max.pack(anchor="w", pady=(4, 0))


        self.lbl_scale_hint = ctk.CTkLabel(frame_params, text="",
                                            font=ctk.CTkFont(size=10), text_color="gray")
        self.lbl_scale_hint.pack(anchor="w", padx=14, pady=(6, 10))

        # ── BOTÃO INICIAR ─────────────────────────────────────────────────────
        self.btn_run = ctk.CTkButton(
            self, text="",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=44, state="disabled", command=self.run_process)
        self.btn_run.pack(fill="x", padx=20, pady=(0, 8))

        # ── LOG + RESULTADOS ──────────────────────────────────────────────────
        row3 = ctk.CTkFrame(self, fg_color="transparent")
        row3.pack(fill="both", expand=True, padx=20, pady=(0, 8))

        frame_log = ctk.CTkFrame(row3, corner_radius=10)
        frame_log.pack(side="left", fill="both", expand=True, padx=(0, 6))
        self.lbl_log = ctk.CTkLabel(frame_log, text="", font=ctk.CTkFont(weight="bold"))
        self.lbl_log.pack(anchor="w", padx=14, pady=(10, 4))
        self.log_box = ctk.CTkTextbox(frame_log, height=240, state="disabled",
                                      font=ctk.CTkFont(family="Consolas", size=11))
        self.log_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        frame_results = ctk.CTkFrame(row3, corner_radius=10)
        frame_results.pack(side="right", fill="both", expand=True, padx=(6, 0))
        self.lbl_results = ctk.CTkLabel(frame_results, text="", font=ctk.CTkFont(weight="bold"))
        self.lbl_results.pack(anchor="w", padx=14, pady=(10, 4))
        self.results_box = ctk.CTkTextbox(frame_results, height=240, state="disabled",
                                          font=ctk.CTkFont(family="Consolas", size=11))
        self.results_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # ── STATUS ────────────────────────────────────────────────────────────
        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12), text_color="gray")
        self.status_label.pack(pady=(0, 10))

    # ── Aplicar tradução ──────────────────────────────────────────────────────
    def _apply_lang(self):
        s = STRINGS[self._lang]
        self.title(s["title"])
        self.lbl_title.configure(text="🔬  GDCount")
        self.lbl_subtitle.configure(text=s["subtitle"])
        self.lbl_group.configure(text=s["group"])
        self.lbl_authors.configure(text=s["authors"])
        self.lbl_lang.configure(text=s["lang_label"])
        self.lbl_csv.configure(text=s["csv_label"])
        self.lbl_input.configure(text=s["input_label"])
        self.lbl_output.configure(text=s["output_label"])
        self.lbl_params.configure(text=s["params_label"])
        self.lbl_dbs.configure(text=s["dbs_label"])
        self.lbl_area.configure(text=s["area_label"])
        self.lbl_scale.configure(text=s["scale_label"])
        self.lbl_scale_sub.configure(text=s["scale_sub"])
        self.lbl_max_area.configure(text=s["max_area_label"])
        self.lbl_max_area_sub.configure(text=s["max_area_sub"])
        self.lbl_max_len.configure(text=s["max_len_label"])
        self.lbl_max_len_sub.configure(text=s["max_len_sub"])
        self.lbl_ar_min.configure(text=s["ar_min_label"])
        self.lbl_ar_min_sub.configure(text=s["ar_min_sub"])
        self.lbl_ar_max.configure(text=s["ar_max_label"])
        self.lbl_ar_max_sub.configure(text=s["ar_max_sub"])
        self.lbl_scale_hint.configure(text=s["scale_hint"])
        self.btn_add.configure(text=s["btn_add"])
        self.btn_clear.configure(text=s["btn_clear"])
        self.btn_change.configure(text=s["btn_change"])
        self.btn_abrir_pasta.configure(text=s["btn_open"])
        self.btn_run.configure(
            text=s["btn_run"] if self.btn_run.cget("state") != "disabled"
            else s["btn_run"])

        # Atualiza textos dinâmicos
        if not self.output_dir:
            self.lbl_saida.configure(text=s["output_default"])
        n = len(self.selected_files)
        self.lbl_contador.configure(text=s["n_images"](n) if n else "")
        self.status_label.configure(text=s["status_wait"])

    # ── Eventos dos seletores ─────────────────────────────────────────────────
    def _on_lang_change(self, choice):
        self._lang = "pt" if choice == "Português" else "en"
        self._apply_lang()

    def _on_csv_change(self, choice):
        self._csv_fmt = "br" if choice.startswith("BR") else "en"

    # ── Ações ────────────────────────────────────────────────────────────────
    def select_images(self):
        files = filedialog.askopenfilenames(
            title=self._t("select_title"),
            filetypes=[("Images", "*.jpg *.jpeg *.png *.tif *.tiff")])
        if files:
            for f in files:
                if f not in self.selected_files:
                    self.selected_files.append(f)
            self._update_file_list()
            if not self.output_dir:
                self.output_dir = os.path.dirname(self.selected_files[0])
                self.lbl_saida.configure(text=self.output_dir, text_color="gray")
            self.btn_run.configure(state="normal")

    def clear_images(self):
        self.selected_files = []
        self._update_file_list()
        self.btn_run.configure(state="disabled")
        self.status_label.configure(text=self._t("status_cleared"), text_color="gray")

    def _update_file_list(self):
        self.listbox.configure(state="normal")
        self.listbox.delete("1.0", "end")
        for f in self.selected_files:
            self.listbox.insert("end", os.path.basename(f) + "\n")
        self.listbox.configure(state="disabled")
        n = len(self.selected_files)
        self.lbl_contador.configure(text=self._t("n_images")(n) if n else "")

    def select_output_dir(self):
        folder = filedialog.askdirectory(title=self._t("select_out_title"))
        if folder:
            self.output_dir = folder
            self.lbl_saida.configure(text=folder, text_color="white")

    def open_output_folder(self):
        if self.output_dir and os.path.isdir(self.output_dir):
            os.startfile(self.output_dir)

    def _open_popup(self):
        """Abre a janela de log e resultados."""
        if self._popup is not None:
            try:
                self._popup.destroy()
            except Exception:
                pass
        self._popup = ctk.CTkToplevel(self)
        self._popup.title("GDCount — Log & Results")
        self._popup.geometry("860x500")
        self._popup.resizable(True, True)

        row_pop = ctk.CTkFrame(self._popup, fg_color="transparent")
        row_pop.pack(fill="both", expand=True, padx=16, pady=16)

        frame_log = ctk.CTkFrame(row_pop, corner_radius=10)
        frame_log.pack(side="left", fill="both", expand=True, padx=(0, 6))
        ctk.CTkLabel(frame_log, text=self._t("log_label"),
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=14, pady=(10, 4))
        self.log_box = ctk.CTkTextbox(frame_log, state="disabled",
                                      font=ctk.CTkFont(family="Consolas", size=11))
        self.log_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        frame_res = ctk.CTkFrame(row_pop, corner_radius=10)
        frame_res.pack(side="right", fill="both", expand=True, padx=(6, 0))
        ctk.CTkLabel(frame_res, text=self._t("results_label"),
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=14, pady=(10, 4))
        self.results_box = ctk.CTkTextbox(frame_res, state="disabled",
                                          font=ctk.CTkFont(family="Consolas", size=11))
        self.results_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._popup.lift()
        self._popup.focus()

    def _log(self, msg):
        try:
            if self.log_box is None:
                return
            self.log_box.configure(state="normal")
            self.log_box.insert("end", msg + "\n")
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
            self.log_box.update()
        except Exception:
            pass

    def _show_results(self, text):
        try:
            if self.results_box is None:
                return
            self.results_box.configure(state="normal")
            self.results_box.delete("1.0", "end")
            self.results_box.insert("end", text)
            self.results_box.configure(state="disabled")
        except Exception:
            pass

    def _validate_params(self):
        try:
            dbs = float(self.entry_dbs.get().replace(",", "."))
            area = float(self.entry_area.get().replace(",", "."))
            if dbs <= 0 or area <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(self._t("err_params_title"), self._t("err_params_body"))
            return None, None, None

        px_um_str = self.entry_px_um.get().strip().replace(",", ".")
        px_um = None
        if px_um_str:
            try:
                px_um = float(px_um_str)
                if px_um <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror(self._t("err_scale_title"), self._t("err_scale_body"))
                return None, None, None

        # max_area
        max_area_str = self.entry_max_area.get().strip().replace(",", ".")
        max_area = None
        if max_area_str:
            try:
                max_area = float(max_area_str)
                if max_area <= 0: raise ValueError
            except ValueError:
                messagebox.showerror(self._t("err_params_title"), "Maximum area must be a positive number.")
                return None, None, None, None, None

        # max_length
        max_len_str = self.entry_max_len.get().strip().replace(",", ".")
        max_len = None
        if max_len_str:
            try:
                max_len = float(max_len_str)
                if max_len <= 0: raise ValueError
            except ValueError:
                messagebox.showerror(self._t("err_params_title"), "Maximum length must be a positive number.")
                return None, None, None, None, None

        # aspect ratio min
        ar_min_str = self.entry_ar_min.get().strip().replace(",", ".")
        ar_min = None
        if ar_min_str:
            try:
                ar_min = float(ar_min_str)
                if ar_min < 1.0: raise ValueError
            except ValueError:
                messagebox.showerror(self._t("err_params_title"),
                    "Minimum aspect ratio must be ≥ 1.0." if self._lang == "en"
                    else "Razão de aspecto mínima deve ser ≥ 1,0.")
                return None, None, None, None, None, None, None

        # aspect ratio max
        ar_max_str = self.entry_ar_max.get().strip().replace(",", ".")
        ar_max = None
        if ar_max_str:
            try:
                ar_max = float(ar_max_str)
                if ar_max < 1.0: raise ValueError
            except ValueError:
                messagebox.showerror(self._t("err_params_title"),
                    "Maximum aspect ratio must be ≥ 1.0." if self._lang == "en"
                    else "Razão de aspecto máxima deve ser ≥ 1,0.")
                return None, None, None, None, None, None, None

        if ar_min is not None and ar_max is not None and ar_min > ar_max:
            messagebox.showerror(self._t("err_params_title"),
                "Minimum aspect ratio cannot be greater than maximum." if self._lang == "en"
                else "Razão mínima não pode ser maior que a máxima.")
            return None, None, None, None, None, None, None

        return dbs, area, px_um, max_area, max_len, ar_min, ar_max

    def run_process(self):
        if not self.selected_files:
            messagebox.showwarning(self._t("err_no_img_title"), self._t("err_no_img_body"))
            return

        dbs_val, area_val, px_um, max_area, max_len, ar_min, ar_max = self._validate_params()
        if dbs_val is None:
            return

        self.btn_run.configure(state="disabled", text=self._t("btn_running"))
        self.btn_abrir_pasta.configure(state="disabled")
        self._open_popup()
        self._show_results(self._t("awaiting"))

        redirector = StreamRedirector(self.log_box)
        sys.stdout = redirector
        sys.stderr = redirector

        total    = len(self.selected_files)
        files    = list(self.selected_files)
        outdir   = self.output_dir
        lang     = self._lang
        csvfmt   = self._csv_fmt
        max_area = max_area
        max_len  = max_len
        ar_min        = ar_min
        ar_max        = ar_max

        def worker():
            erros = []
            todos = []
            for i, image_path in enumerate(files, 1):
                nome = os.path.basename(image_path)
                self.after(0, lambda n=nome, i=i, t=total: self.status_label.configure(
                    text=STRINGS[lang]["processing"](i, t, n), text_color="yellow"))
                self.after(0, lambda n=nome, i=i, t=total: self._log(
                    f"\n{'='*46}\n[{i}/{t}] {n}\n{'='*46}"))
                try:
                    import count_grains
                    grain_data = count_grains.count_grains(
                        image_path, output_dir=outdir,
                        dbs_max_dist=dbs_val, min_area=area_val,
                        px_per_um=px_um, csv_format=csvfmt,
                        max_area=max_area, max_length=max_len,
                        ar_min=ar_min, ar_max=ar_max)
                    todos.append((nome, grain_data, px_um))
                except Exception as e:
                    msg = str(e)
                    erros.append((nome, msg))
                    self.after(0, lambda n=nome, m=msg: self._log(f"❌ ERROR: {n}: {m}"))

            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            self.after(0, lambda: self._on_done(total, erros, todos, lang))

        threading.Thread(target=worker, daemon=True).start()

    def _on_done(self, total, erros, todos, lang):
        s = STRINGS[lang]
        self.btn_run.configure(state="normal", text=s["btn_run"])
        self.btn_abrir_pasta.configure(state="normal")
        n_ok = total - len(erros)

        linhas = []
        for nome, grain_data, px_um in todos:
            if px_um is not None:
                areas = grain_data['area'] * ((1.0 / px_um) ** 2)
                ua, ud = "µm²", "µm"
            else:
                areas = grain_data['area']
                ua, ud = "px²", "px"
            diams = areas.apply(lambda a: 2 * math.sqrt(a / math.pi))
            linhas += [
                f"{'─'*42}",
                f"📷 {nome}",
                f"   {s['grains']} : {len(grain_data)}",
                f"   {s['area_mean']} : {areas.mean():.2f} {ua}",
                f"   {s['area_std']}  : {areas.std():.2f} {ua}",
                f"   {s['diam_mean']} : {diams.mean():.2f} {ud}",
                f"   {s['diam_std']}  : {diams.std():.2f} {ud}",
            ]

        self._show_results("\n".join(linhas) if linhas else s["no_results"])

        if not erros:
            self.status_label.configure(text=s["done_all"](total), text_color="#4caf50")
            messagebox.showinfo(s["msg_done_title"], s["msg_done_body"](total))
        else:
            self.status_label.configure(
                text=s["done_partial"](n_ok, total, len(erros)), text_color="orange")
            det = "\n".join(f"• {n}: {m}" for n, m in erros)
            messagebox.showwarning(s["msg_warn_title"], s["msg_warn_body"](n_ok, total, det))


if __name__ == "__main__":
    app = App()
    app.mainloop()
