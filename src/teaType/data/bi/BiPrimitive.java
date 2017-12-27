package teaType.data.bi;

/**
 * The interface {@code BiPrimitive} is a light-weight construct for 
 * simple dual-primitive data-types.
 * 
 * @since JDK 1.91 ~ <i>2017</i>
 * @author Burak Günaydin <b>{@code (arsonite)}</b>
 * @see teaType.data.bi.BiDouble
 * @see teaType.data.bi.BiInteger
 * @see teaType.data.bi.BiObject
 * @see teaType.data.bi.BiString
 */
public abstract interface BiPrimitive {
	
	/**
	 * Clears the variables of any values and either declares
	 * them <i>null</i> or <i>0</i>.
	 */
	public void clear();
	
	/**
	 * Randomizes values of the given {@code BiPrimitive}.<br>
	 * Length of values is limited by <i>bound</i>.
	 * 
	 * @param bound Limits the length of the generated value
	 */
	public void random(int bound);
}