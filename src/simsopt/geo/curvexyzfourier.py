from .curve import Curve
import simsgeopp as sgpp
import numpy as np

class CurveXYZFourier(sgpp.CurveXYZFourier, Curve):

    def __init__(self, quadpoints, order):
        if isinstance(quadpoints, int):
            quadpoints = list(np.linspace(0, 1, quadpoints, endpoint=False))
        elif isinstance(quadpoints, np.ndarray):
            quadpoints = list(quadpoints)
        sgpp.CurveXYZFourier.__init__(self, quadpoints, order)
        Curve.__init__(self)

    def get_dofs(self):
        return np.asarray(sgpp.CurveXYZFourier.get_dofs(self))

    def set_dofs(self, dofs):
        sgpp.CurveXYZFourier.set_dofs(self, dofs)
        for d in self.dependencies:
            d.invalidate_cache()

    # def kappa_impl(self, kappa):
    #     Curve.kappa_impl(self, kappa)



from jax.ops import index, index_add
import jax.numpy as jnp
from math import pi
from .curve import JaxCurve


def jaxfouriercurve_pure(dofs, quadpoints, order):
    k = len(dofs)//3
    coeffs = [dofs[:k], dofs[k:(2*k)], dofs[(2*k):]]
    points = quadpoints
    gamma = np.zeros((len(points), 3))
    for i in range(3):
        gamma = index_add(gamma, index[:, i], coeffs[i][0])
        for j in range(1, order+1):
            gamma = index_add(gamma, index[:, i], coeffs[i][2*j-1] * jnp.sin(2*pi*j*points))
            gamma = index_add(gamma, index[:, i], coeffs[i][2*j]   * jnp.cos(2*pi*j*points))
    return gamma


class JaxCurveXYZFourier(JaxCurve):

    """ 
    A Python+Jax implementation of the CurveXYZFourier class.  There is
    actually no reason why one should use this over the C++ implementation in
    simsgeopp, but the point of this class is to illustrate how jax can be used
    to define a geometric object class and calculate all the derivatives (both
    with respect to dofs and with respect to the angle phi) automatically.
    """

    def __init__(self, quadpoints, order):
        if isinstance(quadpoints, int):
            quadpoints = np.linspace(0, 1, quadpoints, endpoint=False)
        pure = lambda dofs, points: jaxfouriercurve_pure(dofs, points, order)
        self.order = order
        self.coefficients = [np.zeros((2*order+1,)), np.zeros((2*order+1,)), np.zeros((2*order+1,))]
        super().__init__(quadpoints, pure)

    def num_dofs(self):
        return 3*(2*self.order+1)

    def get_dofs(self):
        return np.concatenate(self.coefficients)

    def set_dofs_impl(self, dofs):
        counter = 0
        for i in range(3):
            self.coefficients[i][0] = dofs[counter]
            counter += 1
            for j in range(1, self.order+1):
                self.coefficients[i][2*j-1] = dofs[counter]
                counter += 1
                self.coefficients[i][2*j] = dofs[counter]
                counter += 1
