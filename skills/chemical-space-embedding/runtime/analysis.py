"""PCA/t-SNE/UMAP on explicit numeric descriptors; no property inference."""
from pathlib import Path
import csv
import numpy as np
from .ml_support import check, environment, features, integer, keys, real


def analyze(parameters, data, output_dir):
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE, trustworthiness
    from sklearn.preprocessing import StandardScaler
    import joblib
    keys(parameters, ['algorithm', 'seed', 'n_components', 'fit_rows', 'scale', 'perplexity', 'n_neighbors'])
    x, _ = features(data)
    seed = integer(parameters['seed'], 0, 2**31 - 1, 'seed')
    nfit = integer(parameters['fit_rows'], 5, len(x), 'fit_rows')
    dim = integer(parameters['n_components'], 1, min(3, x.shape[1], nfit - 1), 'n_components')
    if type(parameters['scale']) is not bool or parameters['algorithm'] not in {'pca', 'tsne', 'umap'}:
        raise ValueError('Declare scale Boolean and pca/tsne/umap.')
    scaler = StandardScaler().fit(x[:nfit]) if parameters['scale'] else None
    z = scaler.transform(x) if scaler else x.copy()
    algorithm = parameters['algorithm']
    if algorithm == 'pca':
        model = PCA(n_components=dim, svd_solver='full').fit(z[:nfit])
        embedded = model.transform(z)
        extra = {'explained_variance_ratio': model.explained_variance_ratio_.tolist(), 'out_of_sample': 'LINEAR_PCA_TRANSFORM'}
    elif algorithm == 'tsne':
        if nfit != len(x):
            raise ValueError('This t-SNE is transductive; no claimed transform of held-out points.')
        perplexity = real(parameters['perplexity'], 1, nfit - 1, 'perplexity')
        model = TSNE(n_components=dim, perplexity=perplexity, random_state=seed, init='random',
                     learning_rate='auto', max_iter=500, method='exact')
        embedded = model.fit_transform(z)
        extra = {'KL_divergence': float(model.kl_divergence_), 'out_of_sample': 'NOT_SUPPORTED_TRANSFORM'}
    else:
        import umap
        neighbors = integer(parameters['n_neighbors'], 2, nfit - 1, 'n_neighbors')
        model = umap.UMAP(n_components=dim, n_neighbors=neighbors, n_epochs=100, random_state=seed,
                          transform_seed=seed, n_jobs=1, init='random', metric='euclidean').fit(z[:nfit])
        embedded = np.concatenate([model.embedding_, model.transform(z[nfit:])]) if nfit < len(x) else model.embedding_
        extra = {'umap_version': umap.__version__, 'out_of_sample': 'UMAP_TRANSFORM_APPROXIMATE_NOT_REFIT'}
    if not np.isfinite(embedded).all():
        raise ValueError('Nonfinite embedding.')
    artifact = Path(output_dir) / 'self-produced-embedding.joblib'
    joblib.dump({'scaler': scaler, 'embedding_model': model}, artifact)
    restored = joblib.load(artifact)
    replay = np.array_equal(restored['embedding_model'].embedding_, model.embedding_) if algorithm != 'pca' else True
    if algorithm == 'pca':
        replay = np.allclose(restored['embedding_model'].transform(z), embedded, atol=1e-8, rtol=1e-8)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig=plt.figure(figsize=(7,5),layout='constrained')
    ax=fig.add_subplot(111,projection='3d') if dim==3 else fig.add_subplot(111)
    for start,stop,label,marker in [(0,nfit,'Fit/reference','o'),(nfit,len(x),'Query transform','x')]:
        if start==stop:continue
        part=embedded[start:stop]
        if dim==3:ax.scatter(part[:,0],part[:,1],part[:,2],label=label,marker=marker)
        else:ax.scatter(part[:,0],part[:,1] if dim==2 else np.zeros(len(part)),label=label,marker=marker)
    ax.set_xlabel('Component1 / embedding units')
    ax.set_ylabel('Component2 / embedding units' if dim>1 else 'Display baseline (not a component)')
    if dim==3:ax.set_zlabel('Component3 / embedding units')
    ax.set_title(f'{algorithm.upper()} | dim={dim} | fit={nfit}, query={len(x)-nfit} | seed={seed}')
    ax.legend();fig.savefig(Path(output_dir)/'embedding.png',dpi=140);plt.close(fig)
    with (Path(output_dir) / 'embedding.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        writer.writerow(['id', 'fit_or_query'] + ['component_' + str(i+1) for i in range(dim)])
        writer.writerows([id_, 'fit' if i < nfit else 'query', *values.tolist()]
                         for i, (id_, values) in enumerate(zip(data['ids'], embedded)))
    k = min(3, (len(x) - 1) // 2)
    return {'scope': 'BOUNDED_DESCRIPTOR_VISUALIZATION_NOT_CHEMICAL_SPACE_OR_PROPERTY_CERTIFICATION',
            'environment': environment(), 'algorithm': algorithm, 'embedding': embedded.tolist(),
            'fit_indices': list(range(nfit)), 'query_indices': list(range(nfit, len(x))),
            'trustworthiness_k': k, 'trustworthiness_on_supplied_data': float(trustworthiness(z, embedded, n_neighbors=k)),
            'scaler_fit_mean': scaler.mean_.tolist() if scaler else None, **extra,
            'local_unsupervised_fit_runs': 1, 'plot_file':'embedding.png',
            'checks': [check('embedding_finite_and_aligned', embedded.shape == (len(x), dim)),
                check('owned_PCA_transform_replay' if algorithm=='pca' else 'owned_embedding_state_restore_not_new_point_replay', replay)],
            'limits': ['Explicit Euclidean numeric descriptors only; no automatic Tanimoto metric for binary fingerprints.',
                       't-SNE/UMAP global distances, cluster sizes and axis directions are not direct chemical or physical quantities.',
                       'Trustworthiness is a local geometry diagnostic, not predictive validation.',
                       'Held-out transforms use fit-only scaling; no supervised target or chemical activity inferred.']}
