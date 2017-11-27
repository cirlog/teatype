package teaType.util.statics;

import java.util.Scanner;

public class Parser {
	private static Scanner in;
	@SuppressWarnings("unused")
	private static String userInput;
	
	public static String parseUserInput() {
		in = new Scanner(System.in);
		return userInput = in.next();
	}
	
	public static String parseString() {
		return null;
	}
	
	public static int parseInt() {
		return 0;
	}

	public static char parseChar() {
		return 0;
	}

	public static double parseDouble() {
		return 0;
	}

	public static float parseFloat() {
		return 0;
	}
	
	public static String[] parseStringArray() {
		return null;
	}
	
	public static int[] parseIntegerArray() {
		return null;
	}
	
	public static char[] parseCharArray() {
		return null;
	}
}