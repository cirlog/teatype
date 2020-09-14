package teaType.util.rigid;

import java.io.File;
import java.io.IOException;

import java.util.ArrayList;
import java.util.Scanner;
import java.util.regex.Pattern;

import teaType.util.io.Reader;

public class Replacer {
	public static Reader r;
	public static Scanner in;

	public Replacer() {
	}

	public static void replaceWithStrings(File file) throws IOException {
		// TODO: Better & more efficient code
		in = new Scanner(file);
		ArrayList<String> l = new ArrayList<String>();
		while(in.hasNextLine()) {
			l.add(in.nextLine());
		}
		String[] arr = new String[l.size()];
		int count = 0;
		for(String string : l) {
			in = new Scanner(string);
			arr[count] = in.next(Pattern.compile("[A-Z]*")).toLowerCase();
			count++;
		}
		Writer.stringArrayToFile(arr, file, true, true, true);
	}

	public void replaceWithIntegers() {

	}

	public void replaceWithRegex() {

	}
}