package teaType._debug.commonTests;

public class ForEach {
	public static void main(String[] args) {
		int[] i = new int[100];
		
		for(int integer : i) {
			i[integer] = (int) (Math.random()*1000);
		}
		
		for(Integer integer : i) {
			System.out.println(i[integer]);
		}
	}
}
