import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
import pickle

# Load dataset
df = pd.read_csv("personality_hr_unlabeled_dataset.csv")

# Remove outliers using Isolation Forest
iso = IsolationForest(contamination=0.05, random_state=42)
outliers = iso.fit_predict(df)
df_clean = df[outliers == 1].copy()

# Scale features
scaler = RobustScaler()
X_scaled = scaler.fit_transform(df_clean)

# Apply PCA for dimensionality reduction
pca = PCA(n_components=5)
X_pca = pca.fit_transform(X_scaled)

# KMeans Clustering with k=6
kmeans = KMeans(n_clusters=6, random_state=42, n_init=10)
cluster_labels = kmeans.fit_predict(X_pca)
df_clean['Cluster'] = cluster_labels

# Map clusters to personality labels (based on domain-driven analysis)
cluster_map = {
    0: "Experienced Professionals",
    1: "Analytical Thinkers",
    2: "Team Players",
    3: "Adaptable Experts",
    4: "Creative Leaders",
    5: "Detail Oriented"
}
df_clean["Personality_Label"] = df_clean["Cluster"].map(cluster_map)

# Save labeled dataset
df_clean.to_csv("clustered_personality_hr_data_labeled.csv", index=False)
print("Labeled dataset saved as clustered_personality_hr_data_labeled.csv")

# Save models for future use
with open("scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)
with open("pca.pkl", "wb") as f:
    pickle.dump(pca, f)
with open("kmeans.pkl", "wb") as f:
    pickle.dump(kmeans, f)

print("Models saved: scaler.pkl, pca.pkl, kmeans.pkl")
# Features you're interested in
features = [
    'EXT', 'EST', 'AGR', 'CSN', 'OPN',
    'Technical_Skills', 'Communication_Skills', 'Experience_Years',
    'Education_Level', 'Certifications', 'Leadership_Score',
    'Adaptability_Score', 'Analytical_Thinking',
    'Teamwork_Score', 'Project_Management'
]

# Print min-max ranges for each cluster
for cluster_num in sorted(df_clean['Cluster'].unique()):
    print(f"\nCluster {cluster_num} – {cluster_map[cluster_num]}")
    cluster_data = df_clean[df_clean['Cluster'] == cluster_num]
    for feature in features:
        min_val = cluster_data[feature].min()
        max_val = cluster_data[feature].max()
        print(f"  {feature}: {min_val} – {max_val}")
