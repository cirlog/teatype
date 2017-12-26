package teaType.data.bi;

/**
 * The class {@code BiObject}
 * 
 * @since 2017
 * @author Burak Günaydin<br><i>aka</i> <b>{@code arsonite}</b>
 * @see teaType.data.bi.BiDouble
 * @see teaType.data.bi.BiInteger
 * @see teaType.data.bi.BiString
 */
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