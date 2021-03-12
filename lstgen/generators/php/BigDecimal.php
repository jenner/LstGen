use Brick\Math\BigDecimal as BaseBigDecimal;
use Brick\Math\RoundingMode as RoundingMode;

/**
 * A proxy class to use BigDecimal methods
 * as they are found in PAP XML.
 * Requires brick/math >= 0.6.0
 */
class BigDecimal {

    const ROUND_DOWN = RoundingMode::DOWN;
    const ROUND_UP = RoundingMode::UP;

    private $bd;

    public function __construct($value) {
        $this->bd = BaseBigDecimal::of($value);
    }

    public function divide($other, $scale=null, $rounding=null) {
        if (!$scale && !$rounding) {
            return new BigDecimal($this->bd->exactlyDividedBy($other));
        }
        return new BigDecimal($this->bd->dividedBy($other, $scale, $rounding));
    }

    public static function valueOf($value) {
        return new BigDecimal($value);
    }

    public function multiply($other) {
        return new BigDecimal($this->bd->multipliedBy($other));
    }

    public function setScale($scale, $rounding) {
        return new BigDecimal($this->bd->toScale($scale, $rounding));
    }

    public function add($other) {
        return new BigDecimal($this->bd->plus($other));
    }

    public function subtract($other) {
        return new BigDecimal($this->bd->minus($other));
    }

    public function longValue() {
        return $this->bd->toInt();
    }

    public function floatValue() {
        return $this->bd->toFloat();
    }

    public function compareTo($other) {
        return $this->bd->compareTo($other);
    }

    public function __toString() {
        return $this->bd->__toString();
    }

    public static function zero() {
        return BigDecimal::valueOf(0);
    }

    public static function one() {
        return BigDecimal::valueOf(1);
    }

    public static function ten() {
        return BigDecimal::valueOf(10);
    }

}
