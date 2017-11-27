package teaType.data.bi;

public class BiInteger {
	private int i1;
	private int i2;

	public BiInteger(int i1, int i2) {
		setFirstInteger(i1);
		setSecondInteger(i2);
	}
	
	public void setFirstInteger(int i1) {
		this.i1 = i1;
	}
	
	public void setSecondInteger(int i2) {
		this.i2 = i2;
	}

	public int getFirstInteger() {
		return i1;
	}

	public int getSecondInteger() {
		return i2;
	}
}