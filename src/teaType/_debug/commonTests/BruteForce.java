package teaType._debug.commonTests;

import java.util.Scanner;

public class BruteForce {
	public static void main(String[] args) {
		String input = new Scanner(System.in).next();
		boolean cracked = crack(input);
		if(cracked) {
			System.out.println("Done! " + input);
		}
	}
	
	private final static boolean crack(String input) {
		String s = "";
		StringBuilder sb = new StringBuilder();
		Scanner in = new Scanner(s);
		while(s != input) {
			if(in.hasNextInt()) {
				for(int i = 0; i < s.length()*9*26; i++) {
					for(int i2 = 0; i2 < s.length(); i2++) {
					}
				}
			} else {
				for(int i = 0; i < s.length()*26; i++) {
					
				}
			}
		}
		return true;
	}
}