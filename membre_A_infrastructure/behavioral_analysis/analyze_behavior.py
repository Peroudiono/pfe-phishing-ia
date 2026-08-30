#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse comportementale - Campagne Phishing Classique vs IA
PFE Cyber IA - Membre A
Version corrigée - Compte Clicked Link + Submitted Data comme clic réussi
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuration du style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("Set2")

# Dossier des résultats
RESULTS_DIR = "../campaign_results"

# --- 1. CHARGEMENT DES DONNEES ---
print("\n" + "="*50)
print("📊 ANALYSE COMPORTEMENTALE - PHISHING CLASSIQUE")
print("="*50)

# Vérifier que les fichiers existent
if not os.path.exists(f"{RESULTS_DIR}/resultats_test_classique_results.csv"):
    print(f"❌ Fichier introuvable : {RESULTS_DIR}/resultats_test_classique_results.csv")
    print("   Assure-toi d'avoir copié les fichiers CSV depuis GoPhish.")
    exit(1)

if not os.path.exists(f"{RESULTS_DIR}/resultats_test_classique_raw.csv"):
    print(f"❌ Fichier introuvable : {RESULTS_DIR}/resultats_test_classique_raw.csv")
    print("   Assure-toi d'avoir copié les fichiers CSV depuis GoPhish.")
    exit(1)

events = pd.read_csv(f"{RESULTS_DIR}/resultats_test_classique_raw.csv")
results = pd.read_csv(f"{RESULTS_DIR}/resultats_test_classique_results.csv")

print(f"✅ Events chargés : {len(events)} événements")
print(f"✅ Results chargés : {len(results)} cibles")

# Nettoyage
events["time"] = pd.to_datetime(events["time"])
events = events[events["email"] != ""]  # enlève la ligne "Campaign Created" sans email

# --- 2. TAUX PAR STATUT ---
print("\n" + "="*50)
print("📈 STATISTIQUES GLOBALES")
print("="*50)

print("\n=== Répartition des statuts (résumé par personne) ===")
status_counts = results["status"].value_counts()
print(status_counts)
print()

print("=== Taux (%) ===")
status_pct = (results["status"].value_counts(normalize=True) * 100).round(1)
print(status_pct)

# --- 3. DELAI DE REACTION ---
print("\n" + "="*50)
print("⏱️ DÉLAI DE RÉACTION (Email Sent → Clicked Link)")
print("="*50)

sent = events[events["message"] == "Email Sent"][["email", "time"]].rename(columns={"time": "t_sent"})
clicked = events[events["message"] == "Clicked Link"][["email", "time"]].rename(columns={"time": "t_clicked"})

if len(sent) > 0 and len(clicked) > 0:
    reaction = sent.merge(clicked, on="email")
    reaction["delai_minutes"] = (reaction["t_clicked"] - reaction["t_sent"]).dt.total_seconds() / 60

    print("\n=== Délai de réaction par personne ===")
    print(reaction[["email", "delai_minutes"]])
    
    if len(reaction) > 0:
        print(f"\nDélai moyen : {reaction['delai_minutes'].mean():.2f} minutes")
        print(f"Délai médian : {reaction['delai_minutes'].median():.2f} minutes")
        print(f"Délai min : {reaction['delai_minutes'].min():.2f} minutes")
        print(f"Délai max : {reaction['delai_minutes'].max():.2f} minutes")
else:
    print("\n⚠️ Pas assez de données pour calculer les délais de réaction.")

# --- 4. TAUX DE CLIC PAR POSTE (CORRIGÉ) ---
print("\n" + "="*50)
print("👤 TAUX DE CLIC PAR POSTE")
print("="*50)

# CORRECTION : Compte Clicked Link OU Submitted Data comme "a cliqué"
results["a_clique"] = results["status"].isin(["Clicked Link", "Submitted Data"])
clic_par_poste = results.groupby("position")["a_clique"].mean() * 100

print("\n=== Taux de clic (%) par poste ===")
print(clic_par_poste)

# Graphique 1 : Taux de clic par poste
plt.figure(figsize=(10, 6))
ax = clic_par_poste.sort_values(ascending=False).plot(kind="bar", color="#4C72B0")
plt.title("Taux de clic par poste — Campagne Phishing Classique", fontsize=14, fontweight='bold')
plt.ylabel("Taux de clic (%)", fontsize=12)
plt.xlabel("Poste", fontsize=12)
plt.xticks(rotation=20)
plt.grid(axis='y', alpha=0.3)

# Ajouter les valeurs sur les barres
for i, v in enumerate(clic_par_poste.sort_values(ascending=False)):
    ax.text(i, v + 1, f"{v:.1f}%", ha='center', fontsize=10)

plt.tight_layout()
plt.savefig("clic_par_poste_classique.png", dpi=200)
plt.close()
print("\n✅ Graphique sauvegardé : clic_par_poste_classique.png")

# --- 5. CHRONOLOGIE CUMULATIVE DES CLICS ---
print("\n" + "="*50)
print("📈 CHRONOLOGIE CUMULATIVE DES CLICS")
print("="*50)

if len(clicked) > 0:
    clicked_sorted = clicked.sort_values("t_clicked")
    clicked_sorted["cumul"] = range(1, len(clicked_sorted) + 1)

    plt.figure(figsize=(12, 6))
    plt.step(clicked_sorted["t_clicked"], clicked_sorted["cumul"], 
             where="post", marker="o", color="#C44E52", linewidth=2, markersize=8)
    plt.title("Évolution cumulative des clics dans le temps — Phishing Classique", 
              fontsize=14, fontweight='bold')
    plt.xlabel("Temps", fontsize=12)
    plt.ylabel("Nombre cumulé de clics", fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("chronologie_clics_classique.png", dpi=200)
    plt.close()
    print("✅ Graphique sauvegardé : chronologie_clics_classique.png")
else:
    print("⚠️ Aucun clic enregistré.")

# --- 6. TAUX DE SOUMISSION ---
print("\n" + "="*50)
print("📝 TAUX DE SOUMISSION DU FORMULAIRE")
print("="*50)

submitted = results[results["status"] == "Submitted Data"]
submission_rate = (len(submitted) / len(results)) * 100 if len(results) > 0 else 0
print(f"\nNombre de soumissions : {len(submitted)} / {len(results)}")
print(f"Taux de soumission : {submission_rate:.1f}%")

# --- 7. RÉSUMÉ FINAL ---
print("\n" + "="*50)
print("📊 RÉSUMÉ DE L'ANALYSE")
print("="*50)

click_rate = (results["a_clique"].sum() / len(results)) * 100 if len(results) > 0 else 0
print(f"✅ Nombre total de cibles : {len(results)}")
print(f"✅ Taux de clic global : {click_rate:.1f}%")
print(f"✅ Taux de soumission : {submission_rate:.1f}%")
print(f"✅ Nombre de postes différents : {results['position'].nunique()}")

print("\n" + "="*50)
print("🎯 Analyse terminée !")
print("="*50)
