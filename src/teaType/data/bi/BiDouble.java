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
public class BiDouble {
	
	/**
	 * 
	 */
	private double d1, d2;

	/**
	 * 
	 * 
	 * @param d1
	 * @param d2
	 */
	public BiDouble(double d1, double d2) {
		setFirstDouble(d1);
		setSecondDouble(d2);
	}
	
	/**
	 * 
	 * 
	 * @param d1
	 */
	public void setFirstDouble(double d1) { this.d1 = d1; }
	
	/**
	 * 
	 * 
	 * @param d2
	 */
	public void setSecondDouble(double d2) { this.d2 = d2; }

	/**
	 * 
	 * 
	 * @return
	 */
	public double getFirstDouble() { return d1; }
	
	/**
	 * 
	 * 
	 * @return
	 */
	public double getSecondDouble() { return d2; }
}