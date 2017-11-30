package teaType._debug.commonTests;

public class RegexTest {
	public static void main(String[] args) {
		String s = "Name=Franz&Nummer=2";
		s = s.replaceAll("Name=", "").replaceAll("&", " ").replaceAll("Nummer=", "");
		System.out.println(s);
	}
}
