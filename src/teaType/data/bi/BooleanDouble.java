package teaType.data.bi;

/**
 * The class {@code BooleanDouble} is a very simple dual-primitive data-type.<br>
 * It's main and (only) intended use is the storing of two independent
 * values.<br>
 * One {@code boolean} and one {@code double} value.
 * 
 * @since JDK 1.91 ~ <i>2017</i>
 * @author Burak Günaydin <b>{@code (arsonite)}</b>
 * @see teaType.data.bi.BiPrimitive
 * @see teaType.data.bi.StringBoolean
 * @see teaType.data.bi.StringColor
 * @see teaType.data.bi.StringDouble
 * @see teaType.data.bi.StringInteger
 */
public class BooleanDouble implements BiPrimitive {
	private boolean b;
	final boolean fb;
	private double d;
	final double fd;

	public BooleanDouble(boolean b, double d) {
		setBoolean(b);
		setDouble(d);
	}

	public void setBoolean(boolean b) { this.b = b; }
	public void setDouble(double d) { this.d = d; }

	public boolean getBoolean() { return b; }
	public double getDouble() { return d; }

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