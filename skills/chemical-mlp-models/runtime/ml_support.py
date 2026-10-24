"""Bounded numeric ML inputs, explicit splits and self-produced model replay."""
import csv
from pathlib import Path
import warnings
import numpy as np


def keys(value, required, optional=()):
    if not isinstance(value, dict) or not set(required).issubset(value) or set(value) - set(required) - set(optional):
        raise ValueError('Required fields: ' + ','.join(required) + '; optional: ' + ','.join(optional))


def integer(value, low, high, name):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(name + ' must be an integer in [' + str(low) + ',' + str(high) + '].')
    return value


def real(value, low, high, name):
    if type(value) not in {int, float} or not np.isfinite(value) or not low <= value <= high:
        raise ValueError(name + ' is outside its finite declared range.')
    return float(value)


def require_real_leaves(value):
    """Validate raw numeric leaves before NumPy can promote mixed Booleans."""
    pending = [value]
    visited = 0
    while pending:
        item = pending.pop()
        visited += 1
        if visited > 100000:
            raise ValueError('Numeric input exceeds the bounded traversal budget.')
        if isinstance(item, (list, tuple)):
            pending.extend(item)
        elif isinstance(item, np.ndarray):
            if item.dtype.kind not in 'if':
                raise ValueError('Require real numeric leaves; Boolean/string/null/complex input is not admitted.')
        elif isinstance(item, (bool, np.bool_)) or not isinstance(item, (int, float, np.integer, np.floating)):
            raise ValueError('Require real numeric leaves; Boolean/string/null/complex input is not admitted.')


def features(data, target=False, groups=False):
    required = ['ids', 'features', 'feature_names', 'feature_units'] + (['target', 'target_unit'] if target else []) + (['groups'] if groups else [])
    keys(data, required, ['source_csv_text'])
    require_real_leaves(data['features'])
    x = np.asarray(data['features'])
    if x.dtype.kind not in 'if' or x.ndim != 2 or not 5 <= x.shape[0] <= 200 or not 1 <= x.shape[1] <= 32:
        raise ValueError('Use 5–200 rows and 1–32 real numeric descriptor columns; no strings/Booleans/non-numeric imputation.')
    x = x.astype(float)
    if not np.isfinite(x).all():
        raise ValueError('Feature values must be finite.')
    ids, names, units = data['ids'], data['feature_names'], data['feature_units']
    if not isinstance(ids, list) or len(ids) != len(x) or len(set(ids)) != len(ids) or any(not isinstance(v, str) or not v for v in ids):
        raise ValueError('One unique nonempty string ID per row required.')
    if not isinstance(names, list) or len(names) != x.shape[1] or len(set(names)) != len(names) or any(not isinstance(v, str) or not v for v in names):
        raise ValueError('Explicit unique feature names required.')
    if not isinstance(units, list) or len(units) != len(names) or any(not isinstance(v, str) or not v for v in units):
        raise ValueError('Declare one feature unit label per column; dimensionless must be explicit.')
    y = None
    if target:
        if not isinstance(data['target_unit'], str) or not data['target_unit'].strip():
            raise ValueError('Declare target units or explicit binary-label semantics.')
        require_real_leaves(data['target'])
        y = np.asarray(data['target'])
        if y.dtype.kind not in 'if' or y.shape != (len(x),) or not np.isfinite(y).all():
            raise ValueError('Finite real one-dimensional target aligned with IDs required.')
        y = y.astype(float)
    if groups:
        value = data['groups']
        if not isinstance(value, list) or len(value) != len(x) or any(not isinstance(v, str) or not v for v in value):
            raise ValueError('Explicit nonempty group IDs aligned with rows required.')
    if 'source_csv_text' in data and (not isinstance(data['source_csv_text'], str) or len(data['source_csv_text'].encode('utf-8')) > 128000):
        raise ValueError('Bounded source CSV text required.')
    return x, y


def split(parameters, n):
    integer(parameters['seed'], 0, 2**31 - 1, 'seed')
    test = parameters['test_indices']
    if not isinstance(test, list) or not 1 <= len(test) <= n - 3 or len(set(test)) != len(test) or any(type(i) is not int or not 0 <= i < n for i in test):
        raise ValueError('Declare unique zero-based held-out indices, leaving at least three training rows.')
    train = np.array([i for i in range(n) if i not in set(test)], dtype=int)
    return train, np.asarray(test, dtype=int)


def check(name, condition, actual=None):
    return {'name': name, 'passed': bool(condition), 'actual': bool(condition) if actual is None else actual, 'threshold': True}


def save_model(model, output, test_x):
    import joblib
    artifact = Path(output) / 'self-produced-model.joblib'
    joblib.dump(model, artifact)
    # Only load the just-created owned artifact, never a user-supplied pickle.
    restored = joblib.load(artifact)
    expected, actual = model.predict(test_x), restored.predict(test_x)
    return check('owned_model_save_restore_predictions', np.allclose(expected, actual, atol=1e-10, rtol=1e-10))


def predictions_csv(output, ids, indices, observed, predicted):
    with (Path(output) / 'held-out-predictions.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        writer.writerow(['id', 'source_index', 'observed_target', 'predicted_target'])
        writer.writerows((ids[i], int(i), float(y), float(p)) for i, y, p in zip(indices, observed, predicted))


def environment():
    import sklearn
    return {'numpy': np.__version__, 'scikit_learn': sklearn.__version__}


def bounded_warnings(function):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        value = function()
    return value, [{'category': type(w.message).__name__, 'message': str(w.message)} for w in caught]


def supervised(parameters, data, output_dir, allowed):
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import Ridge, LogisticRegression
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
    from sklearn.neural_network import MLPRegressor, MLPClassifier
    from sklearn.compose import TransformedTargetRegressor
    from sklearn.metrics import mean_absolute_error, mean_squared_error, accuracy_score, balanced_accuracy_score, roc_auc_score
    name = parameters.get('algorithm')
    fields = {'ridge': ['alpha'], 'logistic': ['C'], 'tree_regression': ['max_depth'],
              'forest_regression': ['max_depth', 'n_estimators'], 'forest_classification': ['max_depth', 'n_estimators'],
              'mlp_regression': ['hidden_units', 'max_iter', 'alpha'], 'mlp_classification': ['hidden_units', 'max_iter', 'alpha']}
    if name not in allowed or name not in fields:
        raise ValueError('Algorithm is outside this Skill scope.')
    keys(parameters, ['algorithm', 'seed', 'test_indices', *fields[name]])
    x, y = features(data, target=True, groups='groups' in data)
    train, test = split(parameters, len(x))
    checks = [check('explicit_train_test_disjoint', not set(train).intersection(test))]
    if 'groups' in data:
        groups = np.asarray(data['groups'])
        if set(groups[train]).intersection(groups[test]):
            raise ValueError('Declared groups cross the supplied train/test split; refuse leakage.')
        checks.append(check('declared_group_disjointness', True))
    classification = name in {'logistic', 'forest_classification', 'mlp_classification'}
    if classification and (not np.isin(y, [0, 1]).all() or len(set(y[train])) != 2):
        raise ValueError('Binary labels 0/1 and both classes in training are required.')
    seed = parameters['seed']
    if name == 'ridge':
        base = Ridge(alpha=real(parameters['alpha'], 0, 100, 'alpha'))
    elif name == 'logistic':
        base = LogisticRegression(C=real(parameters['C'], 1e-6, 100, 'C'), max_iter=500, random_state=seed)
    elif name == 'tree_regression':
        base = DecisionTreeRegressor(max_depth=integer(parameters['max_depth'], 1, 8, 'max_depth'), random_state=seed)
    elif name.startswith('forest'):
        estimator = RandomForestClassifier if classification else RandomForestRegressor
        base = estimator(n_estimators=integer(parameters['n_estimators'], 2, 64, 'n_estimators'),
                         max_depth=integer(parameters['max_depth'], 1, 8, 'max_depth'), random_state=seed,
                         bootstrap=True, oob_score=False, n_jobs=1)
    else:
        estimator = MLPClassifier if classification else MLPRegressor
        base = estimator(hidden_layer_sizes=(integer(parameters['hidden_units'], 2, 16, 'hidden_units'),),
                         max_iter=integer(parameters['max_iter'], 50, 500, 'max_iter'),
                         alpha=real(parameters['alpha'], 1e-8, 100, 'alpha'), solver='lbfgs',
                         random_state=seed, tol=1e-5)
    scaled = name in {'ridge', 'logistic', 'mlp_regression', 'mlp_classification'}
    pipeline = make_pipeline(StandardScaler(), base) if scaled else base
    model = TransformedTargetRegressor(regressor=pipeline, transformer=StandardScaler()) if name == 'mlp_regression' else pipeline
    _, caught = bounded_warnings(lambda: model.fit(x[train], y[train]))
    prediction = model.predict(x[test])
    if not np.isfinite(prediction).all():
        raise ValueError('Nonfinite held-out predictions.')
    fitted_pipeline = model.regressor_ if name == 'mlp_regression' else model
    if scaled:
        scaler = fitted_pipeline[0]
        checks.append(check('feature_scaler_fitted_on_training_only', np.allclose(scaler.mean_, x[train].mean(axis=0), atol=1e-12, rtol=1e-12)))
    if name == 'mlp_regression':
        checks.append(check('target_scaler_fitted_on_training_only', np.allclose(model.transformer_.mean_, [y[train].mean()], atol=1e-12, rtol=1e-12)))
    checks.append(check('optimizer_no_convergence_warning', not any(w['category'] == 'ConvergenceWarning' for w in caught)))
    checks.append(save_model(model, output_dir, x[test]))
    predictions_csv(output_dir, data['ids'], test, y[test], prediction)
    if classification:
        probabilities = model.predict_proba(x[test])
        checks.append(check('probability_simplex', np.isfinite(probabilities).all() and np.allclose(probabilities.sum(axis=1), 1)))
        scores = {'accuracy': float(accuracy_score(y[test], prediction)),
                  'balanced_accuracy': float(balanced_accuracy_score(y[test], prediction)),
                  'roc_auc': float(roc_auc_score(y[test], probabilities[:, 1])) if len(set(y[test])) == 2 else None}
    else:
        rss = float(np.sum((prediction - y[test]) ** 2))
        tss = float(np.sum((y[test] - y[test].mean()) ** 2))
        scores = {'MAE': float(mean_absolute_error(y[test], prediction)),
                  'RMSE': float(np.sqrt(mean_squared_error(y[test], prediction))),
                  'R2': float(1-rss/tss) if len(test) > 1 and tss > 0 else None}
    return {'scope': 'BOUNDED_LOCAL_SUPERVISED_TRAINING_AND_OWNED_MODEL_REPLAY_NOT_CHEMICAL_PREDICTIVE_VALIDATION',
            'algorithm': name, 'environment': environment(), 'train_indices': train.tolist(), 'test_indices': test.tolist(),
            'held_out_metrics': scores, 'target_unit': data['target_unit'], 'optimizer_warnings': caught,
            'feature_names': data['feature_names'], 'local_training_runs': 1, 'local_prediction_runs': 2,
            'checks': checks, 'limits': ['Declared labels and group IDs do not authenticate experiments or chemical identity.',
                'No automatic hyperparameter/model selection, probability calibration, uncertainty interval or causal interpretation.',
                'A fixed holdout is not nested validation; using it repeatedly for model choice requires another untouched test set.',
                'Impurity feature importance, if later inspected, is not mechanism or causal evidence.',
                'Only a just-created owned model artifact is reloaded; no user-provided pickle/model code is accepted.']}
