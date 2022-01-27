import unittest
import sys
from pages.resizeImage import open_file


class TestImage(unittest.TestCase):
    def test_image(self):
        image = open_file()
        seam = image.best_seam()

        # Make sure the seam is of the appropriate length.
        self.assertEqual(image.height, len(seam), "Seam wrong size.")

        # Make sure the pixels in the seam are properly connected.
        # seam.sort(cmp=lambda x,y: (x[1]>y[1])-(x[1]<y[1])) # Sort by height.
        # for i in range(1, len(seam)):
        #     self.assertTrue(abs(seam[i][0]-seam[i-1][0]) <= 1, 'Not a proper seam.')
        #     self.assertEqual(i, seam[i][1], 'Not a proper seam.')

        # Make sure the energy of the seam matches what we expect.
        # total = sum([image.energy(coord[0], coord[1]) for coord in seam])
        # self.assertEqual(total, expected_cost)


if __name__ == "__main__":
    unittest.main(argv=sys.argv + ["--verbose"])
