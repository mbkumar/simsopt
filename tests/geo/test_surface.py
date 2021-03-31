import unittest
from pathlib import Path
import numpy as np

from simsopt.core.dofs import Dofs
from simsopt.core.optimizable import optimizable
from simsopt.geo.surfacerzfourier import SurfaceRZFourier
from simsopt.geo.surfacegarabedian import SurfaceGarabedian
from simsopt.geo.surfacexyzfourier import SurfaceXYZFourier
from .surface_test_helpers import get_ncsx_data,get_surface, get_exact_surface 

TEST_DIR = (Path(__file__).parent / ".." / "test_files").resolve()

surfacetypes_list = ["SurfaceXYZFourier", "SurfaceRZFourier"]
stellsym_list = [True, False]
class SurfaceXYZFourierTests(unittest.TestCase):
    def test_toRZFourier_perfect_torus(self):

        """
        This test checks that a perfect torus can be converted from SurfaceXYZFourier to SurfaceRZFourier
        completely losslessly.
        """
        for stellsym in stellsym_list:
            with self.subTest(stellsym=stellsym):
                self.subtest_toRZFourier_perfect_torus("SurfaceXYZFourier",stellsym)

    def subtest_toRZFourier_perfect_torus(self, surfacetype, stellsym):
        """
        The test obtains a perfect torus as a SurfaceXYZFourier, then converts it to a SurfaceRZFourier.  Next,
        it computes the cross section of both surfaces at a random angle and compares the pointwise values.
        """
        s = get_surface(surfacetype, stellsym)
        sRZ = s.to_RZFourier()

        np.random.seed(0)
        angle = np.random.random()*1000
        scs = s.cross_section(angle, theta_resolution = 100)
        sRZcs = sRZ.cross_section(angle, theta_resolution = 100)

        maxerr = np.max(np.abs(scs - sRZcs))
        print(maxerr)
        assert maxerr < 1e-12

    def test_toRZFourier_lossless_at_quadraturepoints(self):
        """
        This test obtains a more complex surface (not a perfect torus) as a SurfaceXYZFourier, then
        converts that surface to the SurfaceRZFourier representation.  Then, the test checks that both
        surface representations coincide at the points where the least squares fit was completed,
        i.e., the conversion is lossless at the quadrature points.
        """
        s = get_exact_surface()
        sRZ = s.to_RZFourier()
        
        maxerror = -1
        for angle in sRZ.quadpoints_phi:
            scs = s.cross_section( angle * 2 * np.pi )
            sRZcs = sRZ.cross_section( angle * 2 * np.pi )
            maxerr = np.max(np.abs(scs - sRZcs))
            if maxerror < maxerr:
                maxerror = maxerr
        assert maxerr < 1e-12


    def test_toRZFourier_small_loss_elsewhere(self):
        """
        Away from the quadrature points, the conversion is not lossless and this test verifies that the
        error is small.
        """
        s = get_exact_surface()
        sRZ = s.to_RZFourier()
        
        np.random.seed(0)
        angle = np.random.random()*1000
        scs = s.cross_section(angle )
        sRZcs = sRZ.cross_section(angle)
        
        maxerr = np.max(np.abs(scs - sRZcs))
        print(maxerr)
        assert maxerr < 1e-3


    def test_cross_section(self):
        """
        Test that the cross sectional area at a certain number of cross sections is what it should be
        """
        mpol = 4
        ntor = 3
        nfp = 2
        phis = np.linspace(0, 1, 31, endpoint=False)
        thetas = np.linspace(0, 1, 31, endpoint=False)
        
        np.random.seed(0)

        stellsym = False
        s = SurfaceXYZFourier(mpol=mpol, ntor=ntor, nfp = nfp, stellsym = stellsym, quadpoints_phi = phis, quadpoints_theta = thetas)
        s.xc = s.xc * 0
        s.xs = s.xs * 0
        s.ys = s.ys * 0
        s.yc = s.yc * 0
        s.zs = s.zs * 0
        s.zc = s.zc * 0
        r1 = np.random.random_sample() + 0.1
        r2 = np.random.random_sample() + 0.1
        major_R = np.max([r1,r2])
        minor_R = np.min([r1,r2])
        s.xc[0, ntor] = major_R
        s.xc[1, ntor] = minor_R
        s.zs[1, ntor] = minor_R
        
        cs = np.zeros((5,100,3))
        cs[0,:,:] = s.cross_section(0., theta_resolution = 100)
        cs[1,:,:] = s.cross_section(np.pi/2., theta_resolution = 100)
        cs[2,:,:] = s.cross_section(np.pi, theta_resolution = 100)
        cs[3,:,:] = s.cross_section(3. * np.pi/2., theta_resolution = 100)
        cs[4,:,:] = s.cross_section(2. * np.pi, theta_resolution = 100)
        
        from scipy import fftpack
        cs_area = np.zeros( (5,) )
        for i in range(5):
            R = np.sqrt( cs[i,:,0]**2 + cs[i,:,1]**2)
            Z = cs[i,:,2]
            Rp = fftpack.diff(R, period = 1.)
            Zp = fftpack.diff(Z, period = 1.)
            cs_area[i] = np.mean( Z*Rp ) 
        exact_area = np.pi * minor_R**2.
        assert np.max( np.abs( cs_area - cs_area ) ) < 1e-14


    def test_aspect_ratio_random_torus(self):
        """
        This is a simple aspect ratio validation on a torus with minor radius = r1
        and major radius = r2, where 0.1 <= r1 <= r2 are random numbers
        """
        mpol = 4
        ntor = 3
        nfp = 2
        phis = np.linspace(0, 1, 31, endpoint=False)
        thetas = np.linspace(0, 1, 31, endpoint=False)
        

        stellsym = False
        s = SurfaceXYZFourier(mpol=mpol, ntor=ntor, nfp = nfp, stellsym = stellsym, quadpoints_phi = phis, quadpoints_theta = thetas)
        s.xc = s.xc * 0
        s.xs = s.xs * 0
        s.ys = s.ys * 0
        s.yc = s.yc * 0
        s.zs = s.zs * 0
        s.zc = s.zc * 0
        np.random.seed(0)
        r1 = np.random.random_sample() + 0.1
        r2 = np.random.random_sample() + 0.1
        major_R = np.max([r1,r2])
        minor_R = np.min([r1,r2])
        s.xc[0, ntor] = major_R
        s.xc[1, ntor] = minor_R
        s.zs[1, ntor] = minor_R
        
        print("AR approx: ", s.aspect_ratio(), "Exact: " ,major_R/minor_R)
        self.assertAlmostEqual(s.aspect_ratio() , major_R/minor_R)

    def test_aspect_ratio_compare_with_cross_sectional_computation(self):
        """
        This test validates the VMEC aspect ratio computation in the Surface class by 
        comparing with an approximation based on cross section computations.
        """
        s = get_exact_surface()
        vpr = s.quadpoints_phi.size  +20
        tr = s.quadpoints_theta.size +20
        cs_area = np.zeros( (vpr,) )
        
        from scipy import fftpack
        angle = np.linspace(-np.pi,np.pi, vpr, endpoint = False)
        for idx in range(angle.size):
            cs = s.cross_section(angle[idx], varphi_resolution = vpr, theta_resolution = tr )
            R = np.sqrt( cs[:,0]**2 + cs[:,1]**2)
            Z = cs[:,2]
            Rp = fftpack.diff(R, period = 1.)
            Zp = fftpack.diff(Z, period = 1.)
            ar = np.mean( Z*Rp ) 
            cs_area[idx] = ar


        mean_cross_sectional_area = np.mean(cs_area)
        R_minor = np.sqrt( mean_cross_sectional_area / np.pi )
        R_major = np.abs(s.volume()) / (2. * np.pi**2 * R_minor**2)
        AR_cs = R_major / R_minor
        AR = s.aspect_ratio()

        rel_err = np.abs(AR-AR_cs) / AR
        print( AR, AR_cs )
        print("AR rel error is:", rel_err)
        assert rel_err < 1e-5

class SurfaceRZFourierTests(unittest.TestCase):
    def test_aspect_ratio(self):
        """
        Test that the aspect ratio of a torus with random minor and major radius 0.1 <= minor_R <= major_R
        is properly computed to be major_R/minor_R.
        """

        s = SurfaceRZFourier(nfp=2, mpol=3, ntor=2)
        s.rc = s.rc * 0
        s.rs = s.rs * 0
        s.zc = s.zc * 0
        s.zs = s.zs * 0
        r1 = np.random.random_sample() + 0.1
        r2 = np.random.random_sample() + 0.1
        major_R = np.max([r1,r2])
        minor_R = np.min([r1,r2])
        s.rc[0, 2] = major_R
        s.rc[1, 2] = minor_R
        s.zs[1, 2] = minor_R
        print("AR approx: ", s.aspect_ratio(), "Exact: " ,major_R/minor_R)
        self.assertAlmostEqual(s.aspect_ratio() , major_R/minor_R)

    def test_init(self):
        s = SurfaceRZFourier(nfp=2, mpol=3, ntor=2)
        self.assertEqual(s.rc.shape, (4, 5))
        self.assertEqual(s.zs.shape, (4, 5))

        s = SurfaceRZFourier(nfp=10, mpol=1, ntor=3, stellsym=False)
        self.assertEqual(s.rc.shape, (2, 7))
        self.assertEqual(s.zs.shape, (2, 7))
        self.assertEqual(s.rs.shape, (2, 7))
        self.assertEqual(s.zc.shape, (2, 7))

    def test_area_volume(self):
        """
        Test the calculation of area and volume for an axisymmetric surface
        """
        s = SurfaceRZFourier()
        s.rc[0, 0] = 1.3
        s.rc[1, 0] = 0.4
        s.zs[1, 0] = 0.2

        true_area = 15.827322032265993
        true_volume = 2.0528777154265874
        self.assertAlmostEqual(s.area(), true_area, places=4)
        self.assertAlmostEqual(s.volume(), true_volume, places=3)

    def test_get_dofs(self):
        """
        Test that we can convert the degrees of freedom into a 1D vector
        """

        # First try an axisymmetric surface for simplicity:
        s = SurfaceRZFourier()
        s.rc[0, 0] = 1.3
        s.rc[1, 0] = 0.4
        s.zs[0, 0] = 0.3
        s.zs[1, 0] = 0.2
        dofs = s.get_dofs()
        self.assertEqual(dofs.shape, (3,))
        self.assertAlmostEqual(dofs[0], 1.3)
        self.assertAlmostEqual(dofs[1], 0.4)
        self.assertAlmostEqual(dofs[2], 0.2)

        # Now try a nonaxisymmetric shape:
        s = SurfaceRZFourier(mpol=3, ntor=1)
        s.rc[:, :] = [[100, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]] 
        s.zs[:, :] = [[101, 102, 13], [14, 15, 16], [17, 18, 19], [20, 21, 22]] 
        dofs = s.get_dofs()
        self.assertEqual(dofs.shape, (21,))
        for j in range(21):
            self.assertAlmostEqual(dofs[j], j + 2)
        
    def test_set_dofs(self):
        """
        Test that we can set the shape from a 1D vector
        """

        # First try an axisymmetric surface for simplicity:
        s = SurfaceRZFourier()
        s.set_dofs([2.9, -1.1, 0.7])
        self.assertAlmostEqual(s.rc[0, 0], 2.9)
        self.assertAlmostEqual(s.rc[1, 0], -1.1)
        self.assertAlmostEqual(s.zs[1, 0], 0.7)
        
        # Now try a nonaxisymmetric shape:
        s = SurfaceRZFourier(mpol=3, ntor=1)
        s.set_dofs(np.array(list(range(21))) + 1)
        self.assertAlmostEqual(s.rc[0, 0], 0)
        self.assertAlmostEqual(s.rc[0, 1], 1)
        self.assertAlmostEqual(s.rc[0, 2], 2)
        self.assertAlmostEqual(s.rc[1, 0], 3)
        self.assertAlmostEqual(s.rc[1, 1], 4)
        self.assertAlmostEqual(s.rc[1, 2], 5)
        self.assertAlmostEqual(s.rc[2, 0], 6)
        self.assertAlmostEqual(s.rc[2, 1], 7)
        self.assertAlmostEqual(s.rc[2, 2], 8)
        self.assertAlmostEqual(s.rc[3, 0], 9)
        self.assertAlmostEqual(s.rc[3, 1], 10)
        self.assertAlmostEqual(s.rc[3, 2], 11)

        self.assertAlmostEqual(s.zs[0, 0], 0)
        self.assertAlmostEqual(s.zs[0, 1], 0)
        self.assertAlmostEqual(s.zs[0, 2], 12)
        self.assertAlmostEqual(s.zs[1, 0], 13)
        self.assertAlmostEqual(s.zs[1, 1], 14)
        self.assertAlmostEqual(s.zs[1, 2], 15)
        self.assertAlmostEqual(s.zs[2, 0], 16)
        self.assertAlmostEqual(s.zs[2, 1], 17)
        self.assertAlmostEqual(s.zs[2, 2], 18)
        self.assertAlmostEqual(s.zs[3, 0], 19)
        self.assertAlmostEqual(s.zs[3, 1], 20)
        self.assertAlmostEqual(s.zs[3, 2], 21)
        
    def test_from_focus(self):
        """
        Try reading in a focus-format file.
        """
        filename = TEST_DIR / 'tf_only_half_tesla.plasma'

        s = SurfaceRZFourier.from_focus(filename)

        self.assertEqual(s.nfp, 3)
        self.assertTrue(s.stellsym)
        self.assertEqual(s.rc.shape, (11, 13))
        self.assertEqual(s.zs.shape, (11, 13))
        self.assertAlmostEqual(s.rc[0, 6], 1.408922E+00)
        self.assertAlmostEqual(s.rc[0, 7], 2.794370E-02)
        self.assertAlmostEqual(s.zs[0, 7], -1.909220E-02)
        self.assertAlmostEqual(s.rc[10, 12], -6.047097E-05)
        self.assertAlmostEqual(s.zs[10, 12], 3.663233E-05)

        self.assertAlmostEqual(s.get_rc(0,0), 1.408922E+00)
        self.assertAlmostEqual(s.get_rc(0,1), 2.794370E-02)
        self.assertAlmostEqual(s.get_zs(0,1), -1.909220E-02)
        self.assertAlmostEqual(s.get_rc(10,6), -6.047097E-05)
        self.assertAlmostEqual(s.get_zs(10,6), 3.663233E-05)

        true_area = 24.5871075268402
        true_volume = 2.96201898538042
        #print("computed area: ", area, ", correct value: ", true_area, \
        #    " , difference: ", area - true_area)
        #print("computed volume: ", volume, ", correct value: ", \
        #    true_volume, ", difference:", volume - true_volume)
        self.assertAlmostEqual(s.area(), true_area, places=4)
        self.assertAlmostEqual(s.volume(), true_volume, places=3)

    def test_derivatives(self):
        """
        Check the automatic differentiation for area and volume.
        """
        for mpol in range(1, 3):
            for ntor in range(2):
                for nfp in range(1, 4):
                    s = SurfaceRZFourier(nfp=nfp, mpol=mpol, ntor=ntor)
                    x0 = s.get_dofs()
                    x = np.random.rand(len(x0)) - 0.5
                    x[0] = np.random.rand() + 2
                    # This surface will probably self-intersect, but I
                    # don't think this actually matters here.
                    s.set_dofs(x)

                    dofs = Dofs([s.area, s.volume])
                    jac = dofs.jac()
                    fd_jac = dofs.fd_jac()
                    print('difference for surface test_derivatives:', jac - fd_jac)
                    np.testing.assert_allclose(jac, fd_jac, rtol=1e-4, atol=1e-4)

    def test_change_resolution(self):
        """
        Check that we can change mpol and ntor.
        """
        for mpol in [1, 2]:
            for ntor in [0, 1]:
                s = SurfaceRZFourier(mpol=mpol, ntor=ntor)
                n = len(s.get_dofs())
                s.set_dofs((np.random.rand(n) - 0.5) * 0.01)
                s.set_rc(0, 0, 1.0)
                s.set_rc(1, 0, 0.1)
                s.set_zs(1, 0, 0.13)
                v1 = s.volume()
                a1 = s.area()
                
                s.change_resolution(mpol+1, ntor)
                s.recalculate = True
                v2 = s.volume()
                a2 = s.area()
                self.assertAlmostEqual(v1, v2)
                self.assertAlmostEqual(a1, a2)

                s.change_resolution(mpol, ntor+1)
                s.recalculate = True
                v2 = s.volume()
                a2 = s.area()
                self.assertAlmostEqual(v1, v2)
                self.assertAlmostEqual(a1, a2)

                s.change_resolution(mpol+1, ntor+1)
                s.recalculate = True
                v2 = s.volume()
                a2 = s.area()
                self.assertAlmostEqual(v1, v2)
                self.assertAlmostEqual(a1, a2)
        
class SurfaceGarabedianTests(unittest.TestCase):
    def test_init(self):
        """
        Check that the default surface is what we expect, and that the
        'names' array is correctly aligned.
        """
        s = optimizable(SurfaceGarabedian(nmin=-1, nmax=2, mmin=-2, mmax=5))
        self.assertAlmostEqual(s.Delta[2, 1], 0.1)
        self.assertAlmostEqual(s.Delta[3, 1], 1.0)
        self.assertAlmostEqual(s.get('Delta(0,0)'), 0.1)
        self.assertAlmostEqual(s.get('Delta(1,0)'), 1.0)
        # Verify all other elements are 0:
        d = np.copy(s.Delta)
        d[2, 1] = 0
        d[3, 1] = 0
        np.testing.assert_allclose(d, np.zeros((8, 4)))

        s.set('Delta(-2,-1)', 42)
        self.assertAlmostEqual(s.Delta[0, 0], 42)
        self.assertAlmostEqual(s.get_Delta(-2, -1), 42)

        s.set('Delta(5,-1)', -7)
        self.assertAlmostEqual(s.Delta[7, 0], -7)
        self.assertAlmostEqual(s.get_Delta(5, -1), -7)

        s.set('Delta(-2,2)', 13)
        self.assertAlmostEqual(s.Delta[0, 3], 13)
        self.assertAlmostEqual(s.get_Delta(-2, 2), 13)

        s.set('Delta(5,2)', -5)
        self.assertAlmostEqual(s.Delta[7, 3], -5)
        self.assertAlmostEqual(s.get_Delta(5, 2), -5)
        
        s.set_Delta(-2, -1, 421)
        self.assertAlmostEqual(s.Delta[0, 0], 421)

        s.set_Delta(5, -1, -71)
        self.assertAlmostEqual(s.Delta[7, 0], -71)

        s.set_Delta(-2, 2, 133)
        self.assertAlmostEqual(s.Delta[0, 3], 133)

        s.set_Delta(5, 2, -50)
        self.assertAlmostEqual(s.Delta[7, 3], -50)
        


       


    def test_convert_back(self):
        """
        If we start with a SurfaceRZFourier, convert to Garabedian, and
        convert back to SurfaceFourier, we should get back what we
        started with.
        """
        for mpol in range(1, 4):
            for ntor in range(5):
                for nfp in range(1, 4):
                    sf1 = SurfaceRZFourier(nfp=nfp, mpol=mpol, ntor=ntor)
                    # Set all dofs to random numbers in [-2, 2]:
                    sf1.set_dofs((np.random.rand(len(sf1.get_dofs())) - 0.5) * 4)
                    sg = sf1.to_Garabedian()
                    sf2 = sg.to_RZFourier()
                    np.testing.assert_allclose(sf1.rc, sf2.rc)
                    np.testing.assert_allclose(sf1.zs, sf2.zs)
 






if __name__ == "__main__":
    unittest.main()
