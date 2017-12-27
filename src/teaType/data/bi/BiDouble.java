package teaType.data.bi;

/**
 * The class {@code BiDouble} is a very simple dual-primitive data-type.<br>
 * It's main and (only) intended use is the storing of two independent
 * {@code double} values.
 * 
 * @since JDK 1.91 ~ <i>2017</i>
 * @author Burak Günaydin <b>{@code (arsonite)}</b>
 * @see teaType.data.bi.BiPrimitive
 * @see teaType.data.bi.BiInteger
 * @see teaType.data.bi.BiObject
 * @see teaType.data.bi.BiString
 */
public class BiDouble implements BiPrimitive {
	
	/** First given value is always the {@code final} one **/
	final double f1, f2;

	/** {@code Non-final} double-value **/
	private double d1, d2;

	/**
	 * Simple constructor 
	 * 
	 * @param d1
	 * @param d2
	 */
	public BiDouble(double d1, double d2) {
		f1 = this.d1 = d1;
		f2 = this.d2 = d2;
	}

	/**
	 * Typical setter-method to modify the first value.
	 * 
	 * @param d1
	 */
	public void setFirstDouble(double d1) { this.d1 = d1; }

	/**
	 * Typical setter-method to modify the first value.
	 * 
	 * @param d2
	 */
	public void setSecondDouble(double d2) { this.d2 = d2; }

	/**
	 * Typical getter-method to get the first value.<br>
	 * If the value was changed, the last {@code non-final} value
	 * is returned.
	 * 
	 * @return First double-value
	 */
	public double getFirstDouble() {
		if(f1 != d1) {
			return d1;	
		}
		return f1;
	}

	/**
	 * Typical getter-method to get the second value.
	 * 
	 * If the value was changed, the last {@code non-final} value
	 * is returned.
	 * @return
	 */
	public double getSecondDouble() {
		if(f2 != d2) {
			return d2;	
		}
		return f2;
	}

	@Override
	public void clear() { d1 = d2 = 0; }
	
	@Override
	public void reset() {
		d1 = f1;
		d2 = f2;
	}

	@Override
	public void random(int bound) {
		
	}
}