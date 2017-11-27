package teaType._debug.libraryTests;

import teaType.util.io.Reader;

public class Reader_Test {
	public static void main(String[] args) {
		Reader r = new Reader();
		String s = "./src/teaType/_debug/_ressources/StringTest.txt";
		String[] arr = r.fileToString(s);
		for(String string : arr) {
			System.out.println(string);
		}
	}
}