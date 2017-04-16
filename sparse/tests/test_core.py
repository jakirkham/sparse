import pytest

import random
import numpy as np
import scipy.sparse
from sparse import COO

import sparse


x = np.zeros(shape=(2, 3, 4), dtype=np.float32)
for i in range(10):
    x[random.randint(0, x.shape[0] - 1),
      random.randint(0, x.shape[1] - 1),
      random.randint(0, x.shape[2] - 1)] = random.randint(0, 100)
y = COO.from_numpy(x)


def random_x(shape, dtype=float):
    x = np.zeros(shape=shape, dtype=float)
    for i in range(max(5, np.prod(x.shape) // 10)):
        x[tuple(random.randint(0, d - 1) for d in x.shape)] = random.randint(0, 100)
    return x


def assert_eq(x, y):
    assert x.shape == y.shape
    assert x.dtype == y.dtype
    assert np.allclose(x, y)


@pytest.mark.parametrize('axis', [None, 0, 1, 2, (0, 2)])
def test_reductions(axis):
    xx = x.sum(axis=axis)
    yy = y.sum(axis=axis)
    assert_eq(xx, yy)


@pytest.mark.parametrize('axis', [None, (1, 2, 0), (2, 1, 0), (0, 1, 2)])
def test_transpose(axis):
    xx = x.transpose(axis)
    yy = y.transpose(axis)
    assert_eq(xx, yy)


@pytest.mark.parametrize('a,b', [[(3, 4), (3, 4)],
                                 [(12,), (3, 4)],
                                 [(12,), (3, -1)],
                                 [(3, 4), (12,)],
                                 [(2, 3, 4, 5), (8, 15)],
                                 [(2, 3, 4, 5), (24, 5)],
                                 [(2, 3, 4, 5), (20, 6)],
])
def test_reshape(a, b):
    x = random_x(a)
    s = COO.from_numpy(x)

    assert_eq(x.reshape(b), s.reshape(b))


def test_to_scipy_sparse():
    x = random_x((3, 5))
    s = COO.from_numpy(x)
    a = s.to_scipy_sparse()
    b = scipy.sparse.coo_matrix(x)

    assert_eq(a.data, b.data)
    assert_eq(a.todense(), b.todense())


@pytest.mark.parametrize('a_shape,b_shape,axes', [
    [(3, 4), (4, 3), (1, 0)],
    [(3, 4), (4, 3), (0, 1)],
    [(3, 4, 5), (4, 3), (1, 0)],
    [(3, 4), (5, 4, 3), (1, 1)],
    [(3, 4), (5, 4, 3), ((0, 1), (2, 1))],
    [(3, 4), (5, 4, 3), ((1, 0), (1, 2))],
])
def test_tensordot(a_shape, b_shape, axes):
    a = random_x(a_shape)
    b = random_x(b_shape)

    sa = COO.from_numpy(a)
    sb = COO.from_numpy(b)

    assert_eq(np.tensordot(a, b, axes),
              sparse.tensordot(sa, sb, axes))


@pytest.mark.xfail
@pytest.mark.parametrize('ufunc', [np.expm1, np.log1p])
def test_ufunc(ufunc):
    x = random_x((2, 3, 4))
    s = COO.from_numpy(x)

    assert isinstance(ufunc(s), COO)

    assert_eq(ufunc(x), ufunc(s))