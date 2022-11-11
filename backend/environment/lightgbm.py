import dataclasses


@dataclasses.dataclass(frozen=True)
class LightGBM:
    METHOD = "regression"
    MODE = "display"
    PARAMS = {
        'objective': 'regression',
        'metric': 'rmse',
        'feature_pre_filter': False,
        'boosting_type': 'gbdt',
        'lambda_l1': 6.6377046563499,
        'lambda_l2': 0.009493220785902975,
        'num_leaves': 31,
        'feature_fraction': 0.748,
        'bagging_fraction': 1.0,
        'bagging_freq': 0,
        'min_child_samples': 20
    }
