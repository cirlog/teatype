package teaType.data.bi;

public class StringBoolean {
	private String s;
	private boolean b;

	public StringBoolean(String s, boolean b) {
		setString(s);
		setBoolean(b);
	}

	public void setString(String s) { this.s = s; }
	
	public void setBoolean(boolean b) { this.b = b; }
	
	public String getString() { return s; }
	
	public boolean getBoolean() { return b; }
}