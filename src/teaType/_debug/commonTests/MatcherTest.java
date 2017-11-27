package teaType._debug.commonTests;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class MatcherTest {
	public static void main(String[] args) {
		String s = "Burak #ist der allerbeste #auf der ganzen Welt."
				+ "Pokemon";
		Pattern p = Pattern.compile("#.*#");
		Matcher m = p.matcher(s);
		
		while(m.find()) {
			System.out.println(m.group());
		}
	}
}