import "math"

const (
	ROUND_DOWN = 1
	ROUND_UP   = 2
)

type BigDecimal struct {
	V float64
}

func (d BigDecimal) Float64() float64 {
	return d.V
}

func (d BigDecimal) Divide(other BigDecimal, roundParams ...int) BigDecimal {
	scale := 0
	rounding := 0
	if len(roundParams) == 2 {
		scale = roundParams[0]
		rounding = roundParams[1]
	} else {
		return BigDecimal{d.V / other.V}
	}

	return BigDecimal{d.V / other.V}.SetScale(scale, rounding)
}

func (d BigDecimal) ValueOf(value float64) BigDecimal {
	return BigDecimal{value}
}

func (d BigDecimal) Multiply(other BigDecimal) BigDecimal {
	return BigDecimal{d.V * other.V}
}

func (d BigDecimal) Add(other BigDecimal) BigDecimal {
	return BigDecimal{d.V + other.V}
}

func (d BigDecimal) Subtract(other BigDecimal) BigDecimal {
	return BigDecimal{d.V - other.V}
}

func (d BigDecimal) IntPart() int64 {
	i, _ := math.Modf(d.V)
	return int64(i)
}

func (d BigDecimal) CompareTo(other BigDecimal) int {
	if d.V > other.V {
		return 1
	} else if d.V < other.V {
		return -1
	}
	return 0
}

func (d BigDecimal) SetScale(scale int, rounding int) BigDecimal {
	exp := math.Pow(10, float64(scale))

	var v float64
	if rounding == ROUND_DOWN {
		if d.V < 0 {
			v = math.Ceil(d.V * exp)
		} else {
			v = math.Floor(d.V * exp)
		}
	} else if rounding == ROUND_UP {
		if d.V < 0 {
			v = math.Floor(d.V * exp)
		} else {
			v = math.Ceil(d.V * exp)
		}
	} else {
		v = math.Round(d.V * exp)
	}
	v = v / exp
	return BigDecimal{v}
}

func NewFromInt(value int64) BigDecimal {
	return BigDecimal{float64(value)}
}

func NewFromFloat(value float64) BigDecimal {
	return BigDecimal{value}
}
