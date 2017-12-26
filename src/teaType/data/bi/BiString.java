package teaType.data.bi;

/**
 * The class {@code BiString}
 * 
 * @since 2017
 * @author Burak Günaydin<br><i>aka</i> <b>{@code arsonite}</b>
 * @see teaType.data.bi.BiDouble
 * @see teaType.data.bi.BiInteger
 * @see teaType.data.bi.BiObject
 */
public class BiString {
	private String s1, s2;

	public BiString(String s1, String s2) {
		setFirstString(s1);
		setSecondString(s2);
	}

	public void setFirstString(String s1) { this.s1 = s1; }
	public void setSecondString(String s2) { this.s2 = s2; }

	public String getFirstString() { return s1; }
	public String getSecondString() { return s2; }
}