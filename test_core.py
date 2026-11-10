"""Independent invariants and hand-calculated examples for the core algorithms."""
import unittest
from core import UniformRNG, add_uniform_noise, moments, mse, smooth_both, validate_filter


class CoreTests(unittest.TestCase):
    def test_rng_known_sequence(self):
        rng = UniformRNG(1)
        expected = [16807, 282475249, 1622650073, 984943658, 1144108930]
        for value in expected:
            rng.random()
            self.assertEqual(rng.state, value)

    def test_hand_calculated_center(self):
        image = [[1., 2., 3.], [4., 5., 6.], [7., 8., 100.]]
        knn, avg = smooth_both(image, 3, 3)
        self.assertEqual(knn[1][1], 5.)  # Selected 5, 4, 6.
        self.assertAlmostEqual(avg[1][1], 136 / 9)
        self.assertAlmostEqual(avg[0][0], 21 / 9)  # Replicated corner.

    def test_k_one_is_identity(self):
        image = [[1., 50., 3.], [4., -2., 9.]]
        self.assertEqual(smooth_both(image, 3, 1)[0], image)

    def test_k_full_window_equals_mean(self):
        knn, avg = smooth_both([[1., 9.], [5., 3.]], 5, 25)
        self.assertEqual(knn, avg)

    def test_constant_preserved(self):
        image = [[7.] * 3 for _ in range(2)]
        self.assertEqual(smooth_both(image, 5, 7), (image, image))

    def test_mse(self):
        self.assertEqual(mse([[1., 2.]], [[3., 1.]]), 2.5)
        with self.assertRaises(ValueError):
            mse([[1.]], [[1., 2.]])

    def test_noise_scale_bounds_and_reproducibility(self):
        image = [[100.] * 300 for _ in range(300)]
        noisy, noise, sigma = add_uniform_noise(image, 0.1, 607)
        mu, sd = moments(noise)
        self.assertAlmostEqual(sigma, 10.)
        self.assertLess(abs(mu), 0.15)
        self.assertLess(abs(sd - sigma), 0.15)
        for row in noise:
            for value in row:
                self.assertLessEqual(abs(value), (3 ** 0.5) * sigma)
        self.assertEqual(noisy, add_uniform_noise(image, 0.1, 607)[0])
        self.assertEqual(add_uniform_noise([[100.]], 0, 607)[0], [[100.]])

    def test_no_clipping(self):
        noisy, _, _ = add_uniform_noise([[0., 100.]], 0.2, 1)
        self.assertLess(noisy[0][0], 0.)

    def test_bad_parameters(self):
        for window, k in [(2, 1), (3, 0), (3, 10), (0, 1), (3, 1.5)]:
            with self.assertRaises(ValueError):
                validate_filter(window, k)


if __name__ == "__main__":
    unittest.main()
