package teaType.data.bi;

import java.awt.Color;

public class StringColor {
	private String s;
	private Color c;

	public StringColor(String s, Color c) {
		setString(s);
		setColor(c);
	}

	public void setString(String s) {
		this.s = s;
	}
	
	public void setColor(Color c) {
		this.c = c;
	}
	
	public String getString() {
		return s;
	}

	public Color getColor() {
		return c;
	}
}