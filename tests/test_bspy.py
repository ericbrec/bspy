import numpy as np
import pytest
import bspy

myCurve = bspy.Spline(1, 2, [4], [5], [[0,0,0,0,0.3,1,1,1,1]], [[0, 0], [0.3, 1],
                    [0.5, 0.0], [0.7, -0.5], [1, 1]])
truth = \
[[0.000000000000000000e+00, 0.000000000000000000e+00, 0.000000000000000000e+00],
 [1.000000000000000021e-02, 2.920888888888888840e-02, 9.571648148148148572e-02],
 [2.000000000000000042e-02, 5.687111111111110839e-02, 1.830651851851851641e-01],
 [2.999999999999999889e-02, 8.303999999999998882e-02, 2.623449999999999949e-01],
 [4.000000000000000083e-02, 1.077688888888889002e-01, 3.338548148148148820e-01],
 [5.000000000000000278e-02, 1.311111111111110950e-01, 3.978935185185185630e-01],
 [5.999999999999999778e-02, 1.531200000000000339e-01, 4.547600000000000531e-01],
 [7.000000000000000666e-02, 1.738488888888889139e-01, 5.047531481481482007e-01],
 [8.000000000000000167e-02, 1.933511111111111402e-01, 5.481718518518519101e-01],
 [8.999999999999999667e-02, 2.116800000000000070e-01, 5.853150000000000297e-01],
 [1.000000000000000056e-01, 2.288888888888888917e-01, 6.164814814814815191e-01],
 [1.100000000000000006e-01, 2.450311111111111440e-01, 6.419701851851852270e-01],
 [1.199999999999999956e-01, 2.601600000000000024e-01, 6.620800000000001129e-01],
 [1.300000000000000044e-01, 2.743288888888888999e-01, 6.771098148148148033e-01],
 [1.400000000000000133e-01, 2.875911111111111307e-01, 6.873585185185184798e-01],
 [1.499999999999999944e-01, 2.999999999999999889e-01, 6.931249999999999911e-01],
 [1.600000000000000033e-01, 3.116088888888888242e-01, 6.947081481481480747e-01],
 [1.700000000000000122e-01, 3.224711111111110973e-01, 6.924068518518518012e-01],
 [1.799999999999999933e-01, 3.326399999999999912e-01, 6.865200000000000191e-01],
 [1.900000000000000022e-01, 3.421688888888889113e-01, 6.773464814814815771e-01],
 [2.000000000000000111e-01, 3.511111111111111516e-01, 6.651851851851853237e-01],
 [2.099999999999999922e-01, 3.595199999999999507e-01, 6.503349999999999964e-01],
 [2.200000000000000011e-01, 3.674488888888888805e-01, 6.330948148148147769e-01],
 [2.300000000000000100e-01, 3.749511111111111239e-01, 6.137635185185186248e-01],
 [2.399999999999999911e-01, 3.820800000000000307e-01, 5.926400000000000556e-01],
 [2.500000000000000000e-01, 3.888888888888888395e-01, 5.700231481481481399e-01],
 [2.600000000000000089e-01, 3.954311111111110666e-01, 5.462118518518517263e-01],
 [2.700000000000000178e-01, 4.017599999999999505e-01, 5.215049999999998853e-01],
 [2.800000000000000266e-01, 4.079288888888888964e-01, 4.962014814814813546e-01],
 [2.899999999999999800e-01, 4.139911111111110875e-01, 4.706001851851852602e-01],
 [2.999999999999999889e-01, 4.199999999999999845e-01, 4.449999999999999512e-01],
 [3.099999999999999978e-01, 4.260004664723031631e-01, 4.196546793002914888e-01],
 [3.200000000000000067e-01, 4.320037317784256592e-01, 3.946374344023322323e-01],
 [3.300000000000000155e-01, 4.380125947521865681e-01, 3.699763411078715869e-01],
 [3.400000000000000244e-01, 4.440298542274052629e-01, 3.456994752186587916e-01],
 [3.500000000000000333e-01, 4.500583090379008944e-01, 3.218349125364429741e-01],
 [3.599999999999999867e-01, 4.561007580174927245e-01, 2.984107288629737620e-01],
 [3.699999999999999956e-01, 4.621600000000000152e-01, 2.754550000000000054e-01],
 [3.800000000000000044e-01, 4.682388338192420285e-01, 2.529958017492711653e-01],
 [3.900000000000000133e-01, 4.743400583090378597e-01, 2.310612099125364527e-01],
 [4.000000000000000222e-01, 4.804664723032070484e-01, 2.096793002915451620e-01],
 [4.100000000000000311e-01, 4.866208746355684678e-01, 1.888781486880466154e-01],
 [4.199999999999999845e-01, 4.928060641399416020e-01, 1.686858309037901626e-01],
 [4.299999999999999933e-01, 4.990248396501458239e-01, 1.491304227405248206e-01],
 [4.400000000000000022e-01, 5.052800000000000624e-01, 1.302400000000000502e-01],
 [4.500000000000000111e-01, 5.115743440233236905e-01, 1.120426384839650347e-01],
 [4.600000000000000200e-01, 5.179106705539359146e-01, 9.456641399416906846e-02],
 [4.700000000000000289e-01, 5.242917784256559965e-01, 7.783940233236148754e-02],
 [4.799999999999999822e-01, 5.307204664723031984e-01, 6.188967930029153769e-02],
 [4.899999999999999911e-01, 5.371995335276968930e-01, 4.674532069970845083e-02],
 [5.000000000000000000e-01, 5.437317784256558983e-01, 3.243440233236150050e-02],
 [5.100000000000000089e-01, 5.503199999999999203e-01, 1.898499999999998800e-02],
 [5.200000000000000178e-01, 5.569669970845482210e-01, 6.425189504373148702e-03],
 [5.300000000000000266e-01, 5.636755685131195071e-01, -5.216953352769719554e-03],
 [5.400000000000000355e-01, 5.704485131195334846e-01, -1.591335276967931200e-02],
 [5.500000000000000444e-01, 5.772886297376094156e-01, -2.563593294460646960e-02],
 [5.600000000000000533e-01, 5.841987172011662288e-01, -3.435661807580180777e-02],
 [5.700000000000000622e-01, 5.911815743440234083e-01, -4.204733236151610848e-02],
 [5.799999999999999600e-01, 5.982399999999999940e-01, -4.867999999999997329e-02],
 [5.899999999999999689e-01, 6.053767930029154698e-01, -5.422654518950437152e-02],
 [5.999999999999999778e-01, 6.125947521865888756e-01, -5.865889212827987698e-02],
 [6.099999999999999867e-01, 6.198966763848395845e-01, -6.194896501457720916e-02],
 [6.199999999999999956e-01, 6.272853644314867472e-01, -6.406868804664718475e-02],
 [6.300000000000000044e-01, 6.347636151603498478e-01, -6.498998542274049550e-02],
 [6.400000000000000133e-01, 6.423342274052477041e-01, -6.468478134110783317e-02],
 [6.500000000000000222e-01, 6.500000000000001332e-01, -6.312499999999995892e-02],
 [6.600000000000000311e-01, 6.577637317784257309e-01, -6.028256559766762002e-02],
 [6.700000000000000400e-01, 6.656282215743440922e-01, -5.612940233236143883e-02],
 [6.800000000000000488e-01, 6.735962682215743680e-01, -5.063743440233228754e-02],
 [6.900000000000000577e-01, 6.816706705539359312e-01, -4.377858600583078852e-02],
 [7.000000000000000666e-01, 6.898542274052479328e-01, -3.552478134110773067e-02],
 [7.099999999999999645e-01, 6.981497376093294127e-01, -2.584794460641390290e-02],
 [7.199999999999999734e-01, 7.065599999999999659e-01, -1.471999999999998310e-02],
 [7.299999999999999822e-01, 7.150878134110787432e-01, -2.112871720116565877e-03],
 [7.399999999999999911e-01, 7.237359766763848956e-01, 1.200151603498558761e-02],
 [7.500000000000000000e-01, 7.325072886297376851e-01, 2.765123906705549417e-02],
 [7.600000000000000089e-01, 7.414045481049563735e-01, 4.486437317784272572e-02],
 [7.700000000000000178e-01, 7.504305539358600008e-01, 6.366899416909629905e-02],
 [7.800000000000000266e-01, 7.595881049562682730e-01, 8.409317784256584161e-02],
 [7.900000000000000355e-01, 7.688800000000000079e-01, 1.061650000000000926e-01],
 [8.000000000000000444e-01, 7.783090379008745785e-01, 1.299125364431487351e-01],
 [8.100000000000000533e-01, 7.878780174927114688e-01, 1.553638629737610910e-01],
 [8.200000000000000622e-01, 7.975897376093294966e-01, 1.825470553935860940e-01],
 [8.300000000000000711e-01, 8.074469970845481459e-01, 2.114901895043733160e-01],
 [8.399999999999999689e-01, 8.174525947521866787e-01, 2.422213411078720791e-01],
 [8.499999999999999778e-01, 8.276093294460642458e-01, 2.747685860058312057e-01],
 [8.599999999999999867e-01, 8.379199999999999982e-01, 3.091600000000003234e-01],
 [8.699999999999999956e-01, 8.483874052478134198e-01, 3.454236588921285600e-01],
 [8.800000000000000044e-01, 8.590143440233236616e-01, 3.835876384839654318e-01],
 [8.900000000000000133e-01, 8.698036151603498745e-01, 4.236800145772597892e-01],
 [9.000000000000000222e-01, 8.807580174927114314e-01, 4.657288629737614816e-01],
 [9.100000000000000311e-01, 8.918803498542275943e-01, 5.097622594752194702e-01],
 [9.200000000000000400e-01, 9.031734110787172920e-01, 5.558082798833825500e-01],
 [9.300000000000000488e-01, 9.146400000000001196e-01, 6.038950000000007368e-01],
 [9.400000000000000577e-01, 9.262829154518952279e-01, 6.540504956268228254e-01],
 [9.500000000000000666e-01, 9.381049562682217680e-01, 7.063028425655986098e-01],
 [9.599999999999999645e-01, 9.501089212827988906e-01, 7.606801166180757745e-01],
 [9.699999999999999734e-01, 9.622976093294459687e-01, 8.172103935860055568e-01],
 [9.799999999999999822e-01, 9.746738192419825975e-01, 8.759217492711370845e-01],
 [9.899999999999999911e-01, 9.872403498542273725e-01, 9.368422594752183752e-01],
 [1.000000000000000000e+00, 1.000000000000000000e+00, 1.000000000000000000e+00]]

def test_add():
    maxerror = 0.0
    spline1 = bspy.Spline(1, 2, (5,), (5,), [np.array([0, 0, 0, 0, 0.3, 0.5, 0.5, 1, 1, 1], float)], 
        np.array(((260, 100), (100, 260), (260, 420), (580, 260), (420, 100)), float))
    spline2 = bspy.Spline(1, 2, (4,), (6,), [np.array([0, 0, 0, 0, 0.5, 0.5, 1, 1, 1, 1], float)], 
        np.array(((260, 100), (100, 260), (260, 420), (420, 420), (580, 260), (420, 100)), float))
    
    # Add with shared independent variable.
    added = spline1.add(spline2, [[0, 0]])
    maxerror = 0.0
    for u in np.linspace(spline1.knots[0][spline1.order[0]-1], spline1.knots[0][spline1.nCoef[0]], 100):
        [x, y] = spline1.evaluate([u]) + spline2.evaluate([u])
        [xTest, yTest] = added.evaluate([u])
        maxerror = max(maxerror, (xTest - x) ** 2 + (yTest - y) ** 2)
    assert maxerror <= np.finfo(float).eps

    # Add with completely independent variables.
    added = spline1 + spline2
    maxerror = 0.0
    for u in np.linspace(spline1.knots[0][spline1.order[0]-1], spline1.knots[0][spline1.nCoef[0]], 100):
        for v in np.linspace(spline2.knots[0][spline2.order[0]-1], spline2.knots[0][spline2.nCoef[0]], 100):
            [x, y] = spline1.evaluate([u]) + spline2.evaluate([v])
            [xTest, yTest] = added.evaluate([u,v])
            maxerror = max(maxerror, (xTest - x) ** 2 + (yTest - y) ** 2)
    assert maxerror <= np.finfo(float).eps

def test_derivatives():
    maxerror = 0.0
    myDerivative = myCurve.differentiate()
    for [u, x, y] in truth:
        [xTest, yTest] = myCurve.derivative([1], [u])
        [x, y] = myDerivative.evaluate([u])
        maxerror = max(maxerror, (xTest - x) ** 2 + (yTest - y) ** 2)
    assert maxerror <= np.finfo(float).eps

def test_dot():
    maxerror = 0.0
    dottedCurve = myCurve.dot([2.0, 3.0])
    for [u, x, y] in truth:
        valueTest = dottedCurve.evaluate([u])
        maxerror = max(maxerror, (valueTest - 2.0 * x - 3.0 * y) ** 2)
    assert maxerror <= np.finfo(float).eps

def test_elevate():
    maxerror = 0.0
    original = bspy.Spline(1, 2, (4,), (6,), [np.array([0, 0, 0, 0, 0.5, 0.5, 1, 1, 1, 1], float)], 
        np.array(((260, 100), (100, 260), (260, 420), (420, 420), (580, 260), (420, 100)), float))
    elevated = original.elevate((1,))
    maxerror = 0.0
    for u in np.linspace(original.knots[0][original.order[0]-1], original.knots[0][original.nCoef[0]], 100):
        [x, y] = original.evaluate([u])
        [xTest, yTest] = elevated.evaluate([u])
        maxerror = max(maxerror, (xTest - x) ** 2 + (yTest - y) ** 2)
    assert maxerror <= np.finfo(float).eps

def test_elevate_and_insert_knots():
    maxerror = 0.0
    original = bspy.Spline(1, 2, (4,), (6,), [np.array([0, 0, 0, 0, 0.5, 0.5, 1, 1, 1, 1], float)], 
        np.array(((260, 100), (100, 260), (260, 420), (420, 420), (580, 260), (420, 100)), float))
    elevated = original.elevate_and_insert_knots((1,), ((.5,.3, .6, .6),))
    maxerror = 0.0
    for u in np.linspace(original.knots[0][original.order[0]-1], original.knots[0][original.nCoef[0]], 100):
        [x, y] = original.evaluate([u])
        [xTest, yTest] = elevated.evaluate([u])
        maxerror = max(maxerror, (xTest - x) ** 2 + (yTest - y) ** 2)
    assert maxerror <= np.finfo(float).eps

def test_evaluate():
    maxerror = 0.0
    for [u, x, y] in truth:
        [xTest, yTest] = myCurve.evaluate([u])
        maxerror = max(maxerror, np.sqrt((xTest - x) ** 2 + (yTest - y) ** 2))
    assert maxerror <= np.finfo(float).eps

def test_find_roots():
    def check_roots(expectedRoots, roots, tolerance):
        assert len(expectedRoots) == len(roots)
        for (expectedRoot, root) in zip(expectedRoots, roots):
            assert abs(expectedRoot - root) < tolerance

    tolerance = 1.0e-6

    spline = bspy.Spline(1, 1, (4,), (4,), ((0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0),), ((1.0, -2.0, -2.0, 1.0),))
    expectedRoots = (0.127322, 0.872678)
    roots = spline.find_roots(tolerance)
    check_roots(expectedRoots, roots, tolerance)

    spline = bspy.Spline(1, 1, (4,), (5,), ((0.0, 0.0, 0.0, 0.0, 1.0, 2.0, 2.0, 2.0, 2.0),), ((1.0, -2.0, -2.0, 3.0, -1.0),))
    expectedRoots = (0.126791, 1.179700, 1.901525)
    roots = spline.find_roots(tolerance)
    check_roots(expectedRoots, roots, tolerance)

    spline = bspy.Spline(1, 1, (4,), (10,), ((0.0, 0.0, 0.0, 0.0, 1.0, 3.0, 4.0, 7.0, 7.0, 8.0, 10.0, 10.0, 10.0, 10.0),), ((1.0, -2.0, -3.0, -4.0, 5.0, 6.0, 7.0, -8.0, -9.0, 1.0),))
    expectedRoots = (0.124277, 3.556169, 7.866681, 9.930791)
    roots = spline.find_roots(tolerance)
    check_roots(expectedRoots, roots, tolerance)

    spline = bspy.Spline(1, 1, (5,), (7,), ((0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 2.0, 4.0, 4.0, 4.0, 4.0, 4.0),), ((1.0, -2.0, -3.0, 4.0, 5.0, -6.0, 1.0),))
    expectedRoots = (0.094002, 1.201821, 3.019268, 3.918820)
    roots = spline.find_roots(tolerance)
    check_roots(expectedRoots, roots, tolerance)

    spline = bspy.Spline(1, 1, (6,), (11,), ((0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 2.0, 2.0, 2.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0),), ((2.0, -1.0, -1.0, -1.0, 1.0, 2.0, 2.0, -3.0, -3.0, 4.0, 1.0),))
    expectedRoots = (0.197807, 0.959259, 2.368276, 3.336228)
    roots = spline.find_roots(tolerance)
    check_roots(expectedRoots, roots, tolerance)

    spline = bspy.Spline(1, 1, (4,), (4,), ((0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0),), ((1.0, -13.0 / 9.0, 25.0 / 12.0, -3.0),))
    expectedRoots = (0.400000,)
    roots = spline.find_roots(tolerance)
    #check_roots(expectedRoots, roots, tolerance)

def test_fold_unfold():
    nInd = 3
    nDep = 3
    order = (2, 3, 4)
    nCoef = (4, 5, 6)
    knots = [np.linspace(0.0, 1.0, order[k] + nCoef[k]) for k in range(nInd)]
    coefs = np.empty((nDep, *nCoef))
    for i in range(coefs.shape[0]):
        for j in range(coefs.shape[1]):
            for k in range(coefs.shape[2]):
                for l in range(coefs.shape[3]):
                    coefs[i,j,k,l] = i + 0.1*j + 0.01*k + 0.001*l
    spline = bspy.Spline(nInd, nDep, order, nCoef, knots, coefs)
    
    folded, coefficientless = spline.fold([0, 2])

    assert folded.nInd == 1
    assert folded.nDep == 72
    assert folded.order == (3,)
    assert folded.nCoef == (5,)
    assert (folded.knots[0] == spline.knots[1]).all()
    assert folded.coefs.shape == (72, 5)

    assert coefficientless.nInd == 2
    assert coefficientless.nDep == 0
    assert coefficientless.order == (2, 4)
    assert coefficientless.nCoef == (4, 6)
    assert (coefficientless.knots[0] == spline.knots[0]).all()
    assert (coefficientless.knots[1] == spline.knots[2]).all()

    unfolded = folded.unfold([0, 2], coefficientless)

    assert unfolded.nInd == spline.nInd
    assert unfolded.nDep == spline.nDep
    assert unfolded.order == spline.order
    assert unfolded.nCoef == spline.nCoef
    assert (unfolded.knots[0] == spline.knots[0]).all()
    assert (unfolded.knots[1] == spline.knots[1]).all()
    assert (unfolded.knots[2] == spline.knots[2]).all()
    assert unfolded.coefs.shape == spline.coefs.shape

    maxerror = 0.0
    for i in range(coefs.shape[0]):
        for j in range(coefs.shape[1]):
            for k in range(coefs.shape[2]):
                for l in range(coefs.shape[3]):
                    maxerror = max(maxerror, abs(unfolded.coefs[i, j, k, l] - spline.coefs[i, j, k, l]))
    assert maxerror <= np.finfo(float).eps

def test_insert_knots():
    maxerror = 0.0
    newCurve = myCurve.insert_knots([[.2, .3]])
    for [u, x, y] in truth:
        [xTest, yTest] = newCurve.evaluate([u])
        maxerror = max(maxerror, (xTest - x) ** 2 + (yTest - y) ** 2)
    assert maxerror <= np.finfo(float).eps

def test_reparametrize():
    maxerror = 0.0
    reparametrized = myCurve.reparametrize([[1.5, 2.0]])
    for [u, x, y] in truth:
        [xTest, yTest] = reparametrized.evaluate([u * 0.5 + 1.5])
        maxerror = max(maxerror, (xTest - x) ** 2 + (yTest - y) ** 2)
    assert maxerror <= np.finfo(float).eps

def test_scale():
    maxerror = 0.0
    scaledCurve = myCurve.scale([2.0, 3.0])
    for [u, x, y] in truth:
        [xTest, yTest] = scaledCurve.evaluate([u])
        maxerror = max(maxerror, (xTest - 2.0 * x) ** 2 + (yTest - 3.0 * y) ** 2)
    assert maxerror <= np.finfo(float).eps

    maxerror = 0.0
    scaledCurve = 3.0 * myCurve
    for [u, x, y] in truth:
        [xTest, yTest] = scaledCurve.evaluate([u])
        maxerror = max(maxerror, (xTest - 3.0 * x) ** 2 + (yTest - 3.0 * y) ** 2)
    assert maxerror <= np.finfo(float).eps

def test_subtract():
    maxerror = 0.0
    spline1 = bspy.Spline(1, 2, (5,), (5,), [np.array([0, 0, 0, 0, 0.3, 0.5, 0.5, 1, 1, 1], float)], 
        np.array(((260, 100), (100, 260), (260, 420), (580, 260), (420, 100)), float))
    spline2 = bspy.Spline(1, 2, (4,), (6,), [np.array([0, 0, 0, 0, 0.5, 0.5, 1, 1, 1, 1], float)], 
        np.array(((260, 100), (100, 260), (260, 420), (420, 420), (580, 260), (420, 100)), float))
    
    # Subtract with shared independent variable.
    subtracted = spline1.subtract(spline2, [[0, 0]])
    maxerror = 0.0
    for u in np.linspace(spline1.knots[0][spline1.order[0]-1], spline1.knots[0][spline1.nCoef[0]], 100):
        [x, y] = spline1.evaluate([u]) - spline2.evaluate([u])
        [xTest, yTest] = subtracted.evaluate([u])
        maxerror = max(maxerror, (xTest - x) ** 2 + (yTest - y) ** 2)
    assert maxerror <= np.finfo(float).eps

    # Subtract with completely independent variables.
    subtracted = spline1 - spline2
    maxerror = 0.0
    for u in np.linspace(spline1.knots[0][spline1.order[0]-1], spline1.knots[0][spline1.nCoef[0]], 100):
        for v in np.linspace(spline2.knots[0][spline2.order[0]-1], spline2.knots[0][spline2.nCoef[0]], 100):
            [x, y] = spline1.evaluate([u]) - spline2.evaluate([v])
            [xTest, yTest] = subtracted.evaluate([u,v])
            maxerror = max(maxerror, (xTest - x) ** 2 + (yTest - y) ** 2)
    assert maxerror <= np.finfo(float).eps

def test_transform():
    maxerror = 0.0
    transformedCurve = myCurve.transform(np.array([[2.0, 3.0], [-1.0, -4.0]]))
    for [u, x, y] in truth:
        [xTest, yTest] = transformedCurve.evaluate([u])
        maxerror = max(maxerror, (xTest - (2.0 * x + 3.0 * y)) ** 2 + (yTest - (-1.0 * x - 4.0 * y)) ** 2)
    assert maxerror <= np.finfo(float).eps

def test_translate():
    maxerror = 0.0
    translatedCurve = myCurve.translate([2.0, 3.0])
    for [u, x, y] in truth:
        [xTest, yTest] = translatedCurve.evaluate([u])
        maxerror = max(maxerror, (xTest - (2.0 + x)) ** 2 + (yTest - (3.0 + y)) ** 2)
    assert maxerror <= np.finfo(float).eps

def test_trim():
    maxerror = 0.0
    left = 13
    right = 89
    trimmed = myCurve.trim([[truth[left][0], truth[right][0]]])
    for [u, x, y] in truth[left:right+1]:
        [xTest, yTest] = trimmed.evaluate([u])
        maxerror = max(maxerror, (xTest - x) ** 2 + (yTest - y) ** 2)
    assert maxerror <= np.finfo(float).eps
