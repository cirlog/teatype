package teaType._debug.commonTests;

import java.io.PrintWriter;

public class RegexTest {
	public static void main(String[] args) {
		PrintWriter out = new PrintWriter(System.out, true);
		//String s = "Name=Franz&Nummer=2";
		//s = s.replaceAll("Name=", "").replaceAll("&", " ").replaceAll("Nummer=", "");
		//out.println(s);
		
		//String host = "n";
		//int port = Integer.parseInt(98 + host.replaceAll("[^\\d]+", ""));
		//out.println(port);
		
//		String s = "GET /?A=Name&B=Number&C=Starte+Suche HTTP/1.1\n";
//		String name = s.replaceAll("GET /\\?A=", "").replaceAll("&B.*", "");
//		String number = s.replaceAll("GET /\\?A=.*&B=", "").replaceAll("&[CD].*", "");
//		String action = s.replaceAll("GET /\\?A=.+&[CD]+?=", "").replaceAll("\\+", "").replaceAll(" HTTP/1.1", "");
//		out.printf("%s%n%s%n%s%n%s%n", s, name, number, action);
		
		Utility u = new Utility();
		String name1 = "Büßtermann";
		String name2 = "Stör";
		String name3 = "Uwe";
		
		name1 = u.replaceVowel(name1);
		System.out.println(name1 + "\n");
		
		name1 = u.replaceVowel(name2);
		System.out.println(name2 + "\n");
		
		name1 = u.replaceVowel(name3);
		System.out.println(name3);
		
	}
}
