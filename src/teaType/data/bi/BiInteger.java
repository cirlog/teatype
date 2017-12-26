package teaType.data.bi;

/**
 * The class {@code BiInteger}
 * 
 * @since 2017
 * @author Burak Günaydin<br><i>aka</i> <b>{@code arsonite}</b>
 * @see teaType.data.bi.BiDouble
 * @see teaType.data.bi.BiObject
 * @see teaType.data.bi.BiString
 */
public class BiInteger {
	private int i1, i2;

	public BiInteger(int i1, int i2) {
		setFirstInteger(i1);
		setSecondInteger(i2);
	}
	
	public void setFirstInteger(int i1) { this.i1 = i1; }
	public void setSecondInteger(int i2) { this.i2 = i2; }

	public int getFirstInteger() { return i1; }
	public int getSecondInteger() { return i2; }
}