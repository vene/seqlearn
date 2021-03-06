from nose.tools import assert_equal, assert_true
from numpy.testing import assert_array_equal

import numpy as np
import re

from seqlearn.evaluation import bio_f_score, SequenceKFold


def test_bio_f_score():
    # Outputs from with the "conlleval" Perl script from CoNLL 2002.
    examples = [
        ("OBIO", "OBIO", 1.),
        ("BII", "OBI", 0.),
        ("BB", "BI", 0.),
        ("BBII", "BBBB", 1 / 3.),
        ("BOOBIB", "BOBOOB", 2 / 3.),
    ]

    for y_true, y_pred, score in examples:
        y_true = list(y_true)
        y_pred = list(y_pred)
        assert_equal(score, bio_f_score(y_true, y_pred))


def test_kfold():
    sequences = [
        "BIIOOOBOO",
        "OOBIOOOBI",
        "OOOOO",
        "BIIOOOOO",
        "OBIOOBIIIII",
        "OOBII",
        "BIBIBIO",
    ]

    y = np.asarray(list(''.join(sequences)))

    for random_state in [75, 82, 91, 57, 291]:
        for indices in [False, True]:
            kfold = SequenceKFold(map(len, sequences), n_folds=3,
                                  shuffle=True, indices=indices,
                                  random_state=random_state)
            folds = list(iter(kfold))
            for train, test in folds:
                if indices:
                    assert_true(np.issubdtype(train.dtype, np.integer))
                    assert_true(np.issubdtype(test.dtype, np.integer))
                    assert_true(np.all(train < len(y)))
                    assert_true(np.all(test < len(y)))
                else:
                    assert_true(np.issubdtype(train.dtype, bool))
                    assert_true(np.issubdtype(test.dtype, bool))
                    assert_equal(len(train), len(y))
                    assert_equal(len(test), len(y))
                    assert_array_equal(~train, test)

                y_train = ''.join(y[train])
                y_test = ''.join(y[test])
                # consistent BIO labeling preserved
                assert_true(re.match(r'O*(?:BI*)O*', y_train))
                assert_true(re.match(r'O*(?:BI*)O*', y_test))
