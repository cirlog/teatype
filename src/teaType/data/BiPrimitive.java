package teaType.data;

/**
 * The class {@code BiObject} is a very simple dual-primitive data-type.<br>
 * It's main & (only) intended use is the storing of two independent
 * {@code Object} values.
 * 
 * @since JDK 1.91 ~ <i>2017</i>
 * @author Burak Günaydin <b>{@code (arsonite)}</b>
 * @see teaType.data.bi.BiPrimitive
 * @see teaType.data.bi.BiDouble
 * @see teaType.data.bi.BiInteger
 * @see teaType.data.bi.BiString
 */
public class BiPrimitive {

	/** First given value is always the {@code final} one **/
	final Object f1, f2;

	/** Copied {@code non-final Object}-value **/
	private Object o1, o2;

	/** Stores the class of each primitive value */
	final Class<?> c1, c2;

	/**
	 * Simple constructor assigning both the
	 * {@code final} & {@code non-final} the same value
	 * 
	 * @param o1 The first {@code Object}-value
	 * @param o2 The second {@code Object}-value
	 */
	public BiPrimitive(Object o1, Object o2) {
		f1 = this.o1 = o1;
		f2 = this.o2 = o2;
		c1 = o1.getClass();
		c2 = o2.getClass();
	}

	/**
	 * Typical setter-method to modify the first
	 * {@code non-final Object} value.
	 * 
	 * @param d1 The first {@code Object}-value
	 */
	public final void setFirstPrimitive(Object o1) { this.o1 = o1; }

	/**
	 * Typical setter-method to modify the second
	 * {@code non-final Object} value.
	 * 
	 * @param d2 The second {@code Object}-value
	 */
	public final void setSecondPrimitive(Object o2) { this.o2 = o2; }

	/**
	 * Typical getter-method to receive the first {@code Object} value.<br>
	 * 
	 * If the value was changed, the last {@code non-final} value
	 * is returned.
	 * 
	 * @return The first {@code Object} value
	 */
	public final Object getFirstPrimitive() { return o1; }

	/**
	 * Typical getter-method to receive the second {@code Object} value.<br>
	 * 
	 * If the value was changed, the last {@code non-final} value
	 * is returned.
	 * 
	 * @return The second {@code Object} value
	 */
	public final Object getSecondPrimitive() { return o2; }

	public final void print() {

	}

	/**
	 * Clears the variables of any values & either declares
	 * them <i>null</i> or <i>0</i>.
	 */
	public void clear() {
		Class<?> s, i, I, d, D, f, F, sh, Sh, b, B, bo, Bo;
		s = String.class;
		i = int.class;
		I = Integer.class;
		d = double.class;
		D = Double.class;
		f = float.class;
		F = Float.class;
		sh = short.class;
		Sh = Short.class;
		b = byte.class;
		B = Byte.class;
		bo = boolean.class;
		Bo = Boolean.class;
		if(c1 == s) { o1 = ""; }
		else if(c2 == s) { o2 = ""; }
		else if(c1 == i || c2 == I) { o1 = 0; }
		else if(c2 == i || c2 == I) { o2 = 0; }
		else if(c1 == d || c1 == D) { o1 = 0.0; }
		else if(c2 == d || c2 == D) { o2 = 0.0; }
		else if(c1 == f || c1 == F) { o1 = 0.0; }
		else if(c2 == f || c2 == F) { o2 = 0.0; }
		else if(c1 == sh || c1 == Sh) { o1 = 0; }
		else if(c2 == sh || c2 == Sh) { o2 = 0; }
		else if(c1 != s &&
				c1 != i && c1 != I
				) { o1 = null; }
		else if(c2 != s &&
				c2 != i
				) { o2 = null; }
	}

	/**
	 * Resets the {@code non-final} variable to the first declared
	 * {@code final} value.
	 */
	public void reset() {
		o1 = f1;
		o2 = f2;
	}

	/**
	 * Shuffles both values.<br>
	 * Since the first determined values are {@code final},
	 * shuffling them is impossible.
	 */
	public void shuffle() {
		Object temp = o1;
		o1 = o2;
		o2 = temp;
	}

	/**
	 * Randomizes values of the given {@code BiPrimitive}.<br>
	 * Length of values is limited by <i>bound</i>.
	 * 
	 * @param bound Limits the length of the generated value
	 */
	public void random(int bound) {

	}

	public final String toString() {
		return "";
	}
}