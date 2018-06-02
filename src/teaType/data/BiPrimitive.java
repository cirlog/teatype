package teaType.data;

/**
 * The class {@code BiObject} is a very simple dual-primitive data-type.<br>
 * It's main & (only) intended use is the storing of two independent
 * {@code Object} values.
 * 
 * @since JDK 1.91 ~ <i>2018</i>
 * @author Burak Günaydin <b>{@code (arsonite)}</b>
 */
public class BiPrimitive {

	/** First given value is always the {@code final} one **/
	final Object f1, f2;

	/** Copied {@code non-final Object}-value **/
	private Object o1, o2;

	/** Stores the class of each primitive {@code final} value */
	final Class<?> fc1, fc2;

	/** Stores the class of each primitive value */
	private Class<?> c1, c2;

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
		fc1 = c1 = o1.getClass();
		fc2 = c2 = o2.getClass();
	}

	/**
	 * Typical setter-method to modify the first
	 * {@code non-final Object} value.
	 * 
	 * @param d1 The first {@code Object}-value
	 */
	public final void setFirst(Object o1) {
		this.o1 = o1;
		c1 = o1.getClass();
	}

	/**
	 * Typical setter-method to modify the second
	 * {@code non-final Object} value.
	 * 
	 * @param d2 The second {@code Object}-value
	 */
	public final void setSecond(Object o2) {
		this.o2 = o2;
		c2 = o2.getClass();
	}

	/**
	 * Typical getter-method to receive the first {@code Object} value.<br>
	 * 
	 * If the value was changed, the last {@code non-final} value
	 * is returned.
	 * 
	 * @return The first {@code Object} value
	 */
	public final Object getFirst() {
		return o1;
	}

	/**
	 * Typical getter-method to receive the second {@code Object} value.<br>
	 * 
	 * If the value was changed, the last {@code non-final} value
	 * is returned.
	 * 
	 * @return The second {@code Object} value
	 */
	public final Object getSecond() {
		return o2;
	}

	/**
	 * Prints the attributes of current {@code BiPrimitive} object.<br>
	 * Utilizes the {@link #toString()} method.
	 */
	public final void print() { System.out.println(this.toString() + "\n"); }

	/**
	 * Clears the variables of any values & either declares
	 * them <i>null</i> or <i>0</i>.
	 * @see {@link #empty()}
	 */
	public void clear() {
		try {
			o1 = o2 = null;
		} catch(Exception e) {
			if(c1 == boolean.class) {
				o1 = false;
				o2 = 0;
			} else if(c2 == boolean.class) {
				o1 = false;
				o2 = "";
			} else {
				o1 = o2 = 0;
			}
		}
	}

	/**
	 * Not only clears the variables of any value,
	 * but empties the values and its class declaration
	 * altogether.<br>
	 * Utilizes {@link #clear()}.
	 * 
	 * @see {@link #clear()}
	 */
	public void empty() {
		clear();
		c1 = c2 = null;
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
		StringBuilder sb = new StringBuilder();
		sb.append("BiPrimitive" + "\n-----------\n");
		if(c1 != null && fc1 != null) {
			sb.append("First (");
			if(o1 == f1) {
				sb.append(fc1.getSimpleName());
			} else {
				sb.append("(changed) " + c1.getSimpleName());
			}
			if(o1 != null && fc1 != null) {
				sb.append(") Primitive: " + o1.toString());
			}
		} else {
			sb.append("First Primitive is null");
		}
		return sb.toString();
	}
}