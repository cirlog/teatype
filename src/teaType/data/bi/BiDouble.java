package teaType.data.bi;

/**
 * The class {@code BiDouble}
 * 
 * @since 2017
 * @author Burak Günaydin<br><i>aka</i> <b>{@code arsonite}</b>
 * @see teaType.data.bi.BiInteger
 * @see teaType.data.bi.BiObject
 * @see teaType.data.bi.BiString
 */
public class BiDouble {
	private double d1, d2;

	public BiDouble(double d1, double d2) {
		setFirstDouble(d1);
		setSecondDouble(d2);
	}
	
	public void setFirstDouble(double d1) { this.d1 = d1; }
	public void setSecondDouble(double d2) { this.d2 = d2; }

	public double getFirstDouble() { return d1; }
	public double getSecondDouble() { return d2; }
}