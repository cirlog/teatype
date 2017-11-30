package teaType.data.bi;

public class StringDouble {
	private String s;
	private double d;
	
	public StringDouble(String s, double d) {
		setString(s);
		setDouble(d);
	}
	
	public void setString(String s) { this.s = s; }
	
	public void setDouble(double d) { this.d = d; }
	
	public String getString() { return s; }
	
	public double getDouble() { return d; }
}