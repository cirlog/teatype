package teaType.data.bi;

public class BooleanDouble {
	private boolean b;
	private double d;

	public BooleanDouble(boolean b, double d) {
		setBoolean(b);
		setDouble(d);
	}

	public void setBoolean(boolean b) {
		this.b = b;
	}

	public void setDouble(double d) {
		this.d = d;
	}

	public boolean getBoolean() {
		return b;
	}
	
	public double getDouble() {
		return d;
	}
}