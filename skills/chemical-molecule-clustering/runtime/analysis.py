"""Explicit Euclidean descriptor clustering; noise is not a chemical class."""
from pathlib import Path
import csv
import numpy as np
from .ml_support import check, environment, features, integer, keys, real


def analyze(parameters, data, output_dir):
    from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import silhouette_score
    import joblib
    keys(parameters, ['algorithm', 'seed', 'scale', 'n_clusters', 'eps', 'min_samples'])
    x, _ = features(data)
    seed = integer(parameters['seed'], 0, 2**31 - 1, 'seed')
    if type(parameters['scale']) is not bool:
        raise ValueError('Explicit scale Boolean required.')
    scaler = StandardScaler().fit(x) if parameters['scale'] else None
    z = scaler.transform(x) if scaler else x.copy()
    name = parameters['algorithm']
    if name == 'kmeans':
        count = integer(parameters['n_clusters'], 2, len(x) - 1, 'n_clusters')
        model = KMeans(n_clusters=count, n_init=10, random_state=seed)
    elif name == 'ward':
        count = integer(parameters['n_clusters'], 2, len(x) - 1, 'n_clusters')
        model = AgglomerativeClustering(n_clusters=count, linkage='ward', metric='euclidean')
    elif name == 'dbscan':
        model = DBSCAN(eps=real(parameters['eps'], 1e-9, 1e6, 'eps'),
                       min_samples=integer(parameters['min_samples'], 2, len(x), 'min_samples'), metric='euclidean')
    else:
        raise ValueError('Choose kmeans, ward or dbscan; Ward/Tanimoto is not supported.')
    labels = model.fit_predict(z)
    valid = labels != -1
    nclusters = len(set(labels[valid]))
    silhouette = float(silhouette_score(z[valid], labels[valid])) if 2 <= nclusters < int(valid.sum()) else None
    joblib.dump({'scaler': scaler, 'model': model}, Path(output_dir) / 'self-produced-clustering.joblib')
    loaded = joblib.load(Path(output_dir) / 'self-produced-clustering.joblib')
    with (Path(output_dir) / 'clusters.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        writer.writerow(['id', 'cluster_label', 'is_noise'])
        writer.writerows((id_, int(label), bool(label == -1)) for id_, label in zip(data['ids'], labels))
    return {'scope': 'DESCRIPTIVE_EUCLIDEAN_DESCRIPTOR_CLUSTERING_NOT_CHEMICAL_TAXONOMY',
            'environment': environment(), 'labels': labels.tolist(), 'clusters_excluding_noise': nclusters,
            'noise_count': int((labels == -1).sum()), 'silhouette_excluding_noise': silhouette,
            'local_unsupervised_fit_runs': 1,
            'checks': [check('all_rows_retained', labels.shape == (len(x),)),
                       check('owned_saved_label_replay', np.array_equal(loaded['model'].labels_, labels))],
            'limits': ['Cluster labels are arbitrary and may change under parameter choices.',
                       'DBSCAN -1 is noise, not a new chemical class; silhouette is undefined for one/all-singleton cluster sets.',
                       'No Tanimoto/binary fingerprint clustering, activity claim or experimental class validation.',
                       'Ward/DBSCAN here have no general out-of-sample predict method.']}
