from dataclasses import dataclass, field


@dataclass
class BallData:
    ballspeed: float = field(default=0.0)
    spinaxis: float = field(default=0.0)
    totalspin: float = field(default=0.0)
    backspin: float = field(default=0.0)
    sidespin: float = field(default=0.0)
    hla: float = field(default=0.0)
    vla: float = field(default=0.0)
    carry: float = field(default=0)


@dataclass
class ClubHeadData:
    speed: float = field(default=0.0)
    angleofattack: float = field(default=0.0)
    facetotarget: float = field(default=0.0)
    lie: float = field(default=0.0)
    loft: float = field(default=0.0)
    path: float = field(default=0.0)
    speedatimpact: float = field(default=0.0)
    verticalfaceimpact: float = field(default=0)
    horizontalfaceimpact: float = field(default=0)
    closurerate: float = field(default=0)
