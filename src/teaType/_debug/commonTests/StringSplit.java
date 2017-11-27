package teaType._debug.commonTests;

public class StringSplit {
	public static void main(String[] args) {
		String[] arr = {"abc123", "ABC123", "Meier12345", "aabbcc123"};
		String[] temp;
		for(String s : arr) {
			temp = new String[2];
			temp = s.split("(?<=\\D)(?=\\d)");
			System.out.println(temp[0] + " " + temp[1]);
		}
	}
}