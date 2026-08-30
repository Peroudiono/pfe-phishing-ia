import pandas as pd

protocole = pd.read_csv("decision_protocol_classique.csv")
results = pd.read_csv("../campaign_results/resultats_test_classique_results.csv")

results["a_clique_reel"] = results["status"].isin(["Clicked Link", "Submitted Data"])
results["a_soumis_reel"] = results["status"] == "Submitted Data"

comparaison = protocole.merge(
    results[["email", "a_clique_reel", "a_soumis_reel"]],
    on="email"
)
comparaison["clic_conforme"] = comparaison["should_click"] == comparaison["a_clique_reel"]
comparaison["soumission_conforme"] = comparaison["should_submit"] == comparaison["a_soumis_reel"]

print("\n" + "="*60)
print("🔍 COMPARAISON PROTOCOLE vs RÉEL - Campagne Classique")
print("="*60)
print(comparaison[["email", "should_click", "a_clique_reel", "clic_conforme",
                    "should_submit", "a_soumis_reel", "soumission_conforme"]])

taux_conformite = comparaison["clic_conforme"].mean() * 100
print(f"\n✅ Conformité au protocole (clics) : {taux_conformite:.1f}%")

taux_soumission_conformite = comparaison["soumission_conforme"].mean() * 100
print(f"✅ Conformité au protocole (soumissions) : {taux_soumission_conformite:.1f}%")
print("="*60)
