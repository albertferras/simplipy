#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import unittest
import random
import copy
from simplipy.geotool import distance, qdistance
from simplipy.geotool_py import (crosses as crosses_py,
                                 compute_allowed_shortcuts as compute_allowed_shortcuts_py)
from simplipy.geotool_c import (crosses as crosses_c,
                                compute_allowed_shortcuts as compute_allowed_shortcuts_c)


def rand_point():
    return (random.random(), random.random())

class TestGeoTool(unittest.TestCase):
    def test_distance(self):
        cases = [((-3.945, 0.718), (-11.091, -11.741), 14.362868689784781),
                 ((-13.213, 2.417), (-3.39, 14.324), 15.435931393991098),
                 ((-4.671, 6.834), (3.676, 2.781), 9.278966429511426),
                 ((-1.98, 9.318), (-5.526, -9.722), 19.36738794985013),
                 ((4.334, 5.911), (-3.203, -2.28), 11.130986029997521),
                 ((-0.9, -9.9), (0.163, 6.85), 16.783696523710145),
                 ((4.355, 12.574), (1.742, 7.319), 5.868798343783845),
                 ((0, 0), (0, 0), 0)]
        for (px, py), (qx, qy), expected_distance in cases:

            dist = distance(px, py, qx, qy)
            qdist = qdistance(px, py, qx, qy)
            self.assertAlmostEqual(dist, expected_distance)
            self.assertAlmostEqual(dist ** 2, qdist)

    def _test_crosses(self, x1, y1, x2, y2, u1, v1, u2, v2, endpoint_intersects):
        c = crosses_c(x1, y1, x2, y2, u1, v1, u2, v2, endpoint_intersects=endpoint_intersects)
        py = crosses_py(x1, y1, x2, y2, u1, v1, u2, v2, endpoint_intersects=endpoint_intersects)
        if c != py:
            print "Fail for parameters:"
            print x1, y1, x2, y2, u1, v1, u2, v2
            self.fail("C and PY implementation return distinct results (C=%s, PY=%s)" % (c, py))

    def test_crosses(self):
        random.seed(0)
        for endpoint_intersects in (True, False):
            for case in xrange(50000):
                # print "------------"
                x1, y1 = rand_point()
                x2, y2 = rand_point()
                u1, v1 = rand_point()
                u2, v2 = rand_point()
                self._test_crosses(x1, y1, x2, y2, u1, v1, u2, v2, endpoint_intersects)

                self._test_crosses(x1, y1, x2, y2, x1, y1+1e-8, u2, v2, endpoint_intersects)

    def test_compute_allowed_shortcuts(self):
        case1 = [(33.647959832000055, 31.117254950000174), (33.61475670700017, 31.115383205000015), (33.59205162900011, 31.12128327000012), (33.59205162900011, 31.114406643000123), (33.57252037900011, 31.12156810100008), (33.499522332000225, 31.128078518000066), (33.48080488400015, 31.13324616100006), (33.44092858200011, 31.151190497000115), (33.427500847000175, 31.14793528900016), (33.42066491000017, 31.14793528900016), (33.41724694100017, 31.15078359600001), (33.40642337300008, 31.155422268000123)]
        case2 = [(31.435476115000114, 21.99535105400004), (31.49471917600013, 21.995386529000044), (31.521775757000142, 21.99540273100014), (31.62409509300008, 21.99540273100014), (31.72651778200006, 21.99540273100014), (31.828837118000166, 21.99540273100014), (31.931259806000213, 21.99540273100014), (32.03357914200009, 21.99540273100014), (32.136001831000016, 21.99540273100014), (32.23832116700012, 21.99540273100014), (32.34074385600016, 21.99540273100014), (32.443063192000096, 21.99540273100014), (32.524518790000144, 21.99540273100014), (32.54543420400009, 21.99540273100014), (32.647856893000125, 21.99540273100014), (32.75033125800016, 21.99540273100014), (32.85265059400015, 21.99540273100014), (32.95507328300019, 21.99540273100014), (33.05739261800008, 21.99540273100014), (33.15976042200012, 21.99540273100014), (33.159815307000116, 21.99540273100014), (33.181138266322165, 21.995407469401115), (33.39235925300008, 21.995454407000167), (33.6250582280002, 21.995454407000167), (33.8577055260001, 21.995454407000167), (34.08417936900011, 21.995454407000167), (34.09045617700005, 21.995454407000167), (34.32310347500018, 21.995454407000167), (34.555750773000085, 21.99550608300008), (34.788501424000145, 21.995557760000096), (35.02114872200016, 21.995557760000096), (35.25379602000007, 21.995557760000096), (35.486443318000084, 21.995557760000096), (35.71919396900009, 21.99560943600001), (35.95184126800021, 21.99560943600001), (36.184591919000155, 21.99560943600001), (36.41723921700006, 21.99566111300011), (36.64988651500019, 21.995712789000137), (36.88363691500015, 21.99571360900002)]
        case3 = [(34.73216196500019, 27.918943023000125), (34.73188201100001, 27.95714111400015), (34.68177332800022, 27.958703244999995), (34.661785763000154, 27.930218099000072)]
        case4 = [(-64.64763070564058, 32.368227979697096), (-64.6760961579999, 32.38865794500013), (-64.69725501199991, 32.373521226000136), (-64.71313216073449, 32.364352153951856), (-64.72202022916721, 32.35251162240489), (-64.73638711520564, 32.343810277502214), (-64.74165990765951, 32.33307298398118), (-64.73948777580182, 32.32869455709603), (-64.73473870650784, 32.327702250127075), (-64.73289887203498, 32.333733130564795), (-64.72463708989113, 32.33878621989682), (-64.71313216073449, 32.34264752977869), (-64.70538050924401, 32.33605862601193), (-64.71390732588344, 32.329469722245065), (-64.71855831677775, 32.32365598362726), (-64.73599953263107, 32.32288081847814), (-64.74026294095088, 32.32404356620184), (-64.75121008999992, 32.31362539300001), (-64.76183020699995, 32.310939846000124), (-64.78014075399992, 32.303412177000055), (-64.81083399869615, 32.30755937866543), (-64.81396733425686, 32.303978423739), (-64.80537681347022, 32.29342454281469), (-64.79452450138365, 32.289548717069536), (-64.77902119840289, 32.29109904736747), (-64.78091386599993, 32.287543036000145), (-64.80305131802308, 32.27598332696125), (-64.81971736872748, 32.267456510321736), (-64.82901935051595, 32.266681345172785), (-64.83289517626119, 32.25970485883143), (-64.84684814894385, 32.25466628536269), (-64.85770046103045, 32.25466628536269), (-64.86428936479729, 32.26241793685297), (-64.86313074850327, 32.269007567025156), (-64.84878606181653, 32.2678440928964), (-64.84878606181653, 32.270944753492486), (-64.86700244281892, 32.27288266636508), (-64.87204101628768, 32.27637090953583), (-64.86980647402979, 32.27978479354091), (-64.86700244281892, 32.29109904736747), (-64.858088043605, 32.29768795113439), (-64.86428936479729, 32.303114107177734), (-64.86894035569148, 32.30892784579545), (-64.87242859886214, 32.303114107177734), (-64.87979266777805, 32.30543960262487), (-64.8745484041674, 32.29568128932401), (-64.87797690356822, 32.28607364910637), (-64.8766340454707, 32.2789117392533), (-64.88599398897043, 32.28257223072812), (-64.88289332837425, 32.27171991864155)]
        case5 = [(111.19758427000014, 1.0752326460001882), (110.9734119070001, 1.0177167760001566), (110.91057336500015, 1.015701396000111), (110.88039432900021, 1.010533753000118), (110.8526957610002, 0.9972012330000979), (110.79698856600007, 0.9496589150000716), (110.78706669100009, 0.9341559860001496), (110.78623986800002, 0.9162759400000198), (110.78396610600012, 0.9081627400001935), (110.77673140500016, 0.9032534790001563), (110.7712537030001, 0.9043903610000825), (110.7611251230002, 0.9128652960001631), (110.7583345950001, 0.9145189410000398), (110.74572554600016, 0.9080077110000673), (110.7447953700001, 0.9050621540001487), (110.72484826700006, 0.8972590130001379), (110.72071415200006, 0.8973623660000669), (110.70944869000019, 0.9013931270001478), (110.70417769400015, 0.9013931270001478), (110.6930155850001, 0.8946751920001361), (110.67441206900017, 0.8770018510000455), (110.66128625500019, 0.8721442670001096), (110.64774703000009, 0.8739012660001748), (110.63885868300011, 0.8807742310001458), (110.63214074800007, 0.8886290490001869), (110.62480269400007, 0.8931248980001101), (110.6134338790001, 0.8939517210000503), (110.60960982300006, 0.8908511360000944), (110.60599247300016, 0.8833063760001352), (110.59607059800007, 0.8711107380001266), (110.55390262900013, 0.8513703410000772)]

        for epsilon in (0.1, 0.01, 0.05):
            for case in (case1, case2, case3, case4, case5):
                py = compute_allowed_shortcuts_py(copy.deepcopy(case), epsilon)
                c = compute_allowed_shortcuts_c(copy.deepcopy(case), epsilon)
                self.assertEquals(py, c)


if __name__ == "__main__":
    unittest.main()
