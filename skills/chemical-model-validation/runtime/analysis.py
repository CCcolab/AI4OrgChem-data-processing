"""Fold-local scaling and Ridge evaluation with explicit group/time/shuffle semantics."""
from pathlib import Path
import numpy as np
from .ml_support import check, environment, features, integer, keys, real


def analyze(parameters, data, output_dir):
    from sklearn.model_selection import GroupKFold, TimeSeriesSplit, KFold
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import Ridge
    from sklearn.metrics import mean_absolute_error
    import joblib
    keys(parameters, ['scheme', 'seed', 'folds', 'alpha'])
    x, y = features(data, target=True, groups=True)
    groups = np.asarray(data['groups'])
    seed = integer(parameters['seed'], 0, 2**31 - 1, 'seed')
    folds = integer(parameters['folds'], 2, min(8, len(x)-1), 'folds')
    alpha = real(parameters['alpha'], 0, 100, 'alpha')
    scheme = parameters['scheme']
    if scheme == 'group':
        if len(set(groups)) < folds:
            raise ValueError('Fewer independent declared groups than folds.')
        splits = list(GroupKFold(folds).split(x, y, groups))
    elif scheme == 'time':
        splits = list(TimeSeriesSplit(folds).split(x))
    elif scheme == 'shuffle':
        splits = list(KFold(folds, shuffle=True, random_state=seed).split(x))
    else:
        raise ValueError('Declare group, time (input order) or shuffle; no automatic split choice.')
    records, checks = [], []
    for index, (train, test) in enumerate(splits):
        if scheme in {'group', 'time'} and set(groups[train]).intersection(groups[test]):
            raise ValueError('Declared groups cross this fold; choose a compatible group/time protocol.')
        pipeline = make_pipeline(StandardScaler(), Ridge(alpha=alpha)).fit(x[train], y[train])
        predicted = pipeline.predict(x[test])
        if not np.isfinite(predicted).all():
            raise ValueError('Nonfinite fold prediction.')
        checks.append(check('fold_' + str(index) + '_scaler_train_only', np.allclose(pipeline[0].mean_, x[train].mean(axis=0), atol=1e-12, rtol=1e-12)))
        checks.append(check('fold_' + str(index) + '_indices_disjoint', not set(train).intersection(test)))
        if scheme == 'time':
            checks.append(check('fold_' + str(index) + '_past_only', int(train.max()) < int(test.min())))
        joblib.dump(pipeline, Path(output_dir) / ('self-produced-fold-' + str(index) + '.joblib'))
        records.append({'fold': index, 'train_indices': train.tolist(), 'test_indices': test.tolist(),
                        'MAE': float(mean_absolute_error(y[test], predicted)), 'held_out_predictions': predicted.tolist()})
    return {'scope': 'FOLD_LOCAL_PIPELINE_EVALUATION_WITH_EXPLICIT_SPLIT_PROTOCOL_NOT_FULL_NESTED_SELECTION',
            'environment': environment(), 'scheme': scheme, 'folds': records,
            'mean_fold_MAE': float(np.mean([r['MAE'] for r in records])), 'target_unit': data['target_unit'],
            'local_training_runs': len(records), 'checks': checks,
            'limits': ['No hyperparameter search, nested model selection, statistical confidence interval or external validation.',
                       'Group labels and input time order must be justified by the research design; software does not authenticate them.',
                       'Shuffled KFold may leak group/chemical similarity; it is allowed only as an explicitly chosen IID demonstration.',
                       'Fold averaging of MAE is unweighted over folds, stated separately from per-observation pooled error.']}
