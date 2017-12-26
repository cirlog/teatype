package teaType.data.bi;

/**
 * The class {@code }
 * 
 * @since 
 * @author Burak Günaydin<br><i>aka</i> <b>{@code arsonite}</b>
 */
public class BooleanDouble {
	private boolean b;
	private double d;

	public BooleanDouble(boolean b, double d) {
		setBoolean(b);
		setDouble(d);
	}

	public void setBoolean(boolean b) { this.b = b; }
	public void setDouble(double d) { this.d = d; }

	public boolean getBoolean() { return b; }
	public double getDouble() { return d; }
}