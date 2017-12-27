package teaType.data.bi;

/**
 * The class {@code BiInteger} is a very simple dual-primitive data-type.<br>
 * It's main and (only) intended use is the storing of two independent
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

	/**
	 * 
	 */
	private int i1, i2;

	/**
	 * 
	 * 
	 * @param i1
	 * @param i2
	 */
	public BiInteger(int i1, int i2) {
		setFirstInteger(i1);
		setSecondInteger(i2);
	}

	/**
	 * 
	 * 
	 * @param i1
	 */
	public void setFirstInteger(int i1) { this.i1 = i1; }

	/**
	 * 
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