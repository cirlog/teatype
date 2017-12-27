package teaType.data.bi;

/**
 * The class {@code BiObject} is a very simple dual-primitive data-type.<br>
 * It's main and (only) intended use is the storing of two independent
 * {@code Object} values.
 * 
 * @since JDK 1.91 ~ <i>2017</i>
 * @author Burak Günaydin <b>{@code (arsonite)}</b>
 * @see teaType.data.bi.BiPrimitive
 * @see teaType.data.bi.BiDouble
 * @see teaType.data.bi.BiInteger
 * @see teaType.data.bi.BiString
 */
public class BiObject implements BiPrimitive {
	
	/**
	 * 
	 */
	private Object o1, o2;

	/**
	 * 
	 * 
	 * @param o1
	 * @param o2
	 */
	public BiObject(Object o1, Object o2) {
		setFirstObject(o1);
		setSecondObject(o2);
	}
	
	/**
	 * 
	 * @param o2
	 */
	public void setSecondObject(Object o2) { this.o2 = o2; }
	
	/**
	 * 
	 * @param o1
	 */
	public void setFirstObject(Object o1) { this.o1 = o1; }
	
	/**
	 * 
	 * @return
	 */
	public Object getFirstObject() { return o1; }
	
	/**
	 * 
	 * @return
	 */
	public Object getSecondObject() { return o2; }

	@Override
	public void clear() {
	}

	@Override
	public void random(int bound) {
	}
}