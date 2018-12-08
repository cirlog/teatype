package teaType._libraryTest;

import java.io.PrintWriter;
import java.util.ArrayList;

import teaType.util.Array;
import teaType.util.io.Reader;
import teaType.util.io.Writer;

public class Names_Test {
	public static void main(String[] args) {
		PrintWriter out = new PrintWriter(System.out, true);
		
		Reader r = new Reader();
		
		String[] data = r.stringArray("surnames.txt");
		
		for(int i = 0; i < data.length; i++) {
			StringBuilder sb = new StringBuilder();
			String s = data[i].replaceAll("\\d", "").replaceAll("\\.", "").trim();
			String[] arr = new String[2];
			arr[0] = s.substring(0, 1);
			arr[1] = s.substring(1, s.length()).toLowerCase();
			sb.append(arr[0] + arr[1]);
			
			data[i] = sb.toString();
		}

		ArrayList<String> list = Array.toArrayList(data);
		Writer w = new Writer("sur_names.txt");
		w.arraylist(list, true, true, true, false, false);
	}
}
