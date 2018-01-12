package teaType._libraryTest;

import teaType.util.Array;
import teaType.util.rigid.Random;

public class Sort_Test {
	public static void main(String[] args) {
		int[] arr = Random.generateInteger(20, 1000, false, false, false);
		Array.quicksort(arr, true);
		Array.print(arr, true, true);
	}
}