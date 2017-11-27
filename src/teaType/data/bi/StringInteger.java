package teaType.data.bi;

public class StringInteger {
	private String s;
	private int i;

	public StringInteger(String s, int i) {
		setString(s);
		setInteger(i);
	}
	
	public void setString(String s) {
		this.s = s;
	}
	
	public void setInteger(int i) {
		this.i = i;
	}

	public String getString() {
		return s;
	}

	public int getInteger() {
		return i;
	}
}