package teaType.data.bi;

/**
 * The class {@code BiString} is a very simple dual-primitive data-type.<br>
 * It's main and (only) intended use is the storing of two independent
 * {@code String} values.
 * 
 * @since JDK 1.91 ~ <i>2017</i>
 * @author Burak Günaydin <b>{@code (arsonite)}</b>
 * @see teaType.data.bi.BiPrimitive
 * @see teaType.data.bi.BiDouble
 * @see teaType.data.bi.BiInteger
 * @see teaType.data.bi.BiObject
 */
public class BiString implements BiPrimitive {
	private String s1, s2;

	/**
	 * 
	 * 
	 * @param s1 The first string part of the BiString
	 * @param s2 The second string part of the BiString
	 */
	public BiString(String s1, String s2) {
		setFirstString(s1);
		setSecondString(s2);
	}

	/**
	 * 
	 * 
	 * @param s1
	 */
	public void setFirstString(String s1) { this.s1 = s1; }
	
	/**
	 * 
	 * 
	 * @param s2
	 */
	public void setSecondString(String s2) { this.s2 = s2; }

	/**
	 * 
	 * 
	 * @return
	 */
	public String getFirstString() { return s1; }
	
	/**
	 * 
	 * 
	 * @return
	 */
	public String getSecondString() { return s2; }

	@Override
	public void clear() {
	}

	@Override
	public void random(int bound) {
	}
}