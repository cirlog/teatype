package teaType.data.bi;

/**
 * The class {@code BiInteger} is a very simple dual-primitive data-type.<br>
 * It's main & (only) intended use is the storing of two independent
 * {@code double} values.
 * 
 * @since JDK 1.91 ~ <i>2017</i>
 * @author Burak Günaydin <b>{@code (arsonite)}</b>
 * @see teaType.data.bi.BiPrimitive
 * @see teaType.data.bi.BiDouble
 * @see teaType.data.bi.BiObject
 * @see teaType.data.bi.BiString
 */
public class BiInteger implements BiPrimitive {

	/** First given value is always the {@code final} one **/
	final int f1, f2;

	/** Copied {@code non-final} double-value **/
	private int i1, i2;

	/**
	 * Simple constructor assigning both the
	 * {@code final} & {@code non-final} the same value
	 * 
	 * @param i1
	 * @param i2
	 */
	public BiInteger(int i1, int i2) {
		f1 = this.i1 = i1;
		f2 = this.i2 = i2;
	}

	/**
	 * Typical setter-method to modify the first
	 * {@code non-final} value.
	 * 
	 * @param i1
	 */
	public void setFirstInteger(int i1) { this.i1 = i1; }

	/**
	 * Typical setter-method to modify the second
	 * {@code non-final} value.
	 * 
	 * @param i2
	 */
	public void setSecondInteger(int i2) { this.i2 = i2; }

	/**
	 * 
	 * 
	 * @return
	 */
	public int getFirstInteger() { return i1; }

	/**
	 * 
	 * 
	 * @return
	 */
	public int getSecondInteger() { return i2; }

	@Override
	public void clear() {

	}

	@Override
	public void reset() {

	}

	@Override
	public void random(int bound) {

	}
}