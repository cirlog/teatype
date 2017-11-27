package teaType.util.statics;

import java.io.PrintWriter;

public class Print {
	private final static PrintWriter out = new PrintWriter(System.out, true);

	public static final void stringArray(String[] arr, boolean linebreak, boolean whitespace) {
		for(String s : arr) {
			if(linebreak) {
				out.println(s);
			} else {
				if(whitespace) {
					out.print(s + " ");	
				} else {
					out.print(s);
				}
			}
		}
		out.flush();
		out.println();
	}

	public static final void integerArray(int[] arr, boolean linebreak, boolean whitespace) {
		for(int i : arr) {
			if(linebreak) {
				out.println(i);
			} else {
				if(whitespace) {
					out.print(i + " ");	
				} else {
					out.print(i);
				}
			}
		}
		out.flush();
		out.println();
	}
}