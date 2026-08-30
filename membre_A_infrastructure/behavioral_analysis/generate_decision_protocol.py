import random
import pandas as pd

random.seed(42)  # figé et documenté dans le rapport pour la reproductibilité

# Probabilités calibrées sur la littérature (à citer dans le rapport) :
# - Jagatic et al. (2007, Communications of the ACM) : phishing personnalisé ~80% vs générique ~16%
# - Jakobsson : attaque contextuelle 48-96% vs attaque ordinaire ~3%
CLICK_PROB = {
    "classique": 0.18,
    "ia": 0.65,
}
SUBMIT_GIVEN_CLICK_PROB = 0.45

results = pd.read_csv("../campaign_results/resultats_test_classique_results.csv")
targets = results[["email", "position"]].drop_duplicates()

def generate_protocol(campaign_type):
    decisions = []
    for _, row in targets.iterrows():
        clicked = random.random() < CLICK_PROB[campaign_type]
        submitted = clicked and (random.random() < SUBMIT_GIVEN_CLICK_PROB)
        decisions.append({
            "email": row["email"],
            "position": row["position"],
            "campaign_type": campaign_type,
            "should_click": clicked,
            "should_submit": submitted,
        })
    return pd.DataFrame(decisions)

df_classique = generate_protocol("classique")
df_classique.to_csv("decision_protocol_classique.csv", index=False)
print("=== Protocole Classique (pré-enregistré) ===")
print(df_classique)
print(f"\nTaux de clic prévu : {df_classique['should_click'].mean()*100:.1f}%")
