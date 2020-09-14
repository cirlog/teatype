package teaType.util.rigid;

import java.util.Scanner;

public class Parse {
	static String userInput;
	static Scanner in;

	public static String parseUserInput(boolean line) {
		in = new Scanner(System.in);
		if(line) {
			return userInput = in.nextLine();
		} else {
			return userInput = in.next();
		}
	}

	public static String toString(int i) { return String.valueOf(i); }

	public static String toString(double d) { return String.valueOf(d); }

	public static String toString(long l) { return String.valueOf(l); }

	public static String toString(float f) { return String.valueOf(f); }

	public static String toString(boolean b) { return String.valueOf(b); }

	public static int toInteger(String s) {
		in = new Scanner(s);
		if(in.hasNextInt()) {
			return Integer.parseInt(in.next());
		}
		return 0;
	}

	public static int toInteger(double d) { return (int) (d); }

	public static int toInteger(boolean b) {
		if(b) {
			return 1;
		} else {
			return 0;
		}
	}
}