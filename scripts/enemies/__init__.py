from .one_alpha import OneAlpha
from .one_beta import OneBeta

from .two_alpha import TwoAlpha
from .two_beta import TwoBeta

from .three_alpha import ThreeAlpha
from .three_beta import ThreeBeta

from .four_alpha import FourAlpha
from .four_beta import FourBeta

from .five_omega import FiveOmega

ALL_ENEMY_TYPE = (OneAlpha, TwoAlpha, ThreeAlpha, FourAlpha, OneBeta, TwoBeta, ThreeBeta, FourBeta, FiveOmega)

SCORE_UP_MAP = {
    OneAlpha : 1000,
    OneBeta : 1500,
    TwoAlpha : 2000,
    TwoBeta : 2500,
    ThreeAlpha : 3000,
    ThreeBeta : 3500,
    FourAlpha : 4000,
    FourBeta : 4500,
    FiveOmega : 666666
}