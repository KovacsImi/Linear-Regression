# -*- coding: utf-8 -*-
"""
=============================================================================
  EGESZSEGBIZTOSITASI KOLTSEGEK - OLS LINEARIS REGRESSZIOS ELEMZES
  (Medical Insurance Cost - OLS Linear Regression Analysis)
=============================================================================

  Szerzo / Author : [Kovács Imre]
  Datum  / Date   : 2026-11-15
  Python          : 3.10+
  Adatforras      : Kaggle - mirichoi0218/insurance
                    (https://www.kaggle.com/datasets/mirichoi0218/insurance)

  Celvaltozo (y)  : charges  (biztositasi koltseg)
  Magyarazo valtozok (X): age, sex, bmi, children, smoker, region

  A kod Jupyter Notebook strukturaju: minden szekciot "# %%"-jel valaszt el,
  igy barmely IDE-ben (VS Code, PyCharm, Spyder) cellankent futtathatonak kell
  lennie.
=============================================================================
"""

# %% ========================================================================
# 0. KONYVTARAK IMPORTALASA (Library Imports)
# ============================================================================
#import sys
#sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import warnings
warnings.filterwarnings("ignore")

import os
import io
import base64
import numpy as np
import pandas as pd

# --- Vizualizacio (Agg backend: nem-interaktiv, nem blokkol) ---
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

# --- Statisztikai modellezes (Statsmodels) ---
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.stattools import durbin_watson

# --- Normalitasvizsgalat ---
from scipy.stats import shapiro, jarque_bera

# --- Hibaertekek ---
from sklearn.metrics import mean_squared_error, mean_absolute_error

# --- Adatbetoltes Kaggle-rol ---
import kagglehub
from kagglehub import KaggleDatasetAdapter

# --- Kimeneti mappa az abraknak ---
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Globalis abra-szamlalo es Base64 kep-tarolo a HTML riporthoz
_plot_counter = [0]
plot_base64 = {}


def save_and_show(fig, name_hint="plot"):
    """Abra mentese PNG-be, Base64 kodolasa a HTML riporthoz es memoria felszabaditasa."""
    _plot_counter[0] += 1
    fname = f"{_plot_counter[0]:02d}_{name_hint}.png"
    fpath = os.path.join(OUTPUT_DIR, fname)
    
    # 1. Mentes lemezre PNG fajlba
    fig.savefig(fpath, bbox_inches="tight", dpi=150)
    
    # 2. Mentes memoriaba es Base64 kodolas a fuggetlen HTML riporthoz
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    buf.seek(0)
    b64_str = base64.b64encode(buf.read()).decode("utf-8")
    plot_base64[name_hint] = f"data:image/png;base64,{b64_str}"
    
    plt.close(fig)
    print(f"   [ABRA MENTVE] -> {fpath}")


# --- Abra stilus beallitas ---
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
plt.rcParams["figure.dpi"] = 120
plt.rcParams["figure.figsize"] = (10, 6)
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.labelsize"] = 12

print("[OK] Minden konyvtar sikeresen importalva.")

# %% ========================================================================
# 1. ADATBAZIS BEOLVASASA ES ALAPVETO ELLENORZES
#    (Data Loading & Basic Inspection)
# ============================================================================

# 1.0 - Adat beolvasas Kaggle-rol (https://www.kaggle.com/datasets/mirichoi0218/insurance)
df = kagglehub.load_dataset(
    KaggleDatasetAdapter.PANDAS,
    "mirichoi0218/insurance",
    "insurance.csv",
)

print("=" * 70)
print("1. ADATBAZIS BEOLVASASA ES ALAPVETO ELLENORZES")
print("=" * 70)

# 1.1 - Az elso es utolso 5 sor megjelenitese
print("\n--- Az adatbazis elso 5 sora ---")
print(df.head())

print("\n--- Az adatbazis utolso 5 sora ---")
print(df.tail())

# 1.2 - Adattipusok (dtypes)
print("\n--- Adattipusok (dtypes) ---")
print(df.dtypes)

# 1.3 - Altalanos informacio
print("\n--- Altalanos informacio (info) ---")
df.info()

# 1.4 - Duplikaumok vizsgalata
num_duplicates = df.duplicated().sum()
print(f"\n--- Duplikaumok szama: {num_duplicates} ---")
if num_duplicates > 0:
    print("[!] Duplikalt sorok talalhatok! Eltavolitas...")
    df = df.drop_duplicates().reset_index(drop=True)
    print(f"   Uj adatbazis merete: {df.shape}")
else:
    print("[OK] Nincsenek duplikalt sorok.")

# %% ========================================================================
# 2. LEIRO STATISZTIKAK ES FELTARO ADATELEMZES (EDA)
#    (Descriptive Statistics & Exploratory Data Analysis)
# ============================================================================

print("\n" + "=" * 70)
print("2. LEIRO STATISZTIKAK ES FELTARO ADATELEMZES (EDA)")
print("=" * 70)

# --- Valtozok szoveges bemutatasa ---
print("\n--- Az adatbazis valtozoinak leirasa ---")
valtozo_leirasok = {
    "age":      "Az egyen eletkora evekben.",
    "sex":      "Az egyen neme (male/female).",
    "bmi":      "Testtomegindex (Body Mass Index) - megmutatja, hogy valakinek "
                "egeszseges-e a testsulya; a testsuly es a testmagassag "
                "negyzetenek hanyadosabol szamitjak ki, kg/m2 mertekegysegben.",
    "children": "A biztositott gyermekeinek a szama.",
    "smoker":   "Dohanyzik-e az egyen vagy sem (yes/no).",
    "region":   "A regio, ahol az egyen el.",
    "charges":  "Az egyennek felszamitott egeszsegbiztositasi koltsegek (USD)."
}

for valtozo, leiras in valtozo_leirasok.items():
    print(f"  {valtozo:10s} : {leiras}")

# Valtozo tipusok osszefoglalasa
print("\n--- Valtozo tipusok osszefoglalasa ---")
print(f"  Celvaltozo (y)           : charges (folytonos, numerikus)")
print(f"  Magyarazo valtozok (X)   :")
print(f"    - Numerikus valtozok   : age, bmi, children")
print(f"    - Kategorikus valtozok : sex, smoker, region")

# 2.1 - Megfigyelesek es valtozok szama
n_rows, n_cols = df.shape
print(f"\n[STAT] Megfigyelesek (sorok) szama : {n_rows}")
print(f"[STAT] Valtozok (oszlopok) szama   : {n_cols}")

# 2.2 - Leiro statisztikak (numerikus valtozokra)
print("\n--- Leiro statisztikak (numerikus valtozok) ---")
print(df.describe().round(2))

# 2.3 - Leiro statisztikak (kategorikus valtozokra)
print("\n--- Leiro statisztikak (kategorikus valtozok) ---")
print(df.describe(include="object"))

# 2.4 - Hianyzo (missing) ertekek vizsgalata
print("\n--- Hianyzo ertekek osszesitese ---")
missing_df = pd.DataFrame({
    "Hianyzo ertekek szama": df.isnull().sum(),
    "Hianyzo ertekek aranya (%)": (df.isnull().sum() / len(df) * 100).round(2)
})
print(missing_df)

if df.isnull().sum().sum() > 0:
    print("\n[!] Hianyzo adatok talalhatok! Kezeles szukseges...")
    # Numerikus valtozok: median imputacio (robusztus kiugro ertekek eseten)
    num_cols = df.select_dtypes(include=np.number).columns
    for col in num_cols:
        if df[col].isnull().sum() > 0:
            median_val = df[col].median()
            df[col].fillna(median_val, inplace=True)
            print(f"   -> '{col}' hianyzo ertekei mediannal ({median_val}) potolva.")
    # Kategorikus valtozok: modusz (leggyakoribb ertek) imputacio
    cat_cols = df.select_dtypes(include="object").columns
    for col in cat_cols:
        if df[col].isnull().sum() > 0:
            mode_val = df[col].mode()[0]
            df[col].fillna(mode_val, inplace=True)
            print(f"   -> '{col}' hianyzo ertekei modusszal ('{mode_val}') potolva.")
    print("[OK] Hianyzo ertekek kezelve.")
else:
    print("[OK] Nincsenek hianyzo ertekek az adatbazisban.")

# %% ========================================================================
# 2.5 - ELOSZLAS-ABRAK (Distribution Plots)
# ============================================================================

# Numerikus es kategorikus valtozok szetvalasztasa
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
categorical_cols = df.select_dtypes(include="object").columns.tolist()

print(f"\n[NUM] Numerikus valtozok  : {numeric_cols}")
print(f"[CAT] Kategorikus valtozok: {categorical_cols}")

# --- 2.5a: Numerikus valtozok - Hisztogram + KDE ---
print("\n--- Numerikus valtozok eloszlasa (Hisztogram + KDE) ---")
for col in numeric_cols:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    if col == "children":
        # A gyermekek szama diszkret ertekeket vesz fel (0, 1, 2, 3, 4, 5)
        # Ezert diszkret hisztogramkent abrazzuk folytonos KDE trendvonal nelkul,
        # igy a trendvonal nem esik be ket diszkret egesz ertek koze.
        sns.histplot(df[col], discrete=True, kde=False, color="steelblue", ax=axes[0],
                     edgecolor="white", linewidth=0.8, shrink=0.85)
        axes[0].set_title(f"'{col}' eloszlasa (Diszkret hisztogram)")
        axes[0].set_xticks([0, 1, 2, 3, 4, 5])
        for p in axes[0].patches:
            axes[0].annotate(f"{int(p.get_height())}",
                             (p.get_x() + p.get_width() / 2., p.get_height()),
                             ha="center", va="bottom", fontsize=10, fontweight="bold")
    else:
        # Folytonos / tobb erteku numerikus valtozok: Hisztogram + KDE
        sns.histplot(df[col], kde=True, bins=30, color="steelblue", ax=axes[0],
                     edgecolor="white", linewidth=0.5)
        axes[0].set_title(f"'{col}' eloszlasa (Hisztogram + KDE)")

    axes[0].set_xlabel(col)
    axes[0].set_ylabel("Gyakorisag")

    # Boxplot (kiugro ertekek vizualizalasara)
    sns.boxplot(x=df[col], color="lightcoral", ax=axes[1],
                flierprops=dict(marker="o", markersize=4, alpha=0.5))
    axes[1].set_title(f"'{col}' boxplot (kiugro ertekek)")
    axes[1].set_xlabel(col)

    plt.tight_layout()
    save_and_show(fig, f"dist_{col}")

# --- 2.5b: Kategorikus valtozok - Countplot ---
print("\n--- Kategorikus valtozok eloszlasa (Countplot) ---")
for col in categorical_cols:
    fig, ax = plt.subplots(figsize=(8, 5))
    order = df[col].value_counts().index
    sns.countplot(x=df[col], order=order, palette="viridis", ax=ax,
                  edgecolor="black", linewidth=0.5)
    ax.set_title(f"'{col}' ertekeinek gyakorisaga (Countplot)")
    ax.set_xlabel(col)
    ax.set_ylabel("Gyakorisag")

    # Ertekek megjelenitese az oszlopok tetejen
    for p in ax.patches:
        ax.annotate(f"{int(p.get_height())}",
                    (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha="center", va="bottom", fontsize=10, fontweight="bold")
    plt.tight_layout()
    save_and_show(fig, f"count_{col}")

# %% ========================================================================
# 2.6 - CELVALTOZO vs MAGYARAZO VALTOZOK (Scatter Plots)
# ============================================================================

print("\n--- Celvaltozo (charges) vs magyarazo valtozok (Scatter Plot) ---")

# --- 2.6a: charges vs age | charges vs bmi  (hue = smoker) ---
fig = plt.figure(figsize=(14, 6))

ax1 = fig.add_subplot(121)
sns.scatterplot(x="age", y="charges", data=df, palette="magma",
                hue="smoker", ax=ax1, alpha=0.7, edgecolor="white", linewidths=0.3)
ax1.set_title("Charges vs Age (szinezve: smoker)")
ax1.set_xlabel("Age (eletkor, ev)")
ax1.set_ylabel("Charges (koltseg, USD)")

ax2 = fig.add_subplot(122)
sns.scatterplot(x="bmi", y="charges", data=df, palette="viridis",
                hue="smoker", ax=ax2, alpha=0.7, edgecolor="white", linewidths=0.3)
ax2.set_title("Charges vs BMI (szinezve: smoker)")
ax2.set_xlabel("BMI (testtomegindex, kg/m2)")
ax2.set_ylabel("Charges (koltseg, USD)")

plt.tight_layout()
save_and_show(fig, "scatter_age_bmi_vs_charges")

# --- 2.6b: charges vs children | charges vs smoker ---
fig = plt.figure(figsize=(14, 6))

ax3 = fig.add_subplot(121)
sns.scatterplot(x="children", y="charges", data=df, palette="coolwarm",
                hue="smoker", ax=ax3, alpha=0.7, edgecolor="white", linewidths=0.3)
ax3.set_title("Charges vs Children (szinezve: smoker)")
ax3.set_xlabel("Children (gyermekek szama)")
ax3.set_ylabel("Charges (koltseg, USD)")

ax4 = fig.add_subplot(122)
# A smoker valtozonal NEM hasznalunk hue='smoker'-t (onmaga lenne),
# helyette boxplot-ot alkalmazunk a jobb vizualizacioert.
sns.boxplot(x="smoker", y="charges", data=df, palette="Set2", ax=ax4,
            flierprops=dict(marker="o", markersize=4, alpha=0.5))
ax4.set_title("Charges vs Smoker")
ax4.set_xlabel("Smoker (dohanyzik-e)")
ax4.set_ylabel("Charges (koltseg, USD)")

plt.tight_layout()
save_and_show(fig, "scatter_children_smoker_vs_charges")

# --- 2.6c: charges vs sex | charges vs region  (hue = smoker) ---
fig = plt.figure(figsize=(14, 6))

ax5 = fig.add_subplot(121)
sns.stripplot(x="sex", y="charges", data=df, palette="magma",
              hue="smoker", ax=ax5, alpha=0.5, dodge=True, jitter=True, size=3)
ax5.set_title("Charges vs Sex (szinezve: smoker)")
ax5.set_xlabel("Sex (nem)")
ax5.set_ylabel("Charges (koltseg, USD)")

ax6 = fig.add_subplot(122)
sns.stripplot(x="region", y="charges", data=df, palette="viridis",
              hue="smoker", ax=ax6, alpha=0.5, dodge=True, jitter=True, size=3)
ax6.set_title("Charges vs Region (szinezve: smoker)")
ax6.set_xlabel("Region (regio)")
ax6.set_ylabel("Charges (koltseg, USD)")

plt.tight_layout()
save_and_show(fig, "scatter_sex_region_vs_charges")

# %% ========================================================================
# 3. ADATELOKESZITES ES SPEARMAN KORRELACIO VIZSGALAT
#    (Data Preparation & Spearman Correlation Analysis)
# ============================================================================

print("\n" + "=" * 70)
print("3. ADATELOKESZITES ES SPEARMAN KORRELACIO")
print("=" * 70)

# 3.1 - One-Hot Encoding a kategorikus valtozokra
#   drop_first=True -> a Dummy Variable Trap elkerulese erdekeben
#   dtype=float -> statsmodels kompatibilitas
print("\n--- One-Hot Encoding (pd.get_dummies) ---")
df_encoded = pd.get_dummies(df, columns=categorical_cols,
                            drop_first=True, dtype=float)

# 3.1b - Interakcios valtozok letrehozasa
#   A dohanyzo statusz (smoker_yes) moderalo hatast fejt ki az eletkor es a BMI
#   koltsegnovekmenyere, ezert letrehozzuk a kovetkezo interakcios tagokat:
#     bmi_x_smoker = bmi * smoker_yes
#     age_x_smoker = age * smoker_yes
print("\n--- Interakcios valtozok letrehozasa ---")
df_encoded["bmi_x_smoker"] = df_encoded["bmi"] * df_encoded["smoker_yes"]
df_encoded["age_x_smoker"] = df_encoded["age"] * df_encoded["smoker_yes"]
print("   [+] bmi_x_smoker = bmi * smoker_yes")
print("   [+] age_x_smoker = age * smoker_yes")

print(f"   Eredeti adatbazis merete : {df.shape}")
print(f"   Kodolt adatbazis merete  : {df_encoded.shape}")
print(f"       (One-Hot Encoding + 2 interakcios valtozo)")
print(f"\n   Uj oszlopok: {list(df_encoded.columns)}")
print(df_encoded.head())

# 3.2 - Spearman-fele rangkorrelacios matrix
print("\n--- Spearman-fele rangkorrelacios matrix ---")
spearman_corr = df_encoded.corr(method="spearman")
print(spearman_corr.round(2))

# 3.3 - Spearman korrelacio hoterkep (Heatmap)
fig_hm = plt.figure(figsize=(14, 10))
mask = np.triu(np.ones_like(spearman_corr, dtype=bool))  # Felso haromszog maszkolasa
sns.heatmap(spearman_corr, annot=True, fmt=".2f", cmap="coolwarm",
            mask=mask, linewidths=0.5, linecolor="white",
            vmin=-1, vmax=1, center=0,
            cbar_kws={"shrink": 0.8, "label": "Spearman rho"})
plt.title("Spearman-fele Rangkorrelacio Hoterkep", fontsize=16, fontweight="bold")
plt.tight_layout()
save_and_show(fig_hm, "spearman_heatmap")

# %% ========================================================================
# 4. KORRELACIO-ALAPU SZURES ES MULTIKOLLINEARITAS (VIF)
#    (Correlation-Based Filtering & Variance Inflation Factor)
# ============================================================================

print("\n" + "=" * 70)
print("4. KORRELACIO-ALAPU SZURES ES VIF VIZSGALAT")
print("=" * 70)

# --- 4.0 - Celvaltozo es magyarazo valtozok definialasa ---
target = "charges"
X_cols = [c for c in df_encoded.columns if c != target]
y = df_encoded[target].copy()

print(f"\n   Celvaltozo (y)           : {target}")
print(f"   Magyarazo valtozok (X)   : {X_cols}")

# --- 4.1 - Magas korrelacio szurese a magyarazo valtozok kozott ---
print("\n--- 4.1 Magas korrelacio szurese (|r| > 0.7) ---")

corr_X = df_encoded[X_cols].corr(method="spearman")
dropped_corr = []  # Kiszurt valtozok listaja

# Vegigmegyunk az osszes valtozo-paron (felso haromszog)
threshold = 0.7

for i in range(len(X_cols)):
    for j in range(i + 1, len(X_cols)):
        var1, var2 = X_cols[i], X_cols[j]
        corr_val = abs(corr_X.loc[var1, var2])

        if corr_val > threshold:
            # Melyiknek alacsonyabb a korrelacija a celvaltozoval?
            corr_y_var1 = abs(spearman_corr.loc[var1, target])
            corr_y_var2 = abs(spearman_corr.loc[var2, target])

            if corr_y_var1 < corr_y_var2:
                to_drop = var1
            else:
                to_drop = var2

            if to_drop not in dropped_corr:
                dropped_corr.append(to_drop)
                print(f"   [!] |rho({var1}, {var2})| = {corr_val:.4f} > {threshold}")
                print(f"       -> '{to_drop}' kiesik (alacsonyabb korrelacio a celvaltozoval)")
                print(f"         rho({var1}, {target}) = {corr_y_var1:.4f}, "
                      f"rho({var2}, {target}) = {corr_y_var2:.4f}")

if not dropped_corr:
    print("   [OK] Nincs olyan valtozo-par, amelynel |r| > 0.7 -> nincs szures.")
else:
    X_cols = [c for c in X_cols if c not in dropped_corr]
    print(f"\n   Kiszurt valtozok : {dropped_corr}")
    print(f"   Marado valtozok  : {X_cols}")

# --- 4.2 - VIF (Variance Inflation Factor) vizsgalat ---
print("\n--- 4.2 VIF (Variance Inflation Factor) vizsgalat ---")


def calculate_vif(X_data):
    """VIF ertekek kiszamitasa konstanssal kiegeszitett X matrixra."""
    X_const = sm.add_constant(X_data)
    vif_data = pd.DataFrame()
    vif_data["Valtozo"] = X_const.columns
    vif_data["VIF"] = [variance_inflation_factor(X_const.values, i)
                       for i in range(X_const.shape[1])]
    return vif_data


# Iterativ VIF szures: amig van VIF > 5, a legmagasabbat kiszurjuk
vif_iteration = 0
X_vif = df_encoded[X_cols].copy()

while True:
    vif_df = calculate_vif(X_vif)
    # Konstans kiszurese a vizsgalatbol
    vif_no_const = vif_df[vif_df["Valtozo"] != "const"]
    max_vif = vif_no_const["VIF"].max()
    max_vif_var = vif_no_const.loc[vif_no_const["VIF"].idxmax(), "Valtozo"]

    vif_iteration += 1
    print(f"\n   --- VIF Iteracio #{vif_iteration} ---")
    print(vif_no_const.to_string(index=False))

    if max_vif > 5:
        print(f"\n   [!] '{max_vif_var}' VIF = {max_vif:.2f} > 5 -> Kiszures!")
        X_vif = X_vif.drop(columns=[max_vif_var])
    else:
        print(f"\n   [OK] Minden valtozo VIF < 5. Multikollinearitas nem problema.")
        break

X_cols_final = X_vif.columns.tolist()
print(f"\n   Vegso magyarazo valtozok a VIF szures utan: {X_cols_final}")

# %% ========================================================================
# 5. ALAP OLS LINEARIS REGRESSZIOS MODELL
#    (Baseline OLS Linear Regression Model)
# ============================================================================

print("\n" + "=" * 70)
print("5. ALAP OLS LINEARIS REGRESSZIOS MODELL")
print("=" * 70)

# 5.1 - Modell epites
X_base = sm.add_constant(df_encoded[X_cols_final])
y = df_encoded[target]

ols_base = sm.OLS(y, X_base).fit()

# 5.2 - Teljes summary tabla
print("\n--- Alap OLS Modell Summary ---")
print(ols_base.summary())

# Mentjuk a mutatokat az osszehasonlitashoz
base_r2 = ols_base.rsquared
base_adj_r2 = ols_base.rsquared_adj
base_fstat = ols_base.fvalue
base_aic = ols_base.aic
base_bic = ols_base.bic
base_predictions = ols_base.predict(X_base)
base_rmse = np.sqrt(mean_squared_error(y, base_predictions))
base_mae = mean_absolute_error(y, base_predictions)

print(f"\n[STAT] Alapmodell mutatok:")
print(f"   R2           = {base_r2:.6f}")
print(f"   Adj. R2      = {base_adj_r2:.6f}")
print(f"   F-statisztika= {base_fstat:.2f}")
print(f"   RMSE         = {base_rmse:.2f}")
print(f"   MAE          = {base_mae:.2f}")

# %% ========================================================================
# 6. BACKWARD ELIMINATION (HATRAFELE TORTENO ELIMINACIO)
#    (Backward Stepwise Variable Selection)
# ============================================================================

print("\n" + "=" * 70)
print("6. BACKWARD ELIMINATION (VALTOZOSZELEKC IO)")
print("=" * 70)

alpha = 0.05  # Szignifikanciaszint
print(f"\n   Szignifikanciaszint (alpha) = {alpha}")

# Kezdo valtozok (a VIF szures utani keszletbol)
be_cols = X_cols_final.copy()
step = 0
be_history = []

print(f"\n   Kiindulasi valtozok ({len(be_cols)} db): {be_cols}")
print("-" * 70)

while True:
    step += 1
    X_be = sm.add_constant(df_encoded[be_cols])
    model_be = sm.OLS(y, X_be).fit()

    # p-ertekek lekerdezese (a const-ot kihagyjuk a vizsgalatbol!)
    pvalues = model_be.pvalues.drop("const")

    max_pval = pvalues.max()
    max_pval_var = pvalues.idxmax()

    print(f"\n   [STEP] Lepes #{step}")
    print(f"      Valtozok szama      : {len(be_cols)}")
    print(f"      Adj. R2             : {model_be.rsquared_adj:.6f}")
    print(f"      Legmagasabb p-ertek : {max_pval_var} -> p = {max_pval:.6f}")

    if max_pval > alpha:
        print(f"      [X] '{max_pval_var}' p = {max_pval:.6f} > {alpha} -> KISZURES!")
        be_cols.remove(max_pval_var)
        be_history.append({
            "step": step,
            "dropped": max_pval_var,
            "p_val": max_pval,
            "adj_r2": model_be.rsquared_adj,
            "remaining": be_cols.copy()
        })
        print(f"      Marado valtozok: {be_cols}")
    else:
        print(f"      [OK] Minden valtozo szignifikans (p <= {alpha}). Megallas.")
        be_history.append({
            "step": step,
            "dropped": "Nincs (Minden p <= 0.05)",
            "p_val": max_pval,
            "adj_r2": model_be.rsquared_adj,
            "remaining": be_cols.copy()
        })
        break

# Vegso modell a Backward Elimination utan
print("\n" + "-" * 70)
print("   BACKWARD ELIMINATION - VEGSO MODELL")
print("-" * 70)

X_final = sm.add_constant(df_encoded[be_cols])
ols_final = sm.OLS(y, X_final).fit()
print(ols_final.summary())

# %% ========================================================================
# 7. VEGSO MODELL ERTEKELESE
#    (Final Model Evaluation)
# ============================================================================

print("\n" + "=" * 70)
print("7. VEGSO MODELL ERTEKELESE")
print("=" * 70)

# 7.1 - Vegso modell mutatok
final_r2 = ols_final.rsquared
final_adj_r2 = ols_final.rsquared_adj
final_fstat = ols_final.fvalue
final_aic = ols_final.aic
final_bic = ols_final.bic
final_predictions = ols_final.predict(X_final)
final_rmse = np.sqrt(mean_squared_error(y, final_predictions))
final_mae = mean_absolute_error(y, final_predictions)

print(f"\n[STAT] Vegso modell mutatok:")
print(f"   R2           = {final_r2:.6f}")
print(f"   Adj. R2      = {final_adj_r2:.6f}")
print(f"   F-statisztika= {final_fstat:.2f}")
print(f"   RMSE         = {final_rmse:.2f}")
print(f"   MAE          = {final_mae:.2f}")

# 7.2 - Osszehasonlito tablazat: Alapmodell vs. Vegso modell
print("\n--- Modell-osszehasonlitas ---")
comparison = pd.DataFrame({
    "Mutato": ["R2", "Adj. R2", "F-statisztika", "AIC", "BIC", "RMSE", "MAE",
               "Valtozok szama"],
    "Alapmodell (5. pont)": [
        f"{base_r2:.6f}", f"{base_adj_r2:.6f}", f"{base_fstat:.2f}",
        f"{base_aic:.2f}", f"{base_bic:.2f}", f"{base_rmse:.2f}",
        f"{base_mae:.2f}", f"{len(X_cols_final)}"
    ],
    "Vegso modell (BE, 6. pont)": [
        f"{final_r2:.6f}", f"{final_adj_r2:.6f}", f"{final_fstat:.2f}",
        f"{final_aic:.2f}", f"{final_bic:.2f}", f"{final_rmse:.2f}",
        f"{final_mae:.2f}", f"{len(be_cols)}"
    ]
})
print(comparison.to_string(index=False))

# 7.3 - Standardizalt OLS modell (Standardized Beta Coefficients & Relativ Valtozo-fontossag)
print("\n" + "-" * 70)
print("7.3 STANDARDIZALT OLS MODELL (Relativ Valtozo-fontossag)")
print("-" * 70)

from sklearn.preprocessing import StandardScaler

scaler_X = StandardScaler()
X_final_std = pd.DataFrame(scaler_X.fit_transform(df_encoded[be_cols]), columns=be_cols)
y_std = (y - y.mean()) / y.std(ddof=1)

ols_std = sm.OLS(y_std, sm.add_constant(X_final_std)).fit()
print("\n--- Standardizalt OLS Modell Summary ---")
print(ols_std.summary())

# Standardizalt betak osszegzo tablazata
std_betas = []
for c in be_cols:
    raw_b = ols_final.params[c]
    x_sd = df_encoded[c].std(ddof=1)
    std_b = ols_std.params[c]
    p_val = ols_std.pvalues[c]
    impact_dollar = raw_b * x_sd
    std_betas.append({
        "Valtozo": c,
        "Nyers Koefficiens ($)": raw_b,
        "Valtozo Szorasa (SD_X)": x_sd,
        "Standardizalt Beta": std_b,
        "Abszolut Beta (|Beta*|)": abs(std_b),
        "1 SD Hatas ($)": impact_dollar,
        "p-ertek": p_val,
    })

std_betas_df = pd.DataFrame(std_betas).sort_values("Abszolut Beta (|Beta*|)", ascending=False).reset_index(drop=True)
std_betas_df["Rangsor"] = [f"#{i+1}" for i in range(len(std_betas_df))]
print("\n--- Standardizalt Betak es Relativ Fontossagi Rangsor ---")
print(std_betas_df.to_string(index=False))

# --- Standardizalt betak vizualizacioja (Horizontal Bar Chart) ---
fig, ax = plt.subplots(figsize=(10, 5))
plot_df = std_betas_df.sort_values("Standardizalt Beta", ascending=True)
colors = ["#ef4444" if b < 0 else "#00d4ff" for b in plot_df["Standardizalt Beta"]]

bars = ax.barh(plot_df["Valtozo"], plot_df["Standardizalt Beta"], color=colors, edgecolor="black", linewidth=0.6, height=0.55)
ax.axvline(0, color="gray", linestyle="--", linewidth=0.8, alpha=0.7)
ax.set_title("A Vegso Modell Magyarazo Valtozoinak Relativ Hatasnagysaga (Standardizalt Betak)", fontsize=12, fontweight="bold")
ax.set_xlabel("Standardizalt Regresszios Koefficiens (Beta*) - [Szorasvaltozas]")
ax.set_ylabel("Magyarazo Valtozo")

for bar in bars:
    width = bar.get_width()
    text_x = width + (0.015 if width >= 0 else -0.065)
    ax.annotate(f"{width:+.4f}", (text_x, bar.get_y() + bar.get_height() / 2.),
                va="center", fontsize=9, fontweight="bold")

plt.tight_layout()
save_and_show(fig, "standardized_betas")

# %% ========================================================================
# 8. OLS DIAGNOSZTIKAI VIZSGALATOK A VEGSO MODELLEN
#    (OLS Diagnostic Tests on the Final Model)
# ============================================================================

print("\n" + "=" * 70)
print("8. OLS DIAGNOSZTIKAI VIZSGALATOK")
print("=" * 70)

# Rezidualosok (maradektagok) kiszamitasa
residuals = ols_final.resid
fitted_values = ols_final.fittedvalues
n = len(y)

# ----------------------------------------------------------------------
# 8.1 - HIBATAGOK NORMALITASA (Normality of Residuals)
# ----------------------------------------------------------------------
print("\n" + "-" * 70)
print("8.1 HIBATAGOK NORMALITASA")
print("-" * 70)

# 8.1a - Rezidualosok eloszlasa: Hisztogram + KDE
fig_norm, axes = plt.subplots(1, 2, figsize=(14, 5))

sns.histplot(residuals, kde=True, bins=40, color="steelblue", ax=axes[0],
             edgecolor="white", linewidth=0.5, stat="density")
axes[0].set_title("Rezidualosok eloszlasa (Hisztogram + KDE)")
axes[0].set_xlabel("Rezidualosok")
axes[0].set_ylabel("Suruseg")

# 8.1b - Normal Q-Q plot
sm.qqplot(residuals, line="45", fit=True, ax=axes[1],
          markerfacecolor="steelblue", markeredgecolor="white",
          markersize=4, alpha=0.6)
axes[1].set_title("Normal Q-Q Plot")
axes[1].get_lines()[0].set_color("steelblue")
axes[1].get_lines()[1].set_color("red")

plt.tight_layout()
save_and_show(fig_norm, "normality_check")

# 8.1c - Shapiro-Wilk-teszt
# Megjegyzes: Shapiro-Wilk max 5000 mintara mukodik megbizhatoan
if n <= 5000:
    sw_stat, sw_pval = shapiro(residuals)
    print(f"\n   Shapiro-Wilk-teszt:")
    print(f"     Statisztika = {sw_stat:.6f}")
    print(f"     p-ertek     = {sw_pval:.6f}")
    if sw_pval > 0.05:
        print("     -> H0 nem elutasithato: a rezidualosok NORMALIS eloszlasuak (p > 0.05).")
    else:
        print("     -> H0 elutasitva: a rezidualosok NEM normalis eloszlasuak (p <= 0.05).")
else:
    print("   [!] Shapiro-Wilk-teszt kihagyva (n > 5000, nem megbizhato).")

# 8.1d - Jarque-Bera-teszt (nagy mintara is alkalmas)
jb_stat, jb_pval = jarque_bera(residuals)
print(f"\n   Jarque-Bera-teszt:")
print(f"     Statisztika = {jb_stat:.6f}")
print(f"     p-ertek     = {jb_pval:.6f}")
if jb_pval > 0.05:
    print("     -> H0 nem elutasithato: a rezidualosok NORMALIS eloszlasuak (p > 0.05).")
else:
    print("     -> H0 elutasitva: a rezidualosok NEM normalis eloszlasuak (p <= 0.05).")

# ----------------------------------------------------------------------
# 8.2 - HOMOSZKEDASZTICITAS VIZSGALATA (Homoscedasticity)
# ----------------------------------------------------------------------
print("\n" + "-" * 70)
print("8.2 HOMOSZKEDASZTICITAS VIZSGALATA")
print("-" * 70)

# 8.2a - Breusch-Pagan-teszt
bp_stat, bp_pval, bp_fstat, bp_fpval = het_breuschpagan(residuals, X_final)
print(f"\n   Breusch-Pagan-teszt:")
print(f"     LM-statisztika = {bp_stat:.6f}")
print(f"     LM p-ertek     = {bp_pval:.6f}")
print(f"     F-statisztika  = {bp_fstat:.6f}")
print(f"     F p-ertek      = {bp_fpval:.6f}")

if bp_pval > 0.05:
    print("     -> H0 nem elutasithato: HOMOSZKEDASZTICITAS all fenn (p > 0.05).")
    heteroscedasticity_detected = False
else:
    print("     -> H0 elutasitva: HETEROSZKEDASZTICITAS all fenn (p <= 0.05)!")
    heteroscedasticity_detected = True

# 8.2b - Residuals vs. Fitted Values szorodasi abra (+ LOESS trendvonal)
fig_resid, ax = plt.subplots(figsize=(12, 6))

ax.scatter(fitted_values, residuals, alpha=0.4, s=20, color="steelblue",
           edgecolor="white", linewidth=0.3, label="Rezidualosok")
ax.axhline(y=0, color="red", linewidth=1.5, linestyle="--", label="y = 0 referenciavonal")

# LOESS trendvonal (lowess)
try:
    from statsmodels.nonparametric.smoothers_lowess import lowess
    loess_result = lowess(residuals, fitted_values, frac=0.3)
    ax.plot(loess_result[:, 0], loess_result[:, 1], color="darkorange",
            linewidth=2.5, label="LOESS trendvonal")
except ImportError:
    print("   [INFO] LOESS nem elerheto, trendvonal kihagyva.")

ax.set_title("Rezidualosok vs. Becsult ertekek (Residuals vs. Fitted)")
ax.set_xlabel("Becsult ertekek (Fitted Values)")
ax.set_ylabel("Rezidualosok (Residuals)")
ax.legend()
plt.tight_layout()
save_and_show(fig_resid, "residuals_vs_fitted")

# ----------------------------------------------------------------------
# 8.3 - AUTOKORRELACIOS VIZSGALAT (Autocorrelation - Durbin-Watson)
# ----------------------------------------------------------------------
print("\n" + "-" * 70)
print("8.3 AUTOKORRELACIO VIZSGALATA (Durbin-Watson)")
print("-" * 70)

dw_stat = durbin_watson(residuals)
print(f"\n   Durbin-Watson-statisztika: {dw_stat:.4f}")
print(f"   Idealis tartomany: 1.5 - 2.5")

if 1.5 <= dw_stat <= 2.5:
    print("   -> [OK] Nincs szignifikans autokorrelacio a rezidualosokban.")
elif dw_stat < 1.5:
    print("   -> [!] Pozitiv autokorrelacio lehetseges (DW < 1.5)!")
else:
    print("   -> [!] Negativ autokorrelacio lehetseges (DW > 2.5)!")

# ----------------------------------------------------------------------
# 8.4 - KIUGRO ES BEFOLYASOS PONTOK (Cook's Distance)
# ----------------------------------------------------------------------
print("\n" + "-" * 70)
print("8.4 KIUGRO ES BEFOLYASOS PONTOK (Cook's Distance)")
print("-" * 70)

# Cook-tavolsag kiszamitasa
influence = ols_final.get_influence()
cooks_d = influence.cooks_distance[0]

# Kritikus kuszobErtek: 4/n
cooks_threshold = 4 / n
print(f"\n   Kritikus kuszobErtek (4/n) : {cooks_threshold:.6f}")
print(f"   Megfigyelesek szama (n)   : {n}")

# Befolyasos pontok azonositasa
influential_idx = np.where(cooks_d > cooks_threshold)[0]
print(f"   Befolyasos pontok szama   : {len(influential_idx)} "
      f"({len(influential_idx)/n*100:.1f}%)")

# Cook-tavolsagok diagram
fig_cook, ax = plt.subplots(figsize=(14, 6))
ax.stem(range(n), cooks_d, linefmt="steelblue", markerfmt=",", basefmt=" ")
ax.axhline(y=cooks_threshold, color="red", linewidth=1.5, linestyle="--",
           label=f"Kuszob (4/n = {cooks_threshold:.4f})")
ax.set_title("Cook-tavolsagok (Cook's Distance)", fontsize=14, fontweight="bold")
ax.set_xlabel("Megfigyeles indexe")
ax.set_ylabel("Cook-tavolsag")
ax.legend()
plt.tight_layout()
save_and_show(fig_cook, "cooks_distance")

# A legbefolyasosabb 10 pont kilistazasa
if len(influential_idx) > 0:
    top_n = min(10, len(influential_idx))
    top_influential = np.argsort(cooks_d)[-top_n:][::-1]
    print(f"\n   Top {top_n} legbefolyasosabb megfigyeles:")
    print(f"   {'Index':>7} | {'Cook-tavolsag':>15}")
    print(f"   {'-'*7}-+-{'-'*15}")
    for idx in top_influential:
        print(f"   {idx:>7} | {cooks_d[idx]:>15.6f}")
else:
    print("\n   [OK] Nincsenek befolyasos pontok a 4/n kuszob felett.")

# ----------------------------------------------------------------------
# 8.5 - ROBUSZTUS STANDARD HIBAK (HC3) - ha heteroszkedaszticitas van
# ----------------------------------------------------------------------
if heteroscedasticity_detected:
    print("\n" + "-" * 70)
    print("8.5 ROBUSZTUS STANDARD HIBAK (HC3 korrekcio)")
    print("-" * 70)
    print("\n   [!] A Breusch-Pagan-teszt heteroszkedaszticitas-t jelzett.")
    print("   -> Robusztus standard hibakkal korrigalt modell (cov_type='HC3'):\n")

    ols_robust = sm.OLS(y, X_final).fit(cov_type="HC3")
    print(ols_robust.summary())

    print("\n   [INFO] Osszehasonlitas: Hagyomanyos vs. HC3 robusztus standard hibak")
    se_comparison = pd.DataFrame({
        "Valtozo": ols_final.params.index,
        "Koefficiens": ols_final.params.values.round(4),
        "SE (Hagyomanyos)": ols_final.bse.values.round(4),
        "SE (HC3 Robusztus)": ols_robust.bse.values.round(4),
        "p (Hagyomanyos)": ols_final.pvalues.values.round(6),
        "p (HC3 Robusztus)": ols_robust.pvalues.values.round(6),
    })
    print(se_comparison.to_string(index=False))
else:
    print("\n" + "-" * 70)
    print("8.5 ROBUSZTUS STANDARD HIBAK")
    print("-" * 70)
    print("\n   [OK] A Breusch-Pagan-teszt nem jelzett heteroszkedaszticitas-t.")
    print("   -> HC3 korrekcio nem szukseges.")

# %% ========================================================================
# ZARO OSSZEFOGLALO (Final Summary)
# ============================================================================
print("\n" + "=" * 70)
print("ZARO OSSZEFOGLALO")
print("=" * 70)
print(f"""
[INFO] Vegso modell valtozoi: {be_cols}
[STAT] R2     = {final_r2:.4f}  ({final_r2*100:.2f}%)
[STAT] Adj R2 = {final_adj_r2:.4f}  ({final_adj_r2*100:.2f}%)
[STAT] RMSE   = {final_rmse:.2f}
[STAT] MAE    = {final_mae:.2f}

[INFO] A modell a celvaltozo (charges) variancipjpnak ~{final_r2*100:.1f}%-at magyarazza.

Megjegyzes:
  * Ha a normalitasi tesztek elutasitjak H0-t, erdemes lehet
    log-transzformaciot alkalmazni a celvaltozora.
  * Ha heteroszkedaszticitas all fenn, a HC3 robusztus standard hibak
    megbizhatobb kovetkezteteseket biztositanak.
  * A Cook-tavolsag alapjan azonositott befolyasos pontok tovabbi
    vizsgalatot igenyelhetnek (pl. domain-specifikus elemzes).
""")

print("[OK] Az elemzes befejezodott.")
print(f"[INFO] Minden abra itt talalhato: {OUTPUT_DIR}")

# %% ========================================================================
# 9. ONALLO HTML RIPORT GENERALASA (Standalone HTML Report Generation)
# ============================================================================
print("\n" + "=" * 70)
print("9. ONALLO HTML RIPORT GENERALASA (insurance_report.html)")
print("=" * 70)

from report_generator import generate_html_report

report_data = {
    "df_clean": df,
    "missing_df": missing_df,
    "valtozo_leirasok": valtozo_leirasok,
    "numeric_cols": numeric_cols,
    "categorical_cols": categorical_cols,
    "df_encoded": df_encoded,
    "spearman_corr": spearman_corr,
    "dropped_corr": dropped_corr,
    "vif_initial": vif_df,
    "vif_final": vif_df,
    "ols_base": ols_base,
    "ols_final": ols_final,
    "ols_std": ols_std,
    "std_betas_df": std_betas_df,
    "ols_robust": ols_robust if heteroscedasticity_detected else None,
    "ols_final_rmse": final_rmse,
    "ols_final_mae": final_mae,
    "comparison": comparison,
    "be_history": be_history,
    "sw_stat": sw_stat if n <= 5000 else None,
    "sw_pval": sw_pval if n <= 5000 else None,
    "jb_stat": jb_stat,
    "jb_pval": jb_pval,
    "bp_stat": bp_stat,
    "bp_pval": bp_pval,
    "bp_fstat": bp_fstat,
    "bp_fpval": bp_fpval,
    "dw_stat": dw_stat,
    "cooks_threshold": cooks_threshold,
    "influential_count": len(influential_idx),
    "influential_pct": len(influential_idx) / n * 100,
    "top_influential": [(idx, cooks_d[idx]) for idx in top_influential] if len(influential_idx) > 0 else [],
    "plot_base64": plot_base64,
    "output_dir": OUTPUT_DIR,
}

html_report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "insurance_report.html")
generate_html_report(report_data, html_report_path)
print(f"[OK] Onallo HTML riport sikeresen letrehozva: {html_report_path}")

# Szinkronizalas a v2 fajlba is
v2_report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "medical_cost_analysis_report_v2.html")
try:
    import shutil
    shutil.copyfile(html_report_path, v2_report_path)
    print(f"[OK] Szinkronizalva a v2 riportfajlba is: {v2_report_path}")
except Exception as e:
    pass