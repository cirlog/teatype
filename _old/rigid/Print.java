package teaType.util.rigid;

import java.io.PrintStream;
import java.io.UnsupportedEncodingException;

public class Print {
	public static void lines(String text) {
		for(int i = 0; i < text.length(); i++) {
			System.out.print("-");
		}
		System.out.println();
	}

	public static void unicodeTable(int bound, boolean displayHex) throws UnsupportedEncodingException {
		PrintStream out = new PrintStream(System.out, true, "UTF-8");
		String hex;
		for(int i = 33; i < bound; i++) {
			hex = Integer.toHexString(i);
			if(displayHex) {
				out.println(hex + " = " + (char) i);
			} else {
				out.println((char) i);
			}
		}
	}
}
