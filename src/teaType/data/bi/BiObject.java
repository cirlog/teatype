package teaType.data.bi;

public class BiObject {
	private Object o1, o2;

	public BiObject(Object o1, Object o2) {
		setFirstObject(o1);
		setSecondObject(o2);
	}
	
	public void setSecondObject(Object o2) { this.o2 = o2; }

	public void setFirstObject(Object o1) { this.o1 = o1; }
	
	public Object getFirstObject() { return o1; }

	public Object getSecondObject() { return o2; }
}