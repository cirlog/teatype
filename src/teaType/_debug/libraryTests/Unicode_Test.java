package teaType._debug.libraryTests;

import java.io.UnsupportedEncodingException;

import teaType.util.rigid.UnicodeTable;

public class Unicode_Test {
	public static void main(String[] args) {
		try {
			UnicodeTable.print(3000, false);
		} catch (UnsupportedEncodingException e) {
			e.printStackTrace();
		}
	  }
}