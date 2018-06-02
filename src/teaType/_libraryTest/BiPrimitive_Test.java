package teaType._libraryTest;

import teaType.data.BiPrimitive;

public class BiPrimitive_Test {
	public static void main(String[] args) {
		BiPrimitive p = new BiPrimitive("String", 1);
		p.print();
		p.clear();
		p.print();
		p.setFirst("Bepis");
		p.print();
	}
}