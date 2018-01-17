package teaType._libraryTest;

import teaType.data.TeaType;

public class TeaType_Test {
	public static void main(String[] args) {		
		TeaType<Object> tt = new TeaType<Object>();
		tt.add("Sup");
		tt.add(3);
		tt.add(0.5);
		tt.add(true);
		tt.print();
	}
}