package teaType.util.statics;

import java.io.PrintStream;
import java.io.UnsupportedEncodingException;

public class UnicodeTable {
	public static void print(int bound, boolean displayHex) throws UnsupportedEncodingException {
		PrintStream out = new PrintStream(System.out, true, "UTF-8");
		String hex;
		
		for (int i = 33; i < bound; i++) {
			hex = Integer.toHexString(i);
			if(displayHex) {
				out.println(hex + " = " + (char) i);
			} else {
				out.println((char) i);
			}
		}
	}
}