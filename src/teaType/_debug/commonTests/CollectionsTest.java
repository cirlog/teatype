package teaType._debug.commonTests;

import java.io.PrintWriter;
import java.util.ArrayList;

public class CollectionsTest {
	public static void main(String[] args) {
		PrintWriter out = new PrintWriter(System.out, true);
		
		ArrayList<String> list = new ArrayList<String>(10);
		list.add("");
		out.println(list.size());
	}
}