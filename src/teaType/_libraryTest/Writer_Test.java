package teaType._libraryTest;

import java.util.ArrayList;

import teaType.util.io.Writer;

public class Writer_Test {
	public static void main(String[] args) {
		Writer w = new Writer("test.txt");
		ArrayList<String> list = new ArrayList<String>();
		list.add("!String!");
		list.add("#84124#");
		list.add("-Sword of the Sun-");
		list.add(";;");
		w.arraylist(list, true, true, true, false, true);
	}
}